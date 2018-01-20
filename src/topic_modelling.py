"""
Code to perform topic modelling.
"""

from .nlp_processing import NLPProcessing
from sklearn. decomposition import NMF, LatentDirichletAllocation
import numpy as np
from .dataframe_processing import create_model_data

def topic_modelling(df, city, n_words=10, n_topics=10):
    """
    Performs topic modelling on the corpus of documents.
    :param df: Pandas DataFrame, the data to analyze.
    :param city: str, the city to analyze.
    :param n_words: int, the number of words per topic
    :return: n_topics: int, number of topics to use.
    """
    p = NLPProcessing(stemlem="", min_df=0.01, max_df=0.95, num_cities=4, n_grams=(1, 2), use_stopwords=True)
    model = NMF(n_components = n_topics)
    df = create_model_data(df[df["city_term"] == city], num_cities=4)
    features = p.fit_transform(df)
    column_names = np.array(p.vectorize.get_feature_names())
    model.fit(features).transform(features)
    h_sk= model.components_
    words_and_topics(h_sk, column_names, n_words)


def words_and_topics(h, words, num_words):
    """
    Find and print the most important words for each topic identified.
    :param h: ndarray, the H-matrix from non-negative matrix factorization.
    :param words: ndarray, the features.
    :param num_words: int, the number of words per topic
    :return:
    """
    topics = np.flip(h.argsort(axis = 1), axis=1)[:, :num_words]
    for topic in topics:
        print(words[topic])