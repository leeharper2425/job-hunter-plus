"""
Prediction engine for the flask web application
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB

def prediction(model, input):
    """
    Take a model and string input and return a city prediction.
    :param model: a fitted model object.
    :param input: str, the input from the web app.
    :return: str, the predicted city
    """
    classes = {0: "San Francisco, CA", 1: "New York, NY", 2: "Chicago, IL",
               3: "Austin, TX"}
    data = model.processing.transform(input)
    predicted_class = model.model.predict()
    return classes[predicted_class]
