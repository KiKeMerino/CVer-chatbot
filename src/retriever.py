# Logica de retrieval (Top-k)
# Dado un embedding de query, devolver los k chunks más relevantes de la colección

from src.vector_store import collection

def retrieve(query_embedding, top_k=5):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results['documents'][0], results['metadatas'][0]