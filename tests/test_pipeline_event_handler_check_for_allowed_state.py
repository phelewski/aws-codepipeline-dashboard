import pytest
from pipeline_event_handler import PipelineEventHandler


def test_check_for_allowed_state_ensure_class_variables_are_set_with_allowed_state(event):
    event_handler = PipelineEventHandler(event)

    assert not hasattr(event_handler, 'pipeline_name')
    assert not hasattr(event_handler, 'execution_id')

    response = event_handler._check_for_allowed_state()

    assert hasattr(event_handler, 'pipeline_name')
    assert hasattr(event_handler, 'execution_id')
    assert isinstance(response, type(None))


def test_check_for_allowed_state_ensure_non_allowed_state_exits(failing_event):
    with pytest.raises(SystemExit):
        PipelineEventHandler(failing_event)._check_for_allowed_state()
