"""
Fetches papers.
"""
import re
import os
import json
import random
import requests
import lxml.etree
from StringIO import StringIO

def download(phenny, input, verbose=True):
    """
    Downloads a paper.
    """
    # only accept requests in a channel
    if not input.sender.startswith('#'):
        # unless the user is an admin, of course
        if not input.admin:
            phenny.say("i only take requests in the ##hplusroadmap channel.")
            return
        else:
            # just give a warning message to the admin.. not a big deal.
            phenny.say("okay i'll try, but please send me requests in ##hplusroadmap in the future.")

    # get the input
    line = input.group()

    # was this an explicit command?
    explicit = False
    if line.startswith(phenny.nick):
        explicit = True
        line = line[len(phenny.nick):]

        if line.startswith(",") or line.startswith(":"):
            line = line[1:]

    if line.startswith(" "):
        line = line.strip()

    # don't bother if there's nothing there
    if len(line) < 5 or (not "http://" in line and not "https://" in line) or not line.startswith("http"):
        return
    for line in re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line):
        line = filter_fix(line)

        # fix for login.jsp links to ieee xplore
        line = fix_ieee_login_urls(line)

        translation_url = "http://localhost:1969/web"

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "url": line,
            "sessionid": "what"
        }

        data = json.dumps(data)

        response = requests.post(translation_url, data=data, headers=headers)

        if response.status_code == 200:
            # see if there are any attachments
            content = json.loads(response.content)
            item = content[0]
            title = item["title"]

            if item.has_key("attachments"):
                pdf_url = None
                for attachment in item["attachments"]:
                    if attachment.has_key("mimeType") and "application/pdf" in attachment["mimeType"]:
                        pdf_url = attachment["url"]
                        break

                if pdf_url:
                    user_agent = "Mozilla/5.0 (X11; Linux i686 (x86_64)) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11"

                    headers = {
                        "User-Agent": user_agent,
                    }

                    response = None
                    if pdf_url.startswith("https://"):
                        response = requests.get(pdf_url, headers=headers, verify=False)
                    else:
                        response = requests.get(pdf_url, headers=headers)

                    # detect failure
                    if response.status_code == 401:
                        phenny.say("HTTP 401 unauthorized " + str(pdf_url))
                        continue
                    elif response.status_code != 200:
                        phenny.say("HTTP " + str(response.status_code) + " " + str(pdf_url))
                        continue

                    data = response.content

                    # grr..
                    title = title.encode("ascii", "ignore")

                    path = os.path.join("/home/bryan/public_html/papers2/paperbot/", title + ".pdf")

                    file_handler = open(path, "w")
                    file_handler.write(data)
                    file_handler.close()

                    filename = requests.utils.quote(title)
                    url = "http://diyhpl.us/~bryan/papers2/paperbot/" + filename + ".pdf"

                    phenny.say(url)
                    continue
                elif verbose and explicit:
                    phenny.say(download_url(line))
                    continue
            elif verbose and explicit:
                phenny.say(download_url(line))
                continue
        elif verbose and explicit:
            if response.status_code == 501:
                if verbose:
                    phenny.say("no translator available, raw dump: " + download_url(line))
                    continue
            else:
                if verbose:
                    phenny.say("error: HTTP " + str(response.status_code) + " " + download_url(line))
                    continue
        else:
            continue
    return
download.commands = ["fetch", "get", "download"]
download.priority = "high"
download.rule = r'(.*)'

def download_ieee(url):
    """
    Downloads an IEEE paper. The Zotero translator requires frames/windows to
    be available. Eventually translation-server will be fixed, but until then
    it might be nice to have an IEEE workaround.
    """
    # url = "http://ieeexplore.ieee.org:80/xpl/freeabs_all.jsp?reload=true&arnumber=901261"
    # url = "http://ieeexplore.ieee.org/iel5/27/19498/00901261.pdf?arnumber=901261"
    raise NotImplementedError

def download_url(url):
    response = requests.get(url, headers={"User-Agent": "origami-pdf"})
    content = response.content

    # just make up a default filename
    title = "%0.2x" % random.getrandbits(128)

    # default extension
    extension = ".txt"

    if "pdf" in response.headers["content-type"]:
        extension = ".pdf"
    elif check_if_html(response):
        # parse the html string with lxml.etree
        tree = parse_html(content)

        # extract some metadata with xpaths
        citation_pdf_url = find_citation_pdf_url(tree, url)
        citation_title = find_citation_title(tree)

        if citation_pdf_url and citation_title:
            citation_title = citation_title.encode("ascii", "ignore")
            response = requests.get(citation_pdf_url, headers={"User-Agent": "pdf-defense-force"})
            content = response.content
            if "pdf" in response.headers["content-type"]:
                extension = ".pdf"
                title = citation_title
        else:
            if "sciencedirect.com" in url:
                title = tree.xpath("//h1[@class='svTitle']")[0].text
                pdf_url = tree.xpath("//a[@id='pdfLink']/@href")[0]
                response = requests.get(pdf_url, headers={"User-Agent": "sdf-macross"})
                content = response.content
                if "pdf" in response.headers["content-type"]:
                    extension = ".pdf"
            elif "h1 class=\"articleTitle" in content:
                try:
                    title = tree.xpath("//h1[@class='articleTitle']")[0].text
                    title = title.encode("ascii", "ignore")
                    pdf_url = tree.xpath("//a[@title='View the Full Text PDF']/@href")[0]
                except:
                    pass
                else:
                    if pdf_url.startswith("/"):
                        url_start = url[:url.find("/",8)]
                        pdf_url = url_start + pdf_url
                    response = requests.get(pdf_url, headers={"User-Agent": "pdf-teapot"})
                    content = response.content
                    if "pdf" in response.headers["content-type"]:
                        extension = ".pdf"
            # raise Exception("problem with citation_pdf_url or citation_title")
            # well, at least save the contents from the original url
            pass

    # can't create directories
    title = title.replace("/", "_")

    path = os.path.join("/home/bryan/public_html/papers2/paperbot/", title + extension)

    file_handler = open(path, "w")
    file_handler.write(content)
    file_handler.close()

    url = "http://diyhpl.us/~bryan/papers2/paperbot/" + requests.utils.quote(title) + extension

    return url

def parse_html(content):
    if not isinstance(content, StringIO):
        content = StringIO(content)
    parser = lxml.etree.HTMLParser()
    tree = lxml.etree.parse(content, parser)
    return tree

def check_if_html(response):
    return "text/html" in response.headers["content-type"]

def find_citation_pdf_url(tree, url):
    """
    Returns the <meta name="citation_pdf_url"> content attribute.
    """
    citation_pdf_url = extract_meta_content(tree, "citation_pdf_url")
    if citation_pdf_url and  not citation_pdf_url.startswith("http"):
        if citation_pdf_url.startswith("/"):
            url_start = url[:url.find("/",8)]
            citation_pdf_url = url_start + citation_pdf_url
        else:
            raise Exception("unhandled situation (citation_pdf_url)")
    return citation_pdf_url

def find_citation_title(tree):
    """
    Returns the <meta name="citation_title"> content attribute.
    """
    citation_title = extract_meta_content(tree, "citation_title")
    return citation_title

def extract_meta_content(tree, meta_name):
    try:
        content = tree.xpath("//meta[@name='" + meta_name + "']/@content")[0]
    except:
        return None
    else:
        return content

def filter_fix(url):
    """
    Fixes some common problems in urls.
    """
    if ".proxy.lib.pdx.edu" in url:
        url = url.replace(".proxy.lib.pdx.edu", "")
    return url

def fix_ieee_login_urls(url):
    """
    Fixes urls point to login.jsp on IEEE Xplore. When someone browses to the
    abstracts page on IEEE Xplore, they are sometimes sent to the login.jsp
    page, and then this link is given to paperbot. The actual link is based on
    the arnumber.

    example:
    http://ieeexplore.ieee.org/xpl/login.jsp?tp=&arnumber=806324&url=http%3A%2F%2Fieeexplore.ieee.org%2Fxpls%2Fabs_all.jsp%3Farnumber%3D806324
    """
    if "ieeexplore.ieee.org/xpl/login.jsp" in url:
        if "arnumber=" in url:
            parts = url.split("arnumber=")

            # i guess the url might not look like the example in the docstring
            if "&" in parts[1]:
                arnumber = parts[1].split("&")[0]
            else:
                arnumber = parts[1]

            return "http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=" + arnumber

    # default case when things go wrong
    return url

