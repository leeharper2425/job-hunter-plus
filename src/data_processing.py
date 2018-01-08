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

    def __init__(self, data=None, bucket=None, filename=None, stemlem=None,
                 num_cities=2):
        """
        Instantiate the preprocessing class.
        :param data: Pandas DataFrame containing data.
        :param bucket: str S3 bucket of data if applicable.
        :param filename: str, name of the data file, if applicable.
        :param stemlem: str, stemmatizer or lemmatizer to use.
        :param num_cities: int, the number of cities to retain.
        """
        self.model = None
        self.docs, self.labels = self._extract_info(data, bucket, filename,
                                                    num_cities)
        self.stemlem = stemlem
        self.transformed = self.docs
        self.vectorize = None

    def _extract_info(self, data, bucket, filename, num_cities):
        """
        Load data and extract descriptions and state labels.
        :param data: Pandas DataFrame, or None.
        :param bucket: str or None, s3 bucket name.
        :param filename: str or None, the data filename.
        :param num_cities: int, the number of cities to retain
        :return: Numpy arrays, the document and label arrays.
        """
        df = import_data(bucket, filename) if data is None else data
        replace_dict = {"CA": 0, "NY": 1, "IL": 2, "TX": 3}
        df["label"] = df["location"].str.extract("(TX|CA|NY|IL)", expand=True)\
                                        .replace(replace_dict)
        # Remove any null values from the important fields
        df = self._remove_null(df)
        df = self._remove_null(df, "label")
        # Retain a user decided number of cities.
        df = df[df["label"] < num_cities]
        return self._strip_format(df["job_description"]),\
               df["label"].as_matrix()

    @staticmethod
    def _remove_null(df, field="job_description"):
        """
        Remove any rows where the given field is null
        :param df: Pandas DataFrame
        :param field: str, the column to filter on
        :return: Pandas DataFrame, with nulls removed
        """
        return df[df[field].notnull()]

    @staticmethod
    def _strip_format(series):
        """
        Strip special HTML / unicode characters from text
        :param series: Pandas Series, the job description text
        :return: Numpy array, the cleaned up text
        """
        sm = series.as_matrix()
        for index, document in enumerate(series):
            document = document.replace("\n", " ")
            sm[index] = re.sub("[^\w\s]|â", "", document, flags=re.UNICODE)
        return sm

    def snowball_stemmatizer(self):
        """
        Apply the snowball stemmatizer to the job description text.
        """
        stemmer = SnowballStemmer('english')
        self.transformed = [" ".join([stemmer.stem(word) for word in text.split(" ")])
                            for text in self.docs]

    def porter_stemmatizer(self):
        """
        Apply the Porter stemmatizer to the job description text.
        """
        stemmer = PorterStemmer()
        self.transformed = [" " .join([stemmer.stem(word) for word in text.split(" ")])
                            for text in self.docs]

    def wordnet_lemmatizer(self):
        """
        Apply the WordNet lemmatizer to the job description text.
        """
        lemma = WordNetLemmatizer()
        self.transformed = [" ".join([lemma.lemmatize(word) for word in text.split(" ")])
                            for text in self.docs]

    def count_vectorize(self, min_df=1,  max_df=1.0):
        """
        Vectorize the corpus using bag of words vectorization
        :param min_df: float or int, minimum document frequency of term.
        :param max_df: float or int, maximum document frequency of term.
        :return: SK Learn vectorizer object
        """
        self.vectorize = CountVectorizer(self.transformed, stop_words="english",
                                         min_df=min_df, max_df=max_df)
        self.vectorize.fit(self.transformed)

    def tfidf_vectorize(self, min_df=1, max_df=1.0):
        """
        Vectorize the corpus using TFIDF vectorization
        :param min_df: float or int, minimum document frequency of term.
        :param max_df: float or int, maximum document frequency of term.
        :return: SK Learn vectorizer object
        """
        self.vectorize = TfidfVectorizer(self.transformed, stop_words="english",
                                         min_df=min_df, max_df=max_df)
        self.vectorize.fit(self.transformed)

    def fit(self):
        """
        Performs fitting for the final model, will be populated later
        """
        pass

    def transform(self):
        """
        Transforms the feature matrix based upon the model that is built.
        """
        pass
