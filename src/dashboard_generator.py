import inspect
import json
import os

import boto3
import botocore

from logger import Logger


class DashboardGenerator():
    def __init__(self) -> None:
        self.logger = Logger(logger_name='DashboardGenerator', level='INFO').setup_logger()
        self.cloudwatch = boto3.client('cloudwatch')
        self.namespace = 'Pipeline'
        self.dimension = 'PipelineName'
        self.region = os.environ['AWS_REGION']
        self.dashboard_name = f'Pipelines-{self.region}'
        self.widget_descriptions = [
            {
                "title": "Success Count",
                "description": "total number of successful pipeline executions"
            },
            {
                "title": "Failed Count",
                "description": "total number of failed pipeline executions"
            },
            {
                "title": "Cycle Time",
                "description": "mean time between successful pipeline executions"
            },
            # {
            #     "title": "Success Lead Time",
            #     "description": "todo fill in more information later"
            # },
            {
                "title": "Lead Time",
                "description": "mean lead time from commit to production, including rework"
            },
            {
                "title": "MTBF",
                "description": "mean time between pipeline failures"
            },
            {
                "title": "MTTR",
                "description": "mean time to pipeline recovery"
            },
            {
                "title": "Feedback Time",
                "description": "mean lead time for failed pipeline executions"
            }
        ]

    def _cloudwatch_list_metrics(self) -> list:
        """
        Uses the Boto3 API to create a list of metrics that match the desired name space

        Returns:
            list: List of the specified metrics
        """
        metrics_list = []

        self.logger.debug(f"{inspect.stack()[0][3]} - Checking to see if the event state matches with the allowed list")
        try:
            paginator = self.cloudwatch.get_paginator('list_metrics')

            for response in paginator.paginate(Namespace=self.namespace, RecentlyActive='PT3H'):
                metrics_list.extend(response['Metrics'])
        except botocore.exceptions.ClientError as e:
            self.logger.exception(
                f"{inspect.stack()[0][3]} - Error occurred while gathering the CloudWatch Metrics"
                f"\nBotocore Exception: \n{e}"
            )
            raise

        self.logger.debug(f"{inspect.stack()[0][3]} - metrics_list: {metrics_list}")
        return metrics_list

    def _get_pipelines(self) -> list:
        """
        Runs through the list of metrics and creates a unique list of names that match the desired dimension

        Returns:
            list: Unique list of pipeline names
        """
        metrics_list = self._cloudwatch_list_metrics()
        pipelines = []

        self.logger.debug(
            f"{inspect.stack()[0][3]} - Checking the metrics list for items matching the desired dimension"
        )
        for metric in metrics_list:
            for dimension in metric['Dimensions']:
                if dimension['Name'] == self.dimension:
                    pipelines.append(dimension['Value'])

        self.logger.debug(f"{inspect.stack()[0][3]} - Unique pipeline list: {list(set(pipelines))}")
        return list(set(pipelines))

    def _generate_widget(self, y: int, period: int, pipeline: str) -> dict:
        """
        Defines the CloudWatch Dashboard Widget array structure

        Args:
            y (int): Vertical position of the widget on the dashboard grid
            period (int): The default period, in seconds, for all metrics in this widget
            pipeline (str): The title to be displayed for the graph or number

        Returns:
            dict: Widget array structure
        """
        widgets = {
            "type": "metric",
            "x": 0,
            "y": y,
            "width": 21,
            "height": 3,
            "properties": {
                "view": "singleValue",
                "metrics": [
                    [
                        "Pipeline",
                        "SuccessCount",
                        self.dimension,
                        pipeline,
                        {
                            "label": "Success Count",
                            "stat": "Sum",
                            "color": "#000000"
                        }
                    ],
                    [
                        ".",
                        "FailureCount",
                        ".",
                        ".",
                        {
                            "label": "Failed Count",
                            "stat": "Sum",
                            "color": "#808080"
                        }
                    ],
                    [
                        ".",
                        "SuccessCycleTime",
                        ".",
                        ".",
                        {
                            "label": "Cycle Time",
                            "stat": "Average",
                            "color": "#212ebd"
                        }
                    ],
                    # [
                    #     ".",
                    #     "SuccessLeadTime",
                    #     ".",
                    #     ".",
                    #     {
                    #         "label": "Success Lead Time",
                    #         "stat": "Average",
                    #         "color": "#d6721b"
                    #     }
                    # ],
                    [
                        ".",
                        "DeliveryLeadTime",
                        ".",
                        ".",
                        {
                            "label": "Lead Time",
                            "stat": "Average",
                            "color": "#d6721b"
                        }
                    ],
                    [
                        ".",
                        "YellowTime",
                        ".",
                        ".",
                        {
                            "label": "MTBF",
                            "stat": "Average",
                            "color": "#ffcc33"
                        }
                    ],
                    [
                        ".",
                        "RedTime",
                        ".",
                        ".",
                        {
                            "label": "MTTR",
                            "stat": "Average",
                            "color": "#d62728"
                        }
                    ],
                    [
                        ".",
                        "FailureLeadTime",
                        ".",
                        ".",
                        {
                            "label": "Feedback Time",
                            "stat": "Average",
                            "color": "#a02899"
                        }
                    ]
                ],
                "region": self.region,
                "title": pipeline,
                "period": period
            }
        }

        self.logger.debug(f"{inspect.stack()[0][3]} - widgets: {widgets}")
        return widgets

    def _generate_widget_descriptions(self, x: int, y: int, title: str, description: str) -> dict:
        """
        Generates a widget descriptor

        Args:
            x (int): The horizontal position of the widget on the dashboard grid
            y (int): The vertical position of the widget on the dashboard grid
            title (str): Name of the Widget Object
            description (str): Description of the Widget Object

        Returns:
            dict: Text Widget object details
        """
        widget_description = {
            "type": "text",
            "x": x,
            "y": y,
            "width": 4,
            "height": 2,
            "properties": {
                "markdown": f"### {title}\n{description}"
            }
        }

        self.logger.debug(f"{inspect.stack()[0][3]} - widget_description: {widget_description}")
        return widget_description

    def cloudwatch_put_dashboard(self) -> None:
        """
        Creates or updates the CloudWatch Dashboard with widgets and descriptions for each
        """
        x = 0
        y = 0
        period = 60 * 60 * 24 * 30  # 30 days
        dashboard = {
            "widgets": []
        }

        self.logger.debug(f"{inspect.stack()[0][3]} - Creating the group of widgets")
        for pipeline in self._get_pipelines():
            widgets = self._generate_widget(y, period, pipeline)
            y += 3
            dashboard['widgets'].append(widgets)

        self.logger.debug(f"{inspect.stack()[0][3]} - Creating the widget descriptions")
        for widget_description in self.widget_descriptions:
            title = widget_description['title']
            description = widget_description['description']

            descriptor = self._generate_widget_descriptions(x, y, title, description)
            x += 4
            dashboard['widgets'].append(descriptor)

        self.logger.debug(f"{inspect.stack()[0][3]} - Creating or updating the CloudWatch Dashboard")
        try:
            self.cloudwatch.put_dashboard(DashboardName=self.dashboard_name, DashboardBody=json.dumps(dashboard))
        except botocore.exceptions.ClientError as e:
            self.logger.exception(
                f"{inspect.stack()[0][3]} - Error occurred while creating or updating the CloudWatch Dashboard"
                f"\nBotocore Exception: \n{e}"
            )
            raise
