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

#### Retrieves Bucket Policy
Retrieves the bucket policy for the connected S3 bucket
```python
policy = s3_conn.get_bucket_policy()
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
    object_name='object_name',
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

##### Output

```python

{'url': 'https://{{bucketname}}.s3.amazonaws.com/', 'fields': {'key': '{{object_name}}.mp4', 'x-amz-algorithm': 'AWS4-HMAC-SHA256', 'x-amz-credential': 'ASIASXFYXRCWS2V7P3US/20240731/ap-south-1/s3/aws4_request', 'x-amz-date': '20240731T145524Z', 'x-amz-security-token': 'IQoJb3JpZ2luX2VjEHcaCmFwLXNvdXRoLTEiRzBFAiBNpppLXjpopHVEyPJuNu+zgxIo4u9bWLP5ILcL75CPCQIhAOOHx0OACSBdLzc41Vn2NUzKTvfQHfflqcBuT10tb7RCKocDCGAQABoMMTg3MjE4NDk1NjYxIgx59bFXo014RO8gFQIq5AL7P5gQrNsOgOSPMb8p+XNpoVr32aqynjQtEMMoKecn4C1blpwYVAkUNnMhX/XspXeHwqUZBvwhjIHFe4+rMtznM46O2albdNPOImyp5HwIZmG74xGWqVoOG/1f16PWXJf4n/MgZvGDJgKXKCHC3kUsOnzhHfFJwgPmpaizd6ippEIOkz0bs86lHXqOnmt1HjnzqWij09p8WMto0bLvQxm+Thn+iItqnK+g0YbSEmO9kREig5u4HkUxJ+WkayO0ndXKUlPb85cEih8tbtWSBTEOKi08NppUL4LIR7NF+mUWnzeozohoZXI1FkANvwSpdnOO/4b8/HO16lpXlBi4Hh/V5lTb90aO1rMChXoGT6N+cuEJ/NyTBU/FqsOFahXEgA+DI8FE/zifwse7b8ipMqjchGiSCESgaTYtglE67VB2dQC05PFyf4xI/hS82NHLqPh/SRv2atTbzOJnBFKV3Q9FchSuCjDXnKm1BjqeAer1dmHtWmIJW4HdtR3JzVt2ChohWlG7U8EYgmqbq/EDfp5X/5N4oYOh2YTywjYnlSFTbhPF1wSK9atuYUZ2VPlvaI+c5fFtE1eOMe1GB1Rps959uMaOTn6o2zN+GqqeKo3bYF5KqoSEQT5hGgVgLjM+kZXh8o1O4958io8WHZVDXJniyip5yMXRILacrvlp4d2X4pSfCXBOaEpMWtD8', 'policy': 'eyJleHBpcmF0aW9uIjogIjIwMjQtMDctMzFUMTY6MTI6MDRaIiwgImNvbmRpdGlvbnMiOiBbeyJidWNrZXQiOiAibXlwYXRyaW90YXBwYnVja2V0In0sIHsia2V5IjogIjMxOTUzOTQtdWhkXzM4NDBfMjE2MF8yNWZwcy5tcDQifSwgeyJ4LWFtei1hbGdvcml0aG0iOiAiQVdTNC1ITUFDLVNIQTI1NiJ9LCB7IngtYW16LWNyZWRlbnRpYWwiOiAiQVNJQVNYRllYUkNXUzJWN1AzVVMvMjAyNDA3MzEvYXAtc291dGgtMS9zMy9hd3M0X3JlcXVlc3QifSwgeyJ4LWFtei1kYXRlIjogIjIwMjQwNzMxVDE0NTUyNFoifSwgeyJ4LWFtei1zZWN1cml0eS10b2tlbiI6ICJJUW9KYjNKcFoybHVYMlZqRUhjYUNtRndMWE52ZFhSb0xURWlSekJGQWlCTnBwcExYanBvcEhWRXlQSnVOdSt6Z3hJbzR1OWJXTFA1SUxjTDc1Q1BDUUloQU9PSHgwT0FDU0JkTHpjNDFWbjJOVXpLVHZmUUhmZmxxY0J1VDEwdGI3UkNLb2NEQ0dBUUFCb01NVGczTWpFNE5EazFOall4SWd4NTliRlhvMDE0Uk84Z0ZRSXE1QUw3UDVnUXJOc09nT1NQTWI4cCtYTnBvVnIzMmFxeW5qUXRFTU1vS2VjbjRDMWJscHdZVkFrVU5uTWhYL1hzcFhlSHdxVVpCdndoaklIRmU0K3JNdHpuTTQ2TzJhbGJkTlBPSW15cDVId0labUc3NHhHV3FWb09HLzFmMTZQV1hKZjRuL01nWnZHREpnS1hLQ0hDM2tVc09uemhIZkZKd2dQbXBhaXpkNmlwcEVJT2t6MGJzODZsSFhxT25tdDFIam56cVdpajA5cDhXTXRvMGJMdlF4bStUaG4raUl0cW5LK2cwWWJTRW1POWtSRWlnNXU0SGtVeEorV2theU8wbmRYS1VsUGI4NWNFaWg4dGJ0V1NCVEVPS2kwOE5wcFVMNExJUjdORittVVduemVvem9ob1pYSTFGa0FOdndTcGRuT08vNGI4L0hPMTZscFhsQmk0SGgvVjVsVGI5MGFPMXJNQ2hYb0dUNk4rY3VFSi9OeVRCVS9GcXNPRmFoWEVnQStESThGRS96aWZ3c2U3YjhpcE1xamNoR2lTQ0VTZ2FUWXRnbEU2N1ZCMmRRQzA1UEZ5ZjR4SS9oUzgyTkhMcVBoL1NSdjJhdFRiek9KbkJGS1YzUTlGY2hTdUNqRFhuS20xQmpxZUFlcjFkbUh0V21JSlc0SGR0UjNKelZ0MkNob2hXbEc3VThFWWdtcWJxL0VEZnA1WC81TjRvWU9oMllUeXdqWW5sU0ZUYmhQRjF3U0s5YXR1WVVaMlZQbHZhSStjNWZGdEUxZU9NZTFHQjFScHM5NTl1TWFPVG42bzJ6TitHcXFlS28zYllGNUtxb1NFUVQ1aEdnVmdMak0ra1pYaDhvMU80OTU4aW84V0haVkRYSm5peWlwNXlNWFJJTGFjcnZscDRkMlg0cFNmQ1hCT2FFcE1XdEQ4In1dfQ==', 'x-amz-signature': '878f7196136da54e345460f49b636ef5ea1ca54fd5615f86e25f77ff1a20d755'}}

```

#### Generate Presigned Delete URL
Generate a presigned URL for Delete an object

```python
responce = s3_conn.presigned_delete_url(object_name='object_name', expiration=3600)
```

##### Output

```python
"https://{{bucket_name}}.s3.amazonaws.com/hdfwf.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIASXFYXRCWTXZSH6N3%2F20240812%2Fap-south-1%2Fs3%2Faws4_request&X-Amz-Date=20240812T151744Z&X-Amz-Expires=4600&X-Amz-SignedHeaders=host&X-Amz-Signature=a680ee638e9cc27f2ec21cae36ad807cffb2fc74e1e91fa55709f25f324d1e22"
```

#### Uploads a file to the connected S3 bucket.

```python
responce = s3_conn.upload_object(file=file, key_name="object_name")

# example:
with open('file_name',"rb") as file_obj:
    s3_conn.upload_object(file=file_obj, key_name="object_name")
```
`file`: Bytes of the file to upload

`key_name`: S3 object name (e.g., 'folder/filename.txt').

#### Retrieves an object from the connected S3 bucket.

return: The object metadata

```python
key_object = s3_conn.get_object(key_name="object_name")

```

#### Deletes an object from the connected S3 bucket

```python
key_object = s3_conn.delete_object(key_name="object_name")

```

#### Lists objects in the connected S3 bucket.

```python
key_object = s3_conn.get_objects()
```

```python
key_object = s3_conn.get_objects(only_objects=True)
```

`only_objects`: If True, returns a list of object metadata (excluding keys).

```python
key_object = s3_conn.get_objects(only_keys=True)
```

`only_keys`: If True, returns a list of object keys.
