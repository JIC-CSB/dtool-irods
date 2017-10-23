CHANGELOG
=========

This project uses `semantic versioning <http://semver.org/>`_.
This change log uses principles from `keep a changelog <http://keepachangelog.com/>`_.

[Unreleased]
------------

Added
^^^^^


Changed
^^^^^^^


Deprecated
^^^^^^^^^^


Removed
^^^^^^^


Fixed
^^^^^


Security
^^^^^^^^


[0.4.0] - 2017-10-23
--------------------

Changed
^^^^^^^

- Improved speed of freezing a dataset in iRODS by making use of
  caches to reduce the number of calls made to iRODS during this
  process


Fixed
^^^^^

- More informative error message when iRODS has not been configured
- More informative error message when iRODS authentication times out
- Stopped client hanging when iRODS authentication has timed out
- storagebroker's ``put_item`` method now returns relpath
- Made the ``IrodsStorageBroker.create_structure`` method more
  robust by checking if the parent collection exists


[0.3.3] - 2017-10-05
--------------------

Fixed
^^^^^

- Fixed defect in iRODS storage broker where files with white space resulted in
  broken identifiers


[0.3.2] - 2017-10-04
--------------------

Fixed
^^^^^

- Fix defect where ``IrodsStorageBroker.put_item`` raised SystemError when
  trying to overwrite an existing file


[0.3.1] - 2017-09-19
--------------------

Added
^^^^^

- Ensure ``dtool verify`` will work as expected by forcing iRODS to
  re-calculate the file hash when asking for it, which ensures that a cached
  copy is not used.


[0.3.0] - 2017-09-15
--------------------

Added
^^^^^

- ``dtool_irods.storagebroker.IrodsStorageBroker.list_dataset_uris`` class method


[0.2.0] - 2017-09-13
--------------------

Added
^^^^^

- ``dtool_irods.storagebroker.IrodsStorageBroker.list_overlay_names``


[0.1.0] 2017-09-05
------------------

Initial release of an iRODS storage broker.
