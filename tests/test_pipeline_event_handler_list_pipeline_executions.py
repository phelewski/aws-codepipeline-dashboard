from unittest import mock

import botocore
import pytest
from pipeline_event_handler import PipelineEventHandler


@mock.patch('pipeline_event_handler.boto3')
def test_list_pipeline_executions_ensure_parameters_are_called_properly(mock_boto, event, env_variables):
    event_handler = PipelineEventHandler(event)
    event_handler._check_for_allowed_state()
    response = event_handler._list_pipeline_executions()

    assert mock_boto.client.return_value.list_pipeline_executions.called
    mock_boto.client.return_value.list_pipeline_executions.assert_called_with(
        pipelineName=event_handler.pipeline_name
    )


@mock.patch('pipeline_event_handler.boto3')
def test_list_pipeline_executions_ensure_exception_is_handled(mock_boto, event, env_variables):
    event_handler = PipelineEventHandler(event)
    event_handler._check_for_allowed_state()
    mock_boto.client.return_value.list_pipeline_executions.side_effect = botocore.exceptions.ClientError({}, 'foo')

    with pytest.raises(botocore.exceptions.ClientError):
        event_handler._list_pipeline_executions()
