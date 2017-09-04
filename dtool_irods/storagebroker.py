"""iRODS storage broker."""

import os
import json
import logging
import tempfile
import time
import datetime

from dtoolcore.utils import (
    generate_identifier,
    mkdir_parents,
)
from dtoolcore.filehasher import FileHasher, md5sum
from dtoolcore.storagebroker import StorageBrokerOSError

from dtool_irods import CommandWrapper

logger = logging.getLogger(__name__)


#############################################################################
# iRODS helper functions.
#############################################################################

def _get_text(irods_path):
    """Get raw text from iRODS."""
    # Command to get contents of file to stdout.
    cmd = CommandWrapper([
        "iget",
        irods_path,
        "-"
    ])
    return cmd()


def _put_text(irods_path, text):
    """Put raw text into iRODS."""
    with tempfile.NamedTemporaryFile() as fh:
        fpath = fh.name
        fh.write(text)
        fh.flush()
        cmd = CommandWrapper([
            "iput",
            "-f",
            fpath,
            irods_path
        ])
        cmd()
    assert not os.path.isfile(fpath)


def _get_obj(irods_path):
    """Return object from JSON text stored in iRODS."""
    return json.loads(_get_text(irods_path))


def _put_obj(irods_path, obj):
    """Put python object into iRODS as JSON text."""
    text = json.dumps(obj)
    _put_text(irods_path, text)


def _path_exists(irods_path):
    cmd = CommandWrapper(["ils", irods_path])
    cmd(exit_on_failure=False)
    return cmd.success()


def _mkdir(irods_path):
    cmd = CommandWrapper(["imkdir", irods_path])
    cmd()


def _mkdir_if_missing(irods_path):
    if not _path_exists(irods_path):
        _mkdir(irods_path)


def _cp(fpath, irods_path):
    cmd = CommandWrapper(["iput", "-f", fpath, irods_path])
    cmd()


def _ls(irods_path):
    cmd = CommandWrapper(["ils", irods_path])
    cmd()
    text = cmd.stdout.strip()
    lines = text.split("\n")
    relevant_lines = lines[1:]
    cleaned_relevant_lines = [l.strip() for l in relevant_lines]
    return cleaned_relevant_lines


def _put_metadata(irods_path, key, value):
    cmd = CommandWrapper(["imeta", "add", "-d", irods_path, key, value])
    cmd()


def _get_metadata(irods_path, key):
    cmd = CommandWrapper(["imeta", "ls", "-d", irods_path, key])
    cmd()
    text = cmd.stdout
    value_line = text.split('\n')[2]
    value = value_line.split()[1]
    return value


def _get_checksum(irods_path):
    # Get the hash.
    cmd = CommandWrapper(["ichksum", irods_path])
    cmd()
    line = cmd.stdout.strip()
    info = line.split()
    compound_chksum = info[1]
    alg, checksum = compound_chksum.split(":")
    return checksum


def _get_size_and_timestamp(irods_path):
    cmd = CommandWrapper(["ils", "-l", irods_path])
    cmd()
    text = cmd.stdout.strip()
    first_line = text.split("\n")[0].strip()
    info = first_line.split()
    size_in_bytes = info[3]
    time_str = info[4]
    dt = datetime.datetime.strptime(time_str, "%Y-%m-%d.%H:%M")
    utc_timestamp = int(time.mktime(dt.timetuple()))
    return size_in_bytes, utc_timestamp

#############################################################################
# iRODS storage broker.
#############################################################################


class IrodsStorageBroker(object):
    """
    Storage broker to interact with datasets in iRODS.
    """

    #: Attribute used to define the type of storage broker.
    key = "irods"

    #: Attribute used by :class:`dtoolcore.ProtoDataSet` to write the hash
    #: function name to the manifest.
    hasher = FileHasher(md5sum)

    def __init__(self, uri, config=None):

        self._abspath = os.path.abspath(uri)
        self._dtool_abspath = os.path.join(self._abspath, '.dtool')
        self._admin_metadata_fpath = os.path.join(self._dtool_abspath, 'dtool')
        self._data_abspath = os.path.join(self._abspath, 'data')
        self._manifest_abspath = os.path.join(
            self._dtool_abspath,
            'manifest.json'
        )
        self._readme_abspath = os.path.join(
            self._abspath,
            'README.yml'
        )
        self._overlays_abspath = os.path.join(
            self._dtool_abspath,
            'overlays'
        )
        self._metadata_fragments_abspath = os.path.join(
            self._dtool_abspath,
            'tmp_fragments'
        )

        self._irods_cache_abspath = os.path.abspath("/tmp/dtool_irods_cache")
        if not os.path.isdir(self._irods_cache_abspath):
            os.mkdir(self._irods_cache_abspath)

    @classmethod
    def generate_uri(cls, name, uuid, prefix):
        dataset_path = os.path.join(prefix, uuid)
        dataset_abspath = os.path.abspath(dataset_path)
        return "{}:{}".format(cls.key, dataset_abspath)

#############################################################################
# Methods used by both ProtoDataSet and DataSet.
#############################################################################

    def get_admin_metadata(self):
        """Return admin metadata from iRODS.

        :returns: administrative metadata as a dictionary
        """
        return _get_obj(self._admin_metadata_fpath)

    def has_admin_metadata(self):
        """Return True if the administrative metadata exists.

        This is the definition of being a "dataset".
        """
        return _path_exists(self._admin_metadata_fpath)

    def get_readme_content(self):
        """Return content of the README file as a string.

        :returns: readme content as a string
        """
        return _get_text(self._readme_abspath)

    def put_overlay(self, overlay_name, overlay):
        """Store the overlay by writing it to iRODS.

        It is the client's responsibility to ensure that the overlay provided
        is a dictionary with valid contents.

        :param overlay_name: name of the overlay
        :overlay: overlay dictionary
        """
        fpath = os.path.join(self._overlays_abspath, overlay_name + '.json')
        _put_obj(fpath, overlay)

#############################################################################
# Methods only used by DataSet.
#############################################################################

    def get_manifest(self):
        """Return the manifest contents from iRODS.

        :returns: manifest as a dictionary
        """
        return _get_obj(self._manifest_abspath)

    def get_overlay(self, overlay_name):
        """Return overlay as a dictionary.

        :param overlay_name: name of the overlay
        :returns: overlay as a dictionary
        """
        fpath = os.path.join(self._overlays_abspath, overlay_name + '.json')
        return _get_obj(fpath)

    def get_item_abspath(self, identifier):
        """Return absolute path at which item content can be accessed.

        :param identifier: item identifier
        :returns: absolute path from which the item content can be accessed
        """
        # Create directory for the specific dataset.
        dataset_cache_abspath = os.path.join(
            self._irods_cache_abspath, self.uuid)
        if not os.path.isdir(dataset_cache_abspath):
            os.mkdir(dataset_cache_abspath)

        # Get the relpath from the handle metadata.
        irods_item_path = os.path.join(self._data_abspath, identifier)
        relpath = _get_metadata(irods_item_path, "handle")
        item_abspath = os.path.join(dataset_cache_abspath, relpath)
        mkdir_parents(item_abspath)

        fetch_file_from_irods = CommandWrapper([
            "iget",
            irods_item_path,
            item_abspath
        ])
        fetch_file_from_irods()

        return item_abspath


#############################################################################
# Methods only used by ProtoDataSet.
#############################################################################

    def create_structure(self):
        """Create necessary structure to hold a dataset."""

        # Ensure that the specified path does not exist and create it.
        if _path_exists(self._abspath):
            raise(StorageBrokerOSError(
                "Path already exists: {}".format(self._abspath)
            ))
        _mkdir(self._abspath)

        # Create more essential subdirectories.
        essential_subdirectories = [
            self._dtool_abspath,
            self._data_abspath,
            self._overlays_abspath
        ]
        for abspath in essential_subdirectories:
            _mkdir_if_missing(abspath)

    def put_admin_metadata(self, admin_metadata):
        """Store the admin metadata by writing to iRODS.

        It is the client's responsibility to ensure that the admin metadata
        provided is a dictionary with valid contents.

        :param admin_metadata: dictionary with administrative metadata
        """
        _put_obj(self._admin_metadata_fpath, admin_metadata)

    def put_manifest(self, manifest):
        """Store the manifest by writing it to iRODS.

        It is the client's responsibility to ensure that the manifest provided
        is a dictionary with valid contents.

        :param manifest: dictionary with manifest structural metadata
        """
        _put_obj(self._manifest_abspath, manifest)

    def put_readme(self, content):
        """
        Put content into the README of the dataset.

        The client is responsible for ensuring that the content is valid YAML.

        :param content: string to put into the README
        """
        _put_text(self._readme_abspath, content)

    def put_item(self, fpath, relpath):
        """Put item with content from fpath at relpath in dataset.

        Missing directories in relpath are created on the fly.

        :param fpath: path to the item on local disk
        :param relpath: relative path name given to the item in the dataset as
                        a handle
        """
        # Put the file into iRODS.
        fname = generate_identifier(relpath)
        dest_path = os.path.join(self._data_abspath, fname)
        _cp(fpath, dest_path)

        # Add the relpath handle as metadata.
        _put_metadata(dest_path, "handle", relpath)

    def iter_item_handles(self):
        """Return iterator over item handles."""
        for line in _ls(self._data_abspath):
            yield line

    def item_properties(self, handle):
        """Return properties of the item with the given handle."""
        irods_item_path = os.path.join(self._data_abspath, handle)

        # Get the hash.
        checksum = _get_checksum(irods_item_path)

        # Get the UTC timestamp and the size in bytes.
        size, timestamp = _get_size_and_timestamp(irods_item_path)

        # Get the relpath from the handle metadata.
        relpath = _get_metadata(irods_item_path, "handle")

        properties = {
            'size_in_bytes': size,
            'utc_timestamp': timestamp,
            'hash': checksum,
            'relpath': relpath
        }
        return properties

    def _handle_to_fragment_absprefixpath(self, handle):
        return generate_identifier(handle)

    def add_item_metadata(self, handle, key, value):
        """Store the given key:value pair for the item associated with handle.

        :param handle: handle for accessing an item before the dataset is
                       frozen
        :param key: metadata key
        :param value: metadata value
        """

    def get_item_metadata(self, handle):
        """Return dictionary containing all metadata associated with handle.

        In other words all the metadata added using the ``add_item_metadata``
        method.

        :param handle: handle for accessing an item before the dataset is
                       frozen
        :returns: dictionary containing item metadata
        """
        return {}

    def post_freeze_hook(self):
        """Post :meth:`dtoolcore.ProtoDataSet.freeze` cleanup actions.

        This method is called at the end of the
        :meth:`dtoolcore.ProtoDataSet.freeze` method.
        """
        if _path_exists(self._metadata_fragments_abspath):
            remove_dir = CommandWrapper(
                ["irm", "-rf", self._metadata_fragments_abspath]
            )
            remove_dir()
