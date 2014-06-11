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
from backend import *
from bibtexparser.bparser import BibTexParser
import shutil
import tempfile


class TestFetcher(unittest.TestCase):
    def setUp(self):
        params.folder = tempfile.mkdtemp()+"/"
        self.bibtex_article_string = """
@article{1303.3130v1,
	abstract={We study the role of the dipolar interaction, correctly accounting for the
Dipolar-Induced Resonance (DIR), in a quasi-one-dimensional system of ultracold
bosons. We first show how the DIR affects the lowest-energy states of two
particles in a harmonic trap. Then, we consider a deep optical lattice loaded
with ultracold dipolar bosons. We describe this many-body system using an
atom-dimer extended Bose-Hubbard model. We analyze the impact of the DIR on the
phase diagram at T=0 by exact diagonalization of a small-sized system. In
particular, the resonance strongly modifies the range of parameters for which a
mass density wave should occur.},
	archiveprefix={arXiv},
	author={N. Bartolo and D. J. Papoular and L. Barbiero and C. Menotti and A. Recati},
	eprint={1303.3130v1},
	file={/home/phyks/Papers/N_Bartolo_A_Recati-j-2013.pdf},
	link={http://arxiv.org/abs/1303.3130v1},
	month={Mar},
	primaryclass={cond-mat.quant-gas},
	tag={},
	title={Dipolar-Induced Resonance for Ultracold Bosons in a Quasi-1D Optical
Lattice},
	year={2013},
}"""
        self.bibtex_article = BibTexParser(self.bibtex_article_string).get_entry_dict()
        self.bibtex_article = self.bibtex_article[self.bibtex_article.keys()[0]]

        self.bibtex_book_string = """
"""
        self.bibtex_book = BibTexParser(self.bibtex_book_string).get_entry_dict()
        self.bibtex_book = self.bibtex_book[self.bibtex_book.keys()[0]]

    def test_getNewName_article(self):
        self.assertEqual(getNewName("test.pdf", self.bibtex_article),
                         params.folder+"N_Bartolo_A_Recati-j-2013-v1.pdf")

    def test_getNewName_article_override(self):
        self.assertEqual(getNewName("test.pdf", self.bibtex_article, override_format="%f"),
                         params.folder+"N_Bartolo.pdf")

    def test_getNewName_book(self):
# TODO
        self.assertEqual(getNewName("test.pdf", self.bibtex_book),
                         params.folder+"")

    def test_getNewName_book_override(self):
# TODO
        self.assertEqual(getNewName("test.pdf", self.bibtex_book, override_format="%a"),
                         params.folder+"N_Bartolo.pdf")

    def test_bibtexAppend(self):
        bibtexAppend(self.bibtex)
        with open(params.folder+'index.bib', 'r') as fh:
            self.assertEqual(fh.read(),
                             '@article{1303.3130v1,\n\tabstract={We study the role of the dipolar interaction, correctly accounting for the\nDipolar-Induced Resonance (DIR), in a quasi-one-dimensional system of ultracold\nbosons. We first show how the DIR affects the lowest-energy states of two\nparticles in a harmonic trap. Then, we consider a deep optical lattice loaded\nwith ultracold dipolar bosons. We describe this many-body system using an\natom-dimer extended Bose-Hubbard model. We analyze the impact of the DIR on the\nphase diagram at T=0 by exact diagonalization of a small-sized system. In\nparticular, the resonance strongly modifies the range of parameters for which a\nmass density wave should occur.},\n\tarchiveprefix={arXiv},\n\tauthor={N. Bartolo and D. J. Papoular and L. Barbiero and C. Menotti and A. Recati},\n\teprint={1303.3130v1},\n\tfile={/home/phyks/Papers/N_Bartolo_A_Recati-j-2013.pdf},\n\tlink={http://arxiv.org/abs/1303.3130v1},\n\tmonth={Mar},\n\tprimaryclass={cond-mat.quant-gas},\n\ttag={},\n\ttitle={Dipolar-Induced Resonance for Ultracold Bosons in a Quasi-1D Optical\nLattice},\n\tyear={2013},\n}\n\n\n')

    def test_bibtexEdit(self):
# TODO
        return

    def test_bibtexRewrite(self):
# TODO
        return

    def test_deleteId(self):
# TODO
        return

    def test_deleteFile(self):
# TODO
        return

    def test_diffFilesIndex(self):
# TODO
        return

    def test_getBibtex(self):
# TODO
        return

    def test_getEntries(self):
# TODO
        return

    def test_updateArxiv(self):
# TODO
        return

    def tearDown(self):
        shutil.rmtree(params.folder)

if __name__ == '__main__':
    unittest.main()
