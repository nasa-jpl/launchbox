import json

import boto3
import botocore
import minio

from manage.result import LBError
from manage.util import LBEnv, LBFile, LBPath


class LBS3:
    @staticmethod
    def resource():
        """Creating a boto3 connection to an S3-compatible storage service."""
        if LBEnv.aws():
            return boto3.resource(
                service_name="s3",
                region_name=LBEnv.get("AWS_REGION_NAME"),
            )
        else:
            return boto3.resource(
                service_name="s3",
                endpoint_url=f'http://minio:{LBEnv.get("MINIO_PORT")}',
                aws_access_key_id=LBEnv.get("MINIO_ROOT_USER"),
                aws_secret_access_key=LBEnv.get("MINIO_ROOT_PASSWORD"),
            )

    class bucket:
        @staticmethod
        def create(bucket):
            s3 = LBS3.resource()
            try:
                s3.create_bucket(Bucket=bucket)
            except botocore.exceptions.ClientError as e:
                code = e.response["Error"]["Code"]
                return LBError(
                    "LBS3.bucket.create",
                    f"Unable to create bucket '{bucket}'; error: {code}",
                    log_level="error",
                )
            else:
                return True

        @staticmethod
        def exists(bucket):
            s3 = LBS3.resource()
            if bucket in [b.name for b in s3.buckets.all()]:
                return True
            return False

        @staticmethod
        def make_public(bucket):
            if not LBEnv.local():
                return False
            if not LBS3.bucket.exists(bucket):
                return False
            # Policy
            path = LBPath.config("minio/bucket_policy.json")
            template = LBFile.read_json(path)
            for statement in template["Statement"]:
                statement["Resource"] = [resource.replace("$bucket", bucket) for resource in statement["Resource"]]
            policy = json.dumps(template)
            # Update bucket policy (in minio)
            try:
                client = minio.Minio(
                    endpoint=f'minio:{LBEnv.get("MINIO_PORT")}',
                    access_key=LBEnv.get("MINIO_ROOT_USER"),
                    secret_key=LBEnv.get("MINIO_ROOT_PASSWORD"),
                    secure=False,
                )
                client.set_bucket_policy(bucket, policy)
            except Exception:
                return False
            else:
                return True

    class object:
        @staticmethod
        def get(bucket, key, local_path):
            s3 = LBS3.resource()
            try:
                s3.Bucket(bucket).download_file(key, local_path)
            except botocore.exceptions.ClientError as e:
                code = e.response["Error"]["Code"]
                return LBError(
                    "LBS3.object.get",
                    f"Unable to get object at {key}; error: {code}",
                    log_level="error",
                )
            else:
                return True

        @staticmethod
        def put(bucket, key, local_path):
            if not LBFile.exists(local_path):
                return LBError(
                    "LBS3.object.put",
                    f"File does not exist at {local_path}",
                    log_level="error",
                )
            s3 = LBS3.resource()
            try:
                s3.Bucket(bucket).upload_file(local_path, key)
            except botocore.exceptions.ClientError as e:
                code = e.response["Error"]["Code"]
                return LBError(
                    "LBS3.object.put",
                    f"Unable to put object at {key}; error: {code}",
                    log_level="error",
                )
            else:
                return True
