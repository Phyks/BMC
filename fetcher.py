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

            if r.status_code != 200 or 'pdf' not in r.headers['content-type']:
                continue

            return r.content
        except:
            warning("Proxy "+proxy+" not available.")
            continue

    return False
