from src.chunking import load_and_chunk_documents
from src.embeddings import generate_embeddings
from src.vector_store import add_documents
from src.vector_store import collection

def index_documents():

    # Evito reindexar si ya hay documentos en la colección
    # if collection.count() > 0:
    #     print("Vector store already indexed.")
    #     return

    # with open('data/cv.md', 'r', encoding='utf-8') as file:
    #     content = file.read()

    # Obtener chunks del texto
    # chunks = chunk_text(content)

    # Carga tanto el CV como la infortmación personal
    chunks = load_and_chunk_documents()

    texts = [chunk['text'] for chunk in chunks]

    # Obtener embeddings
    vectors = generate_embeddings(texts)

    # Guardar en vector store
    add_documents(chunks, vectors)
