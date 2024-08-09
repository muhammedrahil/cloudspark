import boto3
from typing import Optional

class AWSConnection:
    """A class to manage an AWS connection."""

    _session: Optional[boto3.Session] = None

    def __init__(self, access_key: str, secret_access_key: str, region_name: str):
        """
        Initializes the AWSConnection instance with AWS credentials and region information.

        :param access_key: AWS Access Key ID.
        :param secret_access_key: AWS Secret Access Key.
        :param region_name: AWS region name (e.g., 'us-west-2').
        """
        self._access_key = access_key
        self._secret_access_key = secret_access_key
        self._region_name = region_name

    def session_connect(self) -> boto3.Session:
        """
        Establishes and returns a boto3 Session instance using the provided AWS credentials.

        :return: A boto3 Session instance.
        """
        if self._session is None:
            self._session = boto3.Session(
                aws_access_key_id=self._access_key,
                aws_secret_access_key=self._secret_access_key,
                region_name=self._region_name
            )
        return self._session
