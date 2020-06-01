import os
import tempfile
import urllib.request
import xml.dom.minidom
import xml.etree.ElementTree as ET
import gevent

from bs4 import BeautifulSoup
from tinytag import TinyTag
from urllib.error import HTTPError, URLError


def url_to_links(url):
    try:
        main_page_req = urllib.request.Request(url)
        html_page = urllib.request.urlopen(main_page_req)
        soup = BeautifulSoup(html_page, 'html.parser')
        return [x.get('href') for x in soup.find_all('a')]
    except urllib.error.HTTPError:
        return []


def get_mp3_links(links, digest_level, *, use_gevent):
    visited_links = set()
    mp3_links = []

    def link_to_absolute(base_url, link):
        url = urllib.parse.urljoin(base_url, link)
        parsed_url = urllib.request.urlparse(url)
        if parsed_url.scheme != "file":
            return parsed_url.scheme + "://" + parsed_url.netloc + urllib.parse.quote(parsed_url.path)
        else:
            return url

    def process_url(url, level):
        visited_links.add(url)
        _links = [link_to_absolute(url, link) for link in url_to_links(url)]
        links_to_visit = []
        for link in _links:
            if link.endswith(".mp3"):
                mp3_links.append(link)
            elif level > 1:
                req = urllib.request.Request(url, method="HEAD")
                response = urllib.request.urlopen(req)
                if link.endswith("html") or response.getheader("Content-Type").startswith("text/html"):
                    links_to_visit.append(link)
        if level > 1:
            for link in links_to_visit:
                if link not in visited_links:
                    process_url(link, level - 1)

    if use_gevent:
        jobs = [gevent.spawn(process_url, url, digest_level) for url in links]
        gevent.joinall(jobs)
    else:
        for url in links:
            process_url(url, digest_level)
    return mp3_links


def process_mp3s(mp3_links, *, use_gevent):
    analyzed_mp3_sorted_by_genre = {}
    tmp_dir = tempfile.TemporaryDirectory(suffix='mp3')

    def mp3_genre_title(mp3_filename):
        audio_tag = TinyTag.get(mp3_filename)
        if audio_tag.genre is None:
            audio_tag.genre = "Undefined"
        if audio_tag.title is None:
            audio_tag.title = "No-title"
        return audio_tag.genre, audio_tag.title

    def process_mp3(mp3_link):
        file_name = os.path.basename(urllib.parse.urlparse(mp3_link).path)
        try:
            print(f"Load {file_name}")
            req = urllib.request.Request(mp3_link, headers={"Range": "bytes:0-4000"})
            with urllib.request.urlopen(req) as response, \
                    tempfile.NamedTemporaryFile(mode="w+b", delete=False, dir=tmp_dir.name) as out_file:
                data = response.read()
                out_file.write(data)
                tmp_filename = out_file.name
            genre, title = mp3_genre_title(tmp_filename)
            if genre not in analyzed_mp3_sorted_by_genre:
                analyzed_mp3_sorted_by_genre[genre] = []
            analyzed_mp3_sorted_by_genre[genre].append({"filename": file_name, "title": title, "link": mp3_link})
        except URLError:
            pass

    if use_gevent:
        jobs = [gevent.spawn(process_mp3, mp3_link) for mp3_link in mp3_links]
        gevent.joinall(jobs)
    else:
        for mp3_link in mp3_links:
            process_mp3(mp3_link)
    tmp_dir.cleanup()
    return analyzed_mp3_sorted_by_genre


def main():
    root = ET.parse("input.xml").getroot()
    use_gevent = False
    site_list = []
    for child in root:
        if child.tag == "site":
            site_list.append(child.text)

        if child.tag == "gevent":
            use_gevent = child.text.lower() == "true"

    mp3_links = get_mp3_links(site_list, 1, use_gevent=use_gevent)
    analyzed_res = process_mp3s(mp3_links, use_gevent=use_gevent)
    with open("output.xml", "wb") as res_file:
        root1 = ET.Element('Playlist')
        for key, value in analyzed_res.items():
            genre_node = ET.SubElement(root1, 'Genre', {'name': key})
            for mp3_info in value:
                mp3_info_node = ET.SubElement(genre_node, 'music')
                ET.SubElement(mp3_info_node, 'filename').text = mp3_info['filename']
                ET.SubElement(mp3_info_node, 'title').text = mp3_info['title']
                ET.SubElement(mp3_info_node, 'link').text = mp3_info['link']
        mydata = ET.tostring(root1, encoding="unicode")
        preparsed = xml.dom.minidom.parseString(mydata)
        res_file.write(preparsed.toprettyxml().encode("utf-8"))


main()
