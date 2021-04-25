from unittest import mock

import botocore
import pytest
from dashboard_generator import DashboardGenerator


@pytest.fixture
def _region_var(monkeypatch):
    monkeypatch.setenv('AWS_REGION', 'us-east-1')


@mock.patch('dashboard_generator.boto3')
def test_cloudwatch_list_metrics_ensure_paginator_operation_name_is_called_properly(mock_boto, _region_var):
    DashboardGenerator()._cloudwatch_list_metrics()

    assert mock_boto.client.return_value.get_paginator.called
    mock_boto.client.return_value.get_paginator.assert_called_with('list_metrics')


@mock.patch('dashboard_generator.boto3')
def test_cloudwatch_list_metrics_ensure_return_value_is_list(mock_boto, _region_var):
    response = DashboardGenerator()._cloudwatch_list_metrics()

    assert type(response) == list


@mock.patch('dashboard_generator.boto3')
def test_cloudwatch_list_metrics_ensure_exception_is_handled(mock_boto, _region_var):
    mock_boto.client.return_value.get_paginator.side_effect = botocore.exceptions.ClientError({}, 'foo')

    with pytest.raises(botocore.exceptions.ClientError):
        DashboardGenerator()._cloudwatch_list_metrics()
