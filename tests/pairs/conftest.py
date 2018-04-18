import json

import pytest


@pytest.fixture
def namelist_data(shared_datadir):
    contents = (shared_datadir / 'namelist.txt').read_text()
    return json.loads(contents)