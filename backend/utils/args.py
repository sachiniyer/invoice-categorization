"""
Utility functions for arguments.

Verification for arguments and parsing.
"""

from backend.types.errors import ArgError, JSONError
import json


def parse_args(expected, given):
    """
    Parse arguments.

    Given some arguments list, make sure everything is given
    """
    res = {}
    for i in expected:
        res[i] = given.get(i)
    if None in res.values():
        raise ArgError(res)
    return res


def parse_json(data):
    """
    Parse JSON.

    Given some json parse it, or return JSONError
    """
    try:
        res = json.loads(data)
        return res
    except Exception as e:
        if isinstance(e, json.JSONDecodeError):
            raise JSONError(data, True)
        raise JSONError(data, False)
