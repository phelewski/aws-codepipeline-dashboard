import json
import os
from unittest import mock

import botocore
import pytest
from dashboard_generator import DashboardGenerator


@mock.patch('dashboard_generator.boto3')
def test_cloudwatch_put_dashboard_ensure_parameters_are_passed_properly(mock_boto, env_variables):
    dashboard_name = f"Pipelines-{os.environ['AWS_REGION']}"
    dashboard_body = {
        "widgets": [
            {
                "type": "text",
                "x": 0,
                "y": 0,
                "width": 4,
                "height": 2,
                "properties": {
                    "markdown": "### Success Lead Time\nmean lead time for successful pipeline executions"
                }
            },
            {
                "type": "text",
                "x": 4,
                "y": 0,
                "width": 4,
                "height": 2,
                "properties": {
                    "markdown": "### Delivery Lead Time\nmean lead time from commit to production, including rework"
                }
            },
            {
                "type": "text",
                "x": 8,
                "y": 0,
                "width": 4,
                "height": 2,
                "properties": {
                    "markdown": "### Cycle Time\nmean time between successful pipeline executions"
                }
            },
            {
                "type": "text",
                "x": 12,
                "y": 0,
                "width": 4,
                "height": 2,
                "properties": {
                    "markdown": "### MTBF\nmean time between pipeline failures"
                }
            },
            {
                "type": "text",
                "x": 16,
                "y": 0,
                "width": 4,
                "height": 2,
                "properties": {
                    "markdown": "### MTTR\nmean time to pipeline recovery"
                }
            },
            {
                "type": "text",
                "x": 20,
                "y": 0,
                "width": 4,
                "height": 2,
                "properties": {
                    "markdown": "### Feedback Time\nmean lead time for failed pipeline executions"
                }
            }
        ]
    }

    DashboardGenerator().cloudwatch_put_dashboard()

    assert mock_boto.client.return_value.put_dashboard.called
    mock_boto.client.return_value.put_dashboard.assert_called_with(
        DashboardName=dashboard_name,
        DashboardBody=json.dumps(dashboard_body)
    )


@mock.patch('dashboard_generator.boto3')
def test_cloudwatch_put_dashboard_ensure_exception_is_handled(mock_boto, env_variables):
    mock_boto.client.return_value.put_dashboard.side_effect = botocore.exceptions.ClientError({}, 'foo')

    with pytest.raises(botocore.exceptions.ClientError):
        DashboardGenerator().cloudwatch_put_dashboard()


@mock.patch('dashboard_generator.boto3')
@mock.patch('dashboard_generator.DashboardGenerator._get_pipelines')
@mock.patch('dashboard_generator.DashboardGenerator._generate_widget')
@mock.patch('dashboard_generator.DashboardGenerator._generate_widget_descriptions')
def test_cloudwatch_put_dashboard_ensure_methods_are_called(
    mock_generate_widget_descriptions,
    mock_generate_widget,
    mock_get_pipelines,
    mock_boto,
    env_variables
):
    mock_generate_widget_descriptions.return_value = {}
    mock_generate_widget.return_value = {}
    mock_get_pipelines.return_value = ['foobar']
    DashboardGenerator().cloudwatch_put_dashboard()

    assert mock_boto.client.return_value.put_dashboard.called
    assert mock_get_pipelines.called
    assert mock_generate_widget.called
    assert mock_generate_widget_descriptions.called
