import os
from unittest import mock

import pytest


@pytest.fixture()
def env_variables():
    with mock.patch.dict(
        os.environ,
        {
            'AWS_REGION': 'us-east-1',
            'PIPELINE_PATTERN': 'foo*'
        }
    ):
        yield


@pytest.fixture()
def event():
    event = {
        'version': '0',
        'id': '54e8c14a-656d-a3f0-1301-ddb7d16aad1f',
        'detail-type': 'CodePipeline Pipeline Execution State Change',
        'source': 'aws.codepipeline',
        'account': '123456789012',
        'time': '2021-04-26T15:11:59Z',
        'region': 'us-east-1',
        'resources': [
            'arn:aws:codepipeline:us-east-1:123456789012:foobar'
        ],
        'detail': {
            'pipeline': 'foobar',
            'execution-id': 'a577f902-c777-4b06-859a-378e2f3a8abe',
            'state': 'SUCCEEDED',
            'version': 2.0
        }
    }

    return event


@pytest.fixture()
def failing_state_event():
    event = {
        'version': '0',
        'id': '54e8c14a-656d-a3f0-1301-ddb7d16aad1f',
        'detail-type': 'CodePipeline Pipeline Execution State Change',
        'source': 'aws.codepipeline',
        'account': '123456789012',
        'time': '2021-04-26T15:11:59Z',
        'region': 'us-east-1',
        'resources': [
            'arn:aws:codepipeline:us-east-1:123456789012:foobar'
        ],
        'detail': {
            'pipeline': 'foobar',
            'execution-id': 'a577f902-c777-4b06-859a-378e2f3a8abe',
            'state': 'RUNNING',
            'version': 2.0
        }
    }

    return event


@pytest.fixture()
def failing_prefix_event():
    event = {
        'version': '0',
        'id': '54e8c14a-656d-a3f0-1301-ddb7d16aad1f',
        'detail-type': 'CodePipeline Pipeline Execution State Change',
        'source': 'aws.codepipeline',
        'account': '123456789012',
        'time': '2021-04-26T15:11:59Z',
        'region': 'us-east-1',
        'resources': [
            'arn:aws:codepipeline:us-east-1:123456789012:baz'
        ],
        'detail': {
            'pipeline': 'baz',
            'execution-id': 'a577f902-c777-4b06-859a-378e2f3a8abe',
            'state': 'SUCCEEDED',
            'version': 2.0
        }
    }

    return event
