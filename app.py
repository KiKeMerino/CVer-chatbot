from chunking import chunk_text
from embeddings import generate_embeddings

with open('dta/cv.md', 'r', encoding='utf-8') as file:
    content = file.read()

# Obtener chunks del texto
chunks = chunk_text(content)
texts = [chunk['text'] for chunk in chunks]

# Obtener embeddings
vectors = generate_embeddings(texts)
