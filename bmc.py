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
from codecs import open

EDITOR = os.environ.get('EDITOR') if os.environ.get('EDITOR') else 'vim'


def checkBibtex(filename, bibtex_string):
    print("The bibtex entry found for "+filename+" is:")

    bibtex = BibTexParser(bibtex_string)
    bibtex = bibtex.get_entry_dict()
    try:
        bibtex = bibtex[bibtex.keys()[0]]
        print(bibtex_string)
        check = tools.rawInput("Is it correct? [Y/n] ")
    except:
        check = 'n'

    try:
        old_filename = bibtex['file']
    except:
        old_filename = False

    while check.lower() == 'n':
        with tempfile.NamedTemporaryFile(suffix=".tmp") as tmpfile:
            tmpfile.write(bibtex_string)
            tmpfile.flush()
            subprocess.call([EDITOR, tmpfile.name])
            tmpfile.seek(0)
            bibtex = BibTexParser(tmpfile.read()+"\n")

        bibtex = bibtex.get_entry_dict()
        try:
            bibtex = bibtex[bibtex.keys()[0]]
        except:
            tools.warning("Invalid bibtex entry")
            bibtex_string = ''
            tools.rawInput("Press Enter to go back to editor.")
            continue
        if('authors' not in bibtex and 'title' not in bibtex and 'year' not in
           bibtex):
            tools.warning("Invalid bibtex entry")
            bibtex_string = ''
            tools.rawInput("Press Enter to go back to editor.")
            continue

        if old_filename is not False and 'file' not in bibtex:
            tools.warning("Invalid bibtex entry. No filename given.")
            tools.rawInput("Press Enter to go back to editor.")
            check = 'n'
        else:
            bibtex_string = tools.parsed2Bibtex(bibtex)
            print("\nThe bibtex entry for "+filename+" is:")
            print(bibtex_string)
            check = tools.rawInput("Is it correct? [Y/n] ")
    if old_filename is not False and old_filename != bibtex['file']:
        try:
            print("Moving file to new location…")
            shutil.move(old_filename, bibtex['file'])
        except:
            tools.warning("Unable to move file "+old_filename+" to " +
                          bibtex['file']+". You should check it manually.")

    return bibtex


def addFile(src, filetype, manual, autoconfirm, tag):
    """
    Add a file to the library
    """
    doi = False
    arxiv = False
    isbn = False

    if not manual:
        try:
            if filetype == 'article' or filetype is None:
                doi = fetcher.findDOI(src)
            if doi is False and (filetype == 'article' or filetype is None):
                arxiv = fetcher.findArXivId(src)

            if filetype == 'book' or (doi is False and arxiv is False and
                                      filetype is None):
                isbn = fetcher.findISBN(src)
        except KeyboardInterrupt:
            doi = False
            arxiv = False
            isbn = False

    if doi is False and isbn is False and arxiv is False:
        if filetype is None:
            tools.warning("Could not determine the DOI nor the arXiv id nor " +
                          "the ISBN for "+src+". Switching to manual entry.")
            doi_arxiv_isbn = ''
            while doi_arxiv_isbn not in ['doi', 'arxiv', 'isbn', 'manual']:
                doi_arxiv_isbn = tools.rawInput("DOI / arXiv " +
                                                "/ ISBN / manual? ").lower()
            if doi_arxiv_isbn == 'doi':
                doi = tools.rawInput('DOI? ')
            elif doi_arxiv_isbn == 'arxiv':
                arxiv = tools.rawInput('arXiv id? ')
            elif doi_arxiv_isbn == 'isbn':
                isbn = tools.rawInput('ISBN? ')
        elif filetype == 'article':
            tools.warning("Could not determine the DOI nor the arXiv id for " +
                          src+", switching to manual entry.")
            doi_arxiv = ''
            while doi_arxiv not in ['doi', 'arxiv', 'manual']:
                doi_arxiv = tools.rawInput("DOI / arXiv / manual? ").lower()
            if doi_arxiv == 'doi':
                doi = tools.rawInput('DOI? ')
            elif doi_arxiv == 'arxiv':
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

    bibtex = BibTexParser(bibtex)
    bibtex = bibtex.get_entry_dict()
    if len(bibtex) > 0:
        bibtex_name = bibtex.keys()[0]
        bibtex = bibtex[bibtex_name]
        bibtex_string = tools.parsed2Bibtex(bibtex)
    else:
        bibtex_string = ''

    if not autoconfirm:
        bibtex = checkBibtex(src, bibtex_string)

    if not autoconfirm:
        tag = tools.rawInput("Tag for this paper (leave empty for default) ? ")
    else:
        tag = args.tag
    bibtex['tag'] = tag

    new_name = backend.getNewName(src, bibtex, tag)

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
    try:
        if 'IOP' in bibtex['publisher'] and bibtex['type'] == 'article':
            tearpages.tearpage(new_name)
    except:
        pass

    backend.bibtexAppend(bibtex)
    return new_name


def editEntry(entry, file_id='both'):
    bibtex = backend.getBibtex(entry, file_id)
    if bibtex is False:
        tools.warning("Entry "+entry+" does not exist.")
        return False

    if file_id == 'file':
        filename = entry
    else:
        filename = bibtex['file']
    new_bibtex = checkBibtex(filename, tools.parsed2Bibtex(bibtex))

    # Tag update
    if new_bibtex['tag'] != bibtex['tag']:
        print("Editing tag, moving file.")
        new_name = backend.getNewName(new_bibtex['file'],
                                      new_bibtex,
                                      new_bibtex['tag'])

        while os.path.exists(new_name):
            tools.warning("file "+new_name+" already exists.")
            default_rename = new_name.replace(tools.getExtension(new_name),
                                              " (2)" +
                                              tools.getExtension(new_name))
            rename = tools.rawInput("New name ["+default_rename+"]? ")
            if rename == '':
                new_name = default_rename
            else:
                new_name = rename
        new_bibtex['file'] = new_name

        try:
            shutil.move(bibtex['file'], new_bibtex['file'])
        except:
            raise Exception('Unable to move file '+bibtex['file']+' to ' +
                            new_bibtex['file'] + ' according to tag edit.')

        try:
            if not os.listdir(os.path.dirname(bibtex['file'])):
                os.rmdir(os.path.dirname(bibtex['file']))
        except:
            tools.warning("Unable to delete empty tag dir " +
                          os.path.dirname(bibtex['file']))

    try:
        with open(params.folder+'index.bib', 'r', encoding='utf-8') as fh:
            index = BibTexParser(fh.read())
        index = index.get_entry_dict()
    except:
        tools.warning("Unable to open index file.")
        return False

    index[new_bibtex['id']] = new_bibtex
    backend.bibtexRewrite(index)
    return True


def downloadFile(url, filetype, manual, autoconfirm, tag):
    print('Downloading '+url)
    dl, contenttype = fetcher.download(url)

    if dl is not False:
        print('Download finished')
        tmp = tempfile.NamedTemporaryFile(suffix='.'+contenttype)

        with open(tmp.name, 'w+') as fh:
            fh.write(dl)
        new_name = addFile(tmp.name, filetype, manual, autoconfirm, tag)
        tmp.close()
        return new_name
    else:
        tools.warning("Could not fetch "+url)
        return False


def openFile(ident):
    try:
        with open(params.folder+'index.bib', 'r', encoding='utf-8') as fh:
            bibtex = BibTexParser(fh.read())
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

    if diff is False:
        return False

    for key in diff:
        entry = diff[key]
        if entry['file'] == '':
            print("\nFound entry in index without associated file: " +
                  entry['id'])
            print("Title:\t"+entry['title'])
            loop = True
            while confirm:
                filename = tools.rawInput("File to import for this entry " +
                                          "(leave empty to delete the " +
                                          "entry)? ")
                if filename == '':
                    break
                else:
                    if 'doi' in entry.keys():
                        doi = fetcher.findDOI(filename)
                        if doi is not False and doi != entry['doi']:
                            loop = tools.rawInput("Found DOI does not " +
                                                  "match bibtex entry " +
                                                  "DOI, continue anyway " +
                                                  "? [y/N]")
                            loop = (loop.lower() != 'y')
                    if 'Eprint' in entry.keys():
                        arxiv = fetcher.findArXivId(filename)
                        if arxiv is not False and arxiv != entry['Eprint']:
                            loop = tools.rawInput("Found arXiv id does " +
                                                  "not match bibtex " +
                                                  "entry arxiv id, " +
                                                  "continue anyway ? [y/N]")
                            loop = (loop.lower() != 'y')
                    if 'isbn' in entry.keys():
                        isbn = fetcher.findISBN(filename)
                        if isbn is not False and isbn != entry['isbn']:
                            loop = tools.rawInput("Found ISBN does not " +
                                                  "match bibtex entry " +
                                                  "ISBN, continue anyway " +
                                                  "? [y/N]")
                            loop = (loop.lower() != 'y')
                    continue
            if filename == '':
                backend.deleteId(entry['id'])
                print("Deleted entry \""+entry['id']+"\".")
            else:
                new_name = backend.getNewName(filename, entry)
                try:
                    shutil.copy2(filename, new_name)
                    print("Imported new file "+filename+" for entry " +
                          entry['id']+".")
                except IOError:
                    new_name = False
                    sys.exit("Unable to move file to library dir " +
                             params.folder+".")
                backend.bibtexEdit(entry['id'], {'file': filename})
        else:
            print("Found file without any associated entry in index:")
            print(entry['file'])
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
    # Check for empty tag dirs
    for i in os.listdir(params.folder):
        if os.path.isdir(i) and not os.listdir(params.folder + i):
            try:
                os.rmdir(params.folder + i)
            except:
                tools.warning("Found empty tag dir "+params.folder + i +
                              " but could not delete it.")


def update(entry):
    update = backend.updateArXiv(entry)
    if update is not False:
        print("New version found for "+entry)
        print("\t Title: "+update['title'])
        confirm = tools.rawInput("Download it ? [Y/n] ")
        if confirm.lower() == 'n':
            return
        new_name = downloadFile('http://arxiv.org/pdf/'+update['eprint'],
                                'article', False)
        if new_name is not False:
            print(update['eprint']+" successfully imported as "+new_name)
        else:
            tools.warning("An error occurred while downloading "+url)
        confirm = tools.rawInput("Delete previous version ? [y/N] ")
        if confirm.lower() == 'y':
            if not backend.deleteId(entry):
                if not backend.deleteFile(entry):
                    tools.warning("Unable to remove previous version.")
                    return
            print("Previous version successfully deleted.")


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
    parser_download.add_argument('-y', default=False,
                                 help="Confirm all")
    parser_download.add_argument('--tag', default='', help="Tag")
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
    parser_import.add_argument('-y', default=False,
                               help="Confirm all")
    parser_import.add_argument('--tag', default='', help="Tag")
    parser_import.add_argument('file',  nargs='+',
                               help="path to the file to import")
    parser_import.add_argument('--skip',  nargs='+',
                               help="path to files to skip")
    parser_import.set_defaults(func='import')

    parser_delete = subparsers.add_parser('delete', help="delete help")
    parser_delete.add_argument('entries', metavar='entry', nargs='+',
                               help="a filename or an identifier")
    parser_delete.add_argument('--skip',  nargs='+',
                               help="path to files to skip")
    group = parser_delete.add_mutually_exclusive_group()
    group.add_argument('--id', action="store_true", default=False,
                       help="id based deletion")
    group.add_argument('--file', action="store_true", default=False,
                       help="file based deletion")
    parser_delete.add_argument('-f', '--force', default=False,
                               action='store_true',
                               help="delete without confirmation")
    parser_delete.set_defaults(func='delete')

    parser_edit = subparsers.add_parser('edit', help="edit help")
    parser_edit.add_argument('entries', metavar='entry', nargs='+',
                             help="a filename or an identifier")
    parser_edit.add_argument('--skip',  nargs='+',
                             help="path to files to skip")
    group = parser_edit.add_mutually_exclusive_group()
    group.add_argument('--id', action="store_true", default=False,
                       help="id based deletion")
    group.add_argument('--file', action="store_true", default=False,
                       help="file based deletion")
    parser_edit.set_defaults(func='edit')

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

    parser_update = subparsers.add_parser('update', help="update help")
    parser_update.add_argument('--entries', metavar='entry', nargs='+',
                               help="a filename or an identifier")
    parser_update.set_defaults(func='update')

    parser_search = subparsers.add_parser('search', help="search help")
    parser_search.add_argument('query', metavar='entry', nargs='+',
                               help="your query, see README for more info.")
    parser_search.set_defaults(func='search')

    args = parser.parse_args()
    try:
        if args.func == 'download':
            for url in args.url:
                new_name = downloadFile(url, args.type, args.manual, args.y,
                                        args.tag)
                if new_name is not False:
                    print(url+" successfully imported as "+new_name)
                else:
                    tools.warning("An error occurred while downloading "+url)
            sys.exit()

        if args.func == 'import':
            for filename in list(set(args.file) - set(args.skip)):
                new_name = addFile(filename, args.type, args.manual, args.y,
                                   args.tag)
                if new_name is not False:
                    print(sys.argv[2]+" successfully imported as " +
                          new_name+".")
                else:
                    tools.warning("An error occurred while importing " +
                                  filename)
            sys.exit()

        elif args.func == 'delete':
            for filename in list(set(args.entries) - set(args.skip)):
                if not args.force:
                    confirm = tools.rawInput("Are you sure you want to " +
                                             "delete "+filename+" ? [y/N] ")
                else:
                    confirm = 'y'

                if confirm.lower() == 'y':
                    if args.file or not backend.deleteId(filename):
                        if args.id or not backend.deleteFile(filename):
                            tools.warning("Unable to delete "+filename)
                            sys.exit(1)

                    print(filename+" successfully deleted.")
            sys.exit()

        elif args.func == 'edit':
            for filename in list(set(args.entries) - set(args.skip)):
                if args.file:
                    file_id = 'file'
                elif args.id:
                    file_id = 'id'
                else:
                    file_id = 'both'
                editEntry(filename, file_id)
            sys.exit()

        elif args.func == 'list':
            listPapers = tools.listDir(params.folder)
            listPapers.sort()

            for paper in listPapers:
                if tools.getExtension(paper) not in [".pdf", ".djvu"]:
                    continue
                print(paper)

        elif args.func == 'search':
            raise Exception('TODO')

        elif args.func == 'open':
            for filename in args.ids:
                if not openFile(filename):
                    sys.exit("Unable to open file associated " +
                             "to ident "+filename)
            sys.exit()

        elif args.func == 'resync':
            confirm = tools.rawInput("Resync files and bibtex index? [y/N] ")
            if confirm.lower() == 'y':
                resync()
            sys.exit()

        elif args.func == 'update':
            if args.entries is None:
                entries = backend.getEntries()
            else:
                entries = args.entries
            for entry in entries:
                update(entry)
            sys.exit()

    except KeyboardInterrupt:
        sys.exit()
