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
from backend.routes.files import (
    upload_handler,
    list_handler,
    delete_handler,
    get_handler,
    process_handler,
)

load_dotenv()


app = Flask(__name__)
Cors = CORS(
    app, resources={r"/*": {"origins": os.environ.get("ORIGIN", "localhost:3000")}}
)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "default_secret_key")
socketio = SocketIO(
    app, cors_allowed_origins=os.environ.get("ORIGIN", "localhost:3000")
)
session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_API_KEY"),
    aws_secret_access_key=os.environ.get("AWS_API_SECRET"),
    region_name=os.environ.get("AWS_REGION"),
)

db_client = session.client("dynamodb", region_name=os.environ.get("AWS_REGION"))
s3_client = session.client("s3", region_name=os.environ.get("AWS_REGION"))
bedrock_client = session.client("bedrock", region_name=os.environ.get("AWS_REGION"))
disable = os.environ.get("DISABLE", "False").lower() == "true"


@app.route("/", methods=["GET", "PUT", "POST", "PATCH", "DELETE"])
def root():
    """
    Root route.

    Handles all user management
    """
    return user_handler(request, disable, db_client, s3_client)


@socketio.on("message")
def handle_message(message):
    """
    Message route.

    Just echo's back message for status.
    """
    socketio.emit("message", message)


@socketio.on("upload")
def upload_file(message):
    """
    Upload route.

    Used for uploading a chunk of a file.
    """
    if disable:
        return
    upload_handler(message, socketio, db_client, s3_client)


@socketio.on("process")
def process_file(message):
    """
    Process route.

    Sends a file for processsing.
    """
    if disable:
        return
    process_handler(message, socketio, db_client, s3_client, bedrock_client)


@socketio.on("list")
def list_file(message):
    """
    List route.

    Lists all the files available to the user.
    """
    list_handler(message, socketio, db_client, bedrock_client)


@socketio.on("get")
def get_file(message):
    """
    Get route.

    Gets the content for a file.
    """
    get_handler(message, socketio, db_client, s3_client)


@socketio.on("delete")
def delete_file(message):
    """
    Delete route.

    Deletes a given file.
    """
    if disable:
        return
    delete_handler(message, socketio, db_client, s3_client)


if __name__ == "__main__":
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    socketio.run(app, debug=debug)
