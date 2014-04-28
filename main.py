#!/usr/bin/env python2
# -*- coding: utf8 -*-

import tools
import fetcher
import backend
import tearpages
import sys
import shutil
import tempfile
import subprocess
import os
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import homogeneize_latex_encoding
import params

EDITOR = os.environ.get('EDITOR') if os.environ.get('EDITOR') else 'vim'


def parsed2Bibtex(parsed):
    """
    Convert a single bibtex entry dict to bibtex string
    """
    bibtex = '@'+parsed['type']+'{'+parsed['id']+",\n"

    for field in [i for i in sorted(parsed) if i not in ['type', 'id']]:
        bibtex += "\t"+field+"={"+parsed[field]+"},\n"
    bibtex += "}\n"
    return bibtex


def checkBibtex(filename, bibtex):
    print("The bibtex entry found for "+filename+" is :")

    bibtex = BibTexParser(bibtex, customization=homogeneize_latex_encoding)
    bibtex = bibtex.get_entry_dict()
    if len(bibtex) > 0:
        bibtex_name = bibtex.keys()[0]
        bibtex = bibtex[bibtex_name]
        bibtex_string = parsed2Bibtex(bibtex)
    else:
        bibtex_string = ''
    print(bibtex_string)
    check = tools.rawInput("Is it correct ? [Y/n] ")

    while check.lower() == 'n':
        with tempfile.NamedTemporaryFile(suffix=".tmp") as tmpfile:
            tmpfile.write(bibtex_string)
            tmpfile.flush()
            subprocess.call([EDITOR, tmpfile.name])
            bibtex = BibTexParser(tmpfile.read()+"\n", customization=homogeneize_latex_encoding)

        bibtex = bibtex.get_entry_dict()
        if len(bibtex) > 0:
            bibtex_name = bibtex.keys()[0]
            bibtex = bibtex[bibtex_name]
            bibtex_string = parsed2Bibtex(bibtex)
        else:
            bibtex_string = ''
        print("\nThe bibtex entry for "+filename+" is :")
        print(bibtex_string)
        check = tools.rawInput("Is it correct ? [Y/n] ")
    return bibtex


def addFile(src, filetype):
    """
    Add a file to the library
    """
    if filetype == 'article' or filetype is None:
        doi = findDOI(src)

    if filetype == 'book' or (filetype is None and doi is False):
        isbn = findISBN(src)

    if doi is False and isbn is False:
        if filetype is None:
            tools.warning("Could not determine the DOI or the ISBN for "+src+"." +
                    "Switching to manual entry.")
            doi_isbn = ''
            while doi_isbn not in ['doi', 'isbn']:
                doi_isbn = tools.rawInput("DOI / ISBN ? ").lower()
            if doi_isbn == 'doi':
                doi = tools.rawInput('DOI ? ')
            else:
                isbn = tools.rawInput('ISBN ? ')
        elif filetype == 'article':
            tools.warning("Could not determine the DOI for "+src +
                    ", switching to manual entry.")
            doi = tools.rawInput('DOI ? ')
        elif filetype == 'book':
            tools.warning("Could not determine the ISBN for "+src +
                    ", switching to manual entry.")
            isbn = tools.rawInput('ISBN ? ')
    elif doi is not False:
        print("DOI for "+src+" is "+doi+".")
    elif isbn is not False:
        print("ISBN for "+src+" is "+isbn+".")

    if doi is not False and doi != '':
        # Add extra \n for bibtexparser
        bibtex = doi2Bib(doi).strip().replace(',', ",\n")+"\n"
    elif isbn is not False and isbn != '':
        # Idem
        bibtex = isbn2Bib(isbn).strip()+"\n"
    else:
        bibtex = ''

    bibtex = checkBibtex(src, bibtex)

    authors = re.split(' and ', bibtex['author'])

    if bibtex['type'] == 'article':
        new_name = params.format_articles
        try:
            new_name = new_name.replace("%j", bibtex['journal'])
        except:
            pass
    elif bibtex['type'] == 'book':
        new_name = params.format_books

    new_name = new_name.replace("%t", bibtex['title'])
    try:
        new_name = new_name.replace("%Y", bibtex['year'])
    except:
        pass
    new_name = new_name.replace("%f", authors[0].split(',')[0].strip())
    new_name = new_name.replace("%l", authors[-1].split(',')[0].strip())
    new_name = new_name.replace("%a", ', '.join([i.split(',')[0].strip()
                                                for i in authors]))

    new_name = params.folder+tools.slugify(new_name)+tools.getExtension(src)

    while os.path.exists(new_name):
        tools.warning("file "+new_name+" already exists.")
        default_rename = new_name.replace(tools.getExtension(new_name),
                                          " (2)"+tools.getExtension(new_name))
        rename = tools.rawInput("New name ["+default_rename+"] ? ")
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

    bibtexAppend(bibtex)
    return new_name


def deleteId(ident):
    """
    Delete a file based on its id in the bibtex file
    """
    with open(params.folder+'index.bib', 'r') as fh:
        bibtex = BibTexParser(fh.read(), customization=homogeneize_latex_encoding)
    bibtex = bibtex.get_entry_dict()

    if ident not in bibtex.keys():
        return False

    try:
        os.remove(bibtex[ident]['file'])
    except:
        tools.warning("Unable to delete file associated to id "+ident+" : " +
                bibtex[ident]['file'])
    del(bibtex[ident])
    bibtexRewrite(bibtex)
    return True


def deleteFile(filename):
    """
    Delete a file based on its filename
    """
    with open(params.folder+'index.bib', 'r') as fh:
        bibtex = BibTexParser(fh.read(), customization=homogeneize_latex_encoding)
    bibtex = bibtex.get_entry_dict()

    found = False
    for key in bibtex.keys():
        if bibtex[key]['file'] == filename:
            found = True
            try:
                os.remove(bibtex[key]['file'])
            except:
                tools.warning("Unable to delete file associated to id "+key+" : " +
                        bibtex[key]['file'])
            del(bibtex[key])
    if found:
        bibtexRewrite(bibtex)
    return found


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


if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            sys.exit("Usage : TODO")

        if sys.argv[1] == 'download':
            if len(sys.argv) < 3:
                sys.exit("Usage : " + sys.argv[0] +
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
                sys.exit("Usage : " + sys.argv[0] +
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
                sys.exit("Usage : " + sys.argv[0] + " delete FILE|ID")

            confirm = tools.rawInput("Are you sure you want to delete "+sys.argv[2] +
                               " ? [y/N] ")

            if confirm.lower() == 'y':
                if not deleteId(sys.argv[2]):
                    if not deleteFile(sys.argv[2]):
                        tools.warning("Unable to delete "+sys.argv[2])
                        sys.exit(1)

                print(sys.argv[2]+" successfully deleted.")
            sys.exit()

        elif sys.argv[1] == 'list':
            raise Exception('TODO')

        elif sys.argv[1] == 'search':
            raise Exception('TODO')

        elif sys.argv[1] == 'rebuild':
            raise Exception('TODO')
    except KeyboardInterrupt:
        sys.exit()
