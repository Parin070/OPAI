import os
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

MINIO_URL = os.environ.get("MINIO_URL", "http://localhost:9000")
MINIO_PUBLIC_URL = os.environ.get("MINIO_PUBLIC_URL", "http://localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
BUCKET_NAME = "stylesync-images"

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_URL,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)

def init_bucket():
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "404":
            s3_client.create_bucket(Bucket=BUCKET_NAME)
        else:
            print(f"Error checking bucket {BUCKET_NAME}: {e}")
            return
            
    # Always ensure the bucket is public for reading images
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicRead",
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{BUCKET_NAME}/*"]
            }
        ]
    }
    import json
    try:
        s3_client.put_bucket_policy(Bucket=BUCKET_NAME, Policy=json.dumps(policy))
    except Exception as e:
        print(f"Error setting bucket policy: {e}")

def upload_image_to_minio(file_bytes: bytes, filename: str, content_type: str) -> str:
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=filename,
        Body=file_bytes,
        ContentType=content_type
    )
    # The frontend needs to access it, so return the public URL format
    # Because MinIO handles paths like /bucket_name/filename
    return f"{MINIO_PUBLIC_URL}/{BUCKET_NAME}/{filename}"
