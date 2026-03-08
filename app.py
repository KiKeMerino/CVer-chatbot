import streamlit as st
from config import STYLE
from tracker import log_visit, log_question, get_stats
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
    "¿Tienes experiencia con arquitecturas cloud?",
    "¿Qué stack tecnológico dominas?",
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
st.markdown(STYLE, unsafe_allow_html=True)


# ── Google Analytics ──────────────────────────
GA_ID = st.secrets.get("analytics", {}).get("ga_measurement_id", "")
if GA_ID:
    st.markdown(f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA_ID}');
    </script>
    """, unsafe_allow_html=True)

# ── Registrar visita (una vez por sesión) ─────
log_visit()

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
        <div class="hero-name">¡Bienvenido! Soy Enrique</div>
        <p class="hero-bio">
            Ingeniero informático especializado en <span>Data Science</span> e Inteligencia Artificial.<br>
            Aquí podrás conocer a fondo mi experiencia y las herramientas que domino.<br>
            Siéntete libre de navegar por mi portfolio o hacerme las preguntas que quieras. ¿Por dónde te gustaría empezar?
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
            log_question(question)
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
    # ── Estadísticas ──────────────────────────────────────────────────────
    st.subheader("📊 Estadísticas de uso")

    with st.spinner("Cargando datos..."):
        stats = get_stats()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Visitas totales", stats["total_visits"])
    with col2:
        st.metric("Visitantes únicos", stats["unique_visitors"])
    with col3:
        st.metric("Preguntas totales", stats["total_questions"])

    if stats["top_questions"]:
        st.markdown("---")
        st.markdown("**🔝 Preguntas más frecuentes**")
        for q, count in stats["top_questions"]:
            st.markdown(f"- `{count}x` &nbsp; {q}", unsafe_allow_html=True)

    if stats["recent_questions"]:
        st.markdown("---")
        st.markdown("**🕐 Últimas preguntas**")
        for ts, visitor_id, q in stats["recent_questions"]:
            st.markdown(
                f"<div style='margin-bottom:0.6rem'>"
                f"<span style='color:#3d4460;font-size:0.75rem'>{ts} &nbsp;·&nbsp; "
                f"<code style='font-size:0.72rem'>#{visitor_id}</code></span><br>{q}"
                f"</div>",
                unsafe_allow_html=True
            )