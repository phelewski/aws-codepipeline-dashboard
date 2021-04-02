from dashboard_generator import DashboardGenerator
from pipeline_event_handler import PipelineEventHandler


def pipeline_event_handler(event: dict, _context) -> None:
    """
    Runs the items to handle a pipeline execution event

    Args:
        event (dict): Incoming lambda event
    """
    PipelineEventHandler(event).execute_event_steps()


def dashboard_handler(_event, _context) -> None:
    """
    Runs the items to handle the pipeline dashboard creation
    """
    DashboardGenerator().cloudwatch_put_dashboard()
