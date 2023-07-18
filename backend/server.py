#!/usr/bin/env python3
"""
Server for the invoice categorization application.

It allows interation with invoice categorization model.
"""

from flask import Flask, request
from flask_cors import CORS
from excel import to_pandas

app = Flask(__name__)
Cors = CORS(app, resources={r"/*": {"origins": "localhost:8080"}})


@app.route("/", methods=['GET', 'POST'])
def root():
    """
    Root route.

    It takes a POST request of an excel file and returns back data
    Takes in excel in form data with key "data"
    """
    if request.method == 'POST':
        file = request.files['data']
        df = to_pandas(file)
        return df.to_json(orient='records')
    return "Invoice Categorization API"


@app.route("/hello", methods=['GET', 'POST'])
def hello():
    """
    Hello route.

    Responds with a simple hello world
    """
    return "Hello World"
