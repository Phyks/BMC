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


from __future__ import print_function, unicode_literals
import os
import re
import sys
if os.name == "posix":
    from termios import tcflush, TCIOFLUSH

try:
    input = raw_input
except NameError:
    pass

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[\s]+')


def slugify(value):
    """Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens to have nice filenames.

    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    try:
        unicode_type = unicode
    except NameError:
        unicode_type = str
    if not isinstance(value, unicode_type):
        value = unicode_type(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = unicode_type(_slugify_strip_re.sub('', value).strip())
    return _slugify_hyphenate_re.sub('_', value)


def parsed2Bibtex(parsed):
    """Convert a single bibtex entry dict to bibtex string"""
    bibtex = '@'+parsed['ENTRYTYPE']+'{'+parsed['ID']+",\n"

    for field in [i for i in sorted(parsed) if i not in ['ENTRYTYPE', 'ID']]:
        bibtex += "\t"+field+"={"+parsed[field]+"},\n"
    bibtex += "}\n\n"
    return bibtex


def getExtension(filename):
    """Get the extension of filename"""
    return filename[filename.rfind('.'):]


def replaceAll(text, dic):
    """Replace all the dic keys by the associated item in text"""
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


def rawInput(string):
    """Flush stdin and then prompt the user for something"""
    if os.name == "posix":
        tcflush(sys.stdin, TCIOFLUSH)
    return input(string)


def warning(*objs):
    """Write warnings to stderr"""
    print("WARNING: ", *objs, file=sys.stderr)


def listDir(path):
    """List all files in path directory, works recursively

    Return files list
    """
    filenames = []
    for root, dirs, files in os.walk(path):
        for i in files:
            filenames.append(os.path.join(root, i))
    return filenames
