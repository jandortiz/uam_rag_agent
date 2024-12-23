# Módulo que contiene el front del RAG.

import asyncio
import streamlit as st

from python.llm_connection.search_engine import llm_chat_engine


APP_TITLE = "Asistente virtual"
APP_ICON = "🤖"
MODELOS = ['llama-3.1-8b-instant', 'gemma2-9b-it', 'llama-3.3-70b-versatile']


async def main():
    st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON,
                       layout='centered', menu_items={})

    with st.sidebar:
        st.header(f"{APP_ICON} {APP_TITLE} {APP_ICON}", divider='blue')
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

    if 'messages' not in st.session_state.keys():
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": """Te puedo ayudar con cualquier duda relacionada
                con las materias del máster en [Big Data y Ciencia de Datos.](https://www.masteruambigdata.com/)"""
            }
        ]

    if 'chat_engine' not in st.session_state.keys():
        st.session_state.chat_engine = 'hola'
    
    # if user_query := st.chat_input(
    #     placeholder='Pregúntame algo'
    #     ): st.session_state.messages.append({"role": "user", "content": user_query})

    user_query = st.chat_input(placeholder='Pregúntame algo')
    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})

    for mensage in st.session_state.messages:
        with st.chat_message(mensage["role"]):
            st.write(mensage["content"])

    if st.session_state.messages[-1]['role'] != 'assistant':
        with st.chat_message('assistant'):
            response_stream = llm_chat_engine(user_query, modelo_a_usar)
            st.write_stream(response_stream)
            mensaje = {"role": "assistant", "content": response_stream}
            st.session_state.messages.append(mensaje)


if __name__ == "__main__":
    asyncio.run(main())
