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

import unittest
from libbmc.fetcher import *


class TestFetcher(unittest.TestCase):
    def setUp(self):
        with open("libbmc/tests/src/doi.bib", 'r') as fh:
            self.doi_bib = fh.read()
        with open("libbmc/tests/src/arxiv.bib", 'r') as fh:
            self.arxiv_bib = fh.read()
        with open("libbmc/tests/src/isbn.bib", 'r') as fh:
            self.isbn_bib = fh.read()

    def test_download(self):
        dl, contenttype = download('http://arxiv.org/pdf/1312.4006.pdf')
        self.assertIn(contenttype, ['pdf', 'djvu'])
        self.assertNotEqual(dl, '')

    def test_download_invalid_type(self):
        self.assertFalse(download('http://phyks.me/')[0])

    def test_download_invalid_url(self):
        self.assertFalse(download('a')[0])

    def test_findISBN_DJVU(self):
        # ISBN is incomplete in this test because my djvu file is bad
        self.assertEqual(findISBN("libbmc/tests/src/test_book.djvu"), '978295391873')

    def test_findISBN_PDF(self):
        self.assertEqual(findISBN("libbmc/tests/src/test_book.pdf"), '9782953918731')

    def test_findISBN_False(self):
        self.assertFalse(findISBN("libbmc/tests/src/test.pdf"))

    def test_isbn2Bib(self):
        self.assertEqual(isbn2Bib('0198507194'), self.isbn_bib)

    def test_isbn2Bib_False(self):
        self.assertEqual(isbn2Bib('foo'), '')

    def test_findDOI_PDF(self):
        self.assertEqual(findArticleID("libbmc/tests/src/test.pdf"),
                         ("DOI", "10.1103/physrevlett.112.253201"))

    def test_findOnlyDOI(self):
        self.assertEqual(findArticleID("libbmc/tests/src/test.pdf",
                                only=["DOI"]),
                         ("DOI", "10.1103/physrevlett.112.253201"))

    def test_findDOID_DJVU(self):
        # DOI is incomplete in this test because my djvu file is bad
        self.assertEqual(findArticleID("libbmc/tests/src/test.djvu"),
                         ("DOI", "10.1103/physrevlett.112"))

    def test_findDOI_False(self):
        self.assertFalse(findArticleID("libbmc/tests/src/test_arxiv_multi.pdf",
                                       only=["DOI"])[0])

    def test_doi2Bib(self):
        self.assertEqual(doi2Bib('10.1103/physreva.88.043630'), self.doi_bib)

    def test_doi2Bib_False(self):
        self.assertEqual(doi2Bib('blabla'), '')

    def test_findArXivId(self):
        self.assertEqual(findArticleID("libbmc/tests/src/test_arxiv_multi.pdf"),
                         ("arXiv", '1303.3130v1'))

    def test_findOnlyArXivId(self):
        self.assertEqual(findArticleID("libbmc/tests/src/test_arxiv_multi.pdf",
                                only=["arXiv"]),
                         ("arXiv", '1303.3130v1'))

    def test_findArticleID(self):
        # cf https://github.com/Phyks/BMC/issues/19
        self.assertEqual(findArticleID("libbmc/tests/src/test_arxiv_doi_conflict.pdf"),
                         ("arXiv", '1107.4487v1'))

    def test_arXiv2Bib(self):
        self.assertEqual(arXiv2Bib('1303.3130v1'), self.arxiv_bib)

    def test_arXiv2Bib_False(self):
        self.assertEqual(arXiv2Bib('blabla'), '')

    def test_findHALId(self):
        self.assertTupleEqual(findHALId("libbmc/tests/src/test_hal.pdf"),
                              ('hal-00750893', '3'))

if __name__ == '__main__':
    unittest.main()
