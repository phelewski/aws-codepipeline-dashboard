import datetime
import fnmatch
import inspect
import os
from typing import Optional

import boto3
import botocore
from dateutil.tz import tzlocal  # Needed for time conversion from pipeline state

from logger import Logger


class PipelineEventHandler():
    def __init__(self, event: dict) -> None:
        self.logger = Logger(logger_name='PipelineEventHandler', level='INFO').setup_logger()
        self.event = event
        self.allowed_state = ['SUCCEEDED', 'FAILED']
        self.allowed_status = ['Succeeded', 'Failed']
        self.codepipeline = boto3.client('codepipeline')
        self.cloudwatch = boto3.client('cloudwatch')
        self.count = 'Count'
        self.seconds = 'Seconds'
        self.pipeline_pattern = os.environ['PIPELINE_PATTERN']

    def _check_for_allowed_state(self) -> None:
        """
        Checks the incoming event to ensure that the desired state is present. If the state matches a value from the
        allowed list then the pipeine name and execution id variables are set, otherwise it exits gracefully.
        """
        self.logger.debug(f"{inspect.stack()[0][3]} - Checking to see if the event state matches with the allowed list")
        if self.event['detail']['state'] in self.allowed_state:
            self.pipeline_name = self.event['detail']['pipeline']
            self.execution_id = self.event['detail']['execution-id']
            self.logger.debug(f"{inspect.stack()[0][3]} - Event state matches with the allowed list")
        else:
            self.logger.info(f"{inspect.stack()[0][3]} - Pipeline state doesn't match what we are looking for, exiting")
            exit(0)

    def _check_for_pipeline_prefix(self) -> None:
        """
        Checks the name of the pipeline from the incoming event and compares it against the pipeline pattern to ensure
        that we are only creating metrics and updating the dashboard for the desired pipelines
        """
        self.logger.debug(
            f"{inspect.stack()[0][3]} - Checking to see if the pipeline name matches the pipeline pattern"
        )
        if fnmatch.filter([self.pipeline_name], self.pipeline_pattern) != []:
            self.logger.debug(
                f"{inspect.stack()[0][3]} - Pipeline name matches the pipeline pattern")
            pass
        else:
            self.logger.info(f"{inspect.stack()[0][3]} - Pipeline name doesn't match what we are looking for, exiting")
            exit(0)

    def _list_pipeline_executions(self) -> dict:
        """
        Uses the Boto3 API to gather the a list of the pipeline executions for the pipeline listed within the incoming
        event.

        Returns:
            dict: Summary of the most recent executions for a pipeline
        """
        self.logger.debug(f"{inspect.stack()[0][3]} - Listing {self.pipeline_name} pipeline executions")
        try:
            response = self.codepipeline.list_pipeline_executions(
                pipelineName=self.pipeline_name
            )

            self.logger.debug(f"{inspect.stack()[0][3]} - response: {response}")
            return response
        except botocore.exceptions.ClientError as e:
            self.logger.exception(
                f"{inspect.stack()[0][3]} - Error occurred while listing the pipeline executions"
                f"\nBotocore Exception: \n{e}"
            )
            raise

    def _filter_pipeline_executions(self) -> list:
        """
        Runs through the recent pipeline executions and adds any executions that match the allowed state to a list

        Returns:
            list: Pipeline executions that have a status that match the allowed list
        """
        pipeline_summaries = []
        pipeline_executions = self._list_pipeline_executions()

        self.logger.debug(
            f"{inspect.stack()[0][3]} - Filtering the pipeline executions for those matching the allowed status"
        )
        for execution in pipeline_executions['pipelineExecutionSummaries']:
            if execution['status'] in self.allowed_status:
                pipeline_summaries.append(execution)

        self.logger.debug(f"{inspect.stack()[0][3]} - pipeline_summaries: {pipeline_summaries}")
        return pipeline_summaries

    def _get_pipeline_execution(self, execution_id: str) -> Optional[dict]:
        """
        Checks the list of pipeline execution summaries for a matching execution id

        Args:
            execution_id (str): CodePipeline execution id

        Returns:
            Optional[dict]: CodePipeline execution summary or None
        """
        self.logger.debug(
            f"{inspect.stack()[0][3]} - Gathering the pipeline summary for the following execution id: {execution_id}"
        )
        for execution in self._list_pipeline_executions()['pipelineExecutionSummaries']:
            if execution['pipelineExecutionId'] == execution_id:
                return execution

        self.logger.debug(f"{inspect.stack()[0][3]} - No matching execution found")
        return None

    def _process_pipeline_executions(self) -> None:
        pipeline_executions = self._filter_pipeline_executions()
        pipeline_state_is_final = False

        for execution in pipeline_executions:
            if not pipeline_state_is_final:
                # Find the current execution
                if execution['pipelineExecutionId'] == self.execution_id:
                    self.current_pipeline_execution = execution
                    self.prior_success_plus_one_execution = execution
                elif self.current_pipeline_execution:
                    # If current execution is a success, find the prior success and the one right after that
                    if self.current_pipeline_execution['status'] == 'Succeeded':
                        if execution['status'] == 'Succeeded':
                            self.prior_success_execution = execution
                        else:
                            self.prior_success_plus_one_execution = execution
                    # Next, if state is different from current then we keep it
                    if execution['status'] != self.current_pipeline_execution['status']:
                        self.prior_state_execution = execution
                    # Finally, we are done if the state is the same as current
                    elif execution['status'] == self.current_pipeline_execution['status']:
                        pipeline_state_is_final = True
                        self.pipeline_state_is_final = pipeline_state_is_final
            break

    # def _get_prior_pipeline_execution(self) -> dict:
    #     """
    #     Grabs the second item from the filtered list of pipeline executions

    #     Returns:
    #         dict: CodePipeline execution summary
    #     """
    #     pipeline_executions = self._filter_pipeline_executions()
    #     prior_execution = pipeline_executions[1]

    #     self.logger.debug(f"{inspect.stack()[0][3]} - Prior pipeline execution summary: {prior_execution}")
    #     return prior_execution

    # def _get_prior_successful_pipeline_execution(self) -> None:
    #     """
    #     Runs through the filtered list of pipeline executions to find the previous successful execution and defines
    #     that variable
    #     """
    #     pipeline_executions = self._filter_pipeline_executions()

    #     self.logger.debug(
    #         f"{inspect.stack()[0][3]} - Running through the filtered list of pipeline executions to find the previous "
    #         "successful execution"
    #     )
    #     for execution in pipeline_executions:
    #         if execution['pipelineExecutionId'] == self.execution_id:
    #             pass
    #         elif execution['status'] == 'Succeeded':
    #             self.prior_success_execution_id = execution['pipelineExecutionId']
    #             break
    #         else:
    #             self.prior_success_execution_id = None

    def _handle_final_state(self) -> None:
        """
        Checks the value of the event state and creates a new CloudWatch Metric based on that value
        """
        self.logger.debug(
            f"{inspect.stack()[0][3]} - Checking the event status to determine what CloudWatch Metric to push"
        )
        if self.event['detail']['state'] == 'SUCCEEDED':
            self.add_metric('SuccessCount', self.count, 1)
        elif self.event['detail']['state'] == 'FAILED':
            self.add_metric('FailureCount', self.count, 1)

    def _handle_pipeline_yellow_and_red_time(self) -> None:
        """
        Checks to see if a yellow or red time metric should be added for the pipeline execution
        """
        # current_execution = self._get_pipeline_execution(self.execution_id)
        # prior_execution = self._get_prior_pipeline_execution()

        self.logger.debug(f"{inspect.stack()[0][3]} - Comparing the current and previous execution status")
        if self.current_pipeline_execution['status'] != self.prior_state_execution['status']:
            duration = self._duration_in_seconds(
                self.prior_state_execution['startTime'], self.current_pipeline_execution['startTime']
            )

            if self.current_pipeline_execution['status'] == 'Succeeded':
                self.add_metric('RedTime', self.seconds, duration)
            elif self.current_pipeline_execution['status'] == 'Failed':
                self.add_metric('YellowTime', self.seconds, duration)

    def _handle_pipeline_cycle_time(self) -> None:
        """
        Checks to see if a successful cycle time metric should be added for the pipeline execution
        """
        # current_execution = self._get_pipeline_execution(self.execution_id)
        # prior_successful_execution = self._get_pipeline_execution(self.prior_success_execution_id)

        self.logger.debug(f"{inspect.stack()[0][3]} - Comparing the current and previous successful execution status")
        if self.current_pipeline_execution and self.current_pipeline_execution['status'] == 'Succeeded' and self.prior_success_execution:
            duration = self._duration_in_seconds(
                self.prior_success_execution['lastUpdateTime'], self.current_pipeline_execution['lastUpdateTime']
            )
            self.add_metric('SuccessCycleTime', self.seconds, duration)

    def _handle_pipeline_lead_time(self) -> None:
        """
        Checks to see if a successful or failure metric should be added for the pipeline execution
        """
        # current_execution = self._get_pipeline_execution(self.execution_id)

        self.logger.debug(f"{inspect.stack()[0][3]} - Checking the current execution status")
        if self.current_pipeline_execution['status'] == 'Succeeded':
            duration = self._duration_in_seconds(
                self.current_pipeline_execution['startTime'], self.current_pipeline_execution['lastUpdateTime'])
            self.add_metric('SuccessLeadTime', self.seconds, duration)
            if self.pipeline_state_is_final and self.prior_success_plus_one_execution:
                lead_duration = self._duration_in_seconds(
                    self.prior_success_plus_one_execution['startTime'], self.current_pipeline_execution['lastUpdateTime'])
                self.add_metric('DeliveryLeadTime', self.seconds, lead_duration)
        elif self.current_pipeline_execution['status'] == 'Failed':
            duration = self._duration_in_seconds(
                self.current_pipeline_execution['startTime'], self.current_pipeline_execution['lastUpdateTime'])
            self.add_metric('FailureLeadTime', self.seconds, duration)

    def add_metric(self, metric_name: str, unit: str, value: int) -> None:
        """
        Uses Boto3 API to create a CloudWatch Metric with details provided from the incoming arguments

        Args:
            metric_name (str): Name of the metric
            unit (str): Type of unit to use for storing the metric
            value (int): Value of the metric
        """
        if value == 0:
            self.logger.debug(
                f"{inspect.stack()[0][3]} - Value is 0, Will not create a new CloudWatch Metric data point"
            )
            return

        self.logger.debug(f"{inspect.stack()[0][3]} - Creating a new CloudWatch Metric data point")
        try:
            self.cloudwatch.put_metric_data(
                Namespace='Pipeline',
                MetricData=[
                    {
                        'MetricName': metric_name,
                        'Dimensions': [
                            {
                                'Name': 'PipelineName',
                                'Value': self.pipeline_name
                            }
                        ],
                        'Timestamp': datetime.datetime.strptime(self.event['time'], '%Y-%m-%dT%H:%M:%SZ'),
                        'Unit': unit,
                        'Value': value
                    }
                ]
            )
        except botocore.exceptions.ClientError as e:
            self.logger.exception(
                f"{inspect.stack()[0][3]} - Error occurred while creating a new CloudWatch Metric data point"
                f"\nBotocore Exception: \n{e}"
            )
            raise

    def _duration_in_seconds(self, time_1: int, time_2: int) -> int:
        """
        Subtracts the values of two time value integers, converts that value to seconds, and rounds that value to the
        nearest whole number

        Args:
            time_1 (int): Time value
            time_2 (int): Time value

        Returns:
            int: Time in seconds, rounded to the nearest whole number
        """
        self.logger.debug(f"{inspect.stack()[0][3]} - Time in seconds = {round((time_2 - time_1).total_seconds())}")
        return round((time_2 - time_1).total_seconds())

    def execute_event_steps(self):
        """
        Performs the list of steps and actions to create the necessary pipeline event metrics
        """
        self._check_for_allowed_state()
        self._check_for_pipeline_prefix()
        self._process_pipeline_executions()
        # self._get_prior_pipeline_execution()
        # self._get_prior_successful_pipeline_execution()
        self._handle_final_state()
        self._handle_pipeline_yellow_and_red_time()
        self._handle_pipeline_cycle_time()
        self._handle_pipeline_lead_time()
