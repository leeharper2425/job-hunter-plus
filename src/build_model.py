"""
Model building class
"""

from .nlp_processing import NLPProcessing
from .utils import import_data
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix


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
        self.processing = NLPProcessing(stemlem, min_df, max_df,
                                        num_cities, n_grams,
                                        use_stopwords)
        self.model = model
        self.classes = num_cities

    def fit(self, training=None, bucket=None, filename=None):
        """
        Fit the model.
        Fitting involves preprocessing and model fitting with SK-Learn.
        :param training: Pandas DataFrame containing data.
        :param bucket: str S3 bucket of data if applicable.
        :param filename: str, name of the data file, if applicable.
        """
        df = import_data(bucket, filename) if training is None else training
        features, labels = self.processing.fit_transform(df)
        self.model.fit(features, labels)

    def predict(self, testing):
        """
        Make a prediction about testing data.
        :param testing: str, list or ndarray the documents to predict
        :return: list, a set of predictions
        """
        if isinstance(testing, str):
            testing = [testing]
        testing = self.processing.transform(testing)
        return self.model.predict(testing)

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
        confusion = np.zeros((self.classes, self.classes))
        for train_index, test_index in kf.split(df):
            self.fit(training=df.iloc[train_index])
            X_test, y_test = self.processing.transform(df.iloc[test_index])
            scores.append(self.model.score(X_test, y_test))
            confusion += confusion_matrix(y_test, self.model.predict(X_test))
        print("Model Accuracy = {}".format(np.array(scores).mean()))
        print("Confusion_Matrix:")
        print(confusion)

    def show_informative_features(self, n=20):
        """
        Display the n most and least discriminatory features.
        Note: needs to use a model that contains a feature_importances_ method.
        Note: must be called on a fitted model.
        :param n: int, the number of most discriminatory features to show.
        """
        feature_names = self.processing.vectorize.get_feature_names()
        coefs_names = sorted(zip(self.model.feature_importances_,
                                 feature_names))
        top = zip(coefs_names[:n], coefs_names[:-(n + 1):-1])
        for (coef_1, fn_1), (coef_2, fn_2) in top:
            print("\t%.4f\t%-15s\t\t%.4f\t%-15s" % (coef_1, fn_1, coef_2, fn_2))
