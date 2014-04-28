#!/usr/bin/env python2
# coding=utf8

import os
import tools
import params
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import homogeneize_latex_encoding
from bibtexparser.bwriter import bibtex as bibTexWriter


def parsed2Bibtex(parsed):
    """Convert a single bibtex entry dict to bibtex string"""
    bibtex = '@'+parsed['type']+'{'+parsed['id']+",\n"

    for field in [i for i in sorted(parsed) if i not in ['type', 'id']]:
        bibtex += "\t"+field+"={"+parsed[field]+"},\n"
    bibtex += "}\n"
    return bibtex


def bibtexAppend(data):
    """Append data to the main bibtex file

    data is a dict for one entry in bibtex, as the one from bibtexparser output
    """
    with open(params.folder+'index.bib', 'a') as fh:
        fh.write(parsed2Bibtex(data)+"\n")


def bibtexRewrite(data):
    """Rewrite the bibtex index file.

    data is a dict of bibtex entry dict.
    """
    bibtex = ''
    for entry in data.keys():
        bibtex += parsed2Bibtex(data[entry])+"\n"
    with open(params.folder+'index.bib', 'w') as fh:
        fh.write(bibtex)


def deleteId(ident):
    """Delete a file based on its id in the bibtex file"""
    with open(params.folder+'index.bib', 'r') as fh:
        bibtex = BibTexParser(fh.read(),
                              customization=homogeneize_latex_encoding)
    bibtex = bibtex.get_entry_dict()

    if ident not in bibtex.keys():
        return False

    try:
        os.remove(bibtex[ident]['file'])
    except:
        tools.warning("Unable to delete file associated to id "+ident+" : " +
                      bibtex[ident]['file'])
    del(bibtex[ident])
    bibtexRewrite(bibtex)
    return True


def deleteFile(filename):
    """Delete a file based on its filename"""
    with open(params.folder+'index.bib', 'r') as fh:
        bibtex = BibTexParser(fh.read(),
                              customization=homogeneize_latex_encoding)
    bibtex = bibtex.get_entry_dict()

    found = False
    for key in bibtex.keys():
        if bibtex[key]['file'] == filename:
            found = True
            try:
                os.remove(bibtex[key]['file'])
            except:
                tools.warning("Unable to delete file associated to id " +
                              key+" : "+bibtex[key]['file'])
            del(bibtex[key])
    if found:
        bibtexRewrite(bibtex)
    return found
