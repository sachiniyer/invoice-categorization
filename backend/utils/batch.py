"""
Bedrock batch processing module.

This module contains the functions that are used to process chunks of data in batch mode.
"""

import os
import uuid
from backend.types.errors import BedrockError


def create_batch_job(input_file, output_file, bedrock_client):
    """
    Create a batch job.

    Uses the haiku model, roleName from env
    """
    try:
        response = bedrock_client.create_model_invocation_job(
            roleArn=os.environ.get("AWS_ROLE_ARN"),
            modelId=os.environ.get("AWS_MODEL_ID"),
            jobName=f"invoice-categorization-batch-job-{str(uuid.uuid4())[0:6]}",
            inputDataConfig=({"s3InputDataConfig": {"s3Uri": input_file}}),
            outputDataConfig=({"s3OutputDataConfig": {"s3Uri": output_file}}),
        )
        return response.get("jobArn")
    except Exception as e:
        raise BedrockError(str(e))


def get_batch_job(jobid, bedrock_client):
    """
    Get a batch job.

    Uses the batch job arn to get the status of the job
    """
    try:
        if jobid == "none":
            return "none"
        response = bedrock_client.get_model_invocation_job(jobIdentifier=jobid)
        return response.get("status")
    except Exception as e:
        raise BedrockError(str(e))
