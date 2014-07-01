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


import isbntools
import re
import requesocks as requests  # Requesocks is requests with SOCKS support
import subprocess
import sys
import arxiv2bib as arxiv_metadata
import tools
from bibtexparser.bparser import BibTexParser
from config import Config
from isbntools.dev._fmt import fmtbib


config = Config()


def download(url):
    """Download url tofile

    Check that it is a valid pdf or djvu file. Tries all the
    available proxies sequentially. Returns the raw content of the file, or
    false if it could not be downloaded.
    """
    for proxy in config.get("proxies"):
        r_proxy = {
            "http": proxy,
            "https": proxy,
        }
        try:
            r = requests.get(url, proxies=r_proxy)
            size = int(r.headers['Content-Length'].strip())
            dl = ""
            dl_size = 0
            for buf in r.iter_content(1024):
                if buf:
                    dl += buf
                    dl_size += len(buf)
                    done = int(50 * dl_size / size)
                    sys.stdout.write("\r[%s%s]" % ('='*done, ' '*(50-done)))
                    sys.stdout.write(" "+str(int(float(done)/52*100))+"%")
                    sys.stdout.flush()
            contenttype = False
            if 'pdf' in r.headers['content-type']:
                contenttype = 'pdf'
            elif 'djvu' in r.headers['content-type']:
                contenttype = 'djvu'

            if r.status_code != 200 or contenttype is False:
                continue

            return dl, contenttype
        except ValueError:
            tools.warning("Invalid URL")
            return False, None
        except requests.exceptions.RequestException:
            tools.warning("Unable to get "+url+" using proxy "+proxy+". It " +
                          "may not be available.")
            continue
    return False, None


isbn_re = re.compile(r'isbn[\s]?:?[\s]?((?:[0-9]{3}[ -]?)?[0-9]{1,5}[ -]?[0-9]{1,7}[ -]?[0-9]{1,6}[- ]?[0-9])',
                     re.IGNORECASE)


def findISBN(src):
    """Search for a valid ISBN in src.

    Returns the ISBN or false if not found or an error occurred."""
    if src.endswith(".pdf"):
        totext = subprocess.Popen(["pdftotext", src, "-"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  bufsize=1)
    elif src.endswith(".djvu"):
        totext = subprocess.Popen(["djvutxt", src],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  bufsize=1)
    else:
        return False

    while totext.poll() is None:
        extractfull = ' '.join([i.strip() for i in totext.stdout.readlines()])
        extractISBN = isbn_re.search(extractfull.lower().replace('&#338;',
                                                                 '-'))
        if extractISBN:
            totext.terminate()
            break

    err = totext.communicate()[1]
    if totext.returncode > 0:
        # Error happened
        tools.warning(err)
        return False

    cleanISBN = False
    # Clean ISBN is the ISBN number without separators
    if extractISBN:
        cleanISBN = extractISBN.group(1).replace('-', '').replace(' ', '')
    return cleanISBN


def isbn2Bib(isbn):
    """Tries to get bibtex entry from an ISBN number"""
    # Default merges results from worldcat.org and google books
    try:
        return fmtbib('bibtex', isbntools.meta(isbn, 'default'))
    except TypeError:
        return ''


doi_re = re.compile('(?<=doi)/?:?\s?[0-9\.]{7}/\S*[0-9]', re.IGNORECASE)
doi_pnas_re = re.compile('(?<=doi).?10.1073/pnas\.\d+', re.IGNORECASE)
doi_jsb_re = re.compile('10\.1083/jcb\.\d{9}', re.IGNORECASE)
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
    else:
        return False

    extractfull = ''
    while totext.poll() is None:
        extractfull += ' '.join([i.strip() for i in totext.stdout.readlines()])
        extractDOI = doi_re.search(extractfull.lower().replace('&#338;', '-'))
        if not extractDOI:
            # PNAS fix
            extractDOI = doi_pnas_re.search(extractfull.
                                            lower().
                                            replace('pnas', '/pnas'))
            if not extractDOI:
                # JSB fix
                extractDOI = doi_jsb_re.search(extractfull.lower())
        if extractDOI:
            totext.terminate()
            break

    err = totext.communicate()[1]
    if totext.returncode > 0:
        # Error happened
        tools.warning(err)
        return False

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
    """Returns a bibTeX string of metadata for a given DOI.

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


arXiv_re = re.compile(r'arXiv:\s*([\w\.\/\-]+)', re.IGNORECASE)


def findArXivId(src):
    """Searches for a valid arXiv id in src.

    Returns the arXiv id or False if not found or an error occurred.
    From : https://github.com/minad/bibsync/blob/3fdf121016f6187a2fffc66a73cd33b45a20e55d/lib/bibsync/utils.rb
    """
    if src.endswith(".pdf"):
        totext = subprocess.Popen(["pdftotext", src, "-"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    elif src.endswith(".djvu"):
        totext = subprocess.Popen(["djvutxt", src],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    else:
        return False

    extractfull = ''
    while totext.poll() is None:
        extractfull += ' '.join([i.strip() for i in totext.stdout.readlines()])
        extractID = arXiv_re.search(extractfull)
        if extractID:
            totext.terminate()
            break

    err = totext.communicate()[1]
    if totext.returncode > 0:
        # Error happened
        tools.warning(err)
        return False
    elif extractID is not None:
        return extractID.group(1)
    else:
        return False


def arXiv2Bib(arxiv):
    """Returns bibTeX string of metadata for a given arXiv id

    arxiv is an arxiv id
    """
    bibtex = arxiv_metadata.arxiv2bib([arxiv])
    for bib in bibtex:
        if isinstance(bib, arxiv_metadata.ReferenceErrorInfo):
            continue
        else:
            fetched_bibtex = BibTexParser(bib.bibtex())
            fetched_bibtex = fetched_bibtex.get_entry_dict()
            fetched_bibtex = fetched_bibtex[fetched_bibtex.keys()[0]]
            try:
                del(fetched_bibtex['file'])
            except KeyError:
                pass
            return tools.parsed2Bibtex(fetched_bibtex)
    return ''


HAL_re = re.compile(r'(hal-\d{8}), version (\d+)')


def findHALId(src):
    """Searches for a valid HAL id in src

    Returns a tuple of the HAL id and the version
    or False if not found or an error occurred.
    """
    if src.endswith(".pdf"):
        totext = subprocess.Popen(["pdftotext", src, "-"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    elif src.endswith(".djvu"):
        totext = subprocess.Popen(["djvutxt", src],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    else:
        return False

    while totext.poll() is None:
        extractfull = ' '.join([i.strip() for i in totext.stdout.readlines()])
        extractID = HAL_re.search(extractfull)
        if extractID:
            totext.terminate()
            break

    err = totext.communicate()[1]
    if totext.returncode > 0:
        # Error happened
        tools.warning(err)
        return False
    else:
        return extractID.group(1), extractID.group(2)
