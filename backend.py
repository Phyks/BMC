#!/usr/bin/env python2
# coding=utf8

import os
import re
import tools
import fetcher
import params
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import homogeneize_latex_encoding


def getNewName(src, bibtex, tag=''):
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

    if tag == '':
        new_name = (params.folder + tools.slugify(new_name) +
                    tools.getExtension(src))
    else:
        if not os.path.isdir(params.folder + tag):
            try:
                os.mkdir(params.folder + tag)
            except:
                tools.warning("Unable to create tag dir " +
                              params.folder+tag+".")

        new_name = (params.folder + tools.slugify(tag) +
                    tools.slugify(new_name) + tools.getExtension(src))

    return new_name


def parsed2Bibtex(parsed):
    """Convert a single bibtex entry dict to bibtex string"""
    bibtex = '@'+parsed['type']+'{'+parsed['id']+",\n"

    for field in [i for i in sorted(parsed) if i not in ['type', 'id']]:
        bibtex += "\t"+field+"={"+parsed[field]+"},\n"
    bibtex += "}\n\n"
    return bibtex


def bibtexAppend(data):
    """Append data to the main bibtex file

    data is a dict for one entry in bibtex, as the one from bibtexparser output
    """
    try:
        with open(params.folder+'index.bib', 'a') as fh:
            fh.write(parsed2Bibtex(data)+"\n")
    except:
        tools.warning("Unable to open index file.")
        return False


def bibtexEdit(ident, modifs):
    """Update ident key in bibtex file, modifications are in modifs dict"""

    try:
        with open(params.folder+'index.bib', 'r') as fh:
            bibtex = BibTexParser(fh.read(),
                                  customization=homogeneize_latex_encoding)
        bibtex = bibtex.get_entry_dict()
    except:
        tools.warning("Unable to open index file.")
        return False

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
    try:
        with open(params.folder+'index.bib', 'w') as fh:
            fh.write(bibtex)
    except:
        tools.warning("Unable to open index file.")
        return False


def deleteId(ident):
    """Delete a file based on its id in the bibtex file"""
    try:
        with open(params.folder+'index.bib', 'r') as fh:
            bibtex = BibTexParser(fh.read(),
                                  customization=homogeneize_latex_encoding)
        bibtex = bibtex.get_entry_dict()
    except:
        tools.warning("Unable to open index file.")
        return False

    if ident not in bibtex.keys():
        return False

    try:
        os.remove(bibtex[ident]['file'])
    except:
        tools.warning("Unable to delete file associated to id "+ident+" : " +
                      bibtex[ident]['file'])

    try:
        if not os.listdir(os.path.dirname(bibtex[ident]['file'])):
            os.rmdir(os.path.dirname(bibtex[ident]['file']))
    except:
        tools.warning("Unable to delete empty tag dir " +
                      os.path.dirname(bibtex[ident]['file']))

    try:
        del(bibtex[ident])
        bibtexRewrite(bibtex)
    except KeyError:
        tools.warning("No associated bibtex entry in index for file " +
                      bibtex[ident]['file'])
    return True


def deleteFile(filename):
    """Delete a file based on its filename"""
    try:
        with open(params.folder+'index.bib', 'r') as fh:
            bibtex = BibTexParser(fh.read(),
                                  customization=homogeneize_latex_encoding)
        bibtex = bibtex.get_entry_dict()
    except:
        tools.warning("Unable to open index file.")
        return False

    found = False
    for key in bibtex.keys():
        if os.path.samepath(bibtex[key]['file'], filename):
            found = True
            try:
                os.remove(bibtex[key]['file'])
            except:
                tools.warning("Unable to delete file associated to id " +
                              key+" : "+bibtex[key]['file'])

            try:
                if not os.listdir(os.path.dirname(filename)):
                    os.rmdir(os.path.dirname(filename))
            except:
                tools.warning("Unable to delete empty tag dir " +
                              os.path.dirname(filename))

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
    try:
        with open(params.folder+'index.bib', 'r') as fh:
            index = BibTexParser(fh.read(),
                                 customization=homogeneize_latex_encoding)
        index_diff = index.get_entry_dict()
    except:
        tools.warning("Unable to open index file.")
        return False

    for key in index_diff.keys():
        if index_diff[key]['file'] not in files:
            index_diff[key]['file'] = ''
        else:
            files.remove(index_diff[key]['file'])

    for filename in files:
        index_diff[filename] = {'file': filename}

    return index


def getBibtex(entry, file_id='both'):
    """Returns the bibtex entry corresponding to entry, as a dict

    entry is either a filename or a bibtex ident
    file_id is file or id or both to search for a file / id / both
    """
    try:
        with open(params.folder+'index.bib', 'r') as fh:
            bibtex = BibTexParser(fh.read(),
                                  customization=homogeneize_latex_encoding)
        bibtex = bibtex.get_entry_dict()
    except:
        tools.warning("Unable to open index file.")
        return False

    bibtex_entry = False
    if file_id == 'both' or file_id == 'id':
        try:
            bibtex_entry = bibtex[entry]
        except KeyError:
            pass
    elif file_id == 'both' or file_id == 'file':
        for key in bibtex.keys():
            if os.path.samepath(bibtex[key]['file'], entry):
                bibtex_entry = bibtex[key]
                break
    return bibtex_entry


def getEntries():
    """Returns the list of all entries in the bibtex index"""
    try:
        with open(params.folder+'index.bib', 'r') as fh:
            bibtex = BibTexParser(fh.read(),
                                  customization=homogeneize_latex_encoding)
        bibtex = bibtex.get_entry_dict()
    except:
        tools.warning("Unable to open index file.")
        return False

    return bibtex.keys()


def updateArXiv(entry):
    bibtex = getBibtex(entry)
    # Check arXiv
    if('ArchivePrefix' not in bibtex and
       'arxiv' not in bibtex['ArchivePrefix']):
        return False

    arxiv_id = bibtex['Eprint']
    last_bibtex = BibTexParser(fetcher.arXiv2Bib(arxiv_id),
                               customization=homogeneize_latex_encoding)
    last_bibtex = last_bibtex.get_entry_dict()

    if last_bibtex['Eprint'] != arxiv_id:
        # New version available
        with open(bibtex['file'], 'w+') as fh:
            fh.write(fetcher.download(last_bibtex['Url']))
        bibtex['Eprint'] = last_bibtex['Eprint']
        bibtex['URL'] = last_bibtex['URL']
        for i in [j for j in last_bibtex.keys() if j not in bibtex.keys()]:
            bibtex[i] = last_bibtex[i]
        return last_bibtex
    else:
        return False
