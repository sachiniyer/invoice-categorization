"""
Utility functions for arguments.

Verification for arguments and parsing.
"""

from backend.types.errors import ArgError, JSONError
import json
import base64


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

    Given some JSON, parse it, or return JSONError.
    """
    try:
        # Ensure the payload is a dictionary
        if not isinstance(data, dict):
            raise ValueError("Expected data to be a dictionary.")

        if "chunk" in data:
            base64_chunk = data["chunk"]
            try:
                # Decode the Base64-encoded file chunk
                file_data = base64.b64decode(base64_chunk)
                data["chunk"] = (
                    file_data  # Replace the Base64 string with the raw binary data
                )
            except Exception as e:
                raise JSONError(f"Failed to decode Base64 chunk: {e}", False)

        return data
    except json.JSONDecodeError as e:
        raise JSONError(data, True)
    except Exception as e:
        raise JSONError(data, False)
