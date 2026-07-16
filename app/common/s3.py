"""Factory for creating boto3 S3 clients from application config."""

import json
from typing import Any

import boto3
import botocore.exceptions
import fastapi.concurrency

from app import config

settings = config.get_config()

_NOT_FOUND_ERROR_CODES = {"NoSuchKey", "404"}


def create_s3_client() -> Any:
    """Create a boto3 S3 client using application configuration."""

    return boto3.client(
        "s3",
        region_name=settings.aws_region,
        endpoint_url=settings.floci_endpoint_url,
    )


async def get_json_object(s3_client: Any, bucket: str, key: str) -> Any | None:
    """Fetch and decode a JSON object from S3, returning None if it is absent."""

    try:
        return await fastapi.concurrency.run_in_threadpool(
            _fetch_json, s3_client, bucket, key
        )
    except botocore.exceptions.ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code in _NOT_FOUND_ERROR_CODES:
            return None
        raise


def _fetch_json(s3_client: Any, bucket: str, key: str) -> Any:
    response = s3_client.get_object(Bucket=bucket, Key=key)
    body = response["Body"].read()
    return json.loads(body)
