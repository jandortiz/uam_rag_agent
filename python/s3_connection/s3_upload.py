# Módulo para cargar los pdf's a S3.

import os
import boto3

import streamlit as st

def cargar_archivos_s3() -> None:
    """Toma los archivos indicados en el path local y los sube al bucket de S3
    previamente creado.

    """
    bucket_name = st.secrets['s3_bucket']['BUCKET_NAME']

    # TODO: Encontrar la forma de subir archivos que previamente no se han
    # cargado a S3.

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
            

if __name__=="__main__":
    cargar_archivos_s3()
