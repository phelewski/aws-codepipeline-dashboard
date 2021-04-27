from unittest import mock

import botocore
import pytest
from pipeline_event_handler import PipelineEventHandler


@pytest.fixture()
def pipeline_executions():
    executions = {
        'pipelineExecutionSummaries': [
            {
                'pipelineExecutionId': '48154471-3b8b-4fbf-9304-1458c1d1419c',
                'status': 'Succeeded',
                'startTime': '2021-04-26 11:22:59.994000-04:00',
                'lastUpdateTime': '2021-04-26 11:26:34.695000-04:00',
                'sourceRevisions': [
                    {
                        'actionName': 'Repo',
                        'revisionId': 'baz',
                        'revisionSummary': 'foobar',
                        'revisionUrl': 'https://github.com/foo/bar/commit/baz'
                    }
                ],
                'trigger': {
                    'triggerType': 'StartPipelineExecution',
                    'triggerDetail': 'arn:aws:sts::123456789012:assumed-role/AWSReservedSSO_FOOBAR/foobar'
                }
            },
            {
                'pipelineExecutionId': 'a577f902-c777-4b06-859a-378e2f3a8abe',
                'status': 'InProgress',
                'startTime': '2021-04-26 11:07:41.247000-04:00',
                'lastUpdateTime': '2021-04-26 11:11:59.591000-04:00',
                'sourceRevisions': [
                    {
                        'actionName': 'Repo',
                        'revisionId': 'baz',
                        'revisionSummary': 'foobar',
                        'revisionUrl': 'https://github.com/foo/bar/commit/baz'
                    }
                ],
                'trigger': {
                    'triggerType': 'StartPipelineExecution',
                    'triggerDetail': 'arn:aws:sts::123456789012:assumed-role/AWSReservedSSO_FOOBAR/foobar'
                }
            },
            {
                'pipelineExecutionId': '5edf3cfb-901d-463c-9447-fdfe6b491767',
                'status': 'Failed',
                'startTime': '2021-04-25 11:02:53.013000-04:00',
                'lastUpdateTime': '2021-04-25 11:03:45.440000-04:00',
                'sourceRevisions': [
                    {
                        'actionName': 'Repo',
                        'revisionId': 'baz',
                        'revisionSummary': 'foobar',
                        'revisionUrl': 'https://github.com/foo/bar/commit/baz'
                    }
                ],
                'trigger': {
                    'triggerType': 'StartPipelineExecution',
                    'triggerDetail': 'arn:aws:sts::123456789012:assumed-role/AWSReservedSSO_FOOBAR/foobar'
                }
            }
        ]
    }

    return executions


@mock.patch('pipeline_event_handler.PipelineEventHandler._list_pipeline_executions')
def test_filter_pipeline_executions_ensure_return_is_properly_filtered(
    mock_list_pipeline_executions,
    event,
    pipeline_executions,
    env_variables
):
    mock_list_pipeline_executions.return_value = pipeline_executions

    response = PipelineEventHandler(event)._filter_pipeline_executions()

    assert mock_list_pipeline_executions.called
    assert isinstance(response, list)
    assert len(response) == 2
