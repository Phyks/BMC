#!/usr/bin/env python2
# -*- coding: utf8 -*-

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import backend
import fetcher
import tearpages
import tools
import params
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import homogeneize_latex_encoding

EDITOR = os.environ.get('EDITOR') if os.environ.get('EDITOR') else 'vim'


def checkBibtex(filename, bibtex):
    print("The bibtex entry found for "+filename+" is:")

    bibtex = BibTexParser(bibtex, customization=homogeneize_latex_encoding)
    bibtex = bibtex.get_entry_dict()
    if len(bibtex) > 0:
        bibtex_name = bibtex.keys()[0]
        bibtex = bibtex[bibtex_name]
        bibtex_string = backend.parsed2Bibtex(bibtex)
    else:
        bibtex_string = ''
    print(bibtex_string)
    check = tools.rawInput("Is it correct? [Y/n] ")

    while check.lower() == 'n':
        with tempfile.NamedTemporaryFile(suffix=".tmp") as tmpfile:
            tmpfile.write(bibtex_string)
            tmpfile.flush()
            subprocess.call([EDITOR, tmpfile.name])
            bibtex = BibTexParser(tmpfile.read()+"\n",
                                  customization=homogeneize_latex_encoding)

        bibtex = bibtex.get_entry_dict()
        if len(bibtex) > 0:
            bibtex_name = bibtex.keys()[0]
            bibtex = bibtex[bibtex_name]
            bibtex_string = backend.parsed2Bibtex(bibtex)
        else:
            bibtex_string = ''
        print("\nThe bibtex entry for "+filename+" is:")
        print(bibtex_string)
        check = tools.rawInput("Is it correct? [Y/n] ")
    return bibtex


def addFile(src, filetype, manual):
    """
    Add a file to the library
    """
    doi = False
    arxiv = False
    isbn = False

    if not manual:
        if filetype == 'article' or filetype is None:
            doi = fetcher.findDOI(src)
        if (filetype == 'article' or filetype is None) and doi is False:
            arxiv = fetcher.findArXivId(src)

        if filetype == 'book' or (filetype is None and doi is False and
                                  arxiv is False):
            isbn = fetcher.findISBN(src)

    if doi is False and isbn is False and arxiv is False:
        if filetype is None:
            tools.warning("Could not determine the DOI nor the arXiv id nor " +
                          "the ISBN for "+src+"."+"Switching to manual entry.")
            doi_arxiv_isbn = ''
            while doi_arxiv_isbn not in ['doi', 'arxiv', 'isbn']:
                doi_arxiv_isbn = tools.rawInput("DOI / arXiv / ISBN? ").lower()
            if doi_arxiv_isbn == 'doi':
                doi = tools.rawInput('DOI? ')
            elif doi_arxiv_isbn == 'arxiv':
                arxiv = tools.rawInput('arXiv id? ')
            else:
                isbn = tools.rawInput('ISBN? ')
        elif filetype == 'article':
            tools.warning("Could not determine the DOI nor the arXiv id for " +
                          src+", switching to manual entry.")
            doi_arxiv = ''
            while doi_arxiv not in ['doi', 'arxiv']:
                doi_arxiv = tools.rawInput("DOI / arXiv? ").lower()
            if doi_arxiv == 'doi':
                doi = tools.rawInput('DOI? ')
            else:
                arxiv = tools.rawInput('arXiv id? ')
        elif filetype == 'book':
            tools.warning("Could not determine the ISBN for "+src +
                          ", switching to manual entry.")
            isbn = tools.rawInput('ISBN? ')
    elif doi is not False:
        print("DOI for "+src+" is "+doi+".")
    elif arxiv is not False:
        print("ArXiv id for "+src+" is "+arxiv+".")
    elif isbn is not False:
        print("ISBN for "+src+" is "+isbn+".")

    if doi is not False and doi != '':
        # Add extra \n for bibtexparser
        bibtex = fetcher.doi2Bib(doi).strip().replace(',', ",\n")+"\n"
    elif arxiv is not False and arxiv != '':
        bibtex = fetcher.arXiv2Bib(arxiv).strip().replace(',', ",\n")+"\n"
    elif isbn is not False and isbn != '':
        # Idem
        bibtex = fetcher.isbn2Bib(isbn).strip()+"\n"
    else:
        bibtex = ''

    bibtex = checkBibtex(src, bibtex)

    new_name = backend.getNewName(src, bibtex)

    while os.path.exists(new_name):
        tools.warning("file "+new_name+" already exists.")
        default_rename = new_name.replace(tools.getExtension(new_name),
                                          " (2)"+tools.getExtension(new_name))
        rename = tools.rawInput("New name ["+default_rename+"]? ")
        if rename == '':
            new_name = default_rename
        else:
            new_name = rename
    bibtex['file'] = new_name

    try:
        shutil.copy2(src, new_name)
    except IOError:
        new_name = False
        sys.exit("Unable to move file to library dir " + params.folder+".")

    # Remove first page of IOP papers
    if 'IOP' in bibtex['publisher'] and bibtex['type'] == 'article':
        tearpages.tearpage(new_name)

    backend.bibtexAppend(bibtex)
    return new_name


def downloadFile(url, filetype, manual):
    dl, contenttype = fetcher.download(url)

    if dl is not False:
        tmp = tempfile.NamedTemporaryFile(suffix='.'+contenttype)

        with open(tmp.name, 'w+') as fh:
            fh.write(dl)
        new_name = addFile(tmp.name, filetype, manual)
        tmp.close()
        return new_name
    else:
        tools.warning("Could not fetch "+url)
        return False


def openFile(ident):
    try:
        with open(params.folder+'index.bib', 'r') as fh:
            bibtex = BibTexParser(fh.read(),
                                  customization=homogeneize_latex_encoding)
        bibtex = bibtex.get_entry_dict()
    except:
        tools.warning("Unable to open index file.")
        return False

    if ident not in bibtex.keys():
        return False
    else:
        subprocess.Popen(['xdg-open', bibtex[ident]['file']])
        return True


def resync():
    diff = backend.diffFilesIndex()

    for entry in diff:
        if entry['file'] == '':
            print("Found entry in index without associated file.")
            confirm = False
            while not confirm:
                filename = tools.rawInput("File to import for this entry " +
                                          "(leave empty to delete the " +
                                          "entry)? ")
                if filename == '':
                    break
                else:
                    confirm = True
                    if 'doi' in entry.keys():
                        doi = fetcher.findDOI(filename)
                        if doi is not False and doi != entry['doi']:
                            confirm = tools.rawInput("Found DOI does not " +
                                                     "match bibtex entry " +
                                                     "DOI, continue anyway " +
                                                     "? [y/N]")
                            confirm = (confirm.lower() == 'y')
                    if 'Eprint' in entry.keys():
                        arxiv = fetcher.findArXivId(filename)
                        if arxiv is not False and arxiv != entry['Eprint']:
                            confirm = tools.rawInput("Found arXiv id does " +
                                                     "not match bibtex " +
                                                     "entry arxiv id, " +
                                                     "continue anyway ? [y/N]")
                            confirm = (confirm.lower() == 'y')
                    elif 'isbn' in entry.keys():
                        isbn = fetcher.findISBN(filename)
                        if isbn is not False and isbn != entry['isbn']:
                            confirm = tools.rawInput("Found ISBN does not " +
                                                     "match bibtex entry " +
                                                     "ISBN, continue anyway " +
                                                     "? [y/N]")
                            confirm = (confirm.lower() == 'y')
                    continue
            if filename == '':
                backend.deleteId(entry['id'])
            else:
                new_name = backend.getNewName(filename, entry)
                try:
                    shutil.copy2(filename, new_name)
                except IOError:
                    new_name = False
                    sys.exit("Unable to move file to library dir " +
                             params.folder+".")
                backend.bibtexEdit(entry['id'], {'file': filename})
        else:
            print("Found file without any associated entry in index.")
            action = ''
            while action.lower() not in ['import', 'delete']:
                action = tools.rawInput("What to do? [import / delete] ")
                action = action.lower()
            if action == 'import':
                tmp = tempfile.NamedTemporaryFile()
                shutil.copy(entry['file'], tmp.name)
                filetype = tools.getExtension(entry['file'])
                try:
                    os.remove(entry['file'])
                except:
                    tools.warning("Unable to delete file "+entry['file'])
                if not addFile(tmp.name, filetype):
                    tools.warning("Unable to reimport file "+entry['file'])
                tmp.close()
            else:
                backend.deleteFile(entry['file'])
                print(entry['file'] + " removed from disk and " +
                      "index.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A bibliography " +
                                     "management tool.")
    subparsers = parser.add_subparsers(help="sub-command help")

    parser_download = subparsers.add_parser('download', help="download help")
    parser_download.add_argument('-t', '--type', default=None,
                                 choices=['article', 'book'],
                                 help="type of the file to download")
    parser_download.add_argument('-m', '--manual', default=False,
                                 action='store_true',
                                 help="disable auto-download of bibtex")
    parser_download.add_argument('url',  nargs='+',
                                 help="url of the file to import")
    parser_download.set_defaults(func='download')

    parser_import = subparsers.add_parser('import', help="import help")
    parser_import.add_argument('-t', '--type', default=None,
                               choices=['article', 'book'],
                               help="type of the file to import")
    parser_import.add_argument('-m', '--manual', default=False,
                               action='store_true',
                               help="disable auto-download of bibtex")
    parser_import.add_argument('file',  nargs='+',
                               help="path to the file to import")
    parser_import.set_defaults(func='import')

    parser_delete = subparsers.add_parser('delete', help="delete help")
    parser_delete.add_argument('files', metavar='entry', nargs='+',
                               help="a filename or an identifier")
    parser_delete.add_argument('-f', '--force', default=False,
                               action='store_true',
                               help="delete without confirmation")
    parser_delete.set_defaults(func='delete')

    parser_list = subparsers.add_parser('list', help="list help")
    parser_list.set_defaults(func='list')

    parser_search = subparsers.add_parser('search', help="search help")
    parser_search.set_defaults(func='search')

    parser_open = subparsers.add_parser('open', help="open help")
    parser_open.add_argument('ids', metavar='id',  nargs='+',
                             help="an identifier")
    parser_open.set_defaults(func='open')

    parser_resync = subparsers.add_parser('resync', help="resync help")
    parser_resync.set_defaults(func='resync')

    args = parser.parse_args()
    try:
        if args.func == 'download':
            for url in args.url:
                new_name = downloadFile(url, args.type, args.manual)
                if new_name is not False:
                    print(url+" successfully imported as "+new_name)
                else:
                    tools.warning("An error occurred while downloading "+url)
            sys.exit()

        if args.func == 'import':
            for filename in args.file:
                new_name = addFile(filename, args.type, args.manual)
                if new_name is not False:
                    print(sys.argv[2]+" successfully imported as " +
                          new_name+".")
                else:
                    tools.warning("An error occurred while importing " +
                                  filename)
            sys.exit()

        elif args.func == 'delete':
            for filename in args.file:
                if not args.force:
                    confirm = tools.rawInput("Are you sure you want to " +
                                             "delete "+filename+" ? [y/N] ")
                else:
                    confirm = 'y'

                if confirm.lower() == 'y':
                    if not backend.deleteId(filename):
                        if not backend.deleteFile(filename):
                            tools.warning("Unable to delete "+filename)
                            sys.exit(1)

                    print(filename+" successfully deleted.")
            sys.exit()

        elif args.func == 'list':
            raise Exception('TODO')

        elif args.func == 'search':
            raise Exception('TODO')

        elif args.func == 'open':
            for filename in args.ids:
                if not openFile(filename):
                    sys.exit("Unable to open file associated " +
                             "to ident "+filename)

        elif args.func == 'resync':
            confirm = tools.rawInput("Resync files and bibtex index? [y/N] ")
            if confirm.lower() == 'y':
                resync()

    except KeyboardInterrupt:
        sys.exit()
