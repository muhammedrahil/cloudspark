from setuptools import setup, find_packages
import codecs
import os

# Get the absolute path to the directory containing this file
here = os.path.abspath(os.path.dirname(__file__))

# Read the long description from the README file
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

# Define the version of the package
VERSION = '1.0.3'

# Short description of the package
DESCRIPTION = '''CloudSpark is a powerful Python package designed to simplify the management of AWS S3 and Lambda services. Whether you're working on the frontend or backend, CloudSpark provides an intuitive interface to generate presigned URLs and handle file uploads seamlessly.'''

# Setting up the package
setup(
    name="cloudspark",
    version=VERSION,
    author="Muhammed Rahil M",
    author_email="muhammedrahilmadathingal@gmail.com",
    description=DESCRIPTION,
    long_description=long_description,
    url="https://github.com/muhammedrahil/cloudspark",
    long_description_content_type="text/markdown",
    packages=find_packages(where="app"),
    install_requires=['boto3 >= 1.34.157'],
    keywords=['python', 'aws', 's3', 'lambda', 'presigned urls', 'file uploads'],
    license="MIT",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",  # Add license if applicable
    ]
)
