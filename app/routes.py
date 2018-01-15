"""
File containing the flask routes.
"""

from flask import Flask
from flask import render_template, request
from app import app
import pickle

#Load in the model when the app initializes
with open("model.pkl") as f:
    model = pickle.load(f)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Job Hunter: Matching Data Scientists With Cities", data=None)

@app.route("/predict", methods=["POST"])
def analyze_text():
    #doc = nlp(request.form['text1'])
    #data = [(x.text, x.start, x.end) for x in doc.ents]
    return
    #return render_template('index.html', title='Named Entity Reco/gnition', data=data)