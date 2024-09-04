"""
File db.

Interacts with the dynamodb database and s3
bucket to upload and download files.
"""

import os
from flask import jsonify
import boto3
import json
import time
import random
from backend.types.errors import DBError, FileIDError, UsernameError, JSONError
from backend.utils.batch import create_batch_job
from backend.utils.db.userdb import get_user
from backend.utils.db.dynamo import (
    get_item_db,
    get_item_user,
    create_item_db,
    mark_item_db,
    delete_item_db,
    update_all_items,
)
from backend.utils.db.uploader import (
    elegible_chunks,
    convert_line,
    convert_to_prompts,
    upload_chunk,
)


def get_output_from_jsonl(body):
    """
    Get output from jsonl.

    Gets the model output from the batch jsonl file
    """
    res = []
    for line in body.split("\n"):
        if line != "":
            json_line = json.loads(line)
            res.append(json_line["modelOutput"]["content"][0]["text"])
    return res


def delete_item_s3(fileid, bucket, s3_client):
    """
    Delete item s3 function.

    Deletes an item from s3 given bucket and filename
    """
    try:
        s3_client.delete_object(Bucket=bucket, Key=f"input/{fileid}.jsonl")
        s3_client.delete_object(Bucket=bucket, Key=f"output/{fileid}.jsonl.out")
    except Exception as e:
        if not isinstance(e, s3_client.meta.client.exceptions.NoSuchKey):
            raise DBError(str(e))


def file_ingester(
    username, fileid, filename, chunk, chunk_number, total_chunks, db_client, s3_client
):
    """
    File db handler.

    Entrance for uploading a file
    """
    try:
        get_item_user(fileid, username, db_client)
    except Exception as e:
        if not isinstance(e, FileIDError):
            raise e
        else:
            create_item_db(fileid, username, filename, db_client)
    res = upload_chunk(
        fileid,
        chunk,
        chunk_number,
        total_chunks,
        os.environ.get("AWS_S3_UPLOAD_NAME"),
        s3_client,
    )
    return res


def list_ingester(username, db_client, bedrock_client):
    """
    List ingester.

    Get all fileids for a user using sort key.
    """
    try:
        update_all_items(username, db_client, bedrock_client)
        response = db_client.scan(
            TableName=os.environ.get("AWS_FILE_TABLE_NAME"),
            FilterExpression="#sk = :sk_value",
            ExpressionAttributeNames={"#sk": "username"},
            ExpressionAttributeValues={":sk_value": {"S": username}},
        )
        res = {}
        for i in response["Items"]:
            res[i["fileid"]["S"]] = {
                "filename": i["filename"]["S"],
                "processed": i["processed"]["S"],
            }
        return res
    except Exception as e:
        raise DBError(str(e))


def process_ingester(username, fileid, db_client, s3_client, bedrock_client):
    """
    Process ingester.

    Runs model on a file sitting in the db, and writes output back
    """
    get_item_user(fileid, username, db_client)
    jobid = create_batch_job(
        f"s3://{os.environ.get('AWS_S3_UPLOAD_NAME')}/input/{fileid}.jsonl",
        f"s3://{os.environ.get('AWS_S3_UPLOAD_NAME')}/output/",
        bedrock_client,
    )
    mark_item_db(fileid, jobid, username, db_client)


def get_ingester(username, fileid, socketio, db_client, s3_client):
    """
    Get ingester.

    Stream back chunks of a processed file.
    """
    get_item_user(fileid, username, db_client)

    try:
        db_item = get_item_db(fileid, username, db_client)
        jobid = db_item.get("jobid").split("/")[-1]
        obj = s3_client.get_object(
            Bucket=os.environ.get("AWS_S3_UPLOAD_NAME"),
            Key=f"output/{jobid}/{fileid}.jsonl.out",
        )
        body = obj["Body"].read().decode("utf-8")
        socketio.emit("download", {"data": get_output_from_jsonl(body)})
    except Exception as e:
        raise DBError(str(e))


def delete_ingester(username, fileid, db_client, s3_client):
    """
    Delete ingester.

    Delete a file if the user has access
    """
    get_item_user(fileid, username, db_client)
    delete_item_db(fileid, username, db_client)
    delete_item_s3(fileid, os.environ.get("AWS_S3_UPLOAD_NAME"), s3_client)


def delete_user_ingester(username, db_client, s3_client):
    """
    Delete user ingester.

    Mass delete all files for a user
    """
    list = list_ingester(username, db_client)
    if len(list) == 0:
        return
    for id, info in list[username].items():
        delete_ingester(username, id, db_client, s3_client)
