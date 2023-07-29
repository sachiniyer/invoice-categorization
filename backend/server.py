#!/usr/bin/env python3
"""
Server for the invoice categorization application.

It allows interation with invoice categorization model.
"""

import os
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
import boto3

from backend.routes.users import user_handler

load_dotenv()


app = Flask(__name__)
Cors = CORS(app,
            resources={r"/*": {"origins": os.environ.get("ORIGIN",
                                                         "localhost:3000")}})

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
socketio = SocketIO(app,
                    cors_allowed_origins=os.environ.get("ORIGIN",
                                                        "localhost:3000"))
session = boto3.Session(
    aws_access_key_id=os.environ.get('AWS_API_KEY'),
    aws_secret_access_key=os.environ.get('AWS_API_SECRET'),
    region_name=os.environ.get('AWS_REGION'))
db_client = session.client('dynamodb')


@app.route('/', methods=['GET'])
def root():
    """
    Root route.

    It takes a POST request of an excel file and returns back data
    Takes in excel in form data with key "data"
    """
    return "<p>Invoice Categorization API</p>"


@app.route('/users', methods=['PUT', 'POST', 'PATCH', 'DELETE'])
def users():
    """
    Users route.

    Calls user handler and returns the response
    """
    return user_handler(request, db_client)


@socketio.on('message')
def handle_message(message):
    """
    Message route.

    Top level route to handle websocket messages
    """
    print('Received message:', message)
    socketio.emit('message', message)


if __name__ == '__main__':
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    socketio.run(app, debug=debug)
