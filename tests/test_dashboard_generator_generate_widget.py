import os

import pytest
from dashboard_generator import DashboardGenerator


def test_generate_widget_ensure_return_value_is_dict(env_variables):
    response = DashboardGenerator()._generate_widget(y=1, period=60, pipeline='foo')

    assert type(response) == dict


def test_generate_widget_ensure_values_are_used_properly_in_widget(env_variables):
    y = 1
    period = 60
    pipeline = 'foo'
    dimension = 'PipelineName'
    response = DashboardGenerator()._generate_widget(y, period, pipeline)

    for metric in response['properties']['metrics']:
        if 'SuccessCount' in metric:
            assert metric == [
                'Pipeline',
                'SuccessCount',
                dimension,
                pipeline,
                {
                    'color': '#000000',
                    'label': 'Success Count',
                    'stat': 'Sum'
                }
            ]

    assert response['properties']['region'] == os.environ['AWS_REGION']
    assert response['properties']['title'] == pipeline
    assert response['properties']['period'] == period
