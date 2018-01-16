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
    probs = model.model.predict_proba(data)[0]
    output = [(v, probs[k]) for k, v in classes.items() if k < len(probs)]
    output = sorted(output, key=lambda x: x[1], reverse=True)
    return [(tup[0], str.format("{0:.4f}", tup[1])) for tup in output]
