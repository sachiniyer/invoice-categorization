"""
File route.

Handes the file route from websocket messages:
    create
    list
    get
    delete
"""

from backend.utils.jwt import verify_jwt
from backend.types.errors import CustomError
from backend.utils.args import parse_args, parse_json
from backend.utils.filedb import (file_ingester, list_ingester,
                                  delete_ingester)
from flask import jsonify
import secrets
import string


def generate_file_id(length=32):
    """
    Generate file id.

    Just generate a random token for file id
    """
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return token


def error_handler(e):
   """
   Error handler.

   handles errors and returns understandable error
   """
   if isinstance(e, CustomError):
      message, response = e.response()
      return jsonify({"status": False,
                      "error": message,
                      "response": response})
   return jsonify({"status": False,
                   "error": 'unexpected error',
                   "response": 500})


def upload_handler(message, socketio, db_client, s3_client):
    """
    Create function.

    Takes in a file and sends it to model for processing.
    """
    try:
        message_json = parse_json(message)
        args = parse_args(['filename', 'token', 'chunk',
                           'chunk_number', 'total_chunks'],
                          message_json)

        username = verify_jwt(args['token'])

        fileid = generate_file_id()
        if not (message_json.get('fileid') is None):
            fileid = message_json.get('fileid')

        res = file_ingester(username, fileid, args['filename'], args['chunk'],
                            args['chunk_number'], args['total_chunks'],
                            db_client, s3_client)
        finished = False
        if res == -1:
            finished = True
        socketio.emit(jsonify({
            'status': True,
            'finished': finished,
            'chunk_number': res,
            "response": 200
        }))

    except Exception as e:
        socketio.emit(error_handler(e))


def list_handler(message, socketio, db_client):
    """
    List function.

    Takes in a username and returns a list of files that are owned.
    """
    try:
        message_json = parse_json(message)
        args = parse_args(['token'], message_json)

        username = verify_jwt(args['token'])

        res = list_ingester(username, db_client)

        socketio.emit(jsonify({
            'status': True,
            'files': res,
            "response": 200
        }))
    except Exception as e:
        socketio.emit(error_handler(e))


def delete_handler(message, socketio, db_client, s3_client):
    """
    Delete function.

    Takes in a fileid and removes it from dynamo, and both s3 buckets
    """
    try:
        message_json = parse_json(message)
        args = parse_args(['token', 'fileid'], message_json)

        username = verify_jwt(args['token'])
        delete_ingester(username, args['fileid'], db_client, s3_client)
        socketio.emit(jsonify({
            'status': True,
            "response": 200
        }))
    except Exception as e:
        socketio.emit(error_handler(e))
