# Construccion del prompt

MAX_HISTORY_TURNS = 3

def build_prompt(context_chunks, user_query, chat_history=None):

    # ── 1. Contexto RAG ──────────────────────────────────────────────────
    context = "\n\n".join(context_chunks)

    # ── 2. Historial reciente (últimos N turnos) ─────────────────────────
    history_text = ""
    if chat_history:
        recent = chat_history[-(MAX_HISTORY_TURNS * 2):]
        history_lines = []
        for role, content in recent:
            label = "Usuario" if role == "user" else "Tú (Enrique)"
            history_lines.append(f"{label}: {content}")
        history_text = "\n".join(history_lines)

    # ── 3. Construcción del prompt ────────────────────────────────────────
    prompt_parts = []
    prompt_parts.append("### CONTEXTO RELEVANTE DE TU PERFIL ###")
    prompt_parts.append(context if context else "(No se encontró contexto relevante)")

    if history_text:
        prompt_parts.append("\n### CONVERSACIÓN RECIENTE ###")
        prompt_parts.append(history_text)

    prompt_parts.append("\n### PREGUNTA ACTUAL ###")
    prompt_parts.append(user_query)

    return "\n\n".join(prompt_parts)