"""
Assorted utility functions.
"""

import pandas as pd
import boto3
import os
from io import BytesIO

def import_data(bucket, filename):
    """
    Import a csv file from an s3 bucket into local memory.
    Requires AWS keys to be stored in your bash profile.
    :param bucket: str, name of the s3 bucket.
    :param filename: str, the name of the csv file.
    :return: Pandas Dataframe containing the data.
    """
    s3 = boto3.client("s3", aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                      aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
    obj = s3.get_object(Bucket=bucket, Key=filename)
    return pd.read_csv(BytesIO(obj["Body"].read()))


