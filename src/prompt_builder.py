# Construccion del prompt

def build_prompt(context_chunks, user_query):
    context = "\n\n".join(context_chunks)

    prompt = f"""
    Context: {context}

    Question: {user_query}
    """

    return prompt