# -*- coding: utf8 -*-
# -----------------------------------------------------------------------------
# "THE NO-ALCOHOL BEER-WARE LICENSE" (Revision 42):
# Phyks (webmaster@phyks.me) wrote this file. As long as you retain this notice
# you can do whatever you want with this stuff (and you can also do whatever
# you want with this stuff without retaining it, but that's not cool...). If we
# meet some day, and you think this stuff is worth it, you can buy me a
# <del>beer</del> soda in return.
#                                                                   Phyks
# -----------------------------------------------------------------------------
from __future__ import unicode_literals

import unittest
from libbmc.tools import *


class TestTools(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(slugify(u"à&é_truc.pdf"), "ae_trucpdf")

    def test_parsed2Bibtex(self):
        parsed = {'type': 'article', 'id': 'test', 'field1': 'test1',
                  'field2': 'test2'}
        expected = ('@article{test,\n\tfield1={test1},\n' +
                    '\tfield2={test2},\n}\n\n')
        self.assertEqual(parsed2Bibtex(parsed), expected)

    def test_getExtension(self):
        self.assertEqual(getExtension('test.ext'), '.ext')

    def test_replaceAll(self):
        replace_dict = {"test": "bidule", "machin": "chose"}
        self.assertEqual(replaceAll("test machin truc", replace_dict),
                         "bidule chose truc")

if __name__ == '__main__':
    unittest.main()
