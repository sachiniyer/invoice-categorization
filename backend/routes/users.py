"""
User route.

Handles the user route:
  PUT
  POST
  PATCH
  DELETE
"""

from backend.utils.userdb import create_user, delete_user, update_user, verify_user
from backend.utils.jwt import generate_jwt, verify_jwt
from backend.types.errors import UsernameError, JWTError, DBError
from flask import jsonify


def error_handler(e):
   """
   Error handler.

   handles errors and returns understandable error
   """
   if isinstance(e, UsernameError):
      return jsonify({"status": False,
                      "error": "Username invalid"}), 400
   if isinstance(e, JWTError):
      if e.timeout:
         return jsonify({"status": False,
                         "error": "JWT timed out"}), 400
      return jsonify({"status": False,
                      "error": "Error processing JWT"}), 400
   if isinstance(e, DBError):
      return jsonify({"status": False,
                      "error": "Error with Database"}), 500


def user_put(username, password, db_client):
   """
   Put method.

   Creates a user if it does not exist
   """
   try:
      create_user(username, password, db_client)
      return jsonify({"status": True}), 200
   except Exception as e:
      return error_handler(e)


def user_post(username, password, db_client):
   """
   Post method.

   Logs user in and gives jwt with successful password
   """
   try:
      if verify_user(username, password, db_client):
         jwt = generate_jwt(username)
         return jsonify({"status": True,
                         "jwt": jwt}), 200
      return jsonify({"status": False,
                      "error": "Password invalid"}), 400
   except Exception as e:
      return error_handler(e)


def user_patch(jwt, password, db_client):
   """
   Patch method.

   Updates a password for a user
   """
   try:
      username = verify_jwt(jwt)
      update_user(username, password, db_client)
      return jsonify({"status": True}), 200
   except Exception as e:
      print(e)
      return error_handler(e)


def user_delete(jwt, db_client):
   """
   Delete method.

   Deletes a user
   """
   try:
      username = verify_jwt(jwt)
      delete_user(username, db_client)
      return jsonify({"status": True}), 200
   except Exception as e:
      return error_handler(e)


def user_handler(request, db_client):
   """
   User handler.

   This handles all the requests for the user
   """
   if not request.is_json:
      return jsonify({"error": "Not JSON"}), 400

   data = request.json

   if request.method == 'PUT':
      username = data.get('username')
      password = data.get('password')
      if (not username) or (not password):
         return jsonify({"status": False,
                         "error": (f'username present: {username != None},'
                                   f'password present: {password != None}')})
      return user_put(username, password, db_client)

   if request.method == 'POST':
      username = data.get('username')
      password = data.get('password')
      if (not username) or (not password):
         return jsonify({"status": False,
                         "error": (f'username present: {username != None},'
                                   f'password present: {password != None}')})
      return user_post(username, password, db_client)

   if request.method == 'PATCH':
      token = data.get('token')
      password = data.get('password')
      if (not token) or (not password):
         return jsonify({"status": False,
                         "error": (f'token present: {token != None},'
                                   f'password present: {password != None}')})
      return user_patch(token, password, db_client)

   if request.method == 'DELETE':
      token = data.get('token')
      if not token:
         return jsonify({"status": False,
                         "error": f'token present: {token != None}'})
      return user_delete(token, db_client)
