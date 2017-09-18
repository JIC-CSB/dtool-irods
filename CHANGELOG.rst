CHANGELOG
=========

This project uses `semantic versioning <http://semver.org/>`_.
This change log uses principles from `keep a changelog <http://keepachangelog.com/>`_.

[Unreleased]
------------

Added
^^^^^

- Ensure ``dtool verify`` will work as expected by forcing iRODS to
  re-calculate the file hash when asking for it, which ensures that a cached
  copy is not used.


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
