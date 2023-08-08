"""
Excel to csv.

Makes a csv from excel files.
"""

import pandas as pd
import os
from tqdm import tqdm
import threading
from dotenv import dotenv_values
import requests
import boto3
import time

env_vars = dotenv_values('../.env')


def to_pandas(inf, outf):
    """
    To pandas.

    Converts from excel to pandas.
    """
    # read excel file
    df = pd.read_excel(inf)
    extra = df.columns[4:]
    df['extra'] = df[extra].apply(lambda row:
                                  ','.join(row.dropna().astype(str)), axis=1)
    df.drop(columns=extra, inplace=True)
    df.to_csv(outf, index=False)


def clean_csv(inf, outf):
    """
    Clean csv.

    Removes all unwanted data.
    """
    df = pd.read_csv(inf)
    df_filtered = df[df['label'].str.lower() != 'unmapped']
    df_filtered.to_csv(outf, index=False)


api_key = env_vars['CUSTOM_SEARCH_API_KEY']
search_engine_id = env_vars['SEARCH_ENGINE_ID']


def get_search(term):
    """
    Get search.

    Get's results from google search.
    """
    url = (f'https://www.googleapis.com/customsearch/v1?key={api_key}'
           f'&cx={search_engine_id}&q={term}')
    response = requests.get(url)
    data = response.json()

    res = ""
    if 'searchInformation' in data:
        if data['searchInformation']['totalResults'] == "0":
            return ""
    if 'items' in data:
        for item in data['items']:
            if 'title' in item:
                res += item['title'] + " "
            if 'snippet' in item:
                res += item['snippet'] + " "
    if res == "":
        time.sleep(1)
        return get_search(term)
    return res


session = boto3.Session(
    aws_access_key_id=env_vars['AWS_API_KEY'],
    aws_secret_access_key=env_vars['AWS_API_SECRET'],
    region_name=env_vars['AWS_REGION']
)

dynamodb_client = session.client('dynamodb')


def get_table(term):
    """
    Get table.

    Get's an item from the db
    """
    try:
        key = {
            'name': {'S': term}
        }
        response = dynamodb_client.get_item(
            TableName=env_vars['AWS_TABLE_NAME'],
            Key=key
        )
        item = response.get('Item')
        if item:
            return item["content"]["S"]
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")


def put_table(term, content):
    """
    Put table.

    Puts a table into the db.
    """
    try:
        item = {
            'name': {'S': term},
            'content': {'S': content},
        }
        dynamodb_client.put_item(
            TableName=env_vars['AWS_TABLE_NAME'],
            Item=item
        )
    except Exception as e:
        print(f"An error occurred: {e}")


def get_object(vendor):
    """
    Get object.

    Get's search results from either db or search.
    """
    if not vendor:
        return None
    vendor = str(vendor)
    table_res = get_table(vendor)
    if table_res:
        return table_res
    search_res = get_search(vendor)
    put_table(vendor, search_res)
    return search_res


s3_client = session.client('s3')


def sync_s3(local_path):
    """
    Sync s3.

    Syncs data folder to s3.
    """
    try:
        remote_path = local_path.replace('../data/', '')
        s3_client.upload_file(local_path, env_vars['AWS_DATA_BUCKET'],
                              remote_path)
    except Exception as e:
        print(f"An error occurred: {e}")


def add_search(inf, outf):
    """
    Add search.

    Adds search results to csv.
    """
    df = pd.read_csv(inf)

    overall_bar = tqdm(total=len(df), desc=f"Processing {inf}", position=0)

    def apply_with_progress(row):
        result = get_object(row['vendor'])
        overall_bar.update(1)
        return result

    df['search'] = df.apply(apply_with_progress, axis=1)
    overall_bar.close()
    df.to_csv(outf, index=False)
    sync_s3(outf)


def iterate(in_dir, out_dir, function):
    """
    Iterate with tqdm.

    Iterates through files in a directory and uses tqdm for progress tracking.
    """
    threads = []
    for file in tqdm(os.listdir(in_dir), desc="Files", position=0):
        in_file = os.path.join(in_dir, file)
        out_file = os.path.join(out_dir, file)
        thread = threading.Thread(target=function, args=(in_file, out_file))
        threads.append(thread)

    with tqdm(total=len(threads), desc="Threads", position=1) as pbar:
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
            pbar.update(1)


def iterate_serial(in_dir, out_dir, dir, function):
    """
    Iterate serial.

    Iterate through a directory serial.
    """
    for file in tqdm(os.listdir(in_dir), desc="Files", position=0):
        in_file = os.path.join(in_dir, file)
        out_file = os.path.join(out_dir, file)
        if not os.path.exists(out_file):
            function(in_file, out_file)


iterate_serial("../data/clean", "../data/search", "../data", add_search)
