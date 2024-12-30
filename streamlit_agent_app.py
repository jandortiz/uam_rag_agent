# Módulo que contiene el front del RAG.

import asyncio
import streamlit as st

from python.llm_connection.search_engine import llm_chat_engine


TITULO_APP = "Asistente virtual"
ICONO_APP = "🤖"
MODELOS = ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant',
           'mixtral-8x7b-32768']


def obtener_mensajes() -> None:
    """Crea el mensaje inicial en la sesión de Streamlit.

    """
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": """Hola humano, te puedo ayudar con cualquier duda
                relacionada con las materias del máster."""
            }
        ]
    return st.session_state.messages


async def main():
    """Crea la lógica del front.

    """
    st.set_page_config(page_title=TITULO_APP, page_icon=ICONO_APP,
                       layout='centered', menu_items={})

    with st.sidebar:
        st.header(f"{ICONO_APP} {TITULO_APP} {ICONO_APP}", divider='blue')
        """Aplicación basada en un agente RAG, que sirve como guía de estudio y
        fuente de información para las materias relacionadas con el [máster en
        Big Data y Ciencia de Datos](https://www.masteruambigdata.com/) de la 
        Universidad Autónoma de Madrid.
        Proyecto final realizado como parte del TFM en dicho máster.
        """

        with st.popover(
            label=":material/settings: Configuración", use_container_width=True):
            modelo_a_usar = st.selectbox(
                label='Modelo a usar',
                options=MODELOS,
                placeholder='Selecciona una opción'
                )

    st.session_state.messages = obtener_mensajes()

    with st.container():
        for mensage in st.session_state.messages:
            with st.chat_message(mensage["role"]):
                st.write(mensage["content"])

    user_query = st.chat_input(placeholder='Pregúntame algo')

    if user_query:
        st.chat_message('user').markdown(user_query)
        st.session_state.messages.append({'role':'user', 'content':user_query})

        with st.chat_message('assistant', avatar='assistant'):
            response_stream = llm_chat_engine(user_query, modelo_a_usar)
            guardar_respuesta = st.write_stream(response_stream)
        st.session_state.messages.append(
            {"role": "assistant", "content": guardar_respuesta})


if __name__ == "__main__":
    asyncio.run(main())
