from src.chunking import chunk_text
from src.embeddings import generate_embeddings
from src.vector_store import add_documents
from src.vector_store import collection

def index_cv():

    # Evito reindexar si ya hay documentos en la colección
    if collection.count() > 0:
        print("Vector store already indexed.")
        return

    with open('data/cv.md', 'r', encoding='utf-8') as file:
        content = file.read()

    # Obtener chunks del texto
    chunks = chunk_text(content)

    texts = [chunk['text'] for chunk in chunks]

    # Obtener embeddings
    vectors = generate_embeddings(texts)

    # Guardar en vector store
    add_documents(chunks, vectors)

    # Script para entrenar al modelo con más conocimiento


def wider_knowledge(questions):

    for q in questions:
        answer = input(q + "\n")

        with open("data/knowledge.md", "a", encoding="utf-8") as f:
            f.write(f"\n### {q}\n")
            f.write(f"{answer}\n")

        chunk = {
            "text": f"{q}: {answer}",
            "metadata": {
                "section": "personal_info"
            }
        }

        embedding = generate_embeddings([chunk["text"]])

        add_documents([chunk], embedding)


TRAINING_QUESTIONS = [
    "Where do you live?",
    "Are you open to relocation?",
    "Do you prefer remote or onsite work?",
    "What type of companies interest you most?",
    "What is your strongest technical skill?"
]

# wider_knowledge(TRAINING_QUESTIONS)