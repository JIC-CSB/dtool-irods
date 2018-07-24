import os
import time

from . import tmp_uuid_and_uri  # NOQA
from . import TEST_SAMPLE_DATA


def test_update_readme(tmp_uuid_and_uri):  # NOQA

    uuid, dest_uri = tmp_uuid_and_uri

    from dtoolcore import ProtoDataSet, generate_admin_metadata
    from dtoolcore import DataSet
    from dtoolcore.utils import generate_identifier

    name = "my_dataset"
    admin_metadata = generate_admin_metadata(name)
    admin_metadata["uuid"] = uuid

    sample_data_path = os.path.join(TEST_SAMPLE_DATA)
    local_file_path = os.path.join(sample_data_path, 'tiny.png')

    # Create a minimal dataset
    proto_dataset = ProtoDataSet(
        uri=dest_uri,
        admin_metadata=admin_metadata,
        config_path=None)
    proto_dataset.create()
    proto_dataset.put_readme("First")
    proto_dataset.put_readme("Hello world")
    proto_dataset.freeze()

    # Read in a dataset
    dataset = DataSet.from_uri(dest_uri)

    assert len(dataset._storage_broker._list_historical_readme_keys()) == 0

    dataset.put_readme("Updated")

    assert len(dataset._storage_broker._list_historical_readme_keys()) == 1

    key = dataset._storage_broker._list_historical_readme_keys()[0]
    content = dataset._storage_broker.get_text(key)
    assert content == 'Hello world'

    time.sleep(0.1)

    dataset.put_readme('Updated again')
    assert dataset.get_readme_content() == 'Updated again'
