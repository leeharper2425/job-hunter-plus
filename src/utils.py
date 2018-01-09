"""
Assorted utility functions.
"""

import pandas as pd
import boto3
import os
from io import BytesIO
import re


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


def create_model_data(data, bucket=None, filename=None, num_cities=2):
    """
    Import and process DataFrame data from the Indeed scraper for model building.
    :param data: DataFrame to process and extract information from
    :param bucket: str S3 bucket of data if applicable.
    :param filename: str, name of the data file, if applicable.
    :param num_cities: int, the number of cities to retain.
    :return: ndarrays for the feature matrix and class matrix
    """
    df = import_data(bucket, filename) if data is None else data
    df = remove_null(df, ["job_description"])
    df = create_labels(df)
    df = df[df["label"] < num_cities]
    return create_text_matrix(df["job_description"]), df["label"]


def remove_null(df, fields):
    """
    Remove any rows where the given fields are null
    :param df: Pandas DataFrame
    :param fields: list of str, the columns to filter on
    :return: Pandas DataFrame, with nulls removed
    """
    for column_name in fields:
        df = df[df[column_name].notnull()]
    return df


def create_labels(df):
    """
    Creates integer numeric label based on city_term
    0 = San+Francisco, 1 = New+York, 2 = Chicago, 3 = Austin
    :param df: Pandas DataFrame containing data
    :return: Pandas DataFrame with extra label fields converted to int
    """
    replace_dict = {"San+Francisco": 0,
                    "New+York": 1,
                    "Chicago": 2,
                    "Austin": 3}
    df["label"] = df["city_term"].replace(replace_dict)
    return df


def create_text_matrix(series):
    """
    Strip special characters and return cleaned text in a vector.
    :param series: Pandas Series, the job description text
    :return: Numpy array, the cleaned up text
    """
    sm = series.as_matrix()
    for index, document in enumerate(series):
        document = document.replace("\n", " ")
        sm[index] = re.sub("[^\w\s]|â", "", document, flags=re.UNICODE)
    return
