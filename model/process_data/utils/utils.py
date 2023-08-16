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


class Utils:
    """
    Util class.

    Major class for all util functions
    """

    def __init__(self, env_file):
        """
        Init function.

        Initializes Util class
        """
        self.env_vars = dotenv_values(env_file)
        self.session = boto3.Session(
            aws_access_key_id=self.env_vars['AWS_API_KEY'],
            aws_secret_access_key=self.env_vars['AWS_API_SECRET'],
            region_name=self.env_vars['AWS_REGION']
        )

        self.dynamodb_client = self.session.client('dynamodb')
        self.s3_client = self.session.client('s3')
        self.api_key = self.env_vars['CUSTOM_SEARCH_API_KEY']
        self.search_engine_id = self.env_vars['SEARCH_ENGINE_ID']
        self.max_retries = 10
        self.default_backoff = 3

    def to_pandas(inf, outf):
        """
        To pandas.

        Converts from excel to pandas.
        """
        # read excel file
        df = pd.read_excel(inf)
        extra = df.columns[4:]
        df['extra'] = df[extra].apply(lambda row:
                                      ','.join(row.dropna().astype(str)),
                                      axis=1)
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

    def send_request(self, url):
        """
        Send request.

        Sends a request to google search
        """
        retries = 0

        while retries < self.max_retries:
            try:
                response = requests.get(url)

                if response.status_code == 200:
                    data = response.json()
                    return data
                elif response.status_code == 429:
                    if 'Retry-After' in response.headers:
                        retry_after = int(response.headers['Retry-After'])
                        print("Received 429 error. Retrying after "
                              "{} seconds...".format(retry_after))
                        time.sleep(retry_after)
                    else:
                        print("Received 429 error. Retrying after "
                              "default delay...")
                        time.sleep(self.default_backoff)
                else:
                    print("Request failed with status code:",
                          response.status_code)
                    return None
            except Exception as e:
                print("An error occurred:", e)
                continue

            retries += 1
        print("Max retries reached for {url} . Request failed.")
        return " "

    def get_search(self, term):
        """
        Get search.

        Get's results from google search.
        """
        url = (f'https://www.googleapis.com/customsearch/v1?key={self.api_key}'
               f'&cx={self.search_engine_id}&q={term}')
        try:
            data = self.send_request(url)
        except Exception as e:
            print(f'search for {term} failed with {e}')
            time.sleep(1)
            return self.get_search(term)

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
            return self.get_search(term)
        return res

    def get_table(self, term):
        """
        Get table.

        Get's an item from the db
        """
        try:
            key = {
                'name': {'S': term}
            }
            response = self.dynamodb_client.get_item(
                TableName=self.env_vars['AWS_TABLE_NAME'],
                Key=key
            )
            item = response.get('Item')
            if item:
                return item["content"]["S"]
            else:
                return None
        except Exception as e:
            print(f"An error occurred: {e}")

    def put_table(self, term, content):
        """
        Put table.

        Puts a table into the db.
        """
        try:
            item = {
                'name': {'S': term},
                'content': {'S': content},
            }
            self.dynamodb_client.put_item(
                TableName=self.env_vars['AWS_TABLE_NAME'],
                Item=item
            )
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_object(self, vendor):
        """
        Get object.

        Get's search results from either db or search.
        """
        if not vendor:
            return None
        vendor = str(vendor)
        table_res = self.get_table(vendor)
        if table_res:
            return table_res
        search_res = self.get_search(vendor)
        self.put_table(vendor, search_res)
        return search_res

    def get_random(self, num=10):
        """
        Get random.

        Get some random vendors from the db.
        """
        try:
            response = self.dynamodb_client.scan(
                TableName=self.env_vars['AWS_TABLE_NAME'],
                Limit=num
            )
            items = response.get('Items')
            if items:
                return {item['name']['S']: item['content']['S']
                        for item in items}
            else:
                return None
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_full(self):
        """
        Get full.

        Get all vendors from the db, which is the primary key 'name'
        """
        try:
            paginator = self.dynamodb_client.get_paginator('scan')
            response_iterator = paginator.paginate(
                TableName=self.env_vars['AWS_TABLE_NAME']
            )
            items = []
            response_count = 0
            for response in response_iterator:
                response_count += response['ScannedCount']
                print(f"Scanned {response_count} items")
                items.extend(response['Items'])
            if items:
                return {item['name']['S']: item['content']['S']
                        for item in items}
            else:
                return None
        except Exception as e:
            print(f"An error occurred: {e}")

    def sync_s3(self, local_path):
        """
        Sync s3.

        Syncs data folder to s3.
        """
        try:
            remote_path = local_path.replace('../data/', '')
            self.s3_client.upload_file(local_path,
                                       self.env_vars['AWS_DATA_BUCKET'],
                                       remote_path)
        except Exception as e:
            print(f"An error occurred: {e}")

    def add_search(self, inf, outf):
        """
        Add search.

        Adds search results to csv.
        """
        df = pd.read_csv(inf)

        overall_bar = tqdm(total=len(df), desc=f"Processing {inf}", position=0)

        def apply_with_progress(row):
            result = self.get_object(row['vendor'])
            overall_bar.update(1)
            return result

        df['search'] = df.apply(apply_with_progress, axis=1)
        overall_bar.close()
        df.to_csv(outf, index=False)
        self.sync_s3(outf)

    def iterate(in_dir, out_dir, function):
        """
        Iterate with tqdm.

        Iterates through files in a directory and uses tqdm for progress.
        """
        threads = []
        for file in tqdm(os.listdir(in_dir), desc="Files", position=0):
            in_file = os.path.join(in_dir, file)
            out_file = os.path.join(out_dir, file)
            thread = threading.Thread(target=function, args=(in_file,
                                                             out_file))
            threads.append(thread)

        with tqdm(total=len(threads), desc="Threads", position=1) as pbar:
            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()
                pbar.update(1)

    def iterate_serial(self, in_dir, out_dir, dir, function):
        """
        Iterate serial.

        Iterate through a directory serial.
        """
        for file in tqdm(os.listdir(in_dir), desc="Files", position=0):
            in_file = os.path.join(in_dir, file)
            out_file = os.path.join(out_dir, file)
            if not os.path.exists(out_file):
                function(in_file, out_file)
