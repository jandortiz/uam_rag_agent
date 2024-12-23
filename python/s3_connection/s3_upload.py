import boto3
import os

bucket_name = 'tfm-data-pdf'

# TODO: Encontrar la forma de subir archivos que previamente no se han cargado
# a S3.

s3_client = boto3.client('s3')
# s3_client.create_bucket(
#     Bucket=bucket_name,
#     CreateBucketConfiguration={'LocationConstraint': 'eu-central-1'})


data_path = os.path.join('data')
for root, _, files in os.walk(data_path):
    for file in files:
        file_path = os.path.join(root, file)
        s3_client.upload_file(file_path, bucket_name, f"{file_path}")
        print(f'archivo {file_path} cargado.')
