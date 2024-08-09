import json
import boto3
from typing import Optional, Dict, List, Union
from utils import console_print
from aws_connect import AWSConnection

class S3Connection(AWSConnection):
    """A class to manage AWS S3 connection and operations."""

    __s3_instance: Optional[boto3.client] = None
    _bucket_name: Optional[str] = None

    def __init__(self, access_key: str, secret_access_key: str, region_name: str):
        """
        Initializes the S3 connection using the provided AWS credentials.

        :param access_key: AWS access key.
        :param secret_access_key: AWS secret access key.
        :param region_name: AWS region name (e.g., 'us-west-2').
        """
        super().__init__(access_key=access_key, 
                         secret_access_key=secret_access_key, 
                         region_name=region_name)

    def s3_connect(self, bucket_name: Optional[str] = None) -> boto3.client:
        """
        Establishes and returns an S3 client instance using the provided AWS credentials.

        :param bucket_name: Optional name of the S3 bucket to connect to.
        :return: A boto3 S3 client instance.
        """
        if not self._session:
            self.session_connect()

        if self.__s3_instance is None:
            self.__s3_instance = self._session.client('s3')
        
        if bucket_name:
            self._bucket_name = bucket_name
        
        return self.__s3_instance

    def create_s3bucket(self, bucket_name: str) -> boto3.client:
        """
        Creates an S3 bucket using the provided bucket name. If the bucket already exists, it notifies the user.

        :param bucket_name: The name of the bucket to create.
        :return: The S3 client instance.
        """
        assert self.__s3_instance, "S3 connection not established. Please use s3_connect()."

        try:
            self.__s3_instance.head_bucket(Bucket=bucket_name)
            console_print(msg=f"Bucket '{bucket_name}' already exists.", color="error")
        except self.__s3_instance.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']

            if error_code == '404':
                # Create the bucket if it doesn't exist
                if self._region_name == 'us-east-1':
                    self.__s3_instance.create_bucket(Bucket=bucket_name)
                else:
                    self.__s3_instance.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self._region_name}
                    )
                console_print(msg=f"Bucket '{bucket_name}' created successfully.")
            else:
                console_print(msg=f"An error occurred: {e}", color="error")
                raise

        return self.s3_connect(bucket_name)

    def set_bucket_cors(self, CORSRules: Union[List[Dict], None] = None) -> boto3.client:
        """
        Sets the CORS configuration for the connected S3 bucket.

        :param CORSRules: Optional CORS configuration. If not provided, a default configuration is applied.
        :return: The S3 client instance.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use s3_connect(bucket_name)."

        default_CORSRules = [
            {
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'POST', 'PUT', 'HEAD', 'DELETE'],
                'AllowedOrigins': ['*'],
                'ExposeHeaders': [],
                'MaxAgeSeconds': 3000
            }
        ]
        
        cors_configuration = {
            'CORSRules': CORSRules if CORSRules else default_CORSRules
        }

        self.__s3_instance.put_bucket_cors(Bucket=self._bucket_name, CORSConfiguration=cors_configuration)

        console_print(msg=f"CORS configuration set for bucket '{self._bucket_name}'.")
        return self.__s3_instance

    def get_bucket_cors(self) -> Dict:
        """
        Retrieves the CORS configuration for the connected S3 bucket.

        :return: A dictionary containing the CORS configuration.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use s3_connect(bucket_name)."

        try:
            response = self.__s3_instance.get_bucket_cors(Bucket=self._bucket_name)
        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"An error occurred: {e}", color="error")
            raise

        return response

    def set_bucket_policy(self, bucket_policy: Optional[Union[str, Dict]] = None):
        """
        Sets or updates the bucket policy for the connected S3 bucket.

        :param bucket_policy: Optional policy in JSON format. If not provided, a default policy is applied.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use s3_connect(bucket_name)."

        default_bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:*",
                    "Resource": f"arn:aws:s3:::{self._bucket_name}/*"
                }
            ]
        }

        if bucket_policy:
            if isinstance(bucket_policy, dict):
                bucket_policy = json.dumps(bucket_policy)
        else:
            bucket_policy = json.dumps(default_bucket_policy)
        
        try:
            self.__s3_instance.put_bucket_policy(Bucket=self._bucket_name, Policy=bucket_policy)
            console_print(msg="Bucket policy updated successfully.")
        except self.__s3_instance.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDenied':
                console_print(msg="Access denied: insufficient permissions to set the bucket policy.", color="error")
            else:
                console_print(msg=f"An error occurred: {e}", color="error")
            raise

        return self.__s3_instance

    def delete_bucket_policy(self):
        """
        Deletes the bucket policy from the connected S3 bucket.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use s3_connect(bucket_name)."
        try:
            self.__s3_instance.delete_bucket_policy(Bucket=self._bucket_name)
        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"An error occurred: {e}", color="error")
            raise
        return self.__s3_instance

    def delete_bucket_cors(self):
        """
        Deletes the CORS configuration from the connected S3 bucket.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use s3_connect(bucket_name)."
        try:
            self.__s3_instance.delete_bucket_cors(Bucket=self._bucket_name)
        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"An error occurred: {e}", color="error")
            raise
        return self.__s3_instance

    def get_s3_instance(self) -> boto3.client:
        """
        Returns the current S3 client instance.

        :return: A boto3 S3 client instance if initialized; otherwise, raises an assertion error.
        """
        assert self.__s3_instance, "S3 connection not established. Please use s3_connect(bucket_name)."
        return self.__s3_instance

    def get_s3_bucket_objects(self, only_objects: bool = False, only_keys: bool = False) -> Union[List[Dict], List[str], Dict]:
        """
        Lists objects in the connected S3 bucket.

        :param only_objects: If True, returns a list of object metadata (excluding keys).
        :param only_keys: If True, returns a list of object keys.
        :return: A list of object metadata, keys, or the full response based on the parameters.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use s3_connect(bucket_name)."

        # Fetch the list of objects
        response = self.__s3_instance.list_objects_v2(Bucket=self._bucket_name)

        # Handle case where there are no objects
        if 'Contents' not in response:
            return []

        # Return only objects or only keys based on parameters
        if only_objects:
            return [obj for obj in response['Contents']]
        
        if only_keys:
            return [obj['Key'] for obj in response['Contents']]
        
        # Return full response if neither only_objects nor only_keys is specified
        return response

    def list_user_policies(self, UserName: str) -> Dict:
        """
        Lists inline policies for a specific IAM user.

        :param UserName: The IAM username.
        :return: A dictionary containing the list of inline policies.
        """
        iam_client = self._session.client('iam')
        response = iam_client.list_user_policies(UserName=UserName)
        return response

    def s3_public_access(self, block: bool = True) -> boto3.client:
        """
        Blocks or allows public access to the connected S3 bucket.

        :param block: If True, blocks public access; otherwise, allows public access.
        :return: The S3 client instance.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use s3_connect(bucket_name)."

        try:
            self.__s3_instance.put_public_access_block(
                Bucket=self._bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': block,
                    'IgnorePublicAcls': block,
                    'BlockPublicPolicy': block,
                    'RestrictPublicBuckets': block
                }
            )
            _msg = "blocked" if block else "allowed"
            console_print(msg=f"Public access {_msg} for bucket: {self._bucket_name}")
        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"Error in setting public access: {e}", color="error")
            raise

        return self.__s3_instance
    
    def upload_object(self, file: bytes, key_name: str):
        """
        Uploads a file to the connected S3 bucket.

        :param file: Bytes of the file to upload.
        :param key_name: S3 object name (e.g., 'folder/filename.txt').
        :return: True if the file was uploaded successfully; otherwise, raises an exception.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use s3_connect(bucket_name)."

        try:
            self.__s3_instance.put_object(Bucket=self._bucket_name, Key=key_name, Body=file)
            console_print(msg=f"File '{key_name}' successfully uploaded to bucket '{self._bucket_name}'.")

        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"Error uploading file '{key_name}': {e}", color="error")
            raise
    
    def get_object(self, key_name: str):
        """
        Retrieves an object from the connected S3 bucket.

        :param key_name: S3 object name (e.g., 'folder/filename.txt' or 'filename.txt').
        :return: The object metadata.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use s3_connect(bucket_name)."

        try:
            key_object = self.__s3_instance.get_object(Bucket=self._bucket_name, Key=key_name)
        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"An error occurred: {e}", color="error")
            raise
        return key_object

    def delete_object(self, key_name: str):
        """
        Deletes an object from the connected S3 bucket.

        :param key_name: S3 object name (e.g., 'folder/filename.txt').
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use s3_connect(bucket_name)."

        try:
            self.__s3_instance.delete_object(Bucket=self._bucket_name, Key=key_name)
            console_print(msg=f"Successfully deleted '{key_name}' from bucket '{self._bucket_name}'")
        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"An error occurred: {e}", color="error")
            raise
        return 