import streamlit as st

from src.embeddings import generate_embeddings
from src.retriever import retrieve
from src.prompt_builder import build_prompt
from src.llm import SYSTEM_PROMPT, generate_answer
from src.vector_store import collection
from offline import index_documents


# ────────────────────────────────────────────────
#  Temas canónicos de la entrevista (Cambio 2)
#  Cada tema tiene: clave interna, label visible y pregunta sugerida
# ────────────────────────────────────────────────
INTERVIEW_TOPICS = [
    {
        "key": "edad",
        "label": "Edad",
        "hint": "pregunta su edad o rango de edad de forma natural"
    },
    {
        "key": "salario",
        "label": "Expectativas salariales",
        "hint": "pregunta por su banda salarial bruta anual esperada"
    },
    {
        "key": "modelo_trabajo",
        "label": "Modelo de trabajo",
        "hint": "pregunta si prefiere remoto, híbrido o presencial y en qué proporción"
    },
    {
        "key": "disponibilidad_viaje",
        "label": "Disponibilidad para viajar",
        "hint": "pregunta si estaría dispuesto a viajar y con qué frecuencia"
    },
    {
        "key": "reubicacion",
        "label": "Disponibilidad para reubicarse",
        "hint": "pregunta si estaría abierto a reubicarse geográficamente"
    },
    {
        "key": "incorporacion",
        "label": "Disponibilidad de incorporación",
        "hint": "pregunta cuándo podría incorporarse a un nuevo puesto"
    },
    {
        "key": "motivacion",
        "label": "Motivación para cambiar de trabajo",
        "hint": "pregunta qué le motiva a buscar un nuevo rol ahora"
    },
    {
        "key": "valores",
        "label": "Valores y cultura empresarial",
        "hint": "pregunta qué valores o tipo de cultura busca en una empresa"
    },
    {
        "key": "tipo_empresa",
        "label": "Preferencia de empresa",
        "hint": "pregunta si prefiere startup, scaleup, consultora o gran empresa"
    },
    {
        "key": "fortalezas_blandas",
        "label": "Habilidades blandas",
        "hint": "pregunta por sus principales fortalezas o habilidades blandas no visibles en el CV"
    },
    {
        "key": "debilidades",
        "label": "Áreas de mejora",
        "hint": "pregunta en qué área técnica o personal siente que tiene más margen de crecimiento"
    },
    {
        "key": "hobbies",
        "label": "Hobbies e intereses",
        "hint": "pregunta por sus aficiones o intereses fuera del trabajo"
    },
    {
        "key": "rol_ideal",
        "label": "Rol ideal",
        "hint": "pregunta cómo sería su rol ideal o el proyecto en el que más le gustaría trabajar"
    },
    {
        "key": "stack_preferido",
        "label": "Stack o tecnologías preferidas",
        "hint": "pregunta con qué tecnologías o stack disfruta más trabajando"
    },
    {
        "key": "idiomas",
        "label": "Nivel de inglés u otros idiomas",
        "hint": "pregunta por su nivel de inglés (u otros idiomas) y si tiene certificaciones"
    },
]


def get_pending_topics(covered_keys: list[str]) -> list[dict]:
    """Devuelve los temas que aún no se han cubierto."""
    return [t for t in INTERVIEW_TOPICS if t["key"] not in covered_keys]


# ────────────────────────────────────────────────
#  Función auxiliar – generar knowledge.md  (Cambio 1)
# ────────────────────────────────────────────────
def show_final_markdown_generation():
    """Genera knowledge.md con esquema fijo y extracción estructurada."""
    st.subheader("📄 Contenido generado para `data/knowledge.md`")
    st.caption("Revisa, edita si quieres y luego sube el archivo a tu repo → commit → redeploy")

    # 1. Leer contenido anterior si existe
    old_content = ""
    try:
        with open("data/knowledge.md", "r", encoding="utf-8") as f:
            old_content = f.read().strip()
        if old_content:
            st.info("Se detectó un `knowledge.md` existente. El nuevo contenido lo fusionará respetando los datos anteriores.")
        else:
            st.info("El archivo `knowledge.md` está vacío o recién creado.")
    except FileNotFoundError:
        st.info("No se encontró `data/knowledge.md` → se creará uno nuevo.")
    except Exception as e:
        st.warning(f"No se pudo leer el archivo anterior: {e}")

    # 2. Preparar conversación como texto plano
    conversation_text = "\n".join(
        f"{role.upper()}: {content}"
        for role, content in st.session_state.update_history
    )

    # ── CAMBIO 1: Prompt con esquema fijo ──────────────────────────────────
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
- **Salario bruto anual esperado:** <valor o rango, ej: "45.000 – 55.000 €" o "No especificado">
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
<cualquier información relevante mencionada que no encaje en las secciones anteriores,
o vacío si no hay nada>

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

    # 3. Generar contenido
    with st.spinner("Extrayendo información y generando knowledge.md..."):
        try:
            new_md_content = generate_answer(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,   # baja temperatura → extracción más fiel
                max_tokens=1200,
                system_prompt=(
                    "Eres un extractor de información preciso. "
                    "Responde SOLO con el Markdown solicitado, sin ningún texto adicional."
                )
            )
            new_md_content = new_md_content.strip()

            # Sanity check: que empiece con #
            if not new_md_content.startswith("#"):
                new_md_content = "# Información Personal y Preferencias Profesionales\n\n" + new_md_content

            # 4. Mostrar resultado
            st.code(new_md_content, language="markdown", line_numbers=True)

            # Resumen de temas cubiertos
            covered = st.session_state.get("covered_topics", [])
            pending = get_pending_topics(covered)
            if covered:
                st.success(f"✅ Temas cubiertos en esta sesión: {', '.join(covered)}")
            if pending:
                st.warning(
                    f"⚠️ Temas no cubiertos (considera hacer otra sesión): "
                    f"{', '.join(t['label'] for t in pending)}"
                )

            # Botones de acción
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
                    st.session_state.questions_asked = 0
                    st.session_state.covered_topics = []
                    st.success("Entrevista reiniciada.")
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

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "update_history" not in st.session_state:
    st.session_state.update_history = []

if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = 0

# Cambio 2: registro de temas cubiertos
if "covered_topics" not in st.session_state:
    st.session_state.covered_topics = []


# ────────────────────────────────────────────────
#  MODO CHAT RECRUITERS
# ────────────────────────────────────────────────
if mode == "Chat":

    st.title("CVer - Pregúntame lo que quieras sobre Enrique")

    for role, content in st.session_state.messages:
        with st.chat_message("user" if role == "User" else "assistant"):
            st.markdown(content)

    if st.session_state.question_count >= 12:
        st.warning("Has alcanzado el límite de preguntas por sesión. Por favor, recarga la página para continuar.")
    else:
        if question := st.chat_input("Escribe tu pregunta aquí..."):
            st.session_state.question_count += 1

            with st.chat_message("user"):
                st.markdown(question)
            st.session_state.messages.append(("User", question))

            # RAG Pipeline
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
            st.session_state.messages.append(("CVer", answer))


# ────────────────────────────────────────────────
#  MODO ADMIN – Entrevista con cobertura garantizada  (Cambio 2)
# ────────────────────────────────────────────────
elif mode == "Admin":

    st.title("Admin Panel - Entrena a CVer con más conocimiento")

    # Autenticación
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

    # ── Bienvenida (solo la primera vez) ──────────────────────────────────
    if len(st.session_state.update_history) == 0:
        first_message = (
            "¡Hola! Soy CVer en modo actualización.\n\n"
            "Voy a hacerte preguntas para completar tu perfil con información que no está en el CV: "
            "edad, salario esperado, modelo de trabajo, disponibilidad, valores, etc.\n\n"
            "Responde con naturalidad. Escribe **terminar** cuando quieras generar el archivo.\n\n"
            "Empecemos cuando quieras 👇"
        )
        st.session_state.update_history.append(("assistant", first_message))

    # ── Barra lateral: progreso de temas ──────────────────────────────────
    with st.sidebar:
        st.markdown("### 📊 Progreso de la entrevista")
        covered = st.session_state.covered_topics
        total = len(INTERVIEW_TOPICS)
        done = len(covered)
        st.progress(done / total, text=f"{done}/{total} temas cubiertos")

        for topic in INTERVIEW_TOPICS:
            icon = "✅" if topic["key"] in covered else "⬜"
            st.markdown(f"{icon} {topic['label']}")

    # ── Mostrar historial ─────────────────────────────────────────────────
    for role, content in st.session_state.update_history:
        with st.chat_message("user" if role == "user" else "assistant"):
            st.markdown(content)

    # ── Botón de inicio (solo antes de la primera pregunta) ───────────────
    preguntas_asistente = [m for m in st.session_state.update_history if m[0] == "assistant"]

    if len(preguntas_asistente) <= 1:
        if st.button("▶️ Empezar entrevista", type="primary", use_container_width=True):
            pending = get_pending_topics(st.session_state.covered_topics)
            next_topic = pending[0] if pending else None

            system_first = (
                "Eres un entrevistador profesional y empático. "
                "Haz SOLO UNA pregunta inicial, de forma cálida y natural. "
                "No añadas introducciones largas ni numeración. "
                "Responde SOLO con la pregunta."
            )
            user_first = (
                f"Haz la pregunta sobre este tema: {next_topic['label']}. "
                f"Pista: {next_topic['hint']}."
            ) if next_topic else "Haz una pregunta de presentación general."

            primera_pregunta = generate_answer(
                messages=[
                    {"role": "system", "content": system_first},
                    {"role": "user", "content": user_first}
                ],
                temperature=0.7,
                max_tokens=150,
                system_prompt=None
            )

            st.session_state.update_history.append(("assistant", primera_pregunta))
            st.session_state.questions_asked = 1
            st.rerun()

    # ── Mostrar generación final si ya se solicitó ─────────────────────────
    if st.session_state.get("show_final", False):
        show_final_markdown_generation()

    # ── Input de respuesta ────────────────────────────────────────────────
    if user_input := st.chat_input("Tu respuesta..."):
        st.session_state.update_history.append(("user", user_input))

        # Detectar si el usuario quiere terminar
        terminar = any(
            w in user_input.lower()
            for w in ["terminar", "fin", "finalizar", "ya está", "listo", "stop", "acabar"]
        )

        if terminar:
            st.session_state.update_history.append(
                ("assistant", "¡Perfecto! Generando tu `knowledge.md` con toda la información recopilada...")
            )
            st.session_state.show_final = True
            st.rerun()

        # ── CAMBIO 2: Detectar tema cubierto en la última respuesta ────────
        pending = get_pending_topics(st.session_state.covered_topics)
        next_topic = pending[0] if pending else None

        # Prompt del entrevistador con cobertura de temas garantizada
        topics_status = "\n".join(
            f"  - {'[CUBIERTO]' if t['key'] in st.session_state.covered_topics else '[PENDIENTE]'} {t['label']}"
            for t in INTERVIEW_TOPICS
        )

        system_entrevistador = f"""Eres un entrevistador profesional que ayuda a completar el perfil de un candidato.

ESTADO ACTUAL DE LA ENTREVISTA:
- Preguntas hechas: {st.session_state.questions_asked}
- Temas cubiertos: {st.session_state.covered_topics}
- Próximo tema prioritario: {next_topic['label'] if next_topic else 'ninguno (todos cubiertos)'}

LISTA DE TEMAS:
{topics_status}

INSTRUCCIONES:
1. Analiza la respuesta del usuario y determina si ha respondido sobre el tema anterior.
2. Haz SIEMPRE UNA SOLA pregunta nueva, sobre el siguiente tema PENDIENTE más importante.
3. Si ya están todos los temas cubiertos → pregunta algo de profundización libre.
4. Formula la pregunta de forma natural y conversacional, sin numerarla.
5. NO hagas más de una pregunta.
6. Si el usuario dice "terminar" o similar → responde SOLO: FINALIZAR"""

        conversation_messages = [{"role": "system", "content": system_entrevistador}]
        for role, content in st.session_state.update_history:
            conversation_messages.append({"role": role, "content": content})

        response = generate_answer(
            messages=conversation_messages,
            temperature=0.7,
            max_tokens=200,
            system_prompt=None
        )

        # Marcar el tema anterior como cubierto si había uno pendiente
        if next_topic and next_topic["key"] not in st.session_state.covered_topics:
            st.session_state.covered_topics.append(next_topic["key"])

        st.session_state.update_history.append(("assistant", response))
        st.session_state.questions_asked += 1

        if "FINALIZAR" in response.upper():
            st.session_state.show_final = True

        st.rerun()