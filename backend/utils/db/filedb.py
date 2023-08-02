"""
File db.

Interacts with the dynamodb database and s3
bucket to upload and download files.
"""
import os
from flask import jsonify
from backend.types.errors import DBError, FileIDError, UsernameError, JSONError
from backend.utils.model.model import model_handler

ongoing_uploads = {}


def get_item_db(fileid, db_client):
    """
    Get owner function.

    Gets the owner for a given fileid
    """
    key = {
        'fileid': {
            'S': fileid
        }
    }

    try:
        response = db_client.get_item(
            TableName=os.environ.get('AWS_FILE_TABLE_NAME'),
            Key=key
        )
    except Exception as e:
        raise DBError(str(e))

    item = response.get('Item')
    if item:
        return {
            'fileid': fileid,
            'username': item['username']['S'],
            'filename': item['filename']['S']
        }
    else:
        raise FileIDError(fileid)


def get_item_user(fileid, username, db_client):
    """
    Get item user function.

    Verify user or throw UsernameError
    """
    real_username = get_item_db('username')
    if real_username['username'] is not username:
        raise UsernameError(username)
    return real_username


def create_item_db(fileid, username, filename, db_client):
    """
    Create item.

    Creates an item given a fileid and username
    """
    item = {
        'fileid': {
            'S': fileid
        },
        'username': {
            'S': username
        },
        'filename': {
            'S': filename
        },
        'processed': {
            'BOOL': False
        }
    }

    try:
        item = db_client.put_item(
            TableName=os.environ.get('AWS_FILE_TABLE_NAME'),
            Item=item
        )
        return item
    except Exception as e:
        raise DBError(str(e))


def delete_item_db(fileid, db_client):
    """
    Delete item db function.

    Deletes an item from dynamodb
    """
    key = {
        'fileid': {
            'S': fileid
        }
    }

    try:
        db_client.delete_item(
            TableName=os.environ.get('AWS_FILE_TABLE_NAME'),
            Key=key
        )
    except Exception as e:
        raise DBError(str(e))


def mark_item_db(fileid, username, db_client):
    """
    Mark Item function.

    Marks a file as processed in dynamo.
    """
    try:
        get_item_user(fileid, username, db_client)
    except Exception as e:
        raise e

    key = {
        'fileid': {
            'S': fileid
        }
    }

    try:
        response = db_client.update_item(
            TableName=os.environ.get('AWS_FILE_TABLE_NAME'),
            Key=key,
            UpdateExpression='SET processed = :processed',
            ExpressionAttributeValues={
                ':processed': {
                    'BOOL': True
                }
            },
            ReturnValues='ALL_NEW'
        )
        return response
    except Exception as e:
        raise DBError(str(e))


def delete_item_s3(fileid, bucket, s3_client):
    """
    Delete item s3 function.

    Deletes an item from s3 given bucket and filename
    """
    try:
        s3_client.delete_object(
            Bucket=bucket,
            Key=fileid
        )
    except Exception as e:
        raise DBError(str(e))


def get_chunk_uploader(fileid, bucket, total_chunks, s3_client):
    """
    Get chunk uploader function.

    Get multipart uploader from dictionary or creates one.
    """
    if fileid not in ongoing_uploads:
        try:
            response = s3_client.create_multipart_uploader(
                Bucket=bucket,
                Key=fileid
            )

            ongoing_uploads[fileid] = {
                'uploader': response['UploadId'],
                'set': {}
            }
        except Exception as e:
            raise DBError(str(e))
    return ongoing_uploads[fileid]


def send_chunk(socketio, chunk_data, chunk_number, num_chunks):
    """
    Send chunk.

    Sends a chunk of data back to the client
    """
    try:
        json = jsonify('status', True,
                       'response', 200,
                       'finished', False,
                       'chunk', chunk_data,
                       'chunk_number', chunk_number,
                       'total_chunks', num_chunks)
        socketio.emit('get', json)
    except Exception as e:
        raise JSONError(str(e))


def upload_chunk(fileid, chunk, chunk_number,
                 total_chunks, bucket, s3_client):
    """
    Upload Chunk function.

    Takes a chunk, figures out if there is an uploader (creates if otherwise)
    and uploads chunk
    """
    uploader = get_chunk_uploader(fileid, bucket, s3_client)
    try:
        response = s3_client.upload_part(
            Bucket=bucket,
            Key=fileid,
            PartNumber=chunk_number,
            UploadId=uploader['uploader'],
            Body=chunk
        )
        uploader['set'].append({
            'PartNumber': chunk_number,
            'ETag': response['ETag']
        })
    except Exception as e:
        raise DBError(str(e))

    if len(uploader['set']) == total_chunks:
        try:
            s3_client.complete_multipart_upload(
                Bucket=bucket,
                Key=fileid,
                UploadId=uploader['uploader'],
                MultipartUpload={
                    'Parts': uploader['set']
                }
            )
        except Exception as e:
            raise DBError(str(e))
        return -1
    return chunk_number


def download_file(fileid, s3_client):
    """
    Download file.

    Downloads file to run model on.
    """
    try:
        path = os.path.join(os.enivorn.get('MODEL_DOWNLOAD_PATH'), fileid)
        s3_client.download_file(
            os.environ.get('AWS_S3_UPLOAD_NAME'),
            fileid,
            path
        )
    except Exception as e:
        raise DBError(str(e))


def upload_file(fileid, s3_client):
    """
    Upload file.

    Uploads file that has been modified
    """
    try:
        path = os.path.join(os.enivorn.get('MODEL_UPLOAD_PATH'), fileid)
        s3_client.upload_file(
            path,
            os.environ.get('AWS_S3_UPLOAD_NAME'),
            fileid
        )
    except Exception as e:
        raise DBError(str(e))


def file_ingester(username, fileid, filename, chunk, chunk_number,
                  total_chunks, db_client, s3_client):
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
            create_item_db(fileid, filename, username, db_client)
    res = upload_chunk(fileid, chunk, chunk_number,
                       total_chunks, os.environ.get('AWS_S3_UPLOAD_NAME'),
                       s3_client)
    return res


def list_ingester(username, db_client):
    """
    List ingester.

    Get all fileids for a user using sort key.
    """
    try:
        response = db_client.scan(
            TableName=os.environ.get('AWS_FILE_TABLE_NAME'),
            FilterExpression='#sk = :sk_value',
            ExpressionAttributeNames={
                '#sk': 'username'
            },
            ExpressionAttributeValues={
                ':sk_value': {
                    'S': username
                }
            }
        )
        res = {}
        for i in response['Items']:
            res[i['fileid']['S']] = {
                'filename': i['filename']['S'],
                'processed': i['processed']['BOOL']
            }
        return res
    except Exception as e:
        raise DBError(str(e))


def process_ingester(username, fileid, db_client, s3_client):
    """
    Process ingester.

    Runs model on a file sitting in the db, and writes output back
    """
    get_item_user(fileid, username, db_client)
    download_file(fileid, s3_client)
    model_handler(fileid)
    upload_file(fileid, s3_client)
    mark_item_db(fileid, db_client)


def get_ingester(username, fileid, socketio, db_client, s3_client):
    """
    Get ingester.

    Stream back chunks of a processed file.
    """
    get_item_user(fileid, username, db_client)

    try:
        obj = s3_client.Object(os.environ.get('AWS_S3_PROCESSED_NAME'), fileid)
    except Exception as e:
        raise DBError(str(e))

    try:
        obj.metadata
    except s3_client.meta.client.exceptions.NoSuchKey:
        raise FileIDError(fileid)

    try:
        object_size = obj.content_length
        chunk_size = os.enviorn.get('CHUNK_SIZE')
        num_chunks = (object_size // chunk_size) + 1

        byte_range = 'bytes=0-' + str(chunk_size - 1)

        for chunk_number in range(num_chunks):
            if chunk_number > 0:
                byte_range = (f'bytes={str(chunk_number * chunk_size)}-'
                              f'{str(((chunk_number + 1) * chunk_size) - 1)}')
                response = obj.get(Range=byte_range)
                chunk_data = response['Body'].read()
                socketio.emit('get',)
                send_chunk(socketio, chunk_data, chunk_number, num_chunks)
    except Exception as e:
        if isinstance(e, JSONError):
            raise e
        raise DBError(str(e))


def delete_ingester(username, fileid, db_client, s3_client):
    """
    Delete ingester.

    Delete a file if the user has access
    """
    get_item_user(fileid, username, db_client)
    delete_item_db(fileid, db_client)
    delete_item_s3(fileid, os.enviorn.get('AWS_S3_UPLOAD_NAME'), s3_client)
    delete_item_s3(fileid, os.enviorn.get('AWS_S3_PROCESSED_NAME'), s3_client)


def delete_user_ingester(username, db_client, s3_client):
    """
    Delete user ingester.

    Mass delete all files for a user
    """
    list = list_ingester(username, db_client)
    for id, info in list[username].items():
        delete_ingester(username, id, db_client, s3_client)
