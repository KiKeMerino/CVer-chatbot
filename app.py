import streamlit as st

from src.embeddings import generate_embeddings
from src.retriever import retrieve
from src.prompt_builder import build_prompt
from src.llm import SYSTEM_PROMPT, generate_answer
from src.vector_store import collection
from offline import index_documents


# ────────────────────────────────────────────────
#  Función auxiliar – leer knowledge.md
# ────────────────────────────────────────────────
def read_knowledge() -> str:
    try:
        with open("data/knowledge.md", "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


# ────────────────────────────────────────────────
#  Función auxiliar – generar knowledge.md
# ────────────────────────────────────────────────
def show_final_markdown_generation():
    st.subheader("📄 Contenido generado para `data/knowledge.md`")
    st.caption("Revisa, edita si quieres y luego sube el archivo a tu repo → commit → redeploy")

    old_content = read_knowledge()
    if old_content:
        st.info("Se detectó un `knowledge.md` existente. El nuevo contenido lo fusionará respetando los datos anteriores.")
    else:
        st.info("No se encontró `data/knowledge.md` → se creará uno nuevo.")

    conversation_text = "\n".join(
        f"{role.upper()}: {content}"
        for role, content in st.session_state.update_history
    )

    prompt = f"""Eres un extractor de información personal y profesional muy preciso.

Tu tarea es generar (o actualizar) el archivo `knowledge.md` de un profesional técnico
combinando el contenido anterior con lo extraído de la conversación.

══════════════════════════════════════════════
ESQUEMA OBLIGATORIO (respeta exactamente estas secciones y este orden):
══════════════════════════════════════════════

# Información Personal y Preferencias Profesionales

## Datos personales
- **Edad:** <valor o "No especificado">
- **Idiomas:** <valor o "No especificado">

## Expectativas económicas
- **Salario bruto anual esperado:** <valor o rango, ej: "45.000 - 55.000 €" o "No especificado">
- **Tipo de contrato preferido:** <valor o "No especificado">

## Modelo de trabajo
- **Modalidad preferida:** <Remoto / Híbrido / Presencial / No especificado>
- **Proporción híbrido (si aplica):** <ej: "3 días remoto, 2 presencial" o "No especificado">
- **Disponibilidad para viajar:** <valor o "No especificado">
- **Disponibilidad para reubicarse:** <Sí / No / Depende / No especificado>

## Disponibilidad
- **Fecha de incorporación:** <ej: "Inmediata", "2 semanas", "1 mes" o "No especificado">
- **Situación laboral actual:** <En activo / En búsqueda activa / No especificado>

## Motivación y búsqueda
- **Razón principal para cambiar:** <valor o "No especificado">
- **Tipo de empresa preferida:** <Startup / Scaleup / Consultora / Gran empresa / No especificado>
- **Sector de interés:** <valor o "No especificado">
- **Rol ideal:** <valor o "No especificado">

## Valores y cultura
- **Valores que busca en una empresa:** <lista o "No especificado">
- **Cultura empresarial deseada:** <descripción o "No especificado">

## Habilidades y perfil
- **Fortalezas blandas destacadas:** <lista o "No especificado">
- **Áreas de mejora reconocidas:** <valor o "No especificado">
- **Stack o tecnologías preferidas:** <lista o "No especificado">

## Intereses personales
- **Hobbies o aficiones:** <lista o "No especificado">
- **Proyectos personales relevantes:** <valor o "No especificado">

## Notas adicionales
<cualquier información relevante mencionada que no encaje en las secciones anteriores, o vacío si no hay nada>

══════════════════════════════════════════════
REGLAS DE EXTRACCIÓN:
══════════════════════════════════════════════
1. Extrae SOLO datos mencionados EXPLÍCITAMENTE en la conversación o en el contenido anterior.
2. NUNCA inventes, supongas ni completes con valores típicos.
3. Si un dato no aparece → escribe "No especificado" (nunca lo omitas).
4. Si hay conflicto entre contenido anterior y conversación → usa el dato de la conversación (es más reciente).
5. Si el contenido anterior tiene un dato y la conversación no lo menciona → conserva el anterior.
6. Responde ÚNICAMENTE con el Markdown. Sin explicaciones, sin ```markdown, sin texto extra.

══════════════════════════════════════════════
CONTENIDO ANTERIOR:
══════════════════════════════════════════════
{old_content if old_content else "(ninguno)"}

══════════════════════════════════════════════
CONVERSACIÓN:
══════════════════════════════════════════════
{conversation_text}

Genera el archivo completo ahora:"""

    with st.spinner("Extrayendo información y generando knowledge.md..."):
        try:
            new_md_content = generate_answer(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1200,
                system_prompt=(
                    "Eres un extractor de información preciso. "
                    "Responde SOLO con el Markdown solicitado, sin ningún texto adicional."
                )
            )
            new_md_content = new_md_content.strip()

            if not new_md_content.startswith("#"):
                new_md_content = "# Información Personal y Preferencias Profesionales\n\n" + new_md_content

            st.code(new_md_content, language="markdown", line_numbers=True)

            col1, col2 = st.columns([3, 1])
            with col1:
                st.download_button(
                    label="⬇️ Descargar knowledge.md",
                    data=new_md_content,
                    file_name="knowledge.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with col2:
                if st.button("🔄 Resetear entrevista", type="secondary", use_container_width=True):
                    st.session_state.update_history = []
                    st.session_state.show_final = False
                    st.rerun()

            st.markdown("---")
            st.markdown(
                "**Siguientes pasos:**\n"
                "1. Revisa el contenido generado arriba\n"
                "2. Descarga el archivo con el botón\n"
                "3. Cópialo a `data/knowledge.md` en tu repositorio\n"
                "4. Commit & push → Streamlit redeployará automáticamente\n"
            )

        except Exception as e:
            st.error(f"Error al generar el contenido: {str(e)}")

# ────────────────────────────────────────────────
#  Configuración inicial
# ────────────────────────────────────────────────
st.set_page_config(page_title="CVer - Enrique", page_icon=":robot_face:", layout="wide")

# Reindexar documentos al iniciar la app (una vez por sesión)
@st.cache_resource
def init_db():
    if collection.count() == 0:
        index_documents()

init_db()

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

# En modo chat, limite de 12 preguntas
if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "update_history" not in st.session_state:
    st.session_state.update_history = []

# En modo admin, registro de preguntas para el "Ya has hecho X preguntas"
if "show_final" not in st.session_state:
    st.session_state.show_final = False


# Ver las variables de estado para debugging
# st.write("Estado de la sesión:", st.session_state)

# ────────────────────────────────────────────────
#  MODO CHAT RECRUITERS (beta)
# ────────────────────────────────────────────────
if mode == "Chat":

    st.title("Soy Enrique, preguntame lo que quieras sobre mi")

    for role, content in st.session_state.messages:
        with st.chat_message(role):
            st.markdown(content)

    if st.session_state.question_count >= 12:
        st.warning("Has alcanzado el límite de preguntas por sesión. Por favor, recarga la página para continuar.")
        
    else:
        if question := st.chat_input("Escribe tu pregunta aquí..."):
            st.session_state.question_count += 1

            # Escribo la pregunta del usuario en el chat
            with st.chat_message("user"):
                st.markdown(question)
            st.session_state.messages.append(("user", question))

            # RAG Pipeline
            query_embedding = generate_embeddings([question])[0]
            context_chunks, _ = retrieve(query_embedding)
            prompt = build_prompt(context_chunks, question)
        
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            answer = generate_answer(messages)

            # Escribo la respuesta del asistente en el chat
            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.messages.append(("assistant", answer))


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

    # ── Bienvenida (solo la primera vez) ──────────────────────────────────
    if len(st.session_state.update_history) == 0:
        st.session_state.update_history.append((
            "assistant",
            "¡Hola! Voy a hacerte preguntas para completar tu perfil con información "
            "que no está en el CV o que aparece como 'No especificado'.\n\n"
            "Responde con naturalidad. Escribe **terminar** cuando quieras generar el archivo.\n\n"
            "Pulsa el botón para empezar 👇"
        ))

    # ── Mostrar historial ─────────────────────────────────────────────────
    for role, content in st.session_state.update_history:
        with st.chat_message(role):
            st.markdown(content)

    # ── Botón de inicio (solo con el mensaje de bienvenida) ───────────────
    if len(st.session_state.update_history) == 1:
        if st.button("Empezar entrevista", type="primary", use_container_width=True):
            knowledge_content = read_knowledge()

            primera_pregunta = generate_answer(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un entrevistador profesional y empático. "
                            "Haz SOLO UNA pregunta, de forma cálida y natural, "
                            "sin introducciones ni numeración. Responde SOLO con la pregunta."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Este es el perfil actual del candidato:\n\n"
                            f"{knowledge_content if knowledge_content else '(vacío, no hay información todavía)'}\n\n"
                            "Los campos con valor 'No especificado' o vacíos son los que necesitas cubrir. "
                            "Elige uno y haz una pregunta natural para obtener esa información."
                        )
                    }
                ],
                temperature=0.8,
                max_tokens=150,
                system_prompt=None
            )

            st.session_state.update_history.append(("assistant", primera_pregunta))
            st.rerun()

    # ── Mostrar generación final ───────────────────────────────────────────
    if st.session_state.show_final:
        show_final_markdown_generation()

    # ── Input de respuesta (solo cuando ya hay conversación activa) ────────
    elif len(st.session_state.update_history) > 1:
        if user_input := st.chat_input("Tu respuesta..."):
            st.session_state.update_history.append(("user", user_input))

            # Detectar si el usuario quiere terminar
            terminar = any(
                w in user_input.lower()
                for w in ["terminar", "finalizar", "fin", "stop", "acabar", "listo", "ya está"]
            )

            if terminar:
                st.session_state.update_history.append((
                    "assistant",
                    "¡Perfecto! Generando tu `knowledge.md` con toda la información recopilada..."
                ))
                st.session_state.show_final = True
                st.rerun()

            # El LLM decide la siguiente pregunta leyendo knowledge.md y la conversación
            knowledge_content = read_knowledge()

            system_entrevistador = f"""Eres un entrevistador profesional que ayuda a completar el perfil de un candidato.

Este es su perfil actual en knowledge.md:
{knowledge_content if knowledge_content else "(vacío)"}

INSTRUCCIONES:
1. Identifica qué campos del perfil siguen siendo "No especificado" o vacíos.
2. Haz UNA SOLA pregunta natural sobre uno de esos campos, sin repetir preguntas ya hechas.
3. No numeres ni introduzcas la pregunta, ve directo.
4. Si el usuario dice "terminar" o similar → responde SOLO: FINALIZAR"""

            conversation_messages = [{"role": "system", "content": system_entrevistador}]
            for role, content in st.session_state.update_history:
                conversation_messages.append({"role": role, "content": content})

            response = generate_answer(
                messages=conversation_messages,
                temperature=0.8,
                max_tokens=200,
                system_prompt=None
            )

            if "FINALIZAR" in response.upper():
                st.session_state.show_final = True
            else:
                st.session_state.update_history.append(("assistant", response))

            st.rerun()