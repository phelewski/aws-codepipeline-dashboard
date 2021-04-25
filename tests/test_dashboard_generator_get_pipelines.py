from unittest import mock

import botocore
import pytest
from dashboard_generator import DashboardGenerator


@mock.patch('dashboard_generator.DashboardGenerator._cloudwatch_list_metrics')
def test_get_pipelines_ensure_pipelines_are_returned(mock_cloudwatch_list_metrics, env_variables):
    mock_cloudwatch_list_metrics.return_value = [
        {
            'Namespace': 'Pipeline',
            'MetricName': 'SuccessCount',
            'Dimensions': [
                {
                    'Name': 'PipelineName',
                    'Value': 'foobar'
                }
            ]
        },
        {
            'Namespace': 'Pipeline',
            'MetricName': 'SuccessCount',
            'Dimensions': [
                {
                    'Name': 'PipelineName',
                    'Value': 'foobar'
                }
            ]
        },
        {
            'Namespace': 'Pipeline',
            'MetricName': 'SuccessCount',
            'Dimensions': [
                {
                    'Name': 'PipelineName',
                    'Value': 'foobar'
                }
            ]
        }
    ]

    response = DashboardGenerator()._get_pipelines()

    assert mock_cloudwatch_list_metrics.called
    assert response == ['foobar']
