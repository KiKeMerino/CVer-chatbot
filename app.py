from src.embeddings import generate_embeddings
from src.retriever import retrieve
from src.prompt_builder import build_prompt
from src.llm import generate_answer


def ask(question):

    query_embedding = generate_embeddings([question])[0]

    context_chunks, _ = retrieve(query_embedding)

    prompt = build_prompt(context_chunks, question)

    answer = generate_answer(prompt)

    return answer

question = input("Ask me about Kike: ")
print(ask(question))