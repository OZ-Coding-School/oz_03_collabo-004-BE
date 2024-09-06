import os
import random
import re
import string
from dataclasses import dataclass
from pathlib import Path

import boto3
from articles.models import ArticleImage
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

    def update_image_urls(self, content, article_id):
        """
        임시 이미지 URL을 최종 게시글 이미지 URL로 변환합니다.
        """
        # 정규 표현식을 사용하여 모든 임시 이미지 URL을 찾음
        temp_url_pattern = re.compile(
            rf"https://{self.aws_s3_bucket_name}.s3.{self.aws_region_name}.amazonaws.com/temporary/([a-zA-Z0-9]+.png)"
        )

        # 최종 URL로 변경
        def replace_temp_url(match):
            file_name = match.group(1)
            new_url = f"https://{self.aws_s3_bucket_name}.s3.{self.aws_region_name}.amazonaws.com/articles/{article_id}/{file_name}"
            return new_url

        # content에서 임시 URL을 최종 URL로 변경
        updated_content = re.sub(temp_url_pattern, replace_temp_url, content)
        return updated_content

    @staticmethod
    def upload_files(s3_client, files, article_id=None):
        """
        파일을 S3에 업로드하고, 업로드된 파일의 URL 목록을 반환합니다.
        article_id가 없으면 'temporary' 경로에 저장하고, 있으면 해당 게시글 경로에 저장합니다.
        """
        urls = []
        for file in files:
            random_string = "".join(
                random.choices(string.ascii_letters + string.digits, k=16)
            )

            if article_id:
                # 게시글이 있으면 article/{article_id} 경로 사용
                image_uri = f"articles/{article_id}/{random_string}.png"
            else:
                # 게시글이 없으면 임시 경로 사용
                image_uri = f"temporary/{random_string}.png"

            # S3에 파일 업로드
            s3_client.upload_fileobj(
                file, os.getenv("AWS_STORAGE_BUCKET_NAME"), image_uri
            )

            # 업로드된 파일의 URL을 생성
            image_url = f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/{image_uri}"
            urls.append(image_url)

        return urls

    @staticmethod
    def move_temp_images_to_article(s3_client, temp_image_ids, article):
        """
        임시 이미지들을 최종 게시글 경로로 이동하고, 해당 이미지를 게시글에 연결합니다.
        """
        for image_id in temp_image_ids:
            try:
                image = ArticleImage.objects.get(id=image_id, is_temporary=True)

                # 임시 경로에서 최종 경로로 이미지 복사
                old_key = image.image.split(
                    f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/"
                )[-1]
                new_key = f"articles/{article.id}/{old_key.split('/')[-1]}"  # 게시글 경로로 이동

                # 파일 복사
                S3Instance.copy_file(s3_client, old_key, new_key)

                # 최종 URL로 업데이트
                new_url = f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/{new_key}"
                image.image = new_url
                image.article = article  # 게시글과 연결
                image.is_temporary = False  # 임시 상태 해제
                image.save()

                # 임시 파일 삭제
                S3Instance.delete_file(s3_client, old_key)

            except ArticleImage.DoesNotExist:
                pass

    # s3에서 이미지 객체 삭제
    @staticmethod
    def copy_file(s3_client, source_key, dest_key):
        """
        S3에서 source_key 경로의 파일을 dest_key 경로로 복사합니다.
        """
        try:
            s3_client.copy_object(
                Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"),
                CopySource={
                    "Bucket": os.getenv("AWS_STORAGE_BUCKET_NAME"),
                    "Key": source_key,
                },
                Key=dest_key,
            )
        except Exception as e:
            raise Exception(f"Could not copy file on S3: {str(e)}")

    @staticmethod
    def delete_file(s3_client, file_key):
        """
        S3에서 file_key 경로의 파일을 삭제합니다.
        """
        try:
            s3_client.delete_object(
                Bucket=os.getenv("AWS_STORAGE_BUCKET_NAME"), Key=file_key
            )
        except Exception as e:
            raise Exception(f"Could not delete file from S3: {str(e)}")

    # s3와 db에 있는 이미지 정보 모두 삭제
    @staticmethod
    def delete_images(s3_client, image_ids):
        """
        이미지 ID 목록을 받아서 해당 이미지를 S3에서 삭제하고, DB에서도 삭제 처리합니다.
        """
        deleted_images = []
        for image_id in image_ids:
            try:
                # DB에서 이미지 가져오기
                image = ArticleImage.objects.get(id=image_id)

                # S3에서 이미지 삭제
                s3_key = image.image.split(
                    f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/"
                )[-1]

                # S3에서 파일 삭제
                S3Instance.delete_file(s3_client, s3_key)

                # DB에서 이미지 삭제
                image.delete()
                deleted_images.append(image_id)

            except ArticleImage.DoesNotExist:
                # 해당 이미지가 존재하지 않는 경우 처리
                continue
            except Exception as e:
                raise Exception(f"Failed to delete image {image_id}: {str(e)}")

        return deleted_images
