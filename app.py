import streamlit as st

from styles import MODERN_CSS
from src.embeddings import generate_embeddings
from src.retriever import retrieve
from src.prompt_builder import build_prompt
from src.llm import SYSTEM_PROMPT, generate_answer
from src.vector_store import collection
from offline import index_documents


EXAMPLE_QUESTIONS = [
    "¿Cuál es tu experiencia con Python?",
    "¿Qué proyectos de IA has desarrollado?",
    "¿Cómo trabajas en equipo?",
    "¿Cuáles son tus expectativas salariales?",
    "¿Tienes experiencia con arquitecturas cloud?",
    "¿Qué stack tecnológico dominas?",
    "¿Cuándo podrías incorporarte?",
    "¿Prefieres trabajo remoto o presencial?"
]


# ────────────────────────────────────────────────
#  Configuración inicial
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Enrique | CV interactivo",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="auto"
)

# Inject CSS
st.markdown(MODERN_CSS, unsafe_allow_html=True)

# Init DB
@st.cache_resource
def init_db():
    if collection.count() == 0:
        index_documents()

init_db()

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "temporal1234")


# ────────────────────────────────────────────────
#  Estado global
# ────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# En modo chat, limite de 12 preguntas
if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "update_history" not in st.session_state:
    st.session_state.update_history = []

# En modo admin, registro de preguntas para el "Ya has hecho X preguntas"
if "show_final" not in st.session_state:
    st.session_state.show_final = False


# ────────────────────────────────────────────────
#  Sidebar
# ────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">// navegación</div>', unsafe_allow_html=True)
    mode = st.radio("Modo", ["Chat", "Admin"], index=0)
    # st.markdown("---")
    # st.markdown('<div class="sidebar-title">// estado</div>', unsafe_allow_html=True)
    # st.markdown(f"`chunks_indexados: {collection.count()}`")
    # st.markdown(f"`preguntas_sesión: {st.session_state.question_count}`")

# ────────────────────────────────────────────────
#  MODO CHAT RECRUITERS
# ────────────────────────────────────────────────
if mode == "Chat":

    # ── Hero ──────────────────────────────────────
    st.markdown("""
    <div class="hero-wrap">
        <!-- <div class="hero-prompt">// init_session.py → conectando...</div> -->
        <div class="hero-name">¡Bienvendo! Soy Enrique</div>
        <p class="hero-bio">
            Ingeniero informático especializado en <span>Data Science</span> e Inteligencia Artificial.<br>
            Aquí puedes explorar mi experiencia profesional, consultar mi stack de tecnologías y entender cómo puedo aportar valor a tu equipo.<br>
            Siéntete libre de profundizar en mis proyectos o ponerme a prueba con preguntas técnicas de entrevista. ¿Por dónde te gustaría empezar?
        </p>
        <div class="hero-tags">
            <span class="tag">Python</span>
            <span class="tag">Machine Learning</span>
            <span class="tag">RAG</span>
            <span class="tag">LLMs</span>
            <span class="tag">SQL</span>
            <span class="tag">Cloud</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sugerencias ───────────────────────────────
    if len(st.session_state.messages) >= 0:
        st.markdown('<div class="section-label">// preguntas sugeridas — haz click para empezar</div>', unsafe_allow_html=True)

        cols = st.columns(2)
        for i, q in enumerate(EXAMPLE_QUESTIONS):
            with cols[i % 2]:
                if st.button(q, key=f"chip_{i}", use_container_width=True):
                    st.session_state.prefill_question = q
                    st.rerun()

        st.markdown("---")


    # ── Historial de mensajes ──────────────────────
    if st.session_state.messages:
        st.markdown('<div class="section-label">// conversación activa</div>', unsafe_allow_html=True)

    for role, content in st.session_state.messages:
        with st.chat_message(role):
            st.markdown(content)

    # ── Límite de preguntas ────────────────────────
    if st.session_state.question_count >= 12:
        st.warning("⚠ límite de sesión alcanzado (12 preguntas). Recarga la página para continuar.")
    else:
        # Mostrar contador si ya hay mensajes
        if st.session_state.question_count > 0:
            st.markdown(
                f'<div class="q-counter">{st.session_state.question_count}/12 preguntas usadas</div>',
                unsafe_allow_html=True
            )

        # Pre-rellenar si viene de un chip
        prefill = st.session_state.pop("prefill_question", None) if "prefill_question" in st.session_state else None

        question = st.chat_input("\tEscribe tu pregunta o usa una sugerencia arriba...")

        # Usar chip o input manual
        if prefill and not question:
            question = prefill

        if question:
            st.session_state.question_count += 1

            with st.chat_message("user"):
                st.markdown(question)
            st.session_state.messages.append(("user", question))

            # RAG Pipeline
            with st.spinner(""):
                query_embedding = generate_embeddings([question])[0]
                context_chunks, _ = retrieve(query_embedding)
                prompt = build_prompt(context_chunks, question)
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
                answer = generate_answer(messages)

            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.messages.append(("assistant", answer))
            st.rerun()


# ────────────────────────────────────────────────
#  MODO ADMIN – Entrevista con cobertura garantizada
# ────────────────────────────────────────────────
elif mode == "Admin":

    st.title("Admin Panel - Entrena a CVer con más conocimiento")

    # ── Autenticación ─────────────────────────────────────────────────────
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        pw = st.text_input("Contraseña de admin:", type="password")
        if st.button("Entrar"):
            if pw == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
        st.stop()

    # ── Panel de reindexación ─────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🔧 Gestión del índice")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Chunks indexados", collection.count())
    with col2:
        if st.button("🔄 Forzar reindexación", type="primary", use_container_width=True):
            with st.spinner("Reindexando..."):
                st.cache_resource.clear()
                from src.vector_store import clear_documents
                clear_documents()
                index_documents()
                st.success(f"✅ Reindexado. Chunks ahora: {collection.count()}")
                st.rerun()

    st.markdown("---")