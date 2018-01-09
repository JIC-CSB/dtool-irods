"""Test the IrodsStorageBroker self description metadata."""

import os

from . import tmp_uuid_and_uri  # NOQA


def test_writing_of_dtool_structure_file(tmp_uuid_and_uri):  # NOQA
    from dtoolcore import ProtoDataSet, generate_admin_metadata
    from dtoolcore.utils import generous_parse_uri
    from dtool_irods.storagebroker import _path_exists, _get_obj

    # Create a proto dataset.
    uuid, dest_uri = tmp_uuid_and_uri
    name = "test_dtool_structure_file"
    admin_metadata = generate_admin_metadata(name)
    admin_metadata["uuid"] = uuid
    proto_dataset = ProtoDataSet(
        uri=dest_uri,
        admin_metadata=admin_metadata,
        config_path=None
    )
    proto_dataset.create()

    # Check that the ".dtool/structure.json" file exists.
    expected_irods_path = os.path.join(
        generous_parse_uri(dest_uri).path,
        ".dtool",
        "structure.json"
    )
    assert _path_exists(expected_irods_path)

    expected_content = {
        "data_directory": ["data"],
        "dataset_readme_relpath": ["README.yml"],
        "dtool_directory": [".dtool"],
        "admin_metadata_relpath": [".dtool", "dtool"],
        "structure_metadata_relpath": [".dtool", "structure.json"],
        "dtool_readme_relpath": [".dtool", "README.txt"],
        "manifest_relpath": [".dtool", "manifest.json"],
        "overlays_directory": [".dtool", "overlays"],
        "metadata_fragments_directory": [".dtool", "tmp_fragments"],
    }
    actual_content = _get_obj(expected_irods_path)
    assert expected_content == actual_content


def test_writing_of_dtool_readme_file(tmp_uuid_and_uri):  # NOQA
    from dtoolcore import ProtoDataSet, generate_admin_metadata
    from dtoolcore.utils import generous_parse_uri
    from dtool_irods.storagebroker import _path_exists, _get_text

    # Create a proto dataset.
    uuid, dest_uri = tmp_uuid_and_uri
    name = "test_dtool_readme_file"
    admin_metadata = generate_admin_metadata(name)
    admin_metadata["uuid"] = uuid
    proto_dataset = ProtoDataSet(
        uri=dest_uri,
        admin_metadata=admin_metadata,
        config_path=None
    )
    proto_dataset.create()

    # Check that the ".dtool/README.txt" file exists.
    expected_irods_path = os.path.join(
        generous_parse_uri(dest_uri).path,
        ".dtool",
        "README.txt"
    )
    assert _path_exists(expected_irods_path)

    actual_content = _get_text(expected_irods_path)
    assert actual_content.startswith("README")
