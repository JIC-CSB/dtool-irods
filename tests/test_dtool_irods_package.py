"""Test the dtool_irods package."""


def test_version_is_string():
    import dtool_irods
    assert isinstance(dtool_irods.__version__, str)
