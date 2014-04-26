#!/usr/bin/python2 -u
# coding=utf8

"""
Fetches papers.
"""

from __future__ import print_function
import sys
import requesocks as requests
import params


def warning(*objs):
    """
    Write to stderr
    """
    print("WARNING: ", *objs, file=sys.stderr)


def download_url(url):
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
        except:
            warning("Proxy "+proxy+" not available.")
            continue

    return False
