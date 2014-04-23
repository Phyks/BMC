#!/usr/bin/python2 -u
# coding=utf8
"""
Main app
"""

import sys
import shutil
import requests
from bibtexparser.bparser import BibTexParser
import params


def bibtex_append(data):
    """
    Append data to the main bibtex file
    """
    bibtex = ''
    for field, value in data:
        bibtex += "\n" + field + ": " + value + ","

    # TODO : Write


def add_file(src, doi):
    """
    Add a file to the library
    """
    new_name = folder+"/"+doi

    try:
        shutil.copy2(src, new_name)
    except IOError:
        sys.exit("Unable to move file to library dir " + folder)
    
    data = {"file": new_name}

    bibtex_append(data)

    print("File " + src + " successfully imported.")

 
def doi2bib(doi):
    """
    Return a bibTeX string of metadata for a given DOI.
    From : https://gist.github.com/jrsmith3/5513926
    """
    
    url = "http://dx.doi.org/" + doi
    
    headers = {"accept": "application/x-bibtex"}
    r = requests.get(url, headers = headers)
    
    return r.text


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("Usage : TODO")


    if sys.argv[1] == 'download':
        raise Exception('TODO')

    if sys.argv[1] == 'import':
        if len(sys.argv) < 3:
            sys.exit("Usage : " + sys.argv[0] + " import FILE")

        doi = raw_input('DOI ? ')
        # TODO : Get DOI automagically
        add_file(sys.argv[2], doi)
        sys.exit()

    elif sys.argv[1] == 'list':
        raise Exception('TODO')

    elif sys.argv[1] == 'search':
        raise Exception('TODO')
