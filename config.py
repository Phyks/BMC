import os
import errno
import json
import sys
import tools

# List of available options :
# * folder : folder in which papers are stored
# * proxies : list of proxies to use, e.g. ['', "socks5://localhost:4711"]
# * format_articles, format_books : masks to rename files
# * format_custom : list of lambda functions to apply to rename files.
#    E.g. : format_custom = [lambda x: x.replace('test', 'some_expr')]
# * ignore_fields : list of fields to ignore when returning bibtex

# Available masks to rename files are
# %f = last name of first author
# %l = last name of last author
# %j = name of the journal
# %Y = published year
# %t = title
# %a = authors
# %v = arXiv version (e.g. '-v1') or nothing if not an arXiv paper


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
        return True
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        else:
            return False


class Config():
    def __init__(self):
        self.config_path = os.path.expanduser("~/.config/")
        self.config = {}
        self.load()

    def get(self, param):
        return self.config[param]

    def set(self, param, value):
        self.config[param] = value

    def initialize(self):
        self.set("folder", os.path.expanduser("~/Papers/"))
        self.set("proxies", [''])
        self.set("format_articles", "%f_%l-%j-%Y%v")
        self.set("format_books", "%a-%t")
        self.set("format_custom", [])
        self.set("ignore_fields", ["file", "doi", "tag"])
        self.save()

    def load(self):
        try:
            initialized = make_sure_path_exists(self.config_path)
        except:
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

    def save(self):
        try:
            with open(self.config_path + "bmc.json", 'w') as fh:
                fh.write(json.dumps(self.config))
        except IOError:
            tools.warning("Could not write config file.")
            sys.exit(1)

config = Config()
