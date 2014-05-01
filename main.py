#!/usr/bin/env python2
# -*- coding: utf8 -*-

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


def addFile(src, filetype):
    """
    Add a file to the library
    """
    if filetype == 'article' or filetype is None:
        doi = fetcher.findDOI(src)
    if (filetype == 'article' or filetype is None) and doi is False:
        arxiv = fetcher.findArXivId(src)

    if filetype == 'book' or (filetype is None and doi is False and arxiv is
                              False):
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


def downloadFile(url, filetype):
    dl, contenttype = fetcher.download(url)

    if dl is not False:
        tmp = tempfile.NamedTemporaryFile(suffix='.'+contenttype)

        with open(tmp.name, 'w+') as fh:
            fh.write(dl)
        new_name = addFile(tmp.name, filetype)
        tmp.close()
        return new_name
    else:
        tools.warning("Could not fetch "+url)
        return False


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
    try:
        if len(sys.argv) < 2:
            sys.exit("Usage: TODO")

        if sys.argv[1] == 'download':
            if len(sys.argv) < 3:
                sys.exit("Usage: " + sys.argv[0] +
                         " download FILE [article|book]")

            filetype = None
            if len(sys.argv) > 3 and sys.argv[3] in ["article", "book"]:
                filetype = sys.argv[3].lower()

            new_name = downloadFile(sys.argv[2], filetype)
            if new_name is not False:
                print(sys.argv[2]+" successfully imported as "+new_name)
            sys.exit()

        if sys.argv[1] == 'import':
            if len(sys.argv) < 3:
                sys.exit("Usage: " + sys.argv[0] +
                         " import FILE [article|book]")

            filetype = None
            if len(sys.argv) > 3 and sys.argv[3] in ["article", "book"]:
                filetype = sys.argv[3].lower()

            new_name = addFile(sys.argv[2], filetype)
            if new_name is not False:
                print(sys.argv[2]+" successfully imported as "+new_name+".")
            sys.exit()

        elif sys.argv[1] == 'delete':
            if len(sys.argv) < 3:
                sys.exit("Usage: " + sys.argv[0] + " delete FILE|ID")

            confirm = tools.rawInput("Are you sure you want to delete " +
                                     sys.argv[2]+"? [y/N] ")

            if confirm.lower() == 'y':
                if not backend.deleteId(sys.argv[2]):
                    if not backend.deleteFile(sys.argv[2]):
                        tools.warning("Unable to delete "+sys.argv[2])
                        sys.exit(1)

                print(sys.argv[2]+" successfully deleted.")
            sys.exit()

        elif sys.argv[1] == 'list':
            raise Exception('TODO')

        elif sys.argv[1] == 'search':
            raise Exception('TODO')

        elif sys.argv[1] == 'resync':
            if len(sys.argv) > 2 and sys.argv[2] == 'help':
                sys.exit("Usage: " + sys.argv[0] + " resync")
            confirm = tools.rawInput("Resync files and bibtex index? [y/N] ")
            if confirm.lower() == 'y':
                resync()

    except KeyboardInterrupt:
        sys.exit()
