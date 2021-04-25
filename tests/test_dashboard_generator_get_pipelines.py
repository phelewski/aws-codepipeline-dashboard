from unittest import mock

import botocore
import pytest
from dashboard_generator import DashboardGenerator


@mock.patch('dashboard_generator.DashboardGenerator._cloudwatch_list_metrics')
def test_get_pipelines_ensure_pipeline_name_is_returned(mock_cloudwatch_list_metrics, env_variables):
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


@mock.patch('dashboard_generator.DashboardGenerator._cloudwatch_list_metrics')
def test_get_pipelines_ensure_duplicate_pipeline_names_are_consolidated(mock_cloudwatch_list_metrics, env_variables):
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
    assert len(response) == 1


@mock.patch('dashboard_generator.DashboardGenerator._cloudwatch_list_metrics')
def test_get_pipelines_ensure_return_value_is_list(mock_cloudwatch_list_metrics, env_variables):
    mock_cloudwatch_list_metrics.return_value = [
        {
            'Namespace': 'Pipeline',
            'MetricName': 'SuccessCount',
            'Dimensions': [
                {
                    'Name': 'PipelineName',
                    'Value': 'foo'
                }
            ]
        },
        {
            'Namespace': 'Pipeline',
            'MetricName': 'SuccessCount',
            'Dimensions': [
                {
                    'Name': 'PipelineName',
                    'Value': 'bar'
                }
            ]
        },
        {
            'Namespace': 'Pipeline',
            'MetricName': 'SuccessCount',
            'Dimensions': [
                {
                    'Name': 'PipelineName',
                    'Value': 'baz'
                }
            ]
        }
    ]

    response = DashboardGenerator()._get_pipelines()

    assert mock_cloudwatch_list_metrics.called
    assert type(response) == list
