import tempfile

from backend import tools
from libbmc import fetcher


def download(url, filetype, manual, autoconfirm, tag):
    """
    Download a given URL and add it to the library.

    :param url: URL to download.
    :param filetype: paper / book / ``None``.
    :param manual: Whether BibTeX should be fetched automatically.
    :param autoconfirm: Whether import should be made silent or not.
    :param tag: A tag for this file.
    :returns: The name of the downloaded file once imported, \
            or ``None`` in case of error.
    """
    # Download the paper
    print("Downloading %s…" % (url,))
    dl, contenttype = fetcher.download(url)

    if dl is not None:
        print("Download finished.")

        # Store it to a temporary file
        try:
            tmp = tempfile.NamedTemporaryFile(suffix='.%s' % (contenttype,))
            with open(tmp.name, 'wb+') as fh:
                fh.write(dl)

            # And add it as a normal paper from now on
            new_name = import_file(tmp.name, filetype, manual,
                                   autoconfirm, tag)
            if new_name is None:
                return None
            else:
                return new_name
        finally:
            tmp.close()
    else:
        tools.warning("Could not fetch %s." % (url,))
        return None


def import_file(src, filetype, manual, autoconfirm, tag, rename=True):
    """
    Add a file to the library.

    :param src: The path of the file to import.
    :param filetype: paper / book / ``None``.
    :param manual: Whether BibTeX should be fetched automatically.
    :param autoconfirm: Whether import should be made silent or not.
    :param tag: A tag for this file.
    :param rename: TODO
    :returns: The name of the imported file, or ``None`` in case of error.
    """
    # TODO
    pass
