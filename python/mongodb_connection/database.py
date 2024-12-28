# Módulo para realizar conexión y carga de datos a MongoDB.

from pymongo import MongoClient

from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext, VectorStoreIndex)

from s3fs import S3FileSystem

import streamlit as st

from huggingface_hub import login

embedding_name = st.secrets['HF_embeddings']['HF_EMBEDDING']
Settings.embed_model = HuggingFaceEmbedding(model_name=embedding_name)


@st.cache_resource
def cargar_datos_a_mongodb(uri: str) -> VectorStoreIndex:
    """Lee, procesa, indexa y carga la información relacionada con los pdf's a
    MongoDB.

    Args:
        uri: link que contiene la información para conectarse a MongoDB.

    Returns:
        Índice vectorial de cada pdf procesado.
    """

    # Se crea el cliente y conecta  con la colección.
    cliente_mongodb = MongoClient(uri, timeoutMS=60000, socketTimeoutMS=60000)
    bucket_name = 'tfm-data-pdf/data'
    
    try:
        login(token=st.secrets['huggingface_conn']['HF_TOKEN'])
        s3_fs = S3FileSystem()

        loader = SimpleDirectoryReader(
            input_dir=bucket_name, fs=s3_fs, recursive=True,
            filename_as_id=True)
        
        datos = loader.load_data()
        
        atlas_vector_store = MongoDBAtlasVectorSearch(
            mongodb_client=cliente_mongodb,
            db_name='tfm-master-uam',
            collection_name='materias-master',
            vector_index_name='vector_index'
            )
        
        storage_context = StorageContext.from_defaults(
            vector_store=atlas_vector_store)

        index = VectorStoreIndex.from_documents(
            documents=datos, storage_context=storage_context)
        return index
        

    except Exception as e:
        print(e)

if __name__=='__main__':
    uri = st.secrets['mongodb']['MONGO_URI']
    cargar_datos_a_mongodb(uri=uri)



# TODO: Encontrar la forma de actualizar la BD cuando haya nuevos pdf's en S3.