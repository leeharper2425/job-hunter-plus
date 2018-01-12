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
    df = remove_403_errors(df)
    df = create_labels(df)
    df = df[df["label"] < num_cities]
    df2 = clean_indeed_jobs(df)
    return create_text_matrix(df2["job_description"]), \
           create_text_matrix(df["job_description"]), \
           df["label"].as_matrix()


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


def remove_403_errors(df):
    """
    Remove any rows where a 403 error was returned
    :param df: Pandas DataFrame
    :return: Pandas Dataframe, with 403 errors removed
    """
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


def create_text_matrix(series):
    """
    Strip special characters and return cleaned text in an array.
    :param series: Pandas Series, the job description text
    :return: Numpy array, the cleaned up text
    """
    series = series.apply(lambda x: re.sub(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))", r" \1", x))
    sm = series.as_matrix()
    for index, document in enumerate(series):
        document = document.replace("\n", " ")
        sm[index] = re.sub("[^\w\s]|â", "", document, flags=re.UNICODE)
    return sm


def clean_indeed_jobs(df):
    """
    Extract job info only from postings placed directly on Indeed.
    This is possible due to the standardized structure of the page.
    :param df: Pandas DataFrame containing data.
    :return: DataFrame containing only those jobs, with cleaning performed
    """
    field = "job_description"
    df = df[df[field].str.contains("Indeed - Cookies, Privacy and Terms")]
    df[field] = df[field].apply(lambda x: max(x.split('\n'), key=len).split("Job Type:")[0])
    df = df[~df["job_description"].str.contains("We know salary is a key component")]
    return df
