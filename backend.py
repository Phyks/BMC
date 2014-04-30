#!/usr/bin/env python2
# coding=utf8

import os
import re
import tools
import params
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import homogeneize_latex_encoding
from bibtexparser.bwriter import bibtex as bibTexWriter


def getNewName(src, bibtex):
    """
    Return the formatted name according to params for the given
    bibtex entry
    """
    authors = re.split(' and ', bibtex['author'])

    if bibtex['type'] == 'article':
        new_name = params.format_articles
        try:
            new_name = new_name.replace("%j", bibtex['journal'])
        except:
            pass
    elif bibtex['type'] == 'book':
        new_name = params.format_books

    new_name = new_name.replace("%t", bibtex['title'])
    try:
        new_name = new_name.replace("%Y", bibtex['year'])
    except:
        pass
    new_name = new_name.replace("%f", authors[0].split(',')[0].strip())
    new_name = new_name.replace("%l", authors[-1].split(',')[0].strip())
    new_name = new_name.replace("%a", ', '.join([i.split(',')[0].strip()
                                                for i in authors]))

    new_name = params.folder+tools.slugify(new_name)+tools.getExtension(src)


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


def bibtexEdit(ident, modifs):
    """Update ident key in bibtex file, modifications are in modifs dict"""

    with open(params.folder+'index.bib', 'r') as fh:
        bibtex = BibTexParser(fh.read(),
                              customization=homogeneize_latex_encoding)
    bibtex = bibtex.get_entry_dict()

    for key in modifs.keys():
        bibtex[ident][key] = modifs[key]
    bibtexRewrite(bibtex)


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
    try:
        del(bibtex[ident])
        bibtexRewrite(bibtex)
    except KeyError:
        tools.warning("No associated bibtex entry in index for file " +
                      bibtex[ident]['file'])
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
            try:
                del(bibtex[key])
            except KeyError:
                tools.warning("No associated bibtex entry in index for file " +
                              bibtex[key]['file'])
    if found:
        bibtexRewrite(bibtex)
    return found


def diffFilesIndex():
    """Compute differences between Bibtex index and PDF files

    Returns a dict with bibtex entry:
        * full bibtex entry with file='' if file is not found
        * only file entry if file with missing bibtex entry
    """

    files = tools.listDir(params.folder)
    with open(params.folder+'index.bib', 'r') as fh:
        index = BibTexParser(fh.read(),
                             customization=homogeneize_latex_encoding)

    index_diff = index.get_entry_dict()

    for key in index_diff.keys():
        if index_diff[key]['file'] not in files:
            index_diff[key]['file'] = ''
        else:
            files.remove(index_diff[key]['file'])

    for filename in files:
        index_diff[filename] = {'file': filename}

    return index
