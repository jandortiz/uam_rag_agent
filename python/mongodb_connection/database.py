# Librerías Python.
import os

from pymongo import MongoClient

from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex

from s3fs import S3FileSystem

from huggingface_hub import login

import streamlit as st

from dotenv import load_dotenv
load_dotenv()

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")


@st.cache_resource
def cargar_datos_a_mongodb(uri: str):

    # Se crea el cliente y conecta  con la colección.
    cliente_mongodb = MongoClient(uri, timeoutMS=60000, socketTimeoutMS=60000)
    bucket_name = 'tfm-data-pdf/data'
    
    try:
        login(token=os.getenv('HF_TOKEN'))
        s3_fs = S3FileSystem()
        print('')
        print(s3_fs.ls(bucket_name))

        loader = SimpleDirectoryReader(
            input_dir=bucket_name, fs=s3_fs, recursive=True, filename_as_id=True)
        datos = loader.load_data()
        atlas_vector_store = MongoDBAtlasVectorSearch(
            mongodb_client=cliente_mongodb,
            db_name='tfm-master-uam',
            collection_name='materias-master',
            vector_index_name='vector_index'
            )
        
        storage_context = StorageContext.from_defaults(vector_store=atlas_vector_store)

        
        index = VectorStoreIndex.from_documents(documents=datos, storage_context=storage_context)
        return index
        

    except Exception as e:
        print(e)

if __name__=='__main__':
    uri = os.getenv('MONGO_URI')
    cargar_datos_a_mongodb(uri=uri)



# TODO: Encontrar la forma de actualizar la BD cuando haya nuevos pdf's en S3.