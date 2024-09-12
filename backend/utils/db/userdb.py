"""
User management.

Utility functions to interact with database.
    Create User and Password
    Verify User
    Delete User and Password
    Update Password
"""

import os
from backend.types.errors import UsernameError, DBError
from passlib.hash import pbkdf2_sha256


def get_user(username, db_client):
    """
    Create User.

    creates a user given a username and password.
    Only creates if username is not present.
    """
    key = {"username": {"S": username}}

    try:
        response = db_client.get_item(
            TableName=os.environ.get("AWS_USER_TABLE_NAME"), Key=key
        )
    except Exception as e:
        raise DBError(str(e))

    item = response.get("Item")
    if item:
        return {"username": username, "password": item["password"]["S"]}
    else:
        raise UsernameError(username)


def create_user(username, password, db_client):
    """
    Create a user.

    Only creates a new user if the username does not exist
    """
    found = None

    try:
        found = get_user(username, db_client)
    except Exception as e:
        if not isinstance(e, UsernameError):
            raise e

    if found:
        raise UsernameError(username)

    item = {"username": {"S": username}, "password": {"S": password}}

    try:
        item = db_client.put_item(
            TableName=os.environ.get("AWS_USER_TABLE_NAME"), Item=item
        )
        return item
    except Exception as e:
        raise DBError(str(e))


def delete_user(username, db_client):
    """
    Delete user.

    Deletes a user given a username
    """
    try:
        get_user(username, db_client)
    except Exception as e:
        raise e

    key = {"username": {"S": username}}

    try:
        response = db_client.delete_item(
            TableName=os.environ.get("AWS_USER_TABLE_NAME"), Key=key
        )
        return response
    except Exception as e:
        raise DBError(str(e))


def update_user(username, password, db_client):
    """
    Update user.

    Updates a user's password
    """
    try:
        get_user(username, db_client)
    except Exception as e:
        raise e

    key = {"username": {"S": username}}

    try:
        response = db_client.update_item(
            TableName=os.environ.get("AWS_USER_TABLE_NAME"),
            Key=key,
            UpdateExpression="SET password = :password",
            ExpressionAttributeValues={":password": {"S": password}},
            ReturnValues="ALL_NEW",
        )
        return response
    except Exception as e:
        raise DBError(str(e))


def verify_user(username, password, db_client):
    """
    Verify user.

    Checks whether a username and password matches.
    """
    try:
        db_response = get_user(username, db_client)
    except Exception as e:
        raise e
    return pbkdf2_sha256.verify(password, db_response["password"])
