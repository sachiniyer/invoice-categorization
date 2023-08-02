"""
Model file.

Runs the model and gives back results.
"""

import shutil
import os


def copy_file(source_file_path, destination_file_path):
    """
    Copy file.

    Copy file from one path to another
    """
    try:
        shutil.copy(source_file_path, destination_file_path)
        print(f"File copied from {source_file_path}"
              " to {destination_file_path}")
    except FileNotFoundError:
        print("Source file not found.")
    except PermissionError:
        print("Permission error. Make sure you have appropriate permissions.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def model_handler(fileid):
    """
    Model Handler.

    Takes the file id, and runs the model on the file.
    Overall handler for all the model's processes.
    """
    copy_file(os.path.join(os.enivorn.get('MODEL_DOWNLOAD_PATH'), fileid),
              os.path.join(os.enivorn.get('MODEL_UPLOAD_PATH'), fileid))
