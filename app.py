import streamlit as st

from src.embeddings import generate_embeddings
from src.retriever import retrieve
from src.prompt_builder import build_prompt
from src.llm import generate_answer
from src.vector_store import collection
from offline import index_cv   # función que tengas en offline.py

@st.cache_resource
def init_db():
    if collection.count() == 0:
        index_cv()

init_db()

st.title("CVer - Chat")

question = st.chat_input("Preguntame algo sobre Kike")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.write(msg)

#  Poner limite de preguntas por sesión
if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if question:

    if st.session_state.question_count >= 12:
        st.warning("Has alcanzado el límite de preguntas por sesión. Por favor, recarga la página para continuar.")
        st.stop()

    st.session_state.messages.append(("User", question))

    # 1 Generate embedding of the query
    query_embedding = generate_embeddings([question])[0]

    # 2 Retrieve relevant chunks
    context_chunks, _ = retrieve(query_embedding)
    print(context_chunks)
    # 3 Build prompt
    prompt = build_prompt(context_chunks, question)

    # 4 Generate answer
    answer = generate_answer(prompt)

    st.session_state.messages.append(("CVer", answer))

    st.write(answer)
