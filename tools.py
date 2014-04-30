# -*- coding: utf8 -*-

from __future__ import print_function
import os
import re
import sys
from termios import tcflush, TCIOFLUSH

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[\s]+')


def slugify(value):
    """Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens to have nice filenames.

    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip())
    return _slugify_hyphenate_re.sub('_', value)


def getExtension(filename):
    """Get the extension of filename"""
    return filename[filename.rfind('.'):]


def replaceAll(text, dic):
    """Replace all the dic keys by the associated item in text"""
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text


def rawInput(string):
    """Flush stdin and then prompt the user for something"""
    tcflush(sys.stdin, TCIOFLUSH)
    return raw_input(string)


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
