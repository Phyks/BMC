#!/usr/bin/python2 -u
# coding=utf8
"""
Main app
"""

import sys
import shutil
import requests
import subprocess
import re
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
from bibtexparser.bparser import BibTexParser
import params


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


def PDF2Doi(pdf):
    pdftotext = subprocess.Popen(["pdftotext", pdf, "-"],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
    extractfull = pdftotext.communicate()
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


def addFile(src):
    """
    Add a file to the library
    """
    doi = PDF2Doi(src)

    if doi is False:
        print("Could not determine the DOI for "+src+", switching to manual " +
              "entry.")
        doi = raw_input('DOI ? ')
    else:
        print("DOI for "+src+" is "+doi+".")

    bibtex = doi2Bib(doi).strip().replace(',', ",\n")
    bibtex = StringIO(bibtex)
    bibtex = BibTexParser(bibtex).get_entry_dict()

    # TODO : Rename
    new_name = params.folder+"/"+doi

    bibtex[bibtex.keys()[0]]['file'] = new_name

    try:
        shutil.copy2(src, new_name)
    except IOError:
        sys.exit("Unable to move file to library dir " + params.folder+".")

    bibtexAppend(bibtex)
    print("File " + src + " successfully imported.")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("Usage : TODO")

    if sys.argv[1] == 'download':
        raise Exception('TODO')

    if sys.argv[1] == 'import':
        if len(sys.argv) < 3:
            sys.exit("Usage : " + sys.argv[0] + " import FILE")

        addFile(sys.argv[2])
        sys.exit()

    elif sys.argv[1] == 'list':
        raise Exception('TODO')

    elif sys.argv[1] == 'search':
        raise Exception('TODO')
