import libbmc
import os
import subprocess
import tempfile

from backend import config
from backend import tools
from libbmc import bibtex
from libbmc import fetcher
from libbmc.repositories import arxiv
from libbmc.papers import identifiers
from libbmc.papers import tearpages


def get_entry_from_index(item, file_or_id=None):
    """
    Fetch an entry from the global index.

    :param item: An identifier or filename.
    :param file_or_id: Whether it is a file or an entry identifier. If \
            ``None``, will try to match both.
    :returns: TODO.
    """
    entry = None
    # If explictly an identifier
    if file_or_id == "id":
        entry = bibtex.get_entry(config.get("index"), item)
    # If explicitely a filename
    elif file_or_id == "file":
        entry = bibtex.get_entry_by_filter(config.get("index"),
                                           lambda x: x.file == item)  # TODO
    # Else, get by id or file
    else:
        entry = bibtex.get_entry_by_filter(config.get("index"),
                                           lambda x: (
                                               x.id == item or
                                               x.file == item))  # TODO
    return entry


def download(url, manual, autoconfirm, tag):
    """
    Download a given URL and add it to the library.

    :param url: URL to download.
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
            new_name = import_file(tmp.name, manual,
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


def import_file(src, manual=False, autoconfirm=False,
                tag='', rename=True):
    """
    Add a file to the library.

    :param src: The path of the file to import.
    :param manual: Whether BibTeX should be fetched automatically. \
            Default to ``False``.
    :param autoconfirm: Whether import should be made silent or not. \
            Default to ``False``.
    :param tag: A tag for this file. \
            Default to no tag.
    :param rename: Whether or not the file should be renamed according to the \
            mask in the config.
    :returns: The name of the imported file, or ``None`` in case of error.
    """
    if not manual:
        type, identifier = identifiers.find_identifiers(src)

    if type is None:
        tools.warning("Could not find an identifier for %s. \
                      Switching to manual entry." % (src))
        # Fetch available identifiers types from libbmc
        # Append "manual" for manual entry of BibTeX and "skip" to skip the
        # file.
        available_types_list = (libbmc.__valid_identifiers__ +
                                ["manual", "skip"])
        available_types = " / ".joint(available_types_list)
        # Query for the type to use
        while type not in available_types_list:
            type = input("%s? " % (available_types)).lower()

        if type == "skip":
            # If "skip" is chosen, skip this file
            return None
        elif type == "manual":
            identifier = None
        else:
            # Query for the identifier if required
            identifier = input("Value? ")
    else:
        print("%s found for %s: %s." % (type, src, identifier))

    # Fetch BibTeX automatically if we have an identifier
    bibtex = None
    if identifier is not None:
        # If an identifier was provided, try to automatically fetch the bibtex
        bibtex = identifiers.get_bibtex((type, identifier))

    # TODO: Check bibtex

    # Handle tag
    if not autoconfirm:
        # If autoconfirm is not enabled, query for a tag
        user_tag = input("Tag for this paper [%s]? " % tag)
        if user_tag != "":
            tag = user_tag
    bibtex["tag"] = tag

    # TODO: Handle renaming
    new_name = src
    if rename:
        pass

    bibtex['file'] = os.path.abspath(new_name)

    # Tear some pages if needed
    should_tear_pages = True
    if not autoconfirm:
        # Ask for confirmation
        pages_to_tear = tearpages.tearpage_needed(bibtex)
        user_tear_pages = input("Found some pages to tear: %s. \
                                Confirm? [Y/n]" % (pages_to_tear)).lower()
        if user_tear_pages == "n":
            should_tear_pages = False
    if should_tear_pages:
        tearpages.tearpage(new_name, bibtex=bibtex)

    # TODO: Append to global bibtex index

    return new_name


def delete(item, keep=False, file_or_id=None):
    """
    Delete an entry in the main BibTeX file, and the associated documents.

    :param item: An entry or filename to delete from the database.
    :param keep: Whether or not the document should be kept on the disk. \
            If True, will simply delete the entry in the main BibTeX index.
    :param file_or_id: Whether it is a file or an entry identifier. If \
            ``None``, will try to match both.
    :returns: Nothing.
    """
    entry = get_entry_from_index(item, file_or_id)

    # Delete the entry from the bibtex index
    bibtex.delete(config.get("index"), entry.id)  # TODO

    # If file should not be kept
    if not keep:
        # Delete it
        os.unlink(entry.file)  # TODO


def edit(item, file_or_id):
    """
    Edit an entry in the main BibTeX file.

    :param item: An entry or filename to edit in the database.
    :param file_or_id: Whether it is a file or an entry identifier. If \
            ``None``, will try to match both.
    :returns: Nothing.
    """
    # TODO
    pass


def list_entries():
    """
    List all the available entries and their associated files.

    :returns: A dict with entry identifiers as keys and associated files as \
            values.
    """
    # Get the list of entries from the BibTeX index
    entries_list = bibtex.get(config.get("index"))
    return {entry.id: entry.file for entry in entries_list}  # TODO


def open(id):
    """
    Open the file associated with the provided entry identifier.

    :param id: An entry identifier in the main BibTeX file.
    :returns: ``False`` if an error occured. ``True`` otherwise.
    """
    # Fetch the entry from the BibTeX index
    entry = bibtex.get_entry(config.get("index"), id)
    if entry is None:
        return False
    else:
        # Run xdg-open on the associated file to open it
        subprocess.Popen(['xdg-open', entry.filename])  # TODO
        return True


def export(item, file_or_id=None):
    """
    Export the BibTeX entries associated to some items.

    :param item: An entry or filename to export as BibTeX.
    :param file_or_id: Whether it is a file or an entry identifier. If \
            ``None``, will try to match both.
    :returns: TODO.
    """
    # Fetch the entry from the BibTeX index
    entry = get_entry_from_index(item, file_or_id)
    if entry is not None:
        return bibtex.dict2BibTeX(entry)  # TODO


def resync():
    """
    Compute the diff between the main BibTeX index and the files on the disk,
    and try to resync them.

    :returns: Nothing.
    """
    # TODO
    pass


def update(item, file_or_id=None):
    """
    Update an entry, trying to fetch a more recent version (on arXiv for \
            instance.)

    :param item: An entry or filename to fetch update from.
    :param file_or_id: Whether it is a file or an entry identifier. If \
            ``None``, will try to match both.
    :returns: TODO.
    """
    entry = get_entry_from_index(item, file_or_id)
    # Fetch latest version
    latest_version = arxiv.get_latest_version(entry.eprint)  # TODO
    if latest_version != entry.eprint:  # TODO
        print("New version found for %s: %s" % (entry, latest_version))
        confirm = input("Download it? [Y/n] ")
        if confirm.lower() == 'n':
            return

        # Download the updated version
        # TODO

        # Delete previous version if needed
        # TODO
