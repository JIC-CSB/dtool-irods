"""iRODS storage broker."""

import os
import json
import shutil

from dtoolcore.utils import (
    mkdir_parents,
    generate_identifier,
)
from dtoolcore.filehasher import FileHasher, md5sum

from dtool_irods import CommandWrapper


class IrodsStorageBroker(object):
    """
    Storage broker to interact with datasets in iRODS.
    """

    #: Attribute used to define the type of storage broker.
    key = "irods"

    #: Attribute used by :class:`dtoolcore.ProtoDataSet` to write the hash
    #: function name to the manifest.
    hasher = FileHasher(md5sum)

    def __init__(self, uri, config_path=None):
        pass

#############################################################################
# Methods used by both ProtoDataSet and DataSet.
#############################################################################

    def get_admin_metadata(self):
        """Return admin metadata from iRODS.

        :returns: administrative metadata as a dictionary
        """

    def has_admin_metadata(self):
        """Return True if the administrative metadata exists.

        This is the definition of being a "dataset".
        """

    def get_readme_content(self):
        """Return content of the README file as a string.

        :returns: readme content as a string
        """

    def put_overlay(self, overlay_name, overlay):
        """Store the overlay by writing it to iRODS.

        It is the client's responsibility to ensure that the overlay provided
        is a dictionary with valid contents.

        :param overlay_name: name of the overlay
        :overlay: overlay dictionary
        """

#############################################################################
# Methods only used by DataSet.
#############################################################################

    def get_manifest(self):
        """Return the manifest contents from iRODS.

        :returns: manifest as a dictionary
        """

    def get_overlay(self, overlay_name):
        """Return overlay as a dictionary.

        :param overlay_name: name of the overlay
        :returns: overlay as a dictionary
        """

    def get_item_abspath(self, identifier):
        """Return absolute path at which item content can be accessed.

        :param identifier: item identifier
        :returns: absolute path from which the item content can be accessed
        """

#############################################################################
# Methods only used by ProtoDataSet.
#############################################################################

    def create_structure(self):
        """Create necessary structure to hold a dataset."""

    def put_admin_metadata(self, admin_metadata):
        """Store the admin metadata by writing to iRODS.

        It is the client's responsibility to ensure that the admin metadata
        provided is a dictionary with valid contents.

        :param admin_metadata: dictionary with administrative metadata
        """

    def put_manifest(self, manifest):
        """Store the manifest by writing it to iRODS.

        It is the client's responsibility to ensure that the manifest provided
        is a dictionary with valid contents.

        :param manifest: dictionary with manifest structural metadata
        """

    def put_readme(self, content):
        """
        Put content into the README of the dataset.

        The client is responsible for ensuring that the content is valid YAML.

        :param content: string to put into the README
        """

    def put_item(self, fpath, relpath):
        """Put item with content from fpath at relpath in dataset.

        Missing directories in relpath are created on the fly.

        :param fpath: path to the item on local disk
        :param relpath: relative path name given to the item in the dataset as
                        a handle
        """

    def iter_item_handles(self):
        """Return iterator over item handles."""

    def item_properties(self, handle):
        """Return properties of the item with the given handle."""

    def _handle_to_fragment_absprefixpath(self, handle):
        pass

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

    def post_freeze_hook(self):
        """Post :meth:`dtoolcore.ProtoDataSet.freeze` cleanup actions.

        This method is called at the end of the
        :meth:`dtoolcore.ProtoDataSet.freeze` method.
        """
