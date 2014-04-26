#!/usr/bin/python2 -u
# coding=utf8

"""
Fetches papers.
"""

import requesocks as requests
import params

def download_url(url):
    for proxy in params.proxies:
        r_proxy = {
            "http": proxy,
            "https": proxy,
        }

        r = requests.get(url, proxies=r_proxy)

        if r.status_code != 200 or 'pdf' not in r.headers['content-type']:
            continue

        return r.content

    return False
