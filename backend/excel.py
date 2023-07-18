#!/usr/bin/env python3
"""
Converts bidirectionally between excel and pandas df.

to_pandas takes excel and converts to df
to_excel takes df and converts back to pandas
"""
import pandas as pd
import numpy as np


def to_pandas(excel):
    """
    Convert excel to pandas.

    Throws error if not convertable.
    """
    df = pd.read_excel(excel, sheet_name="Data", header=6)
    df = df.drop(df.columns[0], axis=1)
    df = df.dropna(axis=1)
    df = df[~df['Final Mapping'].str.isupper()]
    label = pd.get_dummies(df['Final Mapping']).apply(
        lambda row: np.array(row.astype(int)), axis=1)
    df = df.rename(columns={'Original Vendor': 'vendor',
                            'GL Account Description': 'description',
                            'Vendor Mapping': 'mapping'})
    df = df[["vendor", "description", "mapping"]]
    df = df.assign(label=label)
    return df
