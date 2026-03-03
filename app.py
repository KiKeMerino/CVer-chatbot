from chunking import chunk_text
from embeddings import generate_embeddings

with open('dta/cv.md', 'r', encoding='utf-8') as file:
    content = file.read()

# Obtener chunks del texto
chunks = chunk_text(content)
texts = [chunk['text'] for chunk in chunks]

# Obtener embeddings
vectors = generate_embeddings(texts)

# Mensaje de error si el número de chunks no coincide con el número de embeddings
if len(chunks) != len(vectors):
    raise ValueError(f"Error: El número de chunks ({len(chunks)}) no coincide con el número de embeddings ({len(vectors)}).")

# else:

#     combined = []
#     for chunk, vector in zip(chunks, vectors):
#         combined.append({
#             "text": chunk['text'],
#             "metadata": chunk['metadata'],
#             "embedding": vector
#         })

ids = [str(i) for i in range(len(chunks))]