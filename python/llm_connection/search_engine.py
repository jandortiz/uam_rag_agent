# Módulo que implementa las funciones necesarias para poner en ejecución el
# LLM.

import os
from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient

from huggingface_hub import login

from llama_index.llms.groq import Groq
from llama_index.core.llms import ChatMessage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def get_embedding(query: str) -> list:
    """Crea la representación vectorial de una cadena de texto.
    Por defecto, usa el modelo BAAI/bge-small-en.

    Args:
        query: cadena de texto usada para crear su correspondiente embedimiento
    
    Returns:
        Lista de números que corresponden a la representación vectorial de la 
        cadena de texto ingresada.

    """
    login(token=os.getenv('HF_TOKEN'))
    embedding_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")
    embedded_query = embedding_model.get_text_embedding(query)
    
    return embedded_query


def get_resultados_query(query:str) -> list:
    """Realiza una búsqueda del texto que más se relaciona con el argumento.
    Dicha búsqueda la realiza en MongoDB y retorna los 10 mejores resultados.

    Args:
        query: cadena de texto correspondiente a la pregunta hecha por el
        usuario.

    Returns:
        Lista con el texto más próximo a la cadena de texto pasada como
        argumento.

    """
    uri = os.getenv('MONGO_URI')
    cliente_mongodb = MongoClient(uri, timeoutMS=60000, socketTimeoutMS=60000)
    coleccion = cliente_mongodb['tfm-master-uam']['materias-master']

    embedded_query = get_embedding(query)

    pipeline = [
        {
            "$vectorSearch": {
                "index": "pdf-search",
                "queryVector": embedded_query,
                "path": "embedding",
                "exact": True,
                "limit": 10
                }
        }, {
            "$project": {
                "_id": 0,
                "text": 1
                }
            }
    ]

    resultado_busqueda = coleccion.aggregate(pipeline=pipeline)
    resultado_final = [documento for documento in resultado_busqueda]
    return resultado_final


def llm_chat_engine(query: str, modelo: str):
    """

    Args:
        query: cadena de texto correspondiente a la pregunta hecha por el
        usuario.
        modelo: cadena de texto que representa el nombre del LLM a usar.
    
    Yields:
        str: texto de respuesta ofrecido por el LLM.
    """
    api_key = os.getenv('GROQ_API_KEY')
    documento_contexto = get_resultados_query(query)
    contexto = ' '.join(documento['text'] for documento in documento_contexto)

    prompt = f""" Use la siguiente información de contexto para responder la
    pregunta realizada al final.
    {contexto}
    Pregunta: {query}
    """

    mensaje = [ChatMessage(role='assistant', content=prompt)]
    
    llm = Groq(model=modelo, api_key=api_key)
    respuesta_llm = llm.stream_chat(mensaje)

    for chunk in respuesta_llm:
        contenido = chunk.delta
        if contenido:
            yield contenido