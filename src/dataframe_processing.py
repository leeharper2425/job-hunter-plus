"""
Functions that perform basic processing on the dataframe to eventually output
a transformed set of feature and label arrays for model training and testing.
"""

from .utils import import_data
import re
import pandas as pd
import numpy as np


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
    df = dedupe_and_403(df)
    df = create_labels(df)
    df = df[df["label"] < num_cities]
    df = clean_indeed_jobs(df)
    return df


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


def dedupe_and_403(df):
    """
    Remove any exact duplicate rows and any 403 errors
    :param df: Pandas DataFrame
    :return: Pandas Dataframe, deduped without 403 errors.
    """
    df = df.drop_duplicates("job_description")
    return df[~df["job_description"].str.contains("403")]


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


def clean_indeed_jobs(df):
    """
    Extract job info only from postings placed directly on Indeed.
    This is possible due to the standardized structure of the page.
    :param df: Pandas DataFrame containing data.
    :return: DataFrame with extra bool "cleaned" column and cleaned descriptions.
    """
    field = "job_description"
    df["cleaned"] = df[field].str.contains("Indeed - Cookies, Privacy and Terms")
    df2 = df[df["cleaned"]]
    df2[field] = df2[field].apply(lambda x: max(x.split('\n'), key=len).split("Job Type:")[0])
    df2["cleaned"] = ~df2["job_description"].str.contains("We know salary is a key component")
    df2 = df2[df2["cleaned"]]
    idx = df2.index.values
    df = df.drop(idx)
    df = df.append(df2, ignore_index = True)
    return df
