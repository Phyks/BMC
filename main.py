#!/usr/bin/env python2
# -*- coding: utf8 -*-
"""
Main app
"""
from __future__ import print_function

import sys
import shutil
import requests
import subprocess
import re
import os
from isbntools import meta
from isbntools.dev.fmt import fmtbib, fmts
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import homogeneize_latex_encoding
import params


def rawInput(string):
    sys.stdout.flush()
    return raw_input(string)


def warning(*objs):
    """
    Write to stderr
    """
    print("WARNING: ", *objs, file=sys.stderr)


def parsed2Bibtex(parsed):
    bibtex = '@'+parsed['type']+'{'+parsed['id']+"\n"
    
    for field in [i for i in sorted(parsed) if i not in ['type', 'id']]:
        bibtex += "\t"+field+"={"+parsed[field]+"},\n"
    bibtex += "}"
    return bibtex


def bibtexAppend(data):
    """
    Append data to the main bibtex file
    data is a dict as the one from bibtexparser output
    """
    bibtex = ''
    for field, value in data:
        bibtex += "\n" + field + ": " + value + ","

    # TODO : Write


def replaceAll(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text


def findISBN(src):
    if src.endswith(".pdf"):
        totext = subprocess.Popen(["pdftotext", src, "-"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    elif src.endswith(".djvu"):
        totext = subprocess.Popen(["djvutxt", src],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

    extractfull = totext.communicate()
    if extractfull[1] is not "":
        return False

    extractfull = extractfull[0]
    extractISBN = re.search(r"isbn (([0-9]{3}[ -])?[0-9][ -][0-9]{2}[ -][0-9]{6}[ -][0-9])",
                           extractfull.lower().replace('&#338;', '-'))

    cleanISBN = False
    if extractISBN:
        cleanISBN = extractISBN.group(1).replace('-', '').replace(' ', '')

    return cleanISBN


def isbn2Bib(isbn):
    return fmtbib('bibtex', meta(isbn, 'default'))


def findDOI(src):
    if src.endswith(".pdf"):
        totext = subprocess.Popen(["pdftotext", src, "-"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    elif src.endswith(".djvu"):
        totext = subprocess.Popen(["djvutxt", src],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

    extractfull = totext.communicate()
    if extractfull[1] is not "":
        return False

    extractfull = extractfull[0]
    extractDOI = re.search('(?<=doi)/?:?\s?[0-9\.]{7}/\S*[0-9]',
                           extractfull.lower().replace('&#338;', '-'))
    if not extractDOI:
        # PNAS fix
        extractDOI = re.search('(?<=doi).?10.1073/pnas\.\d+',
                               extractfull.lower().replace('pnas', '/pnas'))
        if not extractDOI:
            # JSB fix
            extractDOI = re.search('10\.1083/jcb\.\d{9}', extractfull.lower())

    cleanDOI = False
    if extractDOI:
        cleanDOI = extractDOI.group(0).replace(':', '').replace(' ', '')
        if re.search('^/', cleanDOI):
            cleanDOI = cleanDOI[1:]

        # FABSE J fix
        if re.search('^10.1096', cleanDOI):
            cleanDOI = cleanDOI[:20]

        # Second JCB fix
        if re.search('^10.1083', cleanDOI):
            cleanDOI = cleanDOI[:21]

        if len(cleanDOI) > 40:
            cleanDOItemp = re.sub(r'\d\.\d', '000', cleanDOI)
            reps = {'.': 'A', '-': '0'}
            cleanDOItemp = replaceAll(cleanDOItemp[8:], reps)
            digitStart = 0
            for i in range(len(cleanDOItemp)):
                if cleanDOItemp[i].isdigit():
                    digitStart = 1
                    if cleanDOItemp[i].isalpha() and digitStart:
                        break
            cleanDOI = cleanDOI[0:(8+i)]

    return cleanDOI


def doi2Bib(doi):
    """
    Return a bibTeX string of metadata for a given DOI.
    From : https://gist.github.com/jrsmith3/5513926
    """
    url = "http://dx.doi.org/" + doi
    headers = {"accept": "application/x-bibtex"}
    r = requests.get(url, headers=headers)
    return r.text


_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[\s]+')
def _slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    
    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip())
    return _slugify_hyphenate_re.sub('_', value)


def getExtension(filename):
    """
    Get the extension of the filename
    """
    return filename[filename.rfind('.'):]


def checkBibtex(filename, bibtex):
    print("The bibtex entry found for "+filename+" is :")
    print(bibtex)
    check = rawInput("Is it correct ? [Y/n] ")

    bibtex = StringIO(bibtex)
    bibtex = BibTexParser(bibtex, customization=homogeneize_latex_encoding)
    bibtex = bibtex.get_entry_dict()
    bibtex_name = bibtex.keys()[0]
    bibtex = bibtex[bibtex_name]
     
    while check.lower() == 'n':
        fields = [u'type', u'id'] + [i for i in sorted(bibtex)
                                   if i not in ['id', 'type']]

        for field in fields:
            new_value = rawInput(field.capitalize()+" ? ["+bibtex[field]+"] ")
            if new_value != '':
                bibtex[field] = new_value

        while True:
            new_field = rawInput("Add a new field (leave empty to skip) ? ")
            if new_field == '':
                break
            new_value = rawInput("Value for field "+new_field+" ? ")
            bibtex[new_field] = new_value


        print("\nThe bibtex entry for "+filename+" is :")
        print(parsed2Bibtex(bibtex))
        check = rawInput("Is it correct ? [Y/n] ")
    return bibtex


def addFile(src, filetype):
    """
    Add a file to the library
    """
    if filetype == 'article' or filetype is None:
        doi = findDOI(src)

    if filetype == 'book' or (filetype is None and doi is False):
        isbn = findISBN(src)

    if doi is False and isbn is False:
        if filetype is None:
            warning("Could not determine the DOI or the ISBN for "+src+"." +
                    "Switching to manual entry.")
            while doi_isbn not in ['doi', 'isbn']:
                doi_isbn = rawInput("DOI / ISBN ? ").lower()
            if doi_isbn == 'doi':
                doi = rawInput('DOI ? ')
            else:
                isbn = rawInput('ISBN ? ')
        elif filetype == 'article':
            warning("Could not determine the DOI for "+src+", switching to manual " +
                "entry.")
            doi = rawInput('DOI ? ')
        elif filetype == 'book':
            warning("Could not determine the ISBN for "+src+", switching to manual " +
                "entry.")
            isbn = rawInput('ISBN ? ')
    elif doi is not False:
        print("DOI for "+src+" is "+doi+".")
    elif isbn is not False:
        print("ISBN for "+src+" is "+isbn+".")

    if doi is not False:
        # Add extra \n for bibtexparser
        bibtex = doi2Bib(doi).strip().replace(',', ",\n")+"\n"
    else:
        # Idem
        bibtex = isbn2Bib(isbn).strip()+"\n"
    bibtex = checkBibtex(src, bibtex)

    authors = re.split(' and ', bibtex['author'])

    if doi is not False:
        new_name = params.format_articles
        new_name = new_name.replace("%j", bibtex['journal'])
    else:
        new_name = params.format_books

    new_name = new_name.replace("%t", bibtex['title'])
    new_name = new_name.replace("%Y", bibtex['year'])
    new_name = new_name.replace("%f", authors[0].split(',')[0].strip())
    new_name = new_name.replace("%l", authors[-1].split(',')[0].strip())
    new_name = new_name.replace("%a", ', '.join([i.split(',')[0].strip()
                                                for i in authors]))

    new_name = params.folder+_slugify(new_name)+getExtension(src)
    bibtex['file'] = new_name

    while os.path.exists(new_name):
        warning("Error, file "+new_name+" already exists.")
        default_rename = new_name.replace(getExtension(new_name),
                                          " (2)"+getExtension(new_name))
        rename = rawInput("New name ["+default_rename+"] ? ")
        if rename == '':
            new_name = default_rename
        else:
            new_name = rename


    try:
        shutil.copy2(src, new_name)
    except IOError:
        sys.exit("Unable to move file to library dir " + params.folder+".")

    # TODO
    bibtexAppend(bibtex)
    print("File " + src + " successfully imported.")


if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            sys.exit("Usage : TODO")

        if sys.argv[1] == 'download':
            raise Exception('TODO')

        if sys.argv[1] == 'import':
            if len(sys.argv) < 3:
                sys.exit("Usage : " + sys.argv[0] + " import FILE [article|book]")

            filetype = None
            if len(sys.argv) > 3 and sys.argv[3] in ["article", "book"]:
                filetype = sys.argv[3].lower()

            addFile(sys.argv[2], filetype)
            sys.exit()

        elif sys.argv[1] == 'list':
            raise Exception('TODO')

        elif sys.argv[1] == 'search':
            raise Exception('TODO')
    except KeyboardInterrupt:
        sys.exit()
