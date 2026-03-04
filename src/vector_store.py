# Interacción con Chroma
import chromadb
from config import CHROMA_PATH, COLLECTION_NAME

# Crear cliente persistente
client = chromadb.PersistentClient(path=CHROMA_PATH)

# Crear o cargar colección
collection = client.get_or_create_collection(name=COLLECTION_NAME)

def add_documents(chunks, vectors):

    if len(chunks) != len(vectors):
        # Mensaje de error si el número de chunks no coincide con el número de embeddings
        raise ValueError(f"Chunks ({len(chunks)}) and vectors ({len(vectors)}) must have the same length.")

    texts = [chunk['text'] for chunk in chunks]
    metadatas = [chunk['metadata'] for chunk in chunks]
    ids = [str(i) for i in range(len(chunks))]

    collection.upsert(
        documents=texts,
        metadatas=metadatas,
        ids=ids,
        embeddings=vectors
    )