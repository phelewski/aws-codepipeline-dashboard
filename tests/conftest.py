import os
from unittest import mock

import pytest


@pytest.fixture()
def env_variables():
    with mock.patch.dict(os.environ, {'AWS_REGION': 'us-east-1'}):
        yield
