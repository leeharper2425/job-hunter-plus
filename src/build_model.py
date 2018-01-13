"""
Model building class
"""

from .nlp_processing import NLPProcessing
from .utils import import_data
import numpy as np
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import KFold


class JHPModel:
    """
    Class that is used to build the machine learning model for prediction.
    Can save model as a pickle file if desired
    Also contains methods to score and cross-validate the model
    """

    def __init__(self, model, stemlem="", min_df=1, max_df=1.0, num_cities=2,
                 n_grams=1, use_stopwords=True):
        """
        Instantiate the model building object.
        :param model: an instantiated SK-Learn model object
        :param stemlem: str, the stemming/lemmatizing methods to use.
        :param min_df: float, minimum document frequency of vocabulary term.
        :param max_df: float, maximum document frequency of vocabulary term.
        :param num_cities: int, number of classes to use.
        :param n_grams: int, the N-gram size to use.
        :param use_stopwords: bool, remove stop words or not.
        """
        self.pipeline = PipeLine(model, stemlem, min_df, max_df, num_cities,
                                 n_grams, use_stopwords)

    def fit(self, training=None, bucket=None, filename=None, output=None):
        """
        Fit the model.
        Fitting involves preprocessing and model fitting with SK-Learn.
        :param training: Pandas DataFrame containing data.
        :param bucket: str S3 bucket of data if applicable.
        :param filename: str, name of the data file, if applicable.
        :param output: str, the name of the .pkl file to create
        """
        df = import_data(bucket, filename) if training is None else training
        features, labels = self.pipeline.processing.fit_transform(df)
        self.pipeline.model.fit(features, labels)
        if output is not None:
            with open(output, 'wb') as f:
                pickle.dump(self.pipeline, f)

    def cross_validate(self, data=None, bucket=None, filename=None,
                       n_splits=5):
        """
        Quantify performance using K-fold cross-validation.
        Prints the mean model accuracy when completed
        :param n_splits: int, the number of folds to make.
        :param data: Pandas DataFrame containing data.
        :param bucket: str S3 bucket of data if applicable.
        :param filename: str, name of the data file, if applicable.
        """
        kf = KFold(n_splits, shuffle=True)
        df = import_data(bucket, filename) if data is None else data
        scores = []
        for train_index, test_index in kf.split(df):
            self.fit(training=df.iloc[train_index])
            X_test, y_test = self.pipeline.processing.transform(df.iloc[test_index])
            scores.append(self.pipeline.model.score(X_test, y_test))
        print("Model Accuracy = {}".format(np.array(scores).mean()))

    def show_informative_features(self, n=20):
        """
        Display the n most and least discriminatory features.
        Note: needs to use a model that contains a feature_importances_ method.
        Note: must be called on a fitted model.
        :param n: int, the number of most discriminatory features to show.
        """
        feature_names = self.pipeline.processing.vectorize.get_feature_names()
        coefs_names = sorted(zip(self.pipeline.model.feature_importances_,
                                 feature_names))
        top = zip(coefs_names[:n], coefs_names[:-(n + 1):-1])
        for (coef_1, fn_1), (coef_2, fn_2) in top:
            print("\t%.4f\t%-15s\t\t%.4f\t%-15s" % (coef_1, fn_1, coef_2, fn_2))


class PipeLine:
    """
    Class that creates the model building pipeline object.
    The object is a pipeline object that joins together the pre-processing
    and SK-Learn model classes.
    """

    def __init__(self, model, stemlem, min_df, max_df, num_cities, n_grams,
                 use_stopwords):
        """
        Instantiate the pipeline
        :param model: an instantiated SK-Learn model object
        :param stemlem: str, the stemming/lemmatizing methods to use.
        :param min_df: float, minimum document frequency of vocabulary term.
        :param max_df: float, maximum document frequency of vocabulary term.
        :param num_cities: int, number of classes to use.
        :param n_grams: int, the N-gram size to use.
        :param use_stopwords: bool, remove stop words or not.
        """
        self.processing = NLPProcessing(stemlem, min_df, max_df,
                                        num_cities, n_grams,
                                        use_stopwords)
        self.model = model
