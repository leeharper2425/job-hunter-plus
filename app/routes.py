"""
File containing the flask routes.
"""

from flask import Flask
from flask import render_template, request
from app import app
import pickle
from .predict import prediction

#Load in the model when the app initializes
with open("model.pkl", "rb") as f:
    model = pickle.load(f)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Job Hunter: Matching Data Scientists With Cities", data=None)

@app.route("/predict", methods=["POST"])
def analyze_text():
    doc = request.form['text1']
    pred = prediction(model, doc)
    return render_template('index.html', title="City Prediction", data=pred)