# CloudSpark


`cloudspark` is a Python package that provides a convenient way to manage AWS S3 buckets and generate presigned URLs using `boto3`. It supports bucket creation, CORS management, policy setting, and presigned URL generation.

## Features

- **S3 Management**: Effortlessly manage your S3 buckets, objects, and file uploads with built-in methods.

- **Presigned URL Generation**: Generate secure presigned URLs for your S3 objects, enabling users to upload files directly from the frontend without exposing your credentials.

- **Seamless Integration**: Designed to work smoothly with both frontend and backend applications, making file uploads and cloud function management more accessible.


This repository contains several components. For more details on each component, refer to the respective README files.

- [git repository](https://github.com/muhammedrahil/cloudspark)
- [Documentation](README.md)
- [Js-Implementation](js-implementation.md)


## Installation

You can install `cloudspark` via pip. Make sure you have `boto3` installed as well.

```bash 
pip install cloudspark 
```
## Usage
#### Importing the Library
```python
from cloudspark import S3Connection
```
#### Initializing the Connection
Create an instance of `S3Connection` by providing your AWS credentials and region name
```python
s3_conn = S3Connection(access_key='YOUR_ACCESS_KEY',
                       secret_access_key='YOUR_SECRET_ACCESS_KEY',
                       region_name='YOUR_REGION_NAME')
```

#### Connecting to a Bucket
Establish a connection to an S3 bucket: 
```python
s3_bucketclient = s3_conn.connect(bucket_name='your-bucket-name')
```
returns an S3 client instance. 

#### Returns the current S3 client instance 
```python
s3_bucketclient = s3_conn.get_instance()
```
returns an S3 client instance. 

#### Creating a bucket
Creates an S3 bucket with the provided name.
```python
s3_client = s3_conn.connect()
s3_bucketclient = s3_conn.create_s3bucket(bucket_name='new-bucket-name')
```

#### Set Bucket CORS
Set the CORS configuration for the connected bucket

```python
s3_conn.set_bucket_cors()

# CORSRules: A list of dictionaries containing CORS rules.
# If None, a default CORS rule allowing all origins and methods is applied.
cors_rules = [
    {
        'AllowedHeaders': ['*'],
        'AllowedMethods': ['GET', 'POST'],
        'AllowedOrigins': ['*'],
        'ExposeHeaders': [],
        'MaxAgeSeconds': 3000
    }
]

s3_conn.set_bucket_cors(CORSRules=cors_rules)
```
#### Get Bucket CORS
Retrieve the CORS configuration for the connected bucket
```python
cors_config = s3_conn.get_bucket_cors()
```

#### Delete Bucket CORS
Delete the CORS configuration from the connected bucket
```python
s3_conn.delete_bucket_cors()
```
#### Set Bucket Policy
Set or update the bucket policy for the connected bucket
```python

s3_conn.set_bucket_policy()

# A JSON string or dictionary representing the bucket policy. 
# If None, a default public read policy is applied.

policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }
    ]
}
s3_conn.set_bucket_policy(bucket_policy=policy)
```

#### Delete Bucket Policy
Delete the bucket policy from the connected bucket
```python
s3_conn.delete_bucket_policy()
```

#### List User Policies
List inline policies for an IAM user
```python
policies = s3_conn.list_user_policies(UserName='user-name')
```
#### Block or Allow Public Access
Block or allow public access to the bucket
```python
s3_conn.public_access(block=True)  # Block public access
s3_conn.public_access(block=False) # Allow public access
```

#### Generate Presigned Create URL
Generate a presigned URL for creating an object

```python
responce = s3_conn.presigned_create_url(
    object_name='my-object',
    params={'key': 'value'},
    fields={'field': 'value'},
    conditions=[{'condition': 'value'}],
    expiration=3600
)
```
`object_name` : The name of the object to be created in the S3 bucket.

`params`: (Optional) Additional request parameters to include in the presigned URL.

`fields` : (Optional) Pre-filled form fields to include in the presigned URL.

`conditions`: (Optional) Conditions to include in the presigned URL.

`expiration` : (Optional) Time in seconds for which the presigned URL should remain valid. Default is 3600 seconds (1 hour).

#### Generate Presigned Get URL
Generate a presigned URL for accessing an object

```python
responce = s3_conn.presigned_get_url(object_name='my-object', expiration=3600)
```