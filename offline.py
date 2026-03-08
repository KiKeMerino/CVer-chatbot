from src.chunking import load_and_chunk_documents
from src.embeddings import generate_embeddings
from src.vector_store import add_documents, clear_documents

def index_documents():

    clear_documents()  # Limpiar vector store antes de indexar

    # Carga los datos de la carpeta data, los chunkea y obtiene sus metadatos
    chunks = load_and_chunk_documents()

    texts = [chunk['text'] for chunk in chunks]

    # Obtener embeddings
    vectors = generate_embeddings(texts)

    # Guardar en vector store
    add_documents(chunks, vectors)
