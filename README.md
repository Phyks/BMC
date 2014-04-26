BiblioManager
=============

BiblioManager is a simple script to download and store your articles. This is mostly based upon [the paperbot fork from a3nm](https://github.com/a3nm/paperbot).

**Note :** This script is currently a work in progress.

## What is BiblioManager (or what it is **not**) ?

I used to have a folder with poorly named papers and books and wanted something to help me handle it. I don't like Mendeley and Zotero and so on, which are heavy and overkill for my needs. I just want to feed a script with PDF files of papers and books, and I want it to automatically maintain a BibTeX index of these files, to help me cite them and find them back.

This is the goal of BiblioManager. It will :
* Download or import PDF/Djvu files
* Try to get automatically the metadata of the files (keywords, author, review, …)
* Store all the metadata in a BibTex file
* Rename your files to store them in a logical and homogeneous way
* Help you find them back
* Give you directly the bibtex entry necessary to cite them

BiblioManager will always use standard formats such as BibTeX, so that you can easily edit your library, export it and manage it by hand, even if you quit this software for any reason.


## Current status

* Able to import a PDF / djvu file, automagically find the DOI / ISBN, get the bibtex entry back and add it to the library. If DOI / ISBN search fails, it will prompt you for it.
* Able to download a URL, using any specified proxy (you can list many and it will try all of them) and store the pdf file with its metadata.

Should be almost working and usable now, although still to be considered as **experimental**.

**Important note :** I use it for personnal use, but I don't read articles from many journals. If you find any file which is not working, please fill an issue or send me an e-mail with the relevant information. There are alternative ways to get the metadata for example, and I didn't know really which one was the best one as writing this code.


## Installation
TODO -- To be updated


Install pdfminer, pdfparanoia (via pip) and requesocks.
Copy params.py.example as params.py and customize it.
Install pdftotext.
Install djvulibre to use djvu files.
Install isbntools with pip.


## Used source codes

* [pdfparanoia](https://github.com/kanzure/pdfparanoia) : Watermark removal
* [paperbot](https://github.com/kanzure/paperbot) although my fetching of papers is way more basic


## License

TODO

## Inspiration

* MPC
* http://en.dogeno.us/2010/02/release-a-python-script-for-organizing-scientific-papers-pyrenamepdf-py/
* [Bibsoup](http://openbiblio.net/2012/02/09/bibsoup-beta-released/)

## Ideas, TODO

A list of ideas and TODO. Don't hesitate to give feedback on the ones you really want or to propose your owns.

* pdfparanoia to remove the watermarks on pdf files
* Webserver interface
* Various re.compile ?
* check output of subprocesses before it ends
* Split main.py
* Categories

## Roadmap

* Working with local files
    [x] Import
    [x] Deletion
    [ ] Update ?
* Get distant files
    * cf paperbot
* Search engine / list
