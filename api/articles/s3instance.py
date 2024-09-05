import os
import random
import string
from dataclasses import dataclass
from pathlib import Path

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일 로드
load_dotenv(os.path.join(BASE_DIR, ".env"))


@dataclass
class S3Instance:
    def __init__(self):
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region_name = os.getenv("AWS_S3_REGION_NAME")
        self.aws_s3_bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")

    def get_s3_instance(self):
        return boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region_name,
        )

    @staticmethod
    def upload_files(s3_client, files, article_id):
        urls = []
        for file in files:
            try:
                random_string = "".join(
                    random.choices(string.ascii_letters + string.digits, k=16)
                )
                image_uri = f"articles/{article_id}/{random_string}.png"

                s3_client.upload_fileobj(
                    file,
                    os.getenv("AWS_STORAGE_BUCKET_NAME"),
                    image_uri,
                )
                image_url = f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/{image_uri}"
                urls.append(image_url)
            except (NoCredentialsError, PartialCredentialsError) as e:
                raise Exception("Could not upload file to S3: " + str(e))
        return urls

    @staticmethod
    def delete_file(s3_client, file_url):
        try:
            # S3 버킷 내의 파일 경로 추출
            bucket_name = os.getenv("AWS_STORAGE_BUCKET_NAME")
            file_key = file_url.split(
                f"https://{bucket_name}.s3.{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/"
            )[-1]

            s3_client.delete_object(Bucket=bucket_name, Key=file_key)
        except Exception as e:
            raise Exception(f"Could not delete file from S3: {str(e)}")
