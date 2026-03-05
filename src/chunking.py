# Lógica de chunking: dividir el texto en partes manejables para el modelo


def chunk_text(content: str):
    """
    Chunking semántico por secciones (##) y subsecciones (###).
    Usado para el CV, que tiene estructura narrativa.
    """
    chunks = []
    current_section = None
    current_subsection = None
    current_chunk = None

    lines = content.split("\n")

    for line in lines:
        line = line.strip()

        if line.startswith("## "):
            if current_chunk and current_chunk["text"].strip():
                chunks.append(current_chunk)

            current_section = line[3:].strip()
            current_subsection = None
            current_chunk = {
                "text": "",
                "metadata": {"section": current_section}
            }

        elif line.startswith("### "):
            if current_chunk and current_chunk["text"].strip():
                chunks.append(current_chunk)

            current_subsection = line[4:].strip()
            current_chunk = {
                "text": "",
                "metadata": {
                    "section": current_section,
                    "subsection": current_subsection
                }
            }

        else:
            if current_chunk:
                current_chunk["text"] += line + "\n"

    if current_chunk and current_chunk["text"].strip():
        chunks.append(current_chunk)

    return chunks


def chunk_knowledge(content: str):
    """
    Chunking semántico para knowledge.md.

    Estrategia: un chunk por cada campo individual (línea de bullet "- **Campo:** valor").
    Esto permite al retriever recuperar exactamente el dato relevante
    cuando el recruiter pregunta por salario, edad, modelo de trabajo, etc.

    Cada chunk contiene:
      - text: "Campo: valor"  (limpio, sin Markdown)
      - metadata: section, field, value
    
    Además se genera un chunk de sección agrupada para preguntas más amplias.
    """
    chunks = []
    current_section = None
    section_lines = []

    lines = content.split("\n")

    for line in lines:
        stripped = line.strip()

        # ── Nueva sección principal ────────────────────────────────────────
        if stripped.startswith("## "):
            # Guardar chunk agrupado de la sección anterior
            if current_section and section_lines:
                section_text = "\n".join(section_lines).strip()
                if section_text:
                    chunks.append({
                        "text": f"[Sección: {current_section}]\n{section_text}",
                        "metadata": {
                            "section": current_section,
                            "chunk_type": "section_summary"
                        }
                    })
            current_section = stripped[3:].strip()
            section_lines = []

        # ── Campo individual (bullet con **Clave:** valor) ─────────────────
        elif stripped.startswith("- **") and ":**" in stripped and current_section:
            # Extraer campo y valor
            # Formato esperado: - **Campo:** valor
            inner = stripped[2:]  # quitar "- "
            try:
                field_part, value_part = inner.split(":**", 1)
                field = field_part.replace("**", "").strip()
                value = value_part.strip()
            except ValueError:
                # Línea con formato inesperado → la añadimos al buffer de sección
                section_lines.append(stripped)
                continue

            # Ignorar campos vacíos o "No especificado" para no contaminar el índice
            if value and value.lower() not in ("no especificado", ""):
                chunk_text = f"{field}: {value}"
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "section": current_section,
                        "field": field,
                        "value": value,
                        "chunk_type": "field"
                    }
                })

            # Añadir siempre al buffer de sección (incluye "No especificado" para el resumen)
            section_lines.append(f"{field}: {value}")

        # ── Línea de texto libre (notas adicionales, listas sin bullet **) ──
        elif stripped and not stripped.startswith("#"):
            section_lines.append(stripped)

    # Guardar el último chunk de sección
    if current_section and section_lines:
        section_text = "\n".join(section_lines).strip()
        if section_text:
            chunks.append({
                "text": f"[Sección: {current_section}]\n{section_text}",
                "metadata": {
                    "section": current_section,
                    "chunk_type": "section_summary"
                }
            })

    return chunks


def load_and_chunk_documents():
    """
    Carga CV y knowledge.md aplicando estrategias de chunking diferenciadas:
    - CV       → chunk_text()      (semántico por sección/subsección)
    - knowledge → chunk_knowledge() (un chunk por campo + resúmenes de sección)
    """
    chunks = []

    # ── CV ────────────────────────────────────────────────────────────────
    with open("data/cv.md", "r", encoding="utf-8") as f:
        cv_text = f.read()

    for chunk in chunk_text(cv_text):
        chunks.append({
            "text": chunk["text"],
            "metadata": {**chunk["metadata"], "source": "CV"}
        })

    # ── knowledge.md ─────────────────────────────────────────────────────
    try:
        with open("data/knowledge.md", "r", encoding="utf-8") as f:
            knowledge_text = f.read()

        for chunk in chunk_knowledge(knowledge_text):
            chunks.append({
                "text": chunk["text"],
                "metadata": {**chunk["metadata"], "source": "Personal Info"}
            })

    except FileNotFoundError:
        print("⚠️  data/knowledge.md no encontrado. Se omite en la indexación.")

    return chunks