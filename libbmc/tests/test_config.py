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
from __future__ import unicode_literals
import unittest
import json
import os
import tempfile
import shutil
from libbmc.config import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.mkdtemp()+"/"
        self.default_config = {"folder": os.path.expanduser("~/Papers/"),
                               "proxies": [''],
                               "format_articles": "%f_%l-%j-%Y%v",
                               "format_books": "%a-%t",
                               "format_custom": [],
                               "ignore_fields": ["file", "doi", "tag"]}

    def tearDown(self):
        shutil.rmtree(self.folder)

    def test_load_without_file(self):
        config = Config(base_config_path=self.folder)
        self.assertEqual(config.as_dict(), self.default_config)
        with open(self.folder+"bmc.json", 'r') as fh:
            read = json.loads(fh.read())
        self.assertEqual(read, self.default_config)

    def test_load_with_file(self):
        config = self.default_config
        config["foo"] = "bar"
        with open(self.folder+"bmc.json", 'w') as fh:
            json.dump(config, fh)
        config_read = Config(base_config_path=self.folder)
        self.assertEqual(config, config_read.as_dict())

    def test_get(self):
        config = Config(base_config_path=self.folder)
        self.assertEqual(config.get("proxies"), [''])

    def test_set(self):
        config = Config(base_config_path=self.folder)
        config.set("foo", "bar")
        self.assertEqual(config.get("foo"), "bar")

    def test_save(self):
        config = Config(base_config_path=self.folder)
        config.set("foo", "bar")
        config.save()
        with open(self.folder+"bmc.json", 'r') as fh:
            read = json.loads(fh.read())
        self.assertEqual(read, config.as_dict())

    def test_masks(self):
        with open(self.folder+"masks.py", 'w') as fh:
            fh.write("def f(x): return x")
        config = Config(base_config_path=self.folder)
        self.assertEqual("foo", config.get("format_custom")[0]("foo"))


if __name__ == '__main__':
    unittest.main()
