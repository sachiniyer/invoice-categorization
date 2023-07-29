"""
User management.

Utility functions to interact with database.
    Create User and Password
    Verify User
    Delete User and Password
    Update Password
"""
import os
import hmac
from types.errors import UsernameError


def get_user(username, db_client):
    """
    Create User.

    creates a user given a username and password.
    Only creates if username is not present.
    """
    key = {
        'username': {
            'S': username
        }
    }

    try:
        response = db_client.get_item(
            TableName=os.enviorn.get('AWS_TABLE_NAME'),
            Key=key
        )

        item = response.get('item')
        if item:
            return {
                'username': username,
                'password': item['password']['S']
            }
        else:
            return None

    except Exception as e:
        return e


def create_user(username, password, db_client):
    """
    Create a user.

    Only creates a new user if the username does not exist
    """
    try:
        db_response = get_user(username, db_client)
    except Exception as e:
        return e

    if db_response:
        return UsernameError("username")

    item = {
        'username': {
            'S': username
        },
        'password': {
            'S': password
        }
    }

    try:
        item = db_client.put_item(
            TableName=os.environ.get('AWS_TABLE_NAME'),
            item=item
        )
        return item
    except Exception as e:
        return e


def delete_user(username, db_client):
    """
    Delete user.

    Deletes a user given a username
    """
    try:
        db_response = get_user(username, db_client)
    except Exception as e:
        return e

    if not db_response:
        return UsernameError("username")

    key = {
        'username': {
            'S': username
        }
    }

    try:
        response = db_client.delete_item(
            TableName=os.environ.get('AWS_TABLE_NAME'),
            Key=key
        )
        return response
    except Exception as e:
        return e


def update_user(username, password, db_client):
    """
    Update user.

    Updates a user's password
    """
    try:
        db_response = get_user(username, db_client)
    except Exception as e:
        return e

    if not db_response:
        return UsernameError("username")

    key = {
        'username': {
            'S': username
        }
    }

    expression = "SET password = :val"

    value = {
        ':val': password
    }

    try:
        response = db_client.update_item(
            TableName=os.environ.get('AWS_TABLE_NAME'),
            Key=key,
            UpdateExpression=expression,
            ExpressionAttributeValues=value,
            ReturnValues="UPDATED_NEW"
        )
        return response
    except Exception as e:
        return e


def verify_user(username, password, db_client):
    """
    Verify user.

    Checks whether a username and password matches.
    """
    try:
        db_response = get_user(username, db_client)
    except Exception as e:
        return e

    if not db_response:
        return UsernameError("username")

    return hmac.compare_digest(password, db_response['password'])
