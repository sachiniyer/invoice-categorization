"""
DynamoDB functions.

This module contains the functions that are used to interact with the dynamodb database.
"""

import os
from backend.types.errors import DBError, FileIDError, UsernameError
from backend.utils.batch import get_batch_job


def get_item_db(fileid, username, db_client):
    """
    Get owner function.

    Gets the owner for a given fileid
    """
    key = {"fileid": {"S": fileid}, "username": {"S": username}}

    try:
        response = db_client.get_item(
            TableName=os.environ.get("AWS_FILE_TABLE_NAME"), Key=key
        )
    except Exception as e:
        raise DBError(str(e))

    item = response.get("Item")
    if item:
        return {
            "fileid": fileid,
            "username": item["username"]["S"],
            "filename": item["filename"]["S"],
            "processed": item["processed"]["S"],
            "jobid": item["jobid"]["S"],
        }
    else:
        raise FileIDError(fileid)


def get_item_user(fileid, username, db_client):
    """
    Verify that a file exists in the db.

    Verifies that a file exists in the db for a given user
    """
    try:
        item = get_item_db(fileid, username, db_client)
    except Exception as e:
        raise e

    if item["username"] != username:
        raise UsernameError(username)

    return item


def create_item_db(fileid, username, filename, db_client):
    """
    Create item.

    Creates an item given a fileid and username
    """
    item = {
        "fileid": {"S": fileid},
        "username": {"S": username},
        "filename": {"S": filename},
        "processed": {"S": "not processed"},
        "jobid": {"S": "none"},
    }

    try:
        item = db_client.put_item(
            TableName=os.environ.get("AWS_FILE_TABLE_NAME"), Item=item
        )
        return item
    except Exception as e:
        raise DBError(str(e))


def delete_item_db(fileid, username, db_client):
    """
    Delete item db function.

    Deletes an item from dynamodb
    """
    key = {"fileid": {"S": fileid}, "username": {"S": username}}

    try:
        db_client.delete_item(TableName=os.environ.get("AWS_FILE_TABLE_NAME"), Key=key)
    except Exception as e:
        raise DBError(str(e))


def mark_item_db(fileid, jobid, username, db_client):
    """
    Mark Item function.

    Marks a file as processed in dynamo.
    """
    key = {"fileid": {"S": fileid}, "username": {"S": username}}

    try:
        response = db_client.update_item(
            TableName=os.environ.get("AWS_FILE_TABLE_NAME"),
            Key=key,
            ExpressionAttributeNames={"#processed": "processed"},
            UpdateExpression="SET #processed = :processed, jobid = :jobid",
            ExpressionAttributeValues={
                ":processed": {"S": "processing"},
                ":jobid": {"S": jobid},
            },
            ReturnValues="ALL_NEW",
        )
        return response
    except Exception as e:
        raise DBError(str(e))


def update_all_items(username, db_client, bedrock_client):
    """
    Update all items.

    Updates all items in the db with the latest status of the batch job
    """
    response = db_client.scan(
        TableName=os.environ.get("AWS_FILE_TABLE_NAME"),
        FilterExpression="#sk = :sk_value",
        ExpressionAttributeNames={"#sk": "username"},
        ExpressionAttributeValues={":sk_value": {"S": username}},
    )
    items = response.get("Items")
    for item in items:
        fileid = item.get("fileid").get("S")
        jobid = item.get("jobid").get("S")
        status = "not processed"
        if jobid != "none":
            status = (
                "processed"
                if get_batch_job(jobid, bedrock_client) == "Completed"
                else "processing"
            )
        db_client.update_item(
            TableName=os.environ.get("AWS_FILE_TABLE_NAME"),
            Key={"fileid": {"S": fileid}, "username": {"S": username}},
            UpdateExpression="SET #processed = :processed",
            ExpressionAttributeNames={"#processed": "processed"},
            ExpressionAttributeValues={":processed": {"S": status}},
        )
