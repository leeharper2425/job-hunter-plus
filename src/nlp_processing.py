import pandas as pd
import numpy as np
from .utils import create_model_data, stop_word_addition
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer


class Processing:
    """
    Provides methods for transforming text data.
    """

    def __init__(self, stemlem="", min_df=1, max_df=1.0, num_cities=2, n_grams=1):
        """
        Instantiate the preprocessing class.
        :param stemlem: str or list, stemmatizer or lemmatizer to use.
        :param num_cities: int, the number of cities to retain.
        :param min_df: float or int, minimum document frequency of term.
        :param max_df: float or int, maximum document frequency of term.
        :param n_grams: int, n-gram to use
        """
        self.model = None
        self.stemlem = stemlem
        self.min_df = min_df
        self.max_df = max_df
        self.num_cities = num_cities
        self.vectorize = None
        self.n_grams = n_grams

    def fit(self, data=None, bucket=None, filename=None):
        """
        Single function to fit the NLP transformations.
        Uses a user defined stemmer/lemmatizer with TFIDF vectorization.
        :param data: Pandas DataFrame containing data.
        :param bucket: str S3 bucket of data if applicable.
        :param filename: str, name of the data file, if applicable.
        """
        fit_array, _, _ = create_model_data(data, bucket, filename, self.num_cities)
        fit_array = self._do_stemlem(fit_array)
        self.tfidf_vectorize(fit_array)

    def transform(self, data=None, bucket=None, filename=None):
        """
        Single function to apply the NLP transformation.
        :param data: Pandas DataFrame containing data.
        :param bucket: str S3 bucket of data if applicable.
        :param filename: str, name of the data file, if applicable.
        :return: ndarrays for the feature and label matrices
        """
        if self.vectorize is None:
            raise AttributeError("Must fit a processing pipeline before calling\
                                 the transform method")
        _, doc_array, y = create_model_data(data, bucket, filename,
                                            self.num_cities)
        doc_array = self._do_stemlem(doc_array)
        x = self.vectorize.transform(doc_array)
        return x, y

    def fit_transform(self, data=None, bucket=None, filename=None):
        """
        Single function to fit model and apply it in one go.
        :param data: Pandas DataFrame containing data.
        :param bucket: str S3 bucket of data if applicable.
        :param filename: str, name of the data file, if applicable.
        :return: ndarrays for the feature and label matrices
        """
        fit_array, doc_array, y = create_model_data(data, bucket, filename,
                                                    self.num_cities)
        fit_array = self._do_stemlem(fit_array)
        self.tfidf_vectorize(fit_array)
        doc_array = self._do_stemlem(doc_array)
        x = self.vectorize.transform(doc_array)
        return x, y

    def _do_stemlem(self, text_array):
        """
        Controls the stemmatization/lemmatization process.
        Note that, if multiple methods are selected, lemmatization is performed
        before stemmatization.
        :param text_array: ndarray, the documents to process.
        :return: ndarray, the processed documents
        """
        if "wordnet" in self.stemlem:
            text_array = self.wordnet_lemmatizer(text_array)
        if "snowball" in self.stemlem:
            text_array = self.snowball_stemmatizer(text_array)
        elif "porter" in self.stemlem:
            text_array = self.porter_stemmatizer(text_array)
        if self.stemlem == "":
            text_array = list(text_array)
        return text_array

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
        stop_words = stop_word_addition()

        self.vectorize = CountVectorizer(training_docs, stop_words=stop_words,
                                         min_df=self.min_df, max_df=self.max_df)
        self.vectorize.fit(training_docs)

    def tfidf_vectorize(self, training_docs):
        """
        Vectorize the corpus using TFIDF vectorization
        :param training_docs: Numpy array, the text to fit the vectorizer
        :return: SK Learn vectorizer object
        """
        stop_words = stop_word_addition()
        self.vectorize = TfidfVectorizer(training_docs, stop_words=stop_words,
                                         min_df=self.min_df, max_df=self.max_df,
                                         ngram_range=(self.n_grams, self.n_grams))
        self.vectorize.fit(training_docs)
