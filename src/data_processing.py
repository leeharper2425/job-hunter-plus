import pandas as pd
import re
import numpy as np
from .utils import import_data
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer


class Processing:
    """
    Provides methods for transforming text data.
    """

    def __init__(self, stemlem=None, min_df=1, max_df=1.0, num_cities=2):
        """
        Instantiate the preprocessing class.
        :param stemlem: str, stemmatizer or lemmatizer to use.
        :param num_cities: int, the number of cities to retain.
        :param min_df: float or int, minimum document frequency of term.
        :param max_df: float or int, maximum document frequency of term.

        """
        self.model = None
        self.stemlem = stemlem
        self.min_df = min_df
        self.max_df = max_df
        self.num_cities = num_cities
        self.vectorize = None

    def fit(self, data=None, bucket=None, filename=None):
        """
        Single function to fit the NLP transformations.
        Uses a user defined stemmer/lemmatizer with TFIDF vectorization.
        :param data: Pandas DataFrame containing data.
        :param bucket: str S3 bucket of data if applicable.
        :param filename: str, name of the data file, if applicable.
        """
        df = import_data(bucket, filename) if data is None else data
        df - self._remove_null(df, ["job_description"])
        df = self._create_labels(df)
        df = df[df["label"] < self.num_cities]
        X = self._create_text_matrix(df["job_description"])
        y = df["label"]
        self.stemlem(X)
        self.tfidf_vectorize(X)

    @staticmethod
    def _remove_null(df, fields):
        """
        Remove any rows where the given fields are null
        :param df: Pandas DataFrame
        :param fields: list of str, the columns to filter on
        :return: Pandas DataFrame, with nulls removed
        """
        for column_name in fields:
            df = df[df[column_name].notnull()]
        return df

    @staticmethod
    def _create_labels(df):
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

    @staticmethod
    def _create_text_matrix(series):
        """
        Strip special characters and return cleaned text in a vector.
        :param series: Pandas Series, the job description text
        :return: Numpy array, the cleaned up text
        """
        sm = series.as_matrix()
        for index, document in enumerate(series):
            document = document.replace("\n", " ")
            sm[index] = re.sub("[^\w\s]|â", "", document, flags=re.UNICODE)
        return sm

    @staticmethod
    def snowball_stemmatizer(documents):
        """
        Apply the snowball stemmatizer to the job description text.
        """
        stemmer = SnowballStemmer('english')
        return [" ".join([stemmer.stem(word) for word in text.split(" ")])
                for text in documents]

    @staticmethod
    def porter_stemmatizer(documents):
        """
        Apply the Porter stemmatizer to the job description text.
        """
        stemmer = PorterStemmer()
        return [" " .join([stemmer.stem(word) for word in text.split(" ")])
                for text in documents]

    @staticmethod
    def wordnet_lemmatizer(documents):
        """
        Apply the WordNet lemmatizer to the job description text.
        """
        lemma = WordNetLemmatizer()
        return [" ".join([lemma.lemmatize(word) for word in text.split(" ")])
                for text in documents]

    def count_vectorize(self, training_docs):
        """
        Vectorize the corpus using bag of words vectorization
        :param training_docs: Numpy array, the text to fit the vectorizer
        :return: SK Learn vectorizer object
        """
        self.vectorize = CountVectorizer(training_docs, stop_words="english",
                                         min_df=self.min_df, max_df=self.max_df)
        self.vectorize.fit(training_docs)

    def tfidf_vectorize(self, training_docs):
        """
        Vectorize the corpus using TFIDF vectorization
        :param training_docs: Numpy array, the text to fit the vectorizer
        :return: SK Learn vectorizer object
        """
        self.vectorize = TfidfVectorizer(training_docs, stop_words="english",
                                         min_df=self.min_df, max_df=self.max_df)
        self.vectorize.fit(training_docs)



    def transform(self, X):
        """
        Single function to perform the NLP transformation
        :param X: the
        """
        pass
