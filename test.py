import os
import unittest
import parser

dir_path = os.path.dirname(os.path.realpath(__file__))


class Tests(unittest.TestCase):
    def test1(self):
        links = ["file:///" + dir_path + "/resources/site.html"]
        result = parser.get_mp3_links(links, 2, use_gevent=False)
        self.assertEqual(["file:///" + dir_path + "/test-data/All Is Fair In Love And Brostep.mp3",
                          "file:///" + dir_path + "/test-data/Danheim -Vega.mp3"], result)

    def test2(self):
        links = ["file:///" + dir_path + "/test-data/site.html"]
        result = parser.get_mp3_links(links, 2, use_gevent=True)
        self.assertEqual(["file:///" + dir_path + "/test-data/All Is Fair In Love And Brostep.mp3",
                          "file:///" + dir_path + "/test-data/Danheim -Vega.mp3"], result)

    def test3(self):
        links = ["file:///" + dir_path + "/resources/All Is Fair In Love And Brostep.mp3"]
        result = parser.process_mp3s(links, use_gevent=False)
        expected = {'Dubstep / Breakbeat / Electro House': [{'filename': 'All Is Fair In Love And '
                                                                         'Brostep.mp3',
                                                             'link': 'file:///' + dir_path + '/resources/All '
                                                                                             'Is Fair In Love And '
                                                                                             'Brostep.mp3',
                                                             'title': 'All Is Fair In Love And '
                                                                      'Brostep (Feat. The Ragga '
                                                                      'Twins)'}]}
        self.assertEqual(expected, result)

    def test4(self):
        links = ["file:///" + dir_path + "/resources/All Is Fair In Love And Brostep.mp3"]
        result = parser.process_mp3s(links, use_gevent=True)
        expected = {'Dubstep / Breakbeat / Electro House': [{'filename': 'All Is Fair In Love And '
                                                                         'Brostep.mp3',
                                                             'link': 'file:///' + dir_path + '/resources/All '
                                                                                             'Is Fair In Love And '
                                                                                             'Brostep.mp3',
                                                             'title': 'All Is Fair In Love And '
                                                                      'Brostep (Feat. The Ragga '
                                                                      'Twins)'}]}
        self.assertEqual(expected, result)


def main():
    unittest.main()
