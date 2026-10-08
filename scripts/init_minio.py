from src.storage.minio_service import MinIOService
from src.core.config import settings


def initialize_minio_buckets():
    client = MinIOService().client
    for bucket_name in settings.minio_buckets:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"Created bucket: {bucket_name}")


if __name__ == '__main__':
    initialize_minio_buckets()