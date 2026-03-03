# Lógica de chunking: dividir el texto en partes manejables para el modelo

with open('data/cv.md', 'r', encoding='utf-8') as file:
    content = file.read()


def chunk_text(content: str):
    chunks = []
    current_section = None
    current_subsection = None
    current_chunk = None

    lines = content.split("\n")

    for line in lines:
        line = line.strip()

        # --- Sección principal ---
        if line.startswith("## "):
            # Cerrar chunk anterior si tiene contenido
            if current_chunk and current_chunk["text"].strip():
                chunks.append(current_chunk)

            current_section = line[3:].strip()
            current_subsection = None

            # Crear nuevo chunk para posibles secciones sin ###
            current_chunk = {
                "text": "",
                "metadata": {
                    "section": current_section
                }
            }

        # --- Subsección (unidad semántica real) ---
        elif line.startswith("### "):
            # Cerrar chunk anterior si tiene contenido
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

        # --- Texto normal ---
        else:
            if current_chunk:
                current_chunk["text"] += line + "\n"

    # Guardar último chunk si tiene contenido
    if current_chunk and current_chunk["text"].strip():
        chunks.append(current_chunk)

    return chunks