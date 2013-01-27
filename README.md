# paperbot

Paperbot is an IRC bot that fetches academic papers. It monitors all conversation for links to scholarly content, then fetches the content and posts a public link. This seems to help enhance the quality of discussion and make us less ignorant.

<div id="details" />
<div id="deets" />
## deets

All content is scraped using [zotero/translators](https://github.com/zotero/translators). These are javascript scrapers that work on a large number of academic publisher sites and are actively maintained. Paperbot offloads links to [zotero/translation-server](https://github.com/zotero/translation-server), which runs the zotero scrapers headlessly in a gecko and xulrunner environment.

* [zotero/translators](https://github.com/zotero/translators)
* [zotero/translation-server](https://github.com/zotero/translation-server)
* [patched translation-server](https://github.com/kanzure/translation-server)

<div id="todo" />
## TODO

It would be nice to use multiple proxies to resolve a pdf request.

<div id="demo" />
<div id="channel" />
## active demo

say hi to paperbot on irc.freenode.net ##hplusroadmap

<div id="license" />
## license

BSD.

