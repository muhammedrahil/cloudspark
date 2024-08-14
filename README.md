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
#### Policy Fields Explaintion

#### 1. Version
    Key: "Version"
    Value: "2012-10-17"
    Explanation:
    This specifies the version of the policy language. "2012-10-17" is the latest version and is recommended for use.
#### 2. Id
    Key: "Id"
    Value: "Policy1719828879302"
    Explanation:
    The Id is an optional identifier for the policy. It helps in identifying the policy, especially when dealing with multiple policies. The value here is just a unique identifier that you can use to track or refer to this policy.
#### 3. Statement
    Key: "Statement"
    Value: [ ... ]
    Explanation:
    This is an array of statements that define what actions are allowed or denied. Each statement contains specific instructions for who can perform what actions on which resources.
    Inside the Statement Array:
    Sid

        Key: "Sid"
            Value: "Stmt1719828876812"
            Explanation:
            The Sid (Statement ID) is an optional identifier for the specific statement. It helps in identifying and managing individual statements within the policy.
            Effect

        Key: "Effect"
            Value: "Allow"
            Explanation:
            The Effect determines whether the statement allows or denies access. Here, "Allow" means that the actions specified in the Action field are permitted. If it were "Deny", those actions would be explicitly forbidden.
            Principal

        Key: "Principal"
            Value: "*"
            Explanation:
            The Principal specifies the entity that is allowed or denied the actions. "*" means any entity (i.e., any user, role, or service) is allowed to perform the specified actions. You could also restrict this to a specific AWS account or IAM user.
            Action

        Key: "Action"
            Value: "s3:GetObject"
            Explanation:
            The Action specifies what actions are allowed or denied. Here, "s3:GetObject" means that the entities specified in the Principal field are allowed to retrieve objects from the S3 bucket. "s3:GetObject" is the action used for downloading files from S3.
            Resource

        Key: "Resource"
            Value: "arn:aws:s3:::{{bucket_name}}/*"
            Explanation:
            The Resource specifies the particular AWS resource that the policy applies to. Here, the resource is specified as "arn:aws:s3:::{{bucket_name}}/*", which means all objects (files) within the {{bucket_name}} S3 bucket.
            The arn:aws:s3:::{{bucket_name}}/* is an Amazon Resource Name (ARN) that uniquely identifies the S3 bucket and all its objects. The /* at the end means that the policy applies to all objects within the {{bucket_name}} bucket.

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
    params={'key': 'value'}, # Or params= None
    fields={'field': 'value'}, # Or fields= None
    conditions=[{'condition': 'value'}], # Or conditions= None
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
{
  "url": "https://{{bucket_name}}.s3.amazonaws.com/",
  "fields": {
    "key": "{{object_name.extention}}",
    "x-amz-algorithm": "AWS4-HMAC-SHA256",
    "x-amz-credential": "{{access_key}}/20240814/us-east-1/s3/aws4_request",
    "x-amz-date": "20240814T092932Z",
    "x-amz-security-token": "{{sts_token}}",
    "policy": "{{policy}}",
    "x-amz-signature": "{{signature}}"
  }
}

```

#### Generate Presigned Delete URL
Generate a presigned URL for Delete an object

```python
responce = s3_conn.presigned_delete_url(object_name='object_name', expiration=3600)
```

##### Output

```python
"https://{{bucket_name}}.s3.amazonaws.com/hdfwf.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential={{access_key}}%2F20240812%2Fap-south-1%2Fs3%2Faws4_request&X-Amz-Date=20240812T151744Z&X-Amz-Expires=4600&X-Amz-SignedHeaders=host&X-Amz-Signature=a680ee638e9cc27f2ec21cae36ad807cffb2fc74e1e91fa55709f25f324d1e22"
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

#### policy_decode Function

The `policy_decode` function is designed to decode a Base64-encoded AWS S3 policy string and return it as a formatted JSON string. This is useful for inspecting and validating S3 presigned URL policies.

Decodes a Base64-encoded policy string and returns it as a formatted JSON string
```python

policy_dict = s3_conn.policy_decode(policy_encoded="policy_encoded string")

```
