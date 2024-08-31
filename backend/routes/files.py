"""
File route.

Handes the file route from websocket messages:
    create
    list
    get
    delete
"""

import json
import secrets
import string

from flask import jsonify

from backend.types.errors import CustomError
from backend.utils.args import parse_args, parse_json
from backend.utils.db.filedb import (
    file_ingester,
    list_ingester,
    delete_ingester,
    get_ingester,
    process_ingester,
)
from backend.utils.jwt import verify_jwt


def generate_file_id(length=32):
    """
    Generate file id.

    Just generate a random token for file id
    """
    alphabet = string.ascii_letters + string.digits
    token = "".join(secrets.choice(alphabet) for _ in range(length))
    return token


def error_handler(e):
    """
    Error handler.

    handles errors and returns understandable error
    """
    if isinstance(e, CustomError):
        message, response = e.response()
        return jsonify({"status": False, "error": message, "response": response})
    return jsonify({"status": False, "error": "unexpected error", "response": 500})


def upload_handler(message, socketio, db_client, s3_client):
    """
    Create function.

    Takes in a file and sends it to model for processing.
    """
    try:
        message_json = parse_json(message)
        args = parse_args(
            ["filename", "token", "chunk", "chunk_number", "total_chunks"], message_json
        )

        username = verify_jwt(args["token"])

        fileid = generate_file_id()
        if not (message_json.get("fileid") is None):
            fileid = message_json.get("fileid")

        res = file_ingester(
            username,
            fileid,
            args["filename"],
            args["chunk"],
            args["chunk_number"],
            args["total_chunks"],
            db_client,
            s3_client,
        )
        finished = False
        if res == -1:
            finished = True
        socketio.emit(
            "upload",
            json.dumps(
                {
                    "status": True,
                    "finished": finished,
                    "chunk_number": res,
                    "response": 200,
                }
            ),
        )

    except Exception as e:
        socketio.emit("upload", error_handler(e))


def list_handler(message, socketio, db_client):
    """
    List function.

    Takes in a username and returns a list of files that are owned.
    """
    try:
        args = parse_args(["token"], message)

        username = verify_jwt(args["token"])

        res = list_ingester(username, db_client)

        socketio.emit(
            "list", json.dumps({"status": True, "files": res, "response": 200})
        )
    except Exception as e:
        socketio.emit("list", json.dumps(error_handler(e)))


def process_handler(message, socketio, db_client, s3_client):
    """
    Process function.

    Takes a file id and runs the model on that file and writes the output out.
    """
    try:
        message_json = parse_json(message)
        args = parse_args(["token", "fileid"], message_json)

        username = verify_jwt(args["token"])

        socketio.emit(
            "process",
            jsonify(
                {
                    "status": True,
                    "finished": False,
                    "fileid": args["fileid"],
                    "response": 200,
                }
            ),
        )

        process_ingester(username, args["fileid"], db_client, s3_client)

        socketio.emit(
            "process",
            jsonify(
                {
                    "status": True,
                    "finished": True,
                    "fileid": args["fileid"],
                    "response": 200,
                }
            ),
        )

    except Exception as e:
        socketio.emit("process", error_handler(e))


def get_handler(message, socketio, db_client, s3_client):
    """
    Get function.

    Takes in a fileid and streams back the chunks of the file
    """
    try:
        message_json = parse_json(message)
        args = parse_args(["token", "fileid"], message_json)

        username = verify_jwt(args["token"])
        get_ingester(username, args["fileid"], socketio, db_client, s3_client)
        socketio.emit(
            "get", jsonify({"status": True, "response": 200, "finished": True})
        )

    except Exception as e:
        socketio.emit("get", error_handler(e))


def delete_handler(message, socketio, db_client, s3_client):
    """
    Delete function.

    Takes in a fileid and removes it from dynamo, and both s3 buckets
    """
    try:
        message_json = parse_json(message)
        args = parse_args(["token", "fileid"], message_json)

        username = verify_jwt(args["token"])
        delete_ingester(username, args["fileid"], db_client, s3_client)
        socketio.emit("delete", jsonify({"status": True, "response": 200}))
    except Exception as e:
        socketio.emit("delete", error_handler(e))
