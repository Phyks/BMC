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


import os
import re
import tools
import fetcher
import params
from bibtexparser.bparser import BibTexParser
from codecs import open


def getNewName(src, bibtex, tag='', override_format=None):
    """
    Return the formatted name according to params for the given
    bibtex entry
    """
    authors = re.split(' and ', bibtex['author'])

    if bibtex['type'] == 'article':
        if override_format is None:
            new_name = params.format_articles
        else:
            new_name = override_format
        try:
            new_name = new_name.replace("%j", bibtex['journal'])
        except:
            pass
    elif bibtex['type'] == 'book':
        if override_format is None:
            new_name = params.format_books
        else:
            new_name = override_format

    new_name = new_name.replace("%t", bibtex['title'])
    try:
        new_name = new_name.replace("%Y", bibtex['year'])
    except:
        pass
    new_name = new_name.replace("%f", authors[0].split(',')[0].strip())
    new_name = new_name.replace("%l", authors[-1].split(',')[0].strip())
    new_name = new_name.replace("%a", ', '.join([i.split(',')[0].strip()
                                                for i in authors]))
    if('archiveprefix' in bibtex and
       'arXiv' in bibtex['archiveprefix']):
        new_name = new_name.replace("%v",
                                    '-'+bibtex['eprint'][bibtex['eprint'].rfind('v'):])
    else:
        new_name = new_name.replace("%v", '')

    for custom in params.format_custom:
        new_name = custom(new_name)

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

        new_name = (params.folder + tools.slugify(tag) + '/' +
                    tools.slugify(new_name) + tools.getExtension(src))

    return new_name


def bibtexAppend(data):
    """Append data to the main bibtex file

    data is a dict for one entry in bibtex, as the one from bibtexparser output
    """
    try:
        with open(params.folder+'index.bib', 'a', encoding='utf-8') as fh:
            fh.write(tools.parsed2Bibtex(data)+"\n")
    except:
        tools.warning("Unable to open index file.")
        return False


def bibtexEdit(ident, modifs):
    """Update ident key in bibtex file, modifications are in modifs dict"""

    try:
        with open(params.folder+'index.bib', 'r', encoding='utf-8') as fh:
            bibtex = BibTexParser(fh.read())
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
        bibtex += tools.parsed2Bibtex(data[entry])+"\n"
    try:
        with open(params.folder+'index.bib', 'w', encoding='utf-8') as fh:
            fh.write(bibtex)
    except:
        tools.warning("Unable to open index file.")
        return False


def deleteId(ident):
    """Delete a file based on its id in the bibtex file"""
    try:
        with open(params.folder+'index.bib', 'r', encoding='utf-8') as fh:
            bibtex = BibTexParser(fh.read().decode('utf-8'))
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
        with open(params.folder+'index.bib', 'r', encoding='utf-8') as fh:
            bibtex = BibTexParser(fh.read().decode('utf-8'))
        bibtex = bibtex.get_entry_dict()
    except:
        tools.warning("Unable to open index file.")
        return False

    found = False
    for key in bibtex.keys():
        try:
            if os.path.samefile(bibtex[key]['file'], filename):
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
                    tools.warning("No associated bibtex entry in index for " +
                                  "file " + bibtex[key]['file'])
        except:
            pass
    if found:
        bibtexRewrite(bibtex)
    elif os.path.isfile(filename):
        os.remove(filename)
    return found


def diffFilesIndex():
    """Compute differences between Bibtex index and PDF files

    Returns a dict with bibtex entry:
        * full bibtex entry with file='' if file is not found
        * only file entry if file with missing bibtex entry
    """
    files = tools.listDir(params.folder)
    files = [i for i in files if tools.getExtension(i) in ['.pdf', '.djvu']]
    try:
        with open(params.folder+'index.bib', 'r', encoding='utf-8') as fh:
            index = BibTexParser(fh.read())
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

    return index.get_entry_dict()


def getBibtex(entry, file_id='both', clean=False):
    """Returns the bibtex entry corresponding to entry, as a dict

    entry is either a filename or a bibtex ident
    file_id is file or id or both to search for a file / id / both
    clean is to clean the ignored fields specified in params
    """
    try:
        with open(params.folder+'index.bib', 'r', encoding='utf-8') as fh:
            bibtex = BibTexParser(fh.read())
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
    if file_id == 'both' or file_id == 'file':
        if os.path.isfile(entry):
            for key in bibtex.keys():
                if os.path.samefile(bibtex[key]['file'], entry):
                    bibtex_entry = bibtex[key]
                    break
    if clean:
        for field in params.ignore_fields:
            try:
                del(bibtex_entry[field])
            except KeyError:
                pass
    return bibtex_entry


def getEntries():
    """Returns the list of all entries in the bibtex index"""
    try:
        with open(params.folder+'index.bib', 'r', encoding='utf-8') as fh:
            bibtex = BibTexParser(fh.read())
        bibtex = bibtex.get_entry_dict()
    except:
        tools.warning("Unable to open index file.")
        return False

    return bibtex.keys()


def updateArXiv(entry):
    """Look for new versions of arXiv entry `entry`

    Returns False if no new versions or not an arXiv entry,
    Returns the new bibtex otherwise.
    """
    bibtex = getBibtex(entry)
    # Check arXiv
    if('archiveprefix' not in bibtex or
       'arXiv' not in bibtex['archiveprefix']):
        return False

    arxiv_id = bibtex['eprint']
    arxiv_id_no_v = re.sub(r'v\d+\Z', '', arxiv_id)
    ids = set(arxiv_id)

    for entry in getEntries():
        if('archiveprefix' not in bibtex or
           'arXiv' not in bibtex['archiveprefix']):
            continue
        ids.add(bibtex['eprint'])

    last_bibtex = BibTexParser(fetcher.arXiv2Bib(arxiv_id_no_v))
    last_bibtex = last_bibtex.get_entry_dict()
    last_bibtex = last_bibtex[last_bibtex.keys()[0]]

    if last_bibtex['eprint'] not in ids:
        return last_bibtex
    else:
        return False


def search(query):
    """Performs a search in the bibtex index.

    Param: query is a dict of keys and the query for these keys
    """
    raise Exception('TODO')
