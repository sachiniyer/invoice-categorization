"""
Uploader.

This module contains the functions that are used to upload chunks of data to
"""

import os
import json
import pandas as pd
from backend.types.errors import DBError

ongoing_uploads = {}


def get_chunk_uploader(fileid, total_chunks):
    """
    Get chunk uploader function.

    Get multipart uploader from dictionary or creates one.
    """
    if fileid not in ongoing_uploads:
        ongoing_uploads[fileid] = {
            "set": {},
            "finished": [],
            "next": 0,
        }
    return ongoing_uploads[fileid]


def elegible_chunks(uploader):
    """
    Elegible chunks.

    Returns a list of chunks that are ready to be uploaded
    """
    res = []
    while uploader["next"] in uploader["set"]:
        res.append(
            {
                "chunk_number": uploader["next"],
                "chunk": uploader["set"][uploader["next"]],
            }
        )
        uploader["set"].pop(uploader["next"])
        uploader["next"] += 1
    return res


def convert_line(df, index):
    """
    Convert line.

    Turns a line of csv, pairing the column name with the data and adding a prompt to categorize.
    """
    line = df.iloc[index]
    prompt = """Use the following categories and data points to put a company into a Category.
Respond with just the category and no other words. An example response could be "Food Expense" \n\n
    """
    for i in range(len(line)):
        # only add the prompt if the value is not null
        if pd.notna(line[i]):
            prompt += f"{df.columns[i]}: {line[i]}\n"
    return prompt


def convert_to_prompts(input_path, output_path):
    """
    Convert to prompts.

    Converts a file to prompts for the model
    """
    # the 6th line is the headers. Ignore everything above
    df = pd.read_csv(input_path, header=5)
    prompts = []
    for index, row in df.iterrows():
        prompts.append(
            {
                "modelInput": {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": convert_line(df, index),
                                }
                            ],
                        }
                    ],
                },
            }
        )

    with open(output_path, "w") as f:
        for prompt in prompts:
            f.write(json.dumps(prompt))
            f.write("\n")


def upload_chunk(fileid, chunk, chunk_number, total_chunks, bucket, s3_client):
    """
    Upload Chunk function.

    Takes a chunk, figures out if there is an uploader (creates if otherwise)
    and uploads chunk
    """
    if not os.path.exists(os.environ.get("TEMP_FILE_LOCATION")):
        os.makedirs(os.environ.get("TEMP_FILE_LOCATION"))
    if not os.path.exists(
        os.path.join(os.environ.get("TEMP_FILE_LOCATION"), "prompts")
    ):
        os.makedirs(os.path.join(os.environ.get("TEMP_FILE_LOCATION"), "prompts"))
    path = os.path.join(os.environ.get("TEMP_FILE_LOCATION"), fileid)
    output_path = os.path.join(
        os.environ.get("TEMP_FILE_LOCATION"), "prompts", f"{fileid}.jsonl"
    )
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(b"")
    if not os.path.exists(output_path):
        with open(output_path, "wb") as f:
            f.write(b"")

    uploader = get_chunk_uploader(fileid, total_chunks)
    uploader["set"][chunk_number] = chunk
    for i in elegible_chunks(uploader):
        with open(path, "ab") as f:
            f.write(i["chunk"])
        uploader["finished"].append(i["chunk_number"])
    if len(uploader["finished"]) == total_chunks:
        try:
            convert_to_prompts(path, output_path)
            s3_client.upload_file(output_path, bucket, f"input/{fileid}.jsonl")
        except Exception as e:
            raise DBError(str(e))
        return -1
    return chunk_number
