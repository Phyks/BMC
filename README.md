BiblioManager
=============

[![Build Status](https://travis-ci.org/Phyks/BMC.svg?branch=master)](https://travis-ci.org/Phyks/BMC)

BiblioManager is a simple script to download and store your articles. Read on if you want more info :)

**Note :** This script is currently a work in progress.

## What is BiblioManager (or what it is **not**) ?

I used to have a folder with poorly named papers and books and wanted something to help me handle it. I don't like Mendeley and Zotero and so on, which are heavy and overkill for my needs. I just want to feed a script with PDF files of papers and books, or URLs to PDF files, and I want it to automatically maintain a BibTeX index of these files, to help me cite them and find them back. Then, I want it to give me a way to easily retrieve a file, either by author, by title or with some other search method, and give me the associated bibtex entry.

This is the goal of BiblioManager. This script can :
* Download or import PDF/Djvu files
* Try to get automatically the metadata of the files (keywords, author, review, …)
* Store all the metadata in a BibTex file
* Rename your files to store them in a logical and homogeneous way according to a user-defined mask
* Help you find them back
* Give you directly the bibtex entry necessary to cite them
* Remove some of the watermarks included in those files (the front page with your ip address from IOP for instance)

BiblioManager will always use standard formats such as BibTeX, so that you can easily edit your library, export it and manage it by hand, even if you quit this software for any reason.


## Current status

Should be almost working and usable now, although still to be considered as **experimental**. It can be **broken** at **any commit** and not repaired for a few days. I will update this when I will have a version that I can consider to be “stable”.

**Important note :** I use it for personal use, but I don't read articles from many journals. If you find any file which is not working, please fill an issue or send me an e-mail with the relevant information. There are alternative ways to get the metadata for example, and I didn't know really which one was the best one as writing this code. Please do backups regularly if using this. I could not be held responsible for any loss of papers.


* Import
    * working: all (file / tags / bibtex modification / bibtex retrieval / remove watermark pages)
* Download
    * working: all
* Delete
    * working: all (by file and by id)
* Edit
    * working: all
* List
    * working
* Search
    * TODO
* Open
    * working: all
* Resync
    * working
* Update
    * working


**Error reporting :** If you have any issue with this script, please report error. If possible, send me the article responsible for the error, or at least give me the reference so that I can test and debug easily.

## Installation

* Clone this git repository where you want:
```
git clone https://github.com/Phyks/BMC
```
* Install `requesocks`, `bibtexparser` (https://github.com/sciunto/python-bibtexparser), `PyPDF2` and `isbntools` _via_ Pypi
```
sudo pip install requesocks bibtexparser pyPDF2 isbntools
```
(replace pip by pip2 if your distribution ships python3 by default)
* Install `pdftotext` (provided by Xpdf) and `djvulibre` _via_ your package manager or the way you want
* Copy `params.py.example` to `params.py` and customize it to fit your needs

*Note:* To update the script, just run `git pull` in the script dir.

## Usage

### To import an existing PDF / Djvu file

Run `./bmc.py import PATH_TO_FILE [article|book]`. `[article|book]` is an optional argument (article or book) to search only for DOI or ISBN and thus, speed up the import.

It will get automatically the bibtex entry corresponding to the document, and you will be prompted for confirmation. It will then copy the file to your papers dir, renaming it according to the specified mask in `params.py`.

### To download a PDF / Djvu file

Run `./bmc.py download URL_TO_PDF [article|book]`, where `[article|book]` (article or book) is again a parameter to specify to search only for DOI or ISBN only, and thus speed up the import. The `URL_TO_PDF` parameter should be a direct link to the PDF file (meaning it should be the link to the pdf page, which may have an authentication portal and not the page with abstract on many publishers websites).

The script will try to download the file with the proxies specified in `params.py` until it manages to get the file, or runs out of available proxies.

It will get automatically the bibtex entry corresponding to the document, and you will be prompted for confirmation. It will then put the file in your papers dir, renaming it according to the specified mask in `params.py`.

### Delete an entry

Run `./bmc.py delete PARAM` where `PARAM` should be either a path to a paper file, or an ident in the bibtex index. This will remove the corresponding entry in the bibtex index, and will remove the file from your papers dir. Although it will prompt you for confirmation, there's no way to recover your file after deletion, so use with care.

### Search for an entry

TODO

### List all entries

Run `./bmc.py list` to list all the papers in your paper folder.

### Edit entries

Run `./bmc.py edit PARAM` where `PARAM` should be either a path to a paper file or an ident in the bibtex index. This will open a text editor to edit the corresponding bibtex entry.

### Download the latest version for papers from arXiv

Run `./bmc.py update` to look for available updated versions of your arXiv papers. You can use the optionnal `--entries ID` argument (where ID is either a bibtex index identifier or a filename) to search only for a limited subset of papers.

### Importing long articles / books without DOI / ISBN

When you import a long article without any DOI or ISBN, the script will process the whole file before finding out that there is no such information. This can take a while for long articles, and you may feel the script has entered an infinite loop. If you think it's taking too long, you can `^C` and you will be dropped to manual entry of bibtex infos.

### Data storage

All your documents will be stored in the papers dir specified in `params.py`. All the bibtex entries will be added to the `index.bib` file. You should **not** add entries to this file (but you can edit existing entries without any problem), as this will break synchronization between documents in papers dir and the index. If you do so, you can resync the index file with `./bmc.py resync`.

The resync option will check that all bibtex entries have a corresponding file and all file have a corresponding bibtex entry. It will prompt you what to do for unmatched entries.

## License

All the source code I wrote is under a `no-alcohol beer-ware license`. All functions that I didn't write myself are under the original license and their origin is specified in the function itself.
```
* --------------------------------------------------------------------------------
* "THE NO-ALCOHOL BEER-WARE LICENSE" (Revision 42):
* Phyks (webmaster@phyks.me) wrote this file. As long as you retain this notice you
* can do whatever you want with this stuff (and you can also do whatever you want
* with this stuff without retaining it, but that's not cool...). If we meet some
* day, and you think this stuff is worth it, you can buy me a <del>beer</del> soda
* in return.
*																		Phyks
* ---------------------------------------------------------------------------------
```

I used the `tearpages.py` script from sciunto, which can be found [here](https://github.com/sciunto/tear-pages) and is released under a GNU GPLv3 license.

## Inspiration

Here are some sources of inspirations for this project :

* MPC
* http://en.dogeno.us/2010/02/release-a-python-script-for-organizing-scientific-papers-pyrenamepdf-py/
* [Bibsoup](http://openbiblio.net/2012/02/09/bibsoup-beta-released/)
* [Paperbot](https://github.com/kanzure/paperbot)

## Ideas, TODO

A list of ideas and TODO. Don't hesitate to give feedback on the ones you really want or to propose your owns.

60. Unittest
80. Search engine
85. Anti-duplicate ?
90. Look for published version in arXiv
95. No DOI for HAL => metadata with SOAP API… don't want to handle it for now :/
200. Webserver interface ? GUI ? (not likely for now…)

## Thanks

* Nathan Grigg for his [arxiv2bib](https://pypi.python.org/pypi/arxiv2bib/1.0.5#downloads) python module
* François Boulogne for his [python-bibtexparser](https://github.com/sciunto/python-bibtexparser) python module and his integration of new requested features
* pyparsing [search parser example](http://pyparsing.wikispaces.com/file/view/searchparser.py)
