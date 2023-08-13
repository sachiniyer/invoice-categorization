"""
User route.

Handles the user route:
  PUT
  POST
  PATCH
  DELETE
"""

from backend.utils.db.userdb import (create_user, delete_user,
                                     update_user, verify_user)
from backend.utils.args import parse_args
from backend.utils.jwt import generate_jwt, verify_jwt
from backend.utils.db.filedb import delete_user_ingester
from backend.types.errors import (CustomError, PasswordError,
                                  JSONError, ArgError)
from flask import jsonify
from passlib.hash import pbkdf2_sha256


def error_handler(e):
   """
   Error handler.

   handles errors and returns understandable error
   """
   if isinstance(e, CustomError):
      message, response = e.response()
      return jsonify({"status": False,
                      "error": message}), response
   return jsonify({"status": False,
                   "error": 'unexpected error'}), 500


def user_put(username, password, db_client):
   """
   Put method.

   Creates a user if it does not exist
   """
   password = pbkdf2_sha256.hash(password)
   create_user(username, password, db_client)
   return jsonify({"status": True}), 200


def user_post_login(username, password, db_client):
   """
   Post method.

   Logs user in and gives jwt with successful password
   """
   if verify_user(username, password, db_client):
      jwt = generate_jwt(username)
      return jsonify({"status": True,
                      "jwt": jwt}), 200
   raise PasswordError(f'{password} is invalid')


def user_post_token(token):
   """
   Post method.

   Verifies jwt
   """
   verify_jwt(token)
   return jsonify({"status": True}), 200


def user_patch(jwt, password, db_client):
   """
   Patch method.

   Updates a password for a user
   """
   username = verify_jwt(jwt)
   password = pbkdf2_sha256.hash(password)
   update_user(username, password, db_client)
   return jsonify({"status": True}), 200


def user_delete(jwt, db_client, s3_client):
   """
   Delete method.

   Deletes a user
   """
   username = verify_jwt(jwt)
   delete_user_ingester(username, db_client, s3_client)
   delete_user(username, db_client)
   return jsonify({"status": True}), 200


def user_handler(request, db_client, s3_client):
   """
   User handler.

   This handles all the requests for the user
   """
   try:
      if not request.is_json:
         raise JSONError('json invalid', True)

      data = request.json
      if request.method == 'GET':
         return "<p>Invoice Categorization API</p>"

      if request.method == 'PUT':
         args = parse_args(['username', 'password'], data)
         return user_put(args['username'], args['password'], db_client)

      if request.method == 'POST':
         try:
            args = parse_args(['username', 'password'], data)
            return user_post_login(args['username'],
                                   args['password'],
                                   db_client)
         except ArgError:
            args = parse_args(['token'], data)
            return user_post_token(args['token'])

      if request.method == 'PATCH':
         args = parse_args(['token', 'password'], data)
         return user_patch(args['token'], args['password'], db_client)

      if request.method == 'DELETE':
         args = parse_args(['token'], data)
         return user_delete(args['token'], db_client, s3_client)

   except Exception as e:
      return error_handler(e)
