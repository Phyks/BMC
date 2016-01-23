#!/usr/bin/env python

from distutils.core import setup

setup(
    name         = 'BMC',
    version      = "0.4",
    url          = "https://github.com/Phyks/BMC",
    author       = "Phyks (Lucas Verney)",
    license      = "MIT License",
    author_email = "phyks@phyks.me",
    description  = "Simple script to download and store your articles",
    # TODO
    packages     = ['libbmc'],
    scripts      = ['bmc.py'],
)
