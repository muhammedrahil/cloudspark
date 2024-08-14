import json
import boto3
from typing import Optional, Dict, List, Union, Tuple
from cloudspark.utils import console_print  # Consider renaming to something like `log_message` if using logging
from cloudspark.aws_connect import AWSConnection
import base64
from botocore.client import Config

class S3Connection(AWSConnection):
    """
    A class to manage AWS S3 connection and operations, such as bucket creation, CORS management, 
    policy setting, and presigned URL generation.
    """

    __s3_instance: Optional[boto3.client] = None
    _bucket_name: Optional[str] = None

    def __init__(self, access_key: str, secret_access_key: str, region_name: str , DurationSeconds : int = 3600):
        """
        Initializes the S3 connection using the provided AWS credentials.

        :param access_key: AWS Access Key ID.
        :param secret_access_key: AWS Secret Access Key.
        :param region_name: AWS region name (e.g., 'us-east-1').
        """
        AccessKeyId ,SecretAccessKey, SessionToken = self.get_sts_token(AccessKey=access_key, 
                                                                        SecretKey=secret_access_key,
                                                                        DurationSeconds=DurationSeconds)
        super().__init__(access_key = AccessKeyId, 
                         secret_access_key = SecretAccessKey, 
                         region_name = region_name,
                         session_token = SessionToken)

    def connect(self, bucket_name: Optional[str] = None) -> boto3.client:
        """
        Establishes and returns an S3 client instance using the provided AWS credentials.

        :param bucket_name: Name of the S3 bucket to connect to. If provided, sets the internal bucket name.
        :return: The connected S3 client instance.
        """
        if not self._session:
            self.session_connect()  # Ensure the session is initialized

        if self.__s3_instance is None:
            self.__s3_instance = self._session.client('s3', config = Config(signature_version='s3v4'))  # Create an S3 client instance
        
        if bucket_name:
            self._bucket_name = bucket_name  # Set the internal bucket name
        
        return self.__s3_instance

    def get_instance(self) -> boto3.client:
        """
        Returns the current S3 client instance.

        :return: The current S3 client instance.
        :raises AssertionError: If the S3 connection is not established.
        """
        assert self.__s3_instance, "S3 connection not established. Please use connect(bucket_name)."
        return self.__s3_instance

    def create_s3bucket(self, bucket_name: str) -> boto3.client:
        """
        Creates an S3 bucket using the provided bucket name. If the bucket already exists, it notifies the user.

        :param bucket_name: Name of the bucket to create.
        :return: The S3 client instance connected to the created bucket.
        :raises ClientError: If an error occurs during bucket creation.
        """
        assert self.__s3_instance, "S3 connection not established. Please use connect()."

        try:
            # Check if the bucket already exists
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

        return self.connect(bucket_name)

    def set_bucket_cors(self, CORSRules: Union[List[Dict], None] = None) -> boto3.client:
        """
        Sets the CORS (Cross-Origin Resource Sharing) configuration for the connected S3 bucket.

        :param CORSRules: A list of dictionaries containing CORS rules. 
                          If None, a default CORS rule allowing all origins and methods is applied.
        :return: The S3 client instance connected to the bucket with the new CORS configuration.
        :raises AssertionError: If the S3 connection or bucket name is not set.
        :raises ClientError: If an error occurs while setting the CORS configuration.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use connect(bucket_name)."

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

        :return: A dictionary containing the current CORS configuration for the bucket.
        :raises AssertionError: If the S3 connection or bucket name is not set.
        :raises ClientError: If an error occurs while retrieving the CORS configuration.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use connect(bucket_name)."

        try:
            response = self.__s3_instance.get_bucket_cors(Bucket=self._bucket_name)
        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"An error occurred: {e}", color="error")
            raise

        return response

    def delete_bucket_cors(self):
        """
        Deletes the CORS configuration from the connected S3 bucket.

        :raises AssertionError: If the S3 connection or bucket name is not set.
        :raises ClientError: If an error occurs while deleting the CORS configuration.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use connect(bucket_name)."
        try:
            self.__s3_instance.delete_bucket_cors(Bucket=self._bucket_name)
        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"An error occurred: {e}", color="error")
            raise
        return self.__s3_instance

    def set_bucket_policy(self, bucket_policy: Optional[Union[str, Dict]] = None):
        """
        Sets or updates the bucket policy for the connected S3 bucket.

        :param bucket_policy: A JSON string or dictionary representing the bucket policy. 
                              If None, a default public read policy is applied.
        :raises AssertionError: If the S3 connection or bucket name is not set.
        :raises ClientError: If an error occurs while setting the bucket policy.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use connect(bucket_name)."

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

        :raises AssertionError: If the S3 connection or bucket name is not set.
        :raises ClientError: If an error occurs while deleting the bucket policy.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use connect(bucket_name)."
        try:
            self.__s3_instance.delete_bucket_policy(Bucket=self._bucket_name)
        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"An error occurred: {e}", color="error")
            raise
        return self.__s3_instance
    
    def get_bucket_policy(self):
        """
        Retrieves the bucket policy for the connected S3 bucket

        :raises AssertionError: If the S3 connection or bucket name is not set.
        :raises ClientError: If an error occurs while deleting the bucket policy.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use connect(bucket_name)."
        try:
            response = self.__s3_instance.get_bucket_policy(Bucket=self._bucket_name)
        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"An error occurred: {e}", color="error")
            raise
        return response

    def list_user_policies(self, UserName: str) -> Dict:
        """
        Lists inline policies for a specific IAM user.

        :param UserName: The name of the IAM user whose policies are to be listed.
        :return: A dictionary containing the list of user policies.
        """
        assert self._session, "S3 connection not established. Please use connect()."

        iam_client = self._session.client('iam')
        response = iam_client.list_user_policies(UserName=UserName)
        return response

    def public_access(self, block: bool = True) -> boto3.client:
        """
        Blocks or allows public access to the connected S3 bucket.

        :param block: If True, blocks public access. If False, allows public access.
        :return: The S3 client instance connected to the bucket.
        :raises AssertionError: If the S3 connection or bucket name is not set.
        :raises ClientError: If an error occurs while updating the public access configuration.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use connect(bucket_name)."

        block_settings = {
            'BlockPublicAcls': block,
            'IgnorePublicAcls': block,
            'BlockPublicPolicy': block,
            'RestrictPublicBuckets': block
        }

        try:
            self.__s3_instance.put_public_access_block(
                Bucket=self._bucket_name,
                PublicAccessBlockConfiguration=block_settings
            )
            status = "blocked" if block else "allowed"
            console_print(msg=f"Public access {status} for bucket '{self._bucket_name}'.")
        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"An error occurred: {e}", color="error")
            raise

        return self.__s3_instance

    def get_sts_token(self, AccessKey, SecretKey, DurationSeconds : int = 3600) -> Tuple[str, str, str]:
        """
        ## Retrieves AWS STS session tokens using the provided credentials.
        AWS Security Token Service (AWS STS) is available as a global service, and all AWS STS requests go to a single endpoint at https://sts.amazonaws.com.
        AWS recommends using Regional AWS STS endpoints instead of the global endpoint to reduce latency, build in redundancy, and increase session token validity.

        :param AccessKey: AWS Access Key ID.
        :param SecretKey: AWS Secret Access Key.
        :param DurationSeconds: Duration in seconds for which the session token should remain valid (default is 3600 seconds).
        :return: A tuple containing AccessKeyId, SecretAccessKey, and SessionToken.
        :raises Exception: If an error occurs while retrieving the STS token.
      
        """

        try:
            sts_client = boto3.client('sts',
                                    aws_access_key_id=AccessKey,
                                    aws_secret_access_key=SecretKey
                                    )
            response = sts_client.get_session_token(DurationSeconds=DurationSeconds)
            credentials = response['Credentials']
            AccessKeyId = credentials['AccessKeyId']
            SecretAccessKey = credentials['SecretAccessKey']
            SessionToken = credentials['SessionToken']
        except Exception as e:
            console_print(msg=f"An error occurred: {e}", color="error")
            raise

        return (AccessKeyId ,SecretAccessKey, SessionToken)
        
    def presigned_create_url(self, object_name: str, params: Optional[Dict] = None,
                             fields: Optional[Dict] = None, conditions: Optional[List[Dict]] = None,
                             expiration: int = 3600) -> str:
        """
        Generates a presigned URL for creating an object in the S3 bucket.

        :param object_name: The name of the object to be created in the S3 bucket.
        :param params: (Optional) Additional request parameters to include in the presigned URL.
        :param fields: (Optional) Pre-filled form fields to include in the presigned URL.
        :param conditions: (Optional) Conditions to include in the presigned URL.
        :param expiration: (Optional) Time in seconds for which the presigned URL should remain valid.
                           Default is 3600 seconds (1 hour).
        :return: A tuple containing the presigned URL and form fields.
        :raises AssertionError: If the S3 connection or bucket name is not set.
        :raises ClientError: If an error occurs while generating the presigned URL.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use connect(bucket_name)."

        try:
            if params:

                fields = fields if isinstance(fields, dict) else {}
                conditions = conditions if isinstance(conditions, list) else []

                for key,value in params.items():
                    if key != 'file_name':
                        fields[f'x-amz-meta-{key}'] = value
                        conditions.append({f'x-amz-meta-{key}':value})
                        
            response = self.__s3_instance.generate_presigned_post(
                Bucket=self._bucket_name,
                Key=object_name,
                Fields=fields,
                Conditions=conditions,
                ExpiresIn=expiration
            )
        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"An error occurred: {e}", color="error")
            raise

        return json.dumps(response)

    def presigned_delete_url(self, object_name: str, expiration: int = 3600) -> str:
        """
        Generates a presigned URL for delete an object in the S3 bucket.

        :param object_name: The name of the object to be accessed in the S3 bucket.
        :param expiration: (Optional) Time in seconds for which the presigned URL should remain valid.
                           Default is 3600 seconds (1 hour).
        :return: A presigned URL string.
        :raises AssertionError: If the S3 connection or bucket name is not set.
        :raises ClientError: If an error occurs while generating the presigned URL.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use connect(bucket_name)."

        try:
            response = self.__s3_instance.generate_presigned_url(
                'delete_object',
                Params={'Bucket': self._bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"An error occurred: {e}", color="error")
            raise
        return response
    
    def presigned_get_url(self, object_name: str, expiration: int = 3600) -> str:
        """Generate a presigned URL to share an S3 object

        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """

        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use connect(bucket_name)."

        try:
            response = self.__s3_instance.generate_presigned_url(
                'get_object',
                Params={'Bucket': self._bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
        except self.__s3_instance.exceptions.ClientError as e:
            console_print(msg=f"An error occurred: {e}", color="error")
            raise
        return response

    def policy_decode(self, policy_encoded: str) -> Dict:
        """
        Decodes a Base64-encoded policy string and returns it as a formatted JSON string.
        :params policy_encoded: The Base64-encoded policy string that needs to be decoded.

        :return: A dictionary representation of the policy, formatted as a JSON string with indentation.
        """
        try:
            # Decode the Base64-encoded policy string
            policy_decoded = base64.b64decode(policy_encoded).decode()
            # Convert the decoded JSON string into a Python dictionary
            policy_json = json.loads(policy_decoded)
            # Convert the dictionary back to a formatted JSON string with indentation
        except Exception as e:
            raise
        return json.dumps(policy_json, indent=4)

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

    def head_object(self, key_name: str):
        """
        Retrieve metadata of an object from the connected S3 bucket.

        :param key_name: S3 object name (e.g., 'folder/filename.txt' or 'filename.txt').
        :return: The object metadata.
        """
        assert self.__s3_instance and self._bucket_name, "S3 connection not established. Please use s3_connect(bucket_name)."

        try:
            key_object = self.__s3_instance.head_object(Bucket=self._bucket_name, Key=key_name)
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
    
    def get_objects(self, only_objects: bool = False, only_keys: bool = False) -> Union[List[Dict], List[str], Dict]:
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