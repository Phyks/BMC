Forked from https://github.com/a3nm/paperbot
# paperbot

Paperbot is an command line utility that fetches academic papers. When given a URL on stdin or as a CLI argument, it fetches the content and returns a public link on stdout. This seems to help enhance the quality of discussion and make us less ignorant.

Paperbot can easily be turned back into an IRC bot with [irctk](http://gitorious.org/irctk)

<div id="details" />
<div id="deets" />
## deets

All content is scraped using [zotero/translators](https://github.com/zotero/translators). These are javascript scrapers that work on a large number of academic publisher sites and are actively maintained. Paperbot offloads links to [zotero/translation-server](https://github.com/zotero/translation-server), which runs the zotero scrapers headlessly in a gecko and xulrunner environment. The scrapers return metadata and a link to the pdf. Then paperbot fetches that particular pdf. When given a link straight to a pdf, which paperbot is also happy to compulsively archive it.

Paperbot can try multiple instances of translation-server (configured to use different ways to access content) and different SOCKS proxies to retrieve the content.

* [zotero/translators](https://github.com/zotero/translators)
* [zotero/translation-server](https://github.com/zotero/translation-server)
* [patched translation-server](https://github.com/kanzure/translation-server)
* [phenny](https://github.com/sbp/phenny)
* [pdfparanoia](https://github.com/kanzure/pdfparanoia)

<div id="license" />
## license

BSD.
Original project is: https://github.com/kanzure/paperbot

