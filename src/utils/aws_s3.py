import logging
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

BUCKET = "lab-sjfkldslk"


def upload_fileobj(data: BinaryIO, key: str) -> None:
    """
    :param data: data
    :param key: s3 object key
    """
    s3 = boto3.client('s3')
    s3.upload_fileobj(data, BUCKET, key)


def create_presigned_url(object_name: str, expiration: int = 3600) -> str | None:
    """Generate a presigned URL to share an S3 object
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET, 'Key': object_name},
            ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def delete_object(object_name: str) -> None:
    s3 = boto3.resource('s3')
    s3.Object(BUCKET, object_name).delete()
