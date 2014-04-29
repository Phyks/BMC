#!/usr/bin/env python2
# coding=utf8

import isbntools
import re
import requesocks as requests  # Requesocks is requests with SOCKS support
import subprocess
import tools
import params


def download(url):
    """Download url tofile

    Check that it is a valid pdf or djvu file. Tries all the
    available proxies sequentially. Returns the raw content of the file, or
    false if it could not be downloaded.
    """
    for proxy in params.proxies:
        r_proxy = {
            "http": proxy,
            "https": proxy,
        }
        try:
            r = requests.get(url, proxies=r_proxy)
            contenttype = False
            if 'pdf' in r.headers['content-type']:
                contenttype = 'pdf'
            elif 'djvu' in r.headers['content-type']:
                contenttype = 'djvu'

            if r.status_code != 200 or contenttype is False:
                continue

            return r.content, contenttype
        except requests.exceptions.RequestException:
            tools.warning("Unable to get "+url+" using roxy "+proxy+". It " +
                          "may not be available.")
            continue
    return False


isbn_re = re.compile(r"isbn (([0-9]{3}[ -])?[0-9][ -][0-9]{2}[ -][0-9]{6}[-][0-9])")


def findISBN(src):
    """Search for a valid ISBN in src.

    Returns the ISBN or false if not found or an error occurred."""
    if src.endswith(".pdf"):
        totext = subprocess.Popen(["pdftotext", src, "-"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    elif src.endswith(".djvu"):
        totext = subprocess.Popen(["djvutxt", src],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    extractfull = totext.communicate()
    # TODO : ^ Return result before processing the whole book ?
    if extractfull[1] is not "":
        # Error happened
        tools.warning(extractfull[1])
        return False
    extractfull = extractfull[0]
    extractISBN = isbn_re.search(extractfull.lower().replace('&#338;', '-'))
    cleanISBN = False
    # Clean ISBN is the ISBN number without separators
    if extractISBN:
        cleanISBN = extractISBN.group(1).replace('-', '').replace(' ', '')
    return cleanISBN


def isbn2Bib(isbn):
    """Try to get bibtex entry from an ISBN number"""
    try:
        # Default merges results from worldcat.org and google books
        return isbntools.dev.fmt.fmtbib('bibtex',
                                        isbntools.meta(isbn, 'default'))
    except:
        return ''


doi_re = re.compile('(?<=doi)/?:?\s?[0-9\.]{7}/\S*[0-9]')
doi_pnas_re = re.compile('(?<=doi).?10.1073/pnas\.\d+')
doi_jsb_re = re.compile('10\.1083/jcb\.\d{9}')
clean_doi_re = re.compile('^/')
clean_doi_fabse_re = re.compile('^10.1096')
clean_doi_jcb_re = re.compile('^10.1083')
clean_doi_len_re = re.compile(r'\d\.\d')


def findDOI(src):
    """Search for a valid DOI in src.

    Returns the DOI or False if not found or an error occurred.
    From : http://en.dogeno.us/2010/02/release-a-python-script-for-organizing-scientific-papers-pyrenamepdf-py/
    """
    if src.endswith(".pdf"):
        totext = subprocess.Popen(["pdftotext", src, "-"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    elif src.endswith(".djvu"):
        totext = subprocess.Popen(["djvutxt", src],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    extractfull = totext.communicate()
    # TODO : ^ Return result before full conversion ?
    if extractfull[1] is not "":
        # Error happened
        tools.warning(extractfull[1])
        return False
    extractfull = extractfull[0]
    extractDOI = doi_re.search(extractfull.lower().replace('&#338;', '-'))
    if not extractDOI:
        # PNAS fix
        extractDOI = doi_pnas_re.search(extractfull.lower().replace('pnas',
                                                                    '/pnas'))
        if not extractDOI:
            # JSB fix
            extractDOI = doi_jsb_re.search(extractfull.lower())

    cleanDOI = False
    if extractDOI:
        cleanDOI = extractDOI.group(0).replace(':', '').replace(' ', '')
        if clean_doi_re.search(cleanDOI):
            cleanDOI = cleanDOI[1:]
        # FABSE J fix
        if clean_doi_fabse_re.search(cleanDOI):
            cleanDOI = cleanDOI[:20]
        # Second JCB fix
        if clean_doi_jcb_re.search(cleanDOI):
            cleanDOI = cleanDOI[:21]
        if len(cleanDOI) > 40:
            cleanDOItemp = clean_doi_len_re.sub('000', cleanDOI)
            reps = {'.': 'A', '-': '0'}
            cleanDOItemp = tools.replaceAll(cleanDOItemp[8:], reps)
            digitStart = 0
            for i in range(len(cleanDOItemp)):
                if cleanDOItemp[i].isdigit():
                    digitStart = 1
                    if cleanDOItemp[i].isalpha() and digitStart:
                        break
            cleanDOI = cleanDOI[0:(8+i)]
    return cleanDOI


def doi2Bib(doi):
    """Return a bibTeX string of metadata for a given DOI.

    From : https://gist.github.com/jrsmith3/5513926
    """
    url = "http://dx.doi.org/" + doi
    headers = {"accept": "application/x-bibtex"}
    try:
        r = requests.get(url, headers=headers)

        if r.headers['content-type'] == 'application/x-bibtex':
            return r.text
        else:
            return ''
    except requests.exceptions.ConnectionError:
        tools.warning('Unable to contact remote server to get the bibtex ' +
                      'entry for doi '+doi)
        return ''
