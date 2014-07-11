#!/usr/bin/env python

from distutils.core import setup

setup(
    name         = 'BMC',
    version      = "0.2dev",
    url          = "https://github.com/Phyks/BMC",
    author       = "",
    license      = "no-alcohol beer-ware license",
    author_email = "",
    description  = "simple script to download and store your articles",
    packages     = ['libbmc'],
    scripts      = ['bmc.py'],
)
