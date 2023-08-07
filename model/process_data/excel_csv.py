"""
Excel to csv.

Makes a csv from excel files.
"""

import pandas as pd
import sys
import os
from tqdm import tqdm
import multiprocessing as mp


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


def iterate(in_dir, out_dir):
    """
    Iterate.

    Iterates through files in a directory.
    """
    # make this multithreaded
    for file in tqdm(os.listdir(in_dir)):
        if file.endswith(".xlsx"):
            in_file = os.path.join(in_dir, file)
            out_file = os.path.join(out_dir, file.replace('.xlsx', '.csv'))
            mp.Process(target=to_pandas, args=(in_file, out_file)).start()


if __name__ == '__main__':
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    iterate(in_dir, out_dir)
