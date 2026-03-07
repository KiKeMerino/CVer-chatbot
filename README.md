# CVer — CV Interactivo con RAG

Un chatbot basado en **Retrieval-Augmented Generation (RAG)** que actúa como versión interactiva de un CV. Los recruiters pueden hacerle preguntas directamente como si estuvieran en una entrevista real, y el sistema responde en primera persona basándose exclusivamente en la información indexada.

Desplegado en **Streamlit Community Cloud**.

---

## Demo

> **[👉 Ver demo en vivo](https://tu-app.streamlit.app)**  
> *(reemplaza con tu URL de Streamlit Cloud)*

---

## Arquitectura

```
┌─────────────────────────────────────────────────┐
│                   Streamlit UI                   │
│         (Chat recruiter + Admin panel)           │
└────────────────────┬────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │    RAG Pipeline      │
          │                     │
          │  1. Embeddings       │  ← OpenAI text-embedding-3-large
          │  2. Retrieval        │  ← ChromaDB (vector store)
          │  3. Prompt builder   │
          │  4. LLM response     │  ← GPT-4o-mini
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │   Google Sheets      │  ← Tracking de visitas y preguntas
          └─────────────────────┘
```

### Ficheros principales

```
CVer/
├── app.py                  # Aplicación Streamlit (Chat + Admin)
├── styles.py               # Estilos CSS (HACKER_CSS, CLEAN_CSS, MODERN_CSS)
├── tracker.py              # Tracking de visitas/preguntas en Google Sheets
├── offline.py              # Script de indexación de documentos
├── config.py               # Configuración global (paths, modelos)
├── src/
│   ├── chunking.py         # División de documentos en chunks
│   ├── embeddings.py       # Wrapper del modelo de embeddings
│   ├── vector_store.py     # Interacción con ChromaDB
│   ├── retriever.py        # Lógica de retrieval (top-k)
│   ├── prompt_builder.py   # Construcción del prompt con contexto
│   └── llm.py              # Wrapper del modelo generativo
├── data/
│   ├── cv.md               # CV en formato Markdown (no incluido en el repo)
│   └── knowledge.md        # Información personal y preferencias (no incluido)
├── requirements.txt
└── .env.example
```

---

## Requisitos

- Python 3.10+
- Cuenta en [OpenAI](https://platform.openai.com/) con API key
- (Opcional) Google Cloud Service Account para tracking
- (Opcional) Google Analytics Measurement ID

---

## Instalación local

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/cver.git
cd cver

# 2. Crear entorno virtual
python -m venv genai
source genai/bin/activate  # Windows: genai\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY

# 5. Añadir tus datos (no se incluyen en el repo)
# Crear data/cv.md con tu CV en Markdown
# Crear data/knowledge.md con tu información personal

# 6. Indexar documentos
python -c "from offline import index_documents; index_documents()"

# 7. Lanzar la app
streamlit run app.py
```

---

## Configuración

### Variables de entorno (`.env`)

```env
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-large
LLM_MODEL=gpt-4o-mini
CHROMA_PATH=./chroma_db
COLLECTION_NAME=cv_collection
```

### Secrets para Streamlit Cloud (`secrets.toml`)

```toml
ADMIN_PASSWORD = "tu_contraseña_admin"

# ── Google Sheets (tracking) ──────────────────
[gsheets]
spreadsheet_id = "id_de_tu_spreadsheet"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\n..."
client_email = "...@....iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"

# ── Google Analytics (opcional) ───────────────
[analytics]
ga_measurement_id = "G-XXXXXXXXXX"
```

---

## Datos (privados, no incluidos en el repo)

El repositorio **no incluye** los ficheros de datos personales. Para que la app funcione necesitas crear:

**`data/cv.md`** — Tu CV completo en Markdown. Se recomienda estructurarlo con secciones `##` y subsecciones `###` para que el chunking sea semánticamente coherente.

**`data/knowledge.md`** — Información complementaria no visible en el CV: expectativas salariales, disponibilidad, preferencias de trabajo, hobbies, etc. Se genera automáticamente desde el **panel Admin** de la app.

---

## Panel Admin

Accesible desde el sidebar → modo **Admin** (requiere contraseña).

Funcionalidades:
- **Reindexación** — Fuerza la reindexación de los documentos en ChromaDB
- **Entrevista de actualización** — Chat guiado para completar `knowledge.md` con información personal
- **Estadísticas** — Visitas totales, visitantes únicos (por fingerprint IP+UA), preguntas totales, preguntas más frecuentes y últimas preguntas con identificador de visitante

---

## Tracking de visitantes

El sistema registra en Google Sheets:

| Pestaña | Columnas |
|---|---|
| `visitas` | `timestamp · session_id · visitor_id · ip · user_agent` |
| `preguntas` | `timestamp · session_id · visitor_id · pregunta` |

El `visitor_id` es un hash MD5 de `IP + User-Agent` (12 caracteres). Permite identificar si la misma persona vuelve en sesiones distintas sin almacenar datos personales en texto plano.

---

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Frontend | Streamlit 1.54 |
| Embeddings | OpenAI `text-embedding-3-large` |
| Vector store | ChromaDB |
| LLM | OpenAI `gpt-4o-mini` |
| Tracking | Google Sheets API + gspread |
| Analytics | Google Analytics 4 |
| Despliegue | Streamlit Community Cloud |

---

## Licencia

Uso personal. No se permite la reutilización del contenido de los ficheros `data/` (CV e información personal).