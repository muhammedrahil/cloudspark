import boto3

class AWSConnection:
    """A class to manage an AWS connection."""

    def __init__(self, access_key: str, secret_access_key: str, region_name: str, session_token : str = None):
        """
        Initializes the AWSConnection instance with AWS credentials and region information.

        :param access_key: AWS Access Key ID.
        :param secret_access_key: AWS Secret Access Key.
        :param region_name: AWS region name (e.g., 'us-west-2').
        """
        self._session: boto3.Session = None

        self._access_key = access_key
        self._secret_access_key = secret_access_key
        self._region_name = region_name
        self._session_token = session_token

    @classmethod
    def session_connect(cls) -> boto3.Session:
        """
        Establishes and returns a boto3 Session instance using the provided AWS credentials.

        :return: A boto3 Session instance.
        """
        if cls._session is None:
            cls._session = boto3.Session(
                aws_access_key_id=cls._access_key,
                aws_secret_access_key=cls._secret_access_key,
                aws_session_token=cls._session_token,
                region_name=cls._region_name
            )
        return cls._session
