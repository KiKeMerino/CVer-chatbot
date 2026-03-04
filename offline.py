from src.chunking import chunk_text
from src.embeddings import generate_embeddings
from src.vector_store import add_documents

with open('data/cv.md', 'r', encoding='utf-8') as file:
    content = file.read()

# Obtener chunks del texto
chunks = chunk_text(content)
texts = [chunk['text'] for chunk in chunks]

# Obtener embeddings
vectors = generate_embeddings(texts)

# Guardar en vector store
add_documents(chunks, vectors)