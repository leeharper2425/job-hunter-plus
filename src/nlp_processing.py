"""
Class that makes up the natural language processing pipeline.
"""

import pandas as pd
import numpy as np
from .utils import get_stopwords
from .dataframe_processing import create_model_data
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer


class NLPProcessing:
    """
    Provides methods for transforming text data.
    """

    def __init__(self, stemlem="", min_df=1, max_df=1.0, num_cities=2,
                 n_grams=1, use_stopwords=True):
        """
        Instantiate the preprocessing class.
        :param stemlem: str or list, stemmatizer or lemmatizer to use.
        :param num_cities: int, the number of cities to retain.
        :param min_df: float or int, minimum document frequency of term.
        :param max_df: float or int, maximum document frequency of term.
        :param n_grams: int, n-gram to use
        :param use_stopwords: bool, whether to use stopwords or not
        """
        self.model = None
        self.stemlem = stemlem
        self.min_df = min_df
        self.max_df = max_df
        self.num_cities = num_cities
        self.vectorize = None
        self.n_grams = n_grams
        self.use_stopwords = use_stopwords
        self.done_stopwords = False

    def fit(self, data=None, bucket=None, filename=None):
        """
        Single function to fit the NLP transformations.
        Uses a user defined stemmer/lemmatizer with TFIDF vectorization.
        :param data: Pandas DataFrame containing data.
        :param bucket: str S3 bucket of data if applicable.
        :param filename: str, name of the data file, if applicable.
        """
        fit_array, _, _ = create_model_data(data, bucket, filename, self.num_cities)
        fit_array = self._stemlem(fit_array)
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
        doc_array = self._stemlem(doc_array)
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
        fit_array = self._stemlem(fit_array)
        self.tfidf_vectorize(fit_array)
        doc_array = self._stemlem(doc_array)
        x = self.vectorize.transform(doc_array)
        return x, y

    def _stemlem(self, text_array):
        """
        Controls the stemmatization/lemmatization process.
        Note that, if multiple methods are selected, lemmatization is performed
        before stemmatization.
        :param text_array: ndarray, the documents to process.
        :return: ndarray, the processed documents
        """
        self.done_stopwords = False
        if "wordnet" in self.stemlem:
            text_array = self.wordnet_lemmatizer(text_array)
        if "snowball" in self.stemlem:
            text_array = self.do_stem(text_array, SnowballStemmer("english"))
        elif "porter" in self.stemlem:
            text_array = self.do_stem(text_array, PorterStemmer())
        if self.stemlem == "":
            text_array = self.remove_stopwords(text_array)
        return text_array

    def wordnet_lemmatizer(self, documents):
        """
        Apply the WordNet lemmatizer to the job description text.
        This method lemmatizes using all 5 part of speech (POS) tags that
        the Wordnet lemmatizer supports
        :param documents: ndarry of the desctiptions to be lemmatized.
        :return list, the transformed data.
        """
        print("hello")
        wn = WordNetLemmatizer()
        stop_words = set()
        if self.use_stopwords:
            stop_words = get_stopwords()
        self.done_stopwords = True
        for pos_tag in ["a", "s", "r", "n", "v"]:
            documents = [" ".join([wn.lemmatize(word, pos=pos_tag)
                                   for word in text.split(" ")
                                   if word not in stop_words])
                         for text in documents]
        return documents

    def do_stem(self, documents, model):
        """
        Actually perform the stemming / lemmatizing and stop word removal.
        :param documents: the list of documents to transform.
        :param model: the instantiated transformation to use.
        :return: list, the transformed documents
        """
        stop_words = set()
        if self.use_stopwords and not self.done_stopwords:
            stop_words = get_stopwords()
        self.done_stopwords = True
        return [" ".join([model.stem(word) for word in text.split(" ")
                          if word not in stop_words])
                for text in documents]

    def remove_stopwords(self, documents):
        """
        Pure stopword removal without other text transformations
        :param documents: ndarray, the documents to transform
        :return: list, the documents without stop words
        """
        if not self.use_stopwords:
            return list(documents)
        stop_words = get_stopwords()
        return [word for word in documents if word not in stop_words]

    def count_vectorize(self, training_docs):
        """
        Vectorize the corpus using bag of words vectorization
        :param training_docs: Numpy array, the text to fit the vectorizer
        :return: SK Learn vectorizer object
        """
        # Instantiate class and fit vocabulary
        self.vectorize = CountVectorizer(training_docs, min_df=self.min_df,
                                         max_df=self.max_df,
                                         ngram_range=(self.n_grams, self.n_grams))
        self.vectorize.fit(training_docs)

    def tfidf_vectorize(self, training_docs):
        """
        Vectorize the corpus using TFIDF vectorization
        :param training_docs: Numpy array, the text to fit the vectorizer
        :return: SK Learn vectorizer object
        """
        # Instantiate class and fit vocabulary
        self.vectorize = TfidfVectorizer(training_docs, min_df=self.min_df,
                                         max_df=self.max_df,
                                         ngram_range=(self.n_grams, self.n_grams))
        self.vectorize.fit(training_docs)
