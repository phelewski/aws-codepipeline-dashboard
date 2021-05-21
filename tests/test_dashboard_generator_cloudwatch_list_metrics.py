from unittest import mock

import botocore
import pytest
from dashboard_generator import DashboardGenerator


@mock.patch('dashboard_generator.boto3')
def test_cloudwatch_list_metrics_ensure_paginator_operation_name_is_called_properly(mock_boto, env_variables):
    DashboardGenerator()._cloudwatch_list_metrics()

    assert mock_boto.client.return_value.get_paginator.called
    mock_boto.client.return_value.get_paginator.assert_called_with('list_metrics')


@mock.patch('dashboard_generator.boto3')
def test_cloudwatch_list_metrics_ensure_return_value_is_list(_mock_boto, env_variables):
    response = DashboardGenerator()._cloudwatch_list_metrics()

    assert type(response) == list


@mock.patch('dashboard_generator.boto3')
def test_cloudwatch_list_metrics_ensure_exception_is_handled(mock_boto, env_variables):
    mock_boto.client.return_value.get_paginator.side_effect = botocore.exceptions.ClientError({}, 'foo')

    with pytest.raises(botocore.exceptions.ClientError):
        DashboardGenerator()._cloudwatch_list_metrics()
