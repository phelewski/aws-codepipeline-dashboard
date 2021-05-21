import pytest
from dashboard_generator import DashboardGenerator


def test_generate_widget_descriptions_ensure_return_value_is_dict(env_variables):
    response = DashboardGenerator()._generate_widget_descriptions(x=1, y=1, title='foo', description='bar')

    assert type(response) == dict


def test_generate_widget_descriptions_ensure_values_are_used_properly_in_widget(env_variables):
    x = 1
    y = 1
    title = 'foo'
    description = 'bar'
    response = DashboardGenerator()._generate_widget_descriptions(x, y, title, description)

    assert response['x'] == x
    assert response['y'] == y
    assert response['properties']['markdown'] == '### foo\nbar'
