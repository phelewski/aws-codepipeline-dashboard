import io
import shutil
import sys

import boto3
import botocore


class Deploy:
    def __init__(self) -> None:
        self.cloudformation = boto3.client('cloudformation')
        self.s3 = boto3.client('s3')
        self.stack_name = sys.argv[1]
        self.s3_bucket = sys.argv[2]
        self.cft_file_name = sys.argv[3]
        self.pipeline_pattern = sys.argv[4]
        self.cft_s3_file_name = 'aws-codepipeline-dashboard-cft.yaml'
        self.lambda_zip_file_name = 'aws-codepipeline-dashboard-lambda-0.0.9'
        self.lambda_dir_name = 'src'
        self.parameters = [
            {
                'ParameterKey': 'PipelinePattern',
                'ParameterValue': self.pipeline_pattern
            },
            {
                'ParameterKey': 'BucketName',
                'ParameterValue': self.s3_bucket
            },
            {
                'ParameterKey': 'CodeKey',
                'ParameterValue': f"{self.lambda_zip_file_name}.zip"
            }
        ]

    def _convert_file_to_bytes(self, local_file_name: str) -> bytes:
        with open(local_file_name, 'rb') as local_file:
            local_file_bytes = io.BytesIO(local_file.read())

        return local_file_bytes

    def _compress_file(_self, base_name: str, format: str, root_dir: str) -> None:
        try:
            shutil.make_archive(base_name, format, root_dir)
        except Exception as e:
            raise e

    def _upload_file_to_s3(self, bucket: str, key: str, local_file: str) -> None:
        try:
            self.s3.put_object(
                ACL='private',
                Body=self._convert_file_to_bytes(local_file),
                Bucket=bucket,
                Key=key
            )
        except botocore.exceptions.ClientError as e:
            raise e

    def _create_cloudformation_stack(self) -> dict:
        try:
            response = self.cloudformation.create_stack(
                StackName=self.stack_name,
                TemplateURL=f"https://{self.s3_bucket}.s3.amazonaws.com/{self.cft_s3_file_name}",
                Parameters=self.parameters,
                Capabilities=[
                    'CAPABILITY_IAM',
                    'CAPABILITY_AUTO_EXPAND'
                ]
            )

            return response
        except botocore.exceptions.ClientError as e:
            raise e

    def _cloudformation_stack_waiter(self, waiter_type: str) -> None:
        try:
            self.cloudformation.get_waiter(waiter_type).wait(
                StackName=self.stack_name
            )
        except botocore.exceptions.ClientError as e:
            raise e

    def _update_cloudformation_stack(self) -> dict:
        try:
            response = self.cloudformation.update_stack(
                StackName=self.stack_name,
                TemplateURL=f"https://{self.s3_bucket}.s3.amazonaws.com/{self.cft_s3_file_name}",
                Parameters=self.parameters,
                Capabilities=[
                    'CAPABILITY_IAM',
                    'CAPABILITY_AUTO_EXPAND'
                ]
            )

            return response
        except botocore.exceptions.ClientError as e:
            raise e

    def _describe_cloudformation_stack(self) -> dict:
        try:
            response = self.cloudformation.describe_stacks(
                StackName=self.stack_name
            )

            return response
        except botocore.exceptions.ClientError as e:
            if f"Stack with id {self.stack_name} does not exist" in str(e):
                return False
            else:
                raise e

    def deploy_cloudformation(self) -> None:
        print("Compressing Lamdba Script")
        self. _compress_file(self.lambda_zip_file_name, 'zip', self.lambda_dir_name)

        print("Uploading Lambda ZIP to S3")
        self._upload_file_to_s3(self.s3_bucket, f"{self.lambda_zip_file_name}.zip", f"{self.lambda_zip_file_name}.zip")

        print("Uploading CFT to S3")
        self._upload_file_to_s3(self.s3_bucket, self.cft_s3_file_name, self.cft_file_name)

        if self._describe_cloudformation_stack():
            print("Updating stack...")
            self._update_cloudformation_stack()
            print("Waiting for stack update to complete")
            self._cloudformation_stack_waiter('stack_update_complete')
            print("Stack update complete!")
        else:
            print("Stack does not exist yet, creating...")
            self._create_cloudformation_stack()
            print("Waiting for stack creation to complete")
            self._cloudformation_stack_waiter('stack_create_complete')
            print("Stack creation complete!")


def main():
    Deploy().deploy_cloudformation()


if __name__ == "__main__":
    main()
