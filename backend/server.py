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
from backend.routes.files import upload_handler, list_handler

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
s3_client = session.client('s3')


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
    return user_handler(request, db_client, s3_client)


@socketio.on('message')
def handle_message(message):
    """
    Message route.

    Just echo's back message for status.
    """
    socketio.emit('message', message)


@socketio.on('upload')
def upload_file(message):
    """
    Upload route.

    Used for uploading a chunk of a file.
    """
    upload_handler(message, socketio, db_client, s3_client)


@socketio.on('process')
def process_file(message):
    """
    Process route.

    Sends a file for processsing.
    """
    socketio.emit('process', message)


@socketio.on('list')
def list_file(message):
    """
    List route.

    Lists all the files available to the user.
    """
    list_handler(message, socketio, db_client)


@socketio.on('get')
def get_file(message):
    """
    Get route.

    Gets the content for a file.
    """
    socketio.emit('get', message)


@socketio.on('delete')
def delete_file(message):
    """
    Delete route.

    Deletes a given file.
    """
    socketio.emit('delete', message)


if __name__ == '__main__':
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    socketio.run(app, debug=debug)
