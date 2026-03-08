# Lógica de chunking: dividir el texto en partes manejables para el modelo


def chunk_text(content: str):
    """
    Chunking semántico del CV.

    Estrategia: un chunk por subsección (###), pero cada chunk incluye
    el nombre de la sección padre (##) como prefijo explícito en el texto.

    Esto resuelve dos problemas:
    - El embedding no se diluye (chunks cortos y concretos)
    - El retriever conecta bien "experiencia en NTT Data" porque el chunk
      dice explícitamente "[Experiencia laboral] NTT Data – Junior Engineer"
    """
    chunks = []
    current_section = None
    current_chunk = None

    lines = content.split("\n")

    for line in lines:
        line = line.strip()

        # ── Sección principal (##) ─────────────────────────────────────────
        if line.startswith("## "):
            # Cerrar chunk anterior
            if current_chunk and current_chunk["text"].strip():
                chunks.append(current_chunk)

            current_section = line[3:].strip()

            # Chunk inicial de sección (para contenido antes del primer ###)
            current_chunk = {
                "text": f"[{current_section}]\n",
                "metadata": {"section": current_section}
            }

        # ── Subsección (###) ──────────────────────────────────────────────
        elif line.startswith("### "):
            # Cerrar chunk anterior
            if current_chunk and current_chunk["text"].strip():
                chunks.append(current_chunk)

            subsection = line[4:].strip()

            # El prefijo "[Sección > Subsección]" es lo que permite al retriever
            # conectar preguntas como "¿cuándo trabajaste en NTT Data?" con este chunk
            current_chunk = {
                "text": f"[{current_section} > {subsection}]\n",
                "metadata": {
                    "section": current_section,
                    "subsection": subsection
                }
            }

        # ── Texto normal ───────────────────────────────────────────────────
        else:
            if current_chunk and line:
                current_chunk["text"] += line + "\n"

    # Guardar último chunk
    if current_chunk and current_chunk["text"].strip():
        chunks.append(current_chunk)

    return chunks


def load_and_chunk_documents():
    """
    Carga cv.md y knowledge.md y los chunkea.
    Si knowledge.md no existe, se omite sin error.
    """
    chunks = []
    files = ["data/cv.md", "data/knowledge.md", "data/projects.md"]

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                text = f.read()
            for chunk in chunk_text(text):
                source = "CV" if file == "data/cv.md" else ("Personal Info" if file == "data/knowledge.md" else "Projects")
                chunks.append({
                    "text": chunk["text"],
                    "metadata": {**chunk["metadata"], "source": source}
                })
        except FileNotFoundError:
            print(f"⚠️  {file} no encontrado. Se omite en la indexación.")

        except Exception as e:
            print(f"❌ Error al procesar {file}: {e}")

    return chunks