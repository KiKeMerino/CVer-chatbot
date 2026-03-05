import streamlit as st

from src.embeddings import generate_embeddings
from src.retriever import retrieve
from src.prompt_builder import build_prompt
from src.llm import generate_answer
from src.vector_store import collection
from offline import index_documents


# ────────────────────────────────────────────────
#  Función auxiliar – generar personal_info.md
# ────────────────────────────────────────────────
def show_final_markdown_generation():
    st.subheader("Contenido sugerido para personal_info.md")

    # Leemos el archivo actual si existe
    try:
        with open("knowledge.md", "r", encoding="utf-8") as f:
            old_content = f.read().strip()
    except FileNotFoundError:
        old_content = "# Información adicional\n(archivo creado automáticamente)"

    conversation_text = "\n".join([f"{r}: {c}" for r, c in st.session_state.update_history])

    prompt_md = f"""Toma la conversación siguiente y la información anterior y genera un archivo Markdown limpio y bien estructurado.

Información anterior:
{old_content}

Conversación de actualización:
{conversation_text}

Reglas:
- Usa encabezados nivel 2 y 3
- Usa viñetas y listas cuando corresponda
- Mantén lo anterior si no se contradice
- Añade o actualiza la información nueva
- No inventes datos
- Responde SOLO con el contenido Markdown, sin explicaciones adicionales"""

    new_md_content = generate_answer(prompt_md)

    st.code(new_md_content, language="markdown")

    st.download_button(
        label="Descargar personal_info.md",
        data=new_md_content,
        file_name="personal_info.md",
        mime="text/markdown"
    )

    st.info("Pasos siguientes:\n1. Copia el contenido de arriba\n2. Pégalo (o fusiónalo) en personal_info.md\n3. Commit & push\n4. Streamlit redeployará automáticamente")

# ────────────────────────────────────────────────
#  Configuración inicial
# ────────────────────────────────────────────────
st.set_page_config(page_title="CVer - Enrique", page_icon=":robot_face:", layout="wide")

@st.cache_resource
def init_db():
    if collection.count() == 0:
        index_documents()


ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "temporal1234")

# ────────────────────────────────────────────────
#  Selección de modo
# ────────────────────────────────────────────────
mode = st.sidebar.radio("Selecciona modo", ["Chat", "Admin"], index=0)


# ────────────────────────────────────────────────
#  Estado global
# ────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "update_history" not in st.session_state:
    st.session_state.update_history = []

if "question_asked" not in st.session_state:
    st.session_state.question_asked = 0


# ────────────────────────────────────────────────
#  MODO CHAT RECRUITERS
# ────────────────────────────────────────────────
if mode == "Chat":

    st.title("CVer - Preguntame lo que quieras sobre Enrique")

    # Mostrar historial de conversación
    for role, content in st.session_state.messages:
        with st.chat_message("user" if role == "User" else "assistant"):
            st.markdown(content)

    #  Poner limite de preguntas por sesión
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0

    # Limite de preguntas por sesión
    if st.session_state.question_count >= 12:
        st.warning("Has alcanzado el límite de preguntas por sesión. Por favor, recarga la página para continuar.")
        
    else:
        if question:= st.chat_input("Escribe tu pregunta aquí..."):
            st.session_state.question_count += 1

            with st.chat_message("user"):
                st.markdown(question)
            st.session_state.messages.append(("User", question))


            # RAG Pipeline

            # 1 Generate embedding of the query
            query_embedding = generate_embeddings([question])[0]

            # 2 Retrieve relevant chunks
            context_chunks, _ = retrieve(query_embedding)

            # 3 Build prompt
            prompt = build_prompt(context_chunks, question)

            # 4 Generate answer
            answer = generate_answer(prompt)

            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.messages.append(("CVer", answer))


# ────────────────────────────────────────────────
#  MODO OWNER – Entrevista para ampliar conocimiento
# ────────────────────────────────────────────────
elif mode == "Admin":

    st.title("Admin Panel - Entrena a CVer con más conocimiento")

    # Autenticación simple
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        pw = st.text_input("Enter admin password:", type="password")
        if st.button("Login"):
            if pw == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
                # st.success("Authenticated successfully!")
            else:
                st.error("Contraseña incorrecta")
        st.stop()

    # Entrevista
# ── Mensaje de bienvenida e inicio automático ─────────────────────────────
    if len(st.session_state.update_history) == 0:
        # Solo la primera vez (o después de reset)
        first_message = (
            "¡Hola! Soy CVer en modo actualización.\n\n"
            "Voy a hacerte una serie de preguntas para conocer mejor tus preferencias, "
            "expectativas y detalles que no están en el CV.\n"
            "Responde con naturalidad. Cuando quieras terminar escribe: **terminar**\n\n"
            "Empecemos..."
        )
        
        st.session_state.update_history.append(("assistant", first_message))
        # st.rerun()
        
    # Mostrar hiostiral de actualización
    for role, content in st.session_state.update_history:
        with st.chat_message("user" if role == "User" else "assistant"):
            st.markdown(content)

    # ──────────────────────────────────────────────────────────────
    # Botón solo visible si todavía no hemos hecho ninguna pregunta real
    # ──────────────────────────────────────────────────────────────
    preguntas_asistente = [msg[1] for msg in st.session_state.update_history if msg[0] == "assistant"]

    if len(preguntas_asistente) <= 1:  # solo bienvenida → mostramos botón
        if st.button("🚀 Empezar - Hazme la primera pregunta", type="primary", use_container_width=True):
            with st.spinner("Preparando primera pregunta..."):
                primera_pregunta_prompt = """Eres un entrevistador profesional y empático.
                Haz SOLO UNA pregunta inicial inteligente y natural para ampliar el perfil de una persona.
                Elige entre estos temas (elige uno diferente cada vez que sea posible):
                - expectativas salariales actuales
                - preferencia de modelo de trabajo (remoto / híbrido / presencial)
                - disponibilidad para viajar o reubicación
                - rango de edad aproximado (si se siente cómodo compartiendo)
                - principales valores o cultura empresarial deseada
                - fortalezas o habilidades blandas no visibles en el CV
                - motivación principal para buscar nuevo rol
                - preferencias de tamaño de empresa o sector

                Formula la pregunta de forma cálida y profesional.
                NO hagas más de una pregunta. NO añadas introducciones largas.
                Responde SOLO con la pregunta (sin numerarla ni poner "Pregunta 1:")."""

                # Generamos la pregunta con el LLM
                primera_pregunta = generate_answer(primera_pregunta_prompt)

                st.session_state.update_history.append(("assistant", primera_pregunta))
                st.session_state.questions_asked = 1
                st.rerun()





    if prompt := st.chat_input("Tu respuesta..."):
        st.session_state.update_history.append(("User", prompt))

        # Prompt para que el LLM actúe  como entrevistador
        system_prompt = f"""Eres un entrevistador profesional que me ayuda a completar mi perfil y que conoce perfectamente todo lo que ya me has preguntado.
Historial completo de preguntas ya hechas:
{[msg[1] for msg in st.session_state.update_history if msg[0] == "assistant"]}
Ya has hecho {st.session_state.questions_asked} preguntas.
Haz SIEMPRE solo UNA pregunta nueva relevante.
Temas interesantes: edad, expectativas salariales, modelo de trabajo preferido (remoto/híbrido), disponibilidad para viajar, pretensiones de sueldo, valores, fortalezas no visibles en CV, hobbies relevantes para el trabajo, preferencias de equipo, razones para cambiar de trabajo, etc.
No repitas temas ya preguntados.
Si el usuario dice "terminar" o similar → responde SOLO con la palabra FINALIZAR (en mayúsculas)."""
        
        # Llamada al LLM (adapta según tu función)
        full_history = [{"role": "system", "content": system_prompt}]
        for role, content in st.session_state.update_history:
            full_history.append({"role": role, "content": content})

        # response = generate_answer(full_history)   # si tu función acepta lista de dicts
        response = generate_answer("\n".join([f"{r}: {c}" for r,c in st.session_state.update_history]))

        st.session_state.update_history.append(("assistant", response))
        st.session_state.questions_asked += 1

        if "FINALIZAR" in response.upper():
            show_final_markdown_generation()
            
        st.rerun()

