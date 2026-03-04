import streamlit as st

from src.embeddings import generate_embeddings
from src.retriever import retrieve
from src.prompt_builder import build_prompt
from src.llm import generate_answer

st.title("CVer - Chat")

question = st.text_input("Ask me about Kike")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.write(msg)

if question:

    st.session_state.messages.append(("User", question))

    # 1 Generate embedding of the query
    query_embedding = generate_embeddings([question])[0]

    # 2 Retrieve relevant chunks
    context_chunks, _ = retrieve(query_embedding)

    # 3 Build prompt
    prompt = build_prompt(context_chunks, question)

    # 4 Generate answer
    answer = generate_answer(prompt)

    st.session_state.messages.append(("CVer", answer))

    st.write(answer)
