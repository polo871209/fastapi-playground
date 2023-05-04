from ..log import logger
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

BUCKET = "lab-sjfkldslk"


def upload_fileobj(data: BinaryIO, key: str) -> bool:
    """
    :param data: data
    :param key: s3 object key
    """
    s3 = boto3.client('s3')
    try:
        s3.upload_fileobj(data, BUCKET, key)
    except ClientError as e:
        logger.error(f'client error: {e}')
        return False
    except Exception as e:
        logger.error(e)
        return False

    return True


def create_presigned_url(key_name: str, expiration: int = 3600) -> str | bool:
    """Generate a presigned URL to share an S3 object
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET, 'Key': key_name},
            ExpiresIn=expiration)
    except ClientError as e:
        logger.error(f'client error: {e}')
        return False
    except Exception as e:
        logger.error(e)
        return False

    # The response contains the presigned URL
    return response


def delete_object(key_name: str) -> bool:
    s3 = boto3.resource('s3')
    try:
        s3.Object(BUCKET, key_name).delete()
    except ClientError as e:
        logger.error(f'client error: {e}')
        return False
    except Exception as e:
        logger.error(e)
        return False

    return True
