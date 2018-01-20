"""
Assorted utility functions.
"""

import pandas as pd
import boto3
import os
from io import BytesIO
from sklearn.feature_extraction import text
import pickle


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


def get_stopwords():
    """
    Return the list of stopwords that are being used for job classification.
    :return: set, the stopwords to be removed from the corpus
    """
    words = {"york", "francisco", "chicago", "ny", "ca", "austin", "chicago",
             "tx", "nyu", "san", "il", "emeryville", "berkeley", "sf", "2017",
             "nyc", "link", "links", "30", "2018", "2019", "palo", "alto",
             "new", "california", "oakland", "bay", "pagejobs", "403",
             "signin", "jersey", "brooklyn", "manhattan", "langone", "sign",
             "nj", "nonloggedinwelcometitle", "save", "jobdetailsbuttontext",
             "salariesfind", "reviewsfind", "friendrefer", "searchmy",
             "locationsan", "pagejobs", "workday", "peoplesoft", "415",
             "94105", "uscasan", "usnynew", "timeout", "navigation", "albany",
             "cookies", "date", "browser", "searchjobs", "city", "area",
             "carequired", "application", "mateo", "copyright", "resume",
             "indeedcom", "keywords", "firefox", "texas", "job", "long island",
             "location south", "illinois"}
    return text.ENGLISH_STOP_WORDS.union(words)


def pickle_model(model_object, output):
    """
    Pickle a fitted model object
    :param model_object: A fitted model object.
    :param output: str, the name of the pkl file to use.
    :return: None, saves a pickle model object.
    """
    with open(output, 'wb') as f:
        pickle.dump(model_object, f)