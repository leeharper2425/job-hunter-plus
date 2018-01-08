import pandas as pd
import re
import numpy as np
from .utils import import_data
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

class Processing:
    """
    Provides methods for transforming text data.
    """

    def __init__(self, data=None, bucket=None, filename=None, stemlem=None):
        """
        Instantiate the preprocessing class.
        :param data: Pandas DataFrame containing data.
        :param bucket: str S3 bucket of data if applicable.
        :param filename: str, name of the data file, if applicable.
        :param stemlem: str, stemmatizer or lemmatizer to use.
        """
        self.model = None
        self.docs, self.labels = self._extract_info(data, bucket, filename)
        self.stemlem = stemlem
        self.transformed = self.docs
        self.vectorize = None

    def _extract_info(self, data, bucket, filename):
        """
        Load data and extract descriptions and state labels.
        :param data: Pandas DataFrame, or None.
        :param bucket: str or None, s3 bucket name.
        :param filename: str or None, the data filename.
        :return: Numpy arrays, the document and label arrays.
        """
        df = data if data else import_data(bucket, filename)
        replace_dict = {"CA": 0, "NY": 1, "IL": 2, "TX": 3}
        label =   df["location"].str.extract("(TX|CA|NY|IL)", expand=True)\
                                    .replace(replace_dict)
        return self._strip_format(df["job_description"]), label.as_matrix()

    @staticmethod
    def _strip_format(series):
        """
        Strip special HTML / unicode characters from text
        :param series: Pandas Series, the job description text
        :return: Numpy array, the cleaned up text
        """
        sm = series.as_matrix()
        for index, document in enumerate(series):
            sm[index] = re.sub('[^\w\s]|â', "", document, flags=re.UNICODE)
        return sm


    def snowball_stemmatizer(self):
        """
        Apply the snowball stemmatizer to the job description text.
        """
        stemmer = SnowballStemmer('english')
        self.transformed = ["" "".join([stemmer.stem(word) for word in text.split(" ")])
                            for text in self.docs]

    def porter_stemmatizer(self):
        """
        Apply the Porter stemmatizer to the job description text.
        """
        stemmer = PorterStemmer()
        self.transformed = ["" "".join([stemmer.stem(word) for word in text.split(" ")])
                            for text in self.docs]

    def wordnet_lemmatizer(self):
        """
        Apply the WordNet lemmatizer to the job description text.
        """
        lemma = WordNetLemmatizer()
        self.transformed = ["" "".join([lemma.lemmatize(word) for word in text.split(" ")])
                            for text in self.docs]

    def count_vectorize(self, min_df = 1,  max_df = 1.0):
        """
        Vectorize the corpus using Count Vectorization
        :param min_df: float or int, minimum document frequency of term.
        :param max_df: float or int, maximum document frequency of term.
        """


