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
from config import config
import os
import shutil
import tempfile


class TestFetcher(unittest.TestCase):
    def setUp(self):
        config.set("folder", tempfile.mkdtemp()+"/")
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
@book{9780521846516,
    author={C. J. Pethick and H. Smith},
    isbn={9780521846516},
    publisher={Cambridge University Press},
    title={Bose-Einstein Condensation In Dilute Gases},
    year={2008},
}
"""
        self.bibtex_book = BibTexParser(self.bibtex_book_string).get_entry_dict()
        self.bibtex_book = self.bibtex_book[self.bibtex_book.keys()[0]]

    def test_getNewName_article(self):
        self.assertEqual(getNewName("test.pdf", self.bibtex_article),
                         config.get("folder")+"N_Bartolo_A_Recati-j-2013-v1.pdf")

    def test_getNewName_article_override(self):
        self.assertEqual(getNewName("test.pdf", self.bibtex_article, override_format="%f"),
                         config.get("folder")+"N_Bartolo.pdf")

    def test_getNewName_book(self):
        self.assertEqual(getNewName("test.pdf", self.bibtex_book),
                         config.get("folder")+"C_J_Pethick_H_Smith-Bose-Einstein_Condensation_In_Dilute_Gases.pdf")

    def test_getNewName_book_override(self):
        self.assertEqual(getNewName("test.pdf", self.bibtex_book, override_format="%a"),
                         config.get("folder")+"C_J_Pethick_H_Smith.pdf")

    def test_bibtexAppend(self):
        bibtexAppend(self.bibtex_article)
        with open(config.get("folder")+'index.bib', 'r') as fh:
            self.assertEqual(fh.read(),
                             '@article{1303.3130v1,\n\tabstract={We study the role of the dipolar interaction, correctly accounting for the\nDipolar-Induced Resonance (DIR), in a quasi-one-dimensional system of ultracold\nbosons. We first show how the DIR affects the lowest-energy states of two\nparticles in a harmonic trap. Then, we consider a deep optical lattice loaded\nwith ultracold dipolar bosons. We describe this many-body system using an\natom-dimer extended Bose-Hubbard model. We analyze the impact of the DIR on the\nphase diagram at T=0 by exact diagonalization of a small-sized system. In\nparticular, the resonance strongly modifies the range of parameters for which a\nmass density wave should occur.},\n\tarchiveprefix={arXiv},\n\tauthor={N. Bartolo and D. J. Papoular and L. Barbiero and C. Menotti and A. Recati},\n\teprint={1303.3130v1},\n\tfile={/home/phyks/Papers/N_Bartolo_A_Recati-j-2013.pdf},\n\tlink={http://arxiv.org/abs/1303.3130v1},\n\tmonth={Mar},\n\tprimaryclass={cond-mat.quant-gas},\n\ttag={},\n\ttitle={Dipolar-Induced Resonance for Ultracold Bosons in a Quasi-1D Optical\nLattice},\n\tyear={2013},\n}\n\n\n')

    def test_bibtexEdit(self):
        bibtexAppend(self.bibtex_article)
        bibtexEdit(self.bibtex_article['id'], {'id': 'bidule'})
        with open(config.get("folder")+'index.bib', 'r') as fh:
            self.assertEqual(fh.read(),
                             '@article{bidule,\n\tabstract={We study the role of the dipolar interaction, correctly accounting for the\nDipolar-Induced Resonance (DIR), in a quasi-one-dimensional system of ultracold\nbosons. We first show how the DIR affects the lowest-energy states of two\nparticles in a harmonic trap. Then, we consider a deep optical lattice loaded\nwith ultracold dipolar bosons. We describe this many-body system using an\natom-dimer extended Bose-Hubbard model. We analyze the impact of the DIR on the\nphase diagram at T=0 by exact diagonalization of a small-sized system. In\nparticular, the resonance strongly modifies the range of parameters for which a\nmass density wave should occur.},\n\tarchiveprefix={arXiv},\n\tauthor={N. Bartolo and D. J. Papoular and L. Barbiero and C. Menotti and A. Recati},\n\teprint={1303.3130v1},\n\tfile={/home/phyks/Papers/N_Bartolo_A_Recati-j-2013.pdf},\n\tlink={http://arxiv.org/abs/1303.3130v1},\n\tmonth={Mar},\n\tprimaryclass={cond-mat.quant-gas},\n\ttag={},\n\ttitle={Dipolar-Induced Resonance for Ultracold Bosons in a Quasi-1D Optical\nLattice},\n\tyear={2013},\n}\n\n\n')

    def test_bibtexRewrite(self):
        bibtexAppend(self.bibtex_book)
        bibtexRewrite({0: self.bibtex_article})
        with open(config.get("folder")+'index.bib', 'r') as fh:
            self.assertEqual(fh.read(),
                             '@article{1303.3130v1,\n\tabstract={We study the role of the dipolar interaction, correctly accounting for the\nDipolar-Induced Resonance (DIR), in a quasi-one-dimensional system of ultracold\nbosons. We first show how the DIR affects the lowest-energy states of two\nparticles in a harmonic trap. Then, we consider a deep optical lattice loaded\nwith ultracold dipolar bosons. We describe this many-body system using an\natom-dimer extended Bose-Hubbard model. We analyze the impact of the DIR on the\nphase diagram at T=0 by exact diagonalization of a small-sized system. In\nparticular, the resonance strongly modifies the range of parameters for which a\nmass density wave should occur.},\n\tarchiveprefix={arXiv},\n\tauthor={N. Bartolo and D. J. Papoular and L. Barbiero and C. Menotti and A. Recati},\n\teprint={1303.3130v1},\n\tfile={/home/phyks/Papers/N_Bartolo_A_Recati-j-2013.pdf},\n\tlink={http://arxiv.org/abs/1303.3130v1},\n\tmonth={Mar},\n\tprimaryclass={cond-mat.quant-gas},\n\ttag={},\n\ttitle={Dipolar-Induced Resonance for Ultracold Bosons in a Quasi-1D Optical\nLattice},\n\tyear={2013},\n}\n\n\n')

    def test_deleteId(self):
        self.bibtex_article['file'] = config.get("folder")+'test.pdf'
        bibtexAppend(self.bibtex_article)
        open(config.get("folder")+'test.pdf', 'w').close()
        deleteId(self.bibtex_article['id'])
        with open(config.get("folder")+'index.bib', 'r') as fh:
            self.assertEquals(fh.read().strip(), "")
        self.assertFalse(os.path.isfile(config.get("folder")+'test.pdf'))

    def test_deleteFile(self):
        self.bibtex_article['file'] = config.get("folder")+'test.pdf'
        bibtexAppend(self.bibtex_article)
        open(config.get("folder")+'test.pdf', 'w').close()
        deleteFile(self.bibtex_article['file'])
        with open(config.get("folder")+'index.bib', 'r') as fh:
            self.assertEquals(fh.read().strip(), "")
        self.assertFalse(os.path.isfile(config.get("folder")+'test.pdf'))

    def test_diffFilesIndex(self):
        # TODO
        return

    def test_getBibtex(self):
        bibtexAppend(self.bibtex_article)
        got = getBibtex(self.bibtex_article['id'])
        self.assertEqual(got, self.bibtex_article)

    def test_getBibtex_id(self):
        bibtexAppend(self.bibtex_article)
        got = getBibtex(self.bibtex_article['id'], file_id='id')
        self.assertEqual(got, self.bibtex_article)

    def test_getBibtex_file(self):
        self.bibtex_article['file'] = config.get("folder")+'test.pdf'
        open(config.get("folder")+'test.pdf', 'w').close()
        bibtexAppend(self.bibtex_article)
        got = getBibtex(self.bibtex_article['file'], file_id='file')
        self.assertEqual(got, self.bibtex_article)

    def test_getBibtex_clean(self):
        config.set("ignore_fields", ['id', 'abstract'])
        bibtexAppend(self.bibtex_article)
        got = getBibtex(self.bibtex_article['id'], clean=True)
        for i in config.get("ignore_fields"):
            self.assertNotIn(i, got)

    def test_getEntries(self):
        bibtexAppend(self.bibtex_article)
        self.assertEqual(getEntries(),
                         [self.bibtex_article['id']])

    def test_updateArxiv(self):
        # TODO
        return

    def test_search(self):
        # TODO
        return

    def tearDown(self):
        shutil.rmtree(config.get("folder"))

if __name__ == '__main__':
    unittest.main()
