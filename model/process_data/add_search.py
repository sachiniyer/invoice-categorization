"""
Excel to csv.

Makes a csv from excel files.
"""

from utils import Utils

env_vars = '../.env'

utils = Utils(env_vars)

utils.iterate_serial("./data/clean",
                     "./data/search",
                     "./data",
                     utils.add_search)
