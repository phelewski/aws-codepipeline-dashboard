import pytest
from pipeline_event_handler import PipelineEventHandler


def test_check_for_pipeline_prefix_ensure_matching_prefix_creates_non_empty_list(event, env_variables):
    event_handler = PipelineEventHandler(event)
    event_handler._check_for_allowed_state()
    response = event_handler._check_for_pipeline_prefix()

    assert isinstance(response, type(None))


def test_check_for_pipeline_prefix_ensure_non_allowed_state_exits(failing_prefix_event, env_variables):
    event_handler = PipelineEventHandler(failing_prefix_event)
    event_handler._check_for_allowed_state()

    with pytest.raises(SystemExit):
        event_handler._check_for_pipeline_prefix()
