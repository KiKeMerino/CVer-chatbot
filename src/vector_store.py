# Interacción con Chroma
import chromadb
from config import CHROMA_PATH, COLLECTION_NAME

# Crear cliente persistente
client = chromadb.PersistentClient(path=CHROMA_PATH)

# Crear o cargar colección
collection = client.get_or_create_collection(name=COLLECTION_NAME)


def add_documents(chunks, vectors):
    if len(chunks) != len(vectors):
        raise ValueError(
            f"Chunks ({len(chunks)}) y vectors ({len(vectors)}) deben tener la misma longitud."
        )

    texts = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    # IDs basados en hash del texto → estables entre reindexaciones
    ids = [str(i) for i in range(len(chunks))]

    collection.upsert(
        documents=texts,
        metadatas=metadatas,
        ids=ids,
        embeddings=vectors,
    )


def clear_documents():
    """Elimina todos los documentos de la colección para una reindexación limpia."""
    existing = collection.get()
    if existing and existing["ids"]:
        collection.delete(ids=existing["ids"])
        print(f"🗑️  Eliminados {len(existing['ids'])} documentos anteriores.")