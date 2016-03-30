# List of available options (in ~/.config/bmc/bmc.json file):
# * folder : folder in which papers are stored
# * proxies : list of proxies to use, e.g. ['', "socks5://localhost:4711"]
# * format_articles, format_books : masks to rename files
# * ignore_fields : list of fields to ignore when returning bibtex

# Available masks to rename files are
# %f = last name of first author
# %l = last name of last author
# %j = name of the journal
# %Y = published year
# %t = title
# %a = authors
# %v = arXiv version (e.g. '-v1') or nothing if not an arXiv paper

# You can add your custom masks to rename files by adding functions in
# ~/.config/bmc/masks.py.
#    E.g. : def f(x): x.replace('test', 'some_expr')

import os
import errno
import imp
import inspect
import json
import sys

from backend import tools

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
        return False
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        else:
            return True


class Config():
    def __init__(self, base_config_path="~/.config/bmc/"):
        self.config_path = os.path.expanduser(base_config_path)
        self.config = {}
        self.config["format_custom"] = []
        self.load()

    def as_dict(self):
        return self.config

    def get(self, param):
        return self.config.get(param, False)

    def set(self, param, value):
        self.config[param] = value

    def initialize(self):
        self.set("folder", os.path.expanduser("~/Papers/"))
        self.set("index", os.path.expanduser("~/Papers/index.bib"))
        self.set("proxies", [''])
        self.set("format_articles", "%f_%l-%j-%Y%v")
        self.set("format_books", "%a-%t")
        self.set("format_custom", [])
        self.set("ignore_fields", ["file", "doi", "tag"])
        self.save()

    def load(self):
        try:
            folder_exists = make_sure_path_exists(self.config_path)
            if folder_exists and os.path.isfile(self.config_path + "bmc.json"):
                initialized = True
            else:
                initialized = False
        except OSError:
            tools.warning("Unable to create ~/.config folder.")
            sys.exit(1)
        if not initialized:
            self.initialize()
        else:
            try:
                with open(self.config_path + "bmc.json", 'r') as fh:
                    self.config = json.load(fh)
            except (ValueError, IOError):
                tools.warning("Config file could not be read.")
                sys.exit(1)
            try:
                folder_exists = make_sure_path_exists(self.get("folder"))
            except OSError:
                tools.warning("Unable to create paper storage folder.")
                raise
        self.load_masks()

    def save(self):
        try:
            with open(self.config_path + "bmc.json", 'w') as fh:
                fh.write(json.dumps(self.config,
                                    sort_keys=True,
                                    indent=4,
                                    separators=(',', ': ')))
        except IOError:
            tools.warning("Could not write config file.")
            raise

    def load_masks(self):
        if os.path.isfile(self.config_path + "masks.py"):
            try:
                self.info = imp.find_module("masks", [self.config_path])
                self.masks = imp.load_module("masks", *self.info)
                for mask in inspect.getmembers(self.masks, inspect.isfunction):
                    self.config["format_custom"].append(mask[1])
            except ImportError:
                self.clean()
                tools.warning("Unable to import masks config file.")
                pass
            finally:
                try:
                    self.info[0].close()
                except AttributeError:
                    pass
