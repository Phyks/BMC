BiblioManager
=============

BiblioManager is a simple script to download and store your articles. This is mostly based upon [the paperbot fork from a3nm](https://github.com/a3nm/paperbot).

**Note :** This script is currently a work in progress.

## What is BiblioManager (or what it is **not**) ?

I used to have a folder with poorly named papers and books and wanted something to help me handle it. I don't like Mendeley and Zotero and so on, which are heavy and overkill for my needs. I just want to feed a script with PDF files of papers and books, and I want it to automatically maintain a BibTeX index of these files, to help me cite them and find them back.

This is the goal of BiblioManager. It will :
* Download or import PDF files (but also epub, djvu etc.)
* Try to get automatically the metadata of the files (keywords, author, review, …)
* Store all the metadata in a BibTex file
* Rename your files to store them in a logical and homogeneous way
* Help you find them back
* Give you directly the bibtex entry necessary to cite them

BiblioManager will always use standard formats such as BibTeX, so that you can easily edit your library, export it and manage it by hand, even if you quit this software for any reason.


## Installation
TODO -- To be updated


Install pdfminer, pdfparanoia (via pip) and requesocks.
Init the submodules and install Zotero translation server.
Copy params.py.example as params.py and customize it.


## Paperbot

Paperbot is a command line utility that fetches academic papers. When given a URL on stdin or as a CLI argument, it fetches the content and returns a public link on stdout. This seems to help enhance the quality of discussion and make us less ignorant.

All content is scraped using [zotero/translators](https://github.com/zotero/translators). These are javascript scrapers that work on a large number of academic publisher sites and are actively maintained. Paperbot offloads links to [zotero/translation-server](https://github.com/zotero/translation-server), which runs the zotero scrapers headlessly in a gecko and xulrunner environment. The scrapers return metadata and a link to the pdf. Then paperbot fetches that particular pdf. When given a link straight to a pdf, which paperbot is also happy to compulsively archive it.

I kept part of the code to handle pdf downloading, and added a backend behind it.

Paperbot can try multiple instances of translation-server (configured to use different ways to access content) and different SOCKS proxies to retrieve the content.


## Used source codes

* [zotero/translators](https://github.com/zotero/translators) : Links finder
* [zotero/translation-server](https://github.com/zotero/translation-server) : Links finder
* [pdfparanoia](https://github.com/kanzure/pdfparanoia) : Watermark removal


## License

TODO
