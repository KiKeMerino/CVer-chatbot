import hashlib
import json
import os

from src.chunking import load_and_chunk_documents
from src.embeddings import generate_embeddings
from src.vector_store import add_documents, clear_documents
from src.vector_store import collection

# Fichero donde guardamos el hash de los documentos fuente
HASH_FILE = ".index_hash"
SOURCE_FILES = ["data/cv.md", "data/knowledge.md"]


def _compute_sources_hash() -> str:
    """Calcula un hash MD5 combinado de todos los ficheros fuente."""
    h = hashlib.md5()
    for path in SOURCE_FILES:
        try:
            with open(path, "rb") as f:
                h.update(f.read())
        except FileNotFoundError:
            # Si no existe el fichero, lo ignoramos (knowledge.md puede no existir aún)
            h.update(b"")
    return h.hexdigest()


def _read_stored_hash() -> str:
    """Lee el hash guardado del último índice. Devuelve '' si no existe."""
    try:
        with open(HASH_FILE, "r") as f:
            return json.load(f).get("hash", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return ""


def _save_hash(hash_value: str):
    """Guarda el hash actual para comparaciones futuras."""
    with open(HASH_FILE, "w") as f:
        json.dump({"hash": hash_value}, f)


def index_documents(force: bool = False):
    """
    Indexa los documentos en ChromaDB.

    Solo reindexea si:
      - force=True (llamada explícita)
      - La colección está vacía
      - El hash de los ficheros fuente ha cambiado desde la última indexación

    Al reindexar: borra todos los documentos anteriores antes de insertar
    los nuevos, evitando chunks huérfanos con IDs sobrantes.
    """
    current_hash = _compute_sources_hash()
    stored_hash = _read_stored_hash()
    collection_empty = collection.count() == 0

    needs_reindex = force or collection_empty or (current_hash != stored_hash)

    if not needs_reindex:
        print("✅ Índice actualizado. No es necesario reindexar.")
        return

    reason = "forzado" if force else ("colección vacía" if collection_empty else "documentos modificados")
    print(f"🔄 Reindexando ({reason})...")

    # 1. Limpiar colección anterior
    clear_documents()

    # 2. Cargar y chunkear documentos
    chunks = load_and_chunk_documents()

    if not chunks:
        print("⚠️  No se encontraron chunks. Verifica que data/cv.md existe.")
        return

    texts = [chunk["text"] for chunk in chunks]

    # 3. Generar embeddings
    vectors = generate_embeddings(texts)

    # 4. Guardar en ChromaDB
    add_documents(chunks, vectors)

    # 5. Persistir el hash para la próxima comparación
    _save_hash(current_hash)

    print(f"✅ Indexados {len(chunks)} chunks correctamente.")