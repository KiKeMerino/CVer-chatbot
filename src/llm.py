# Wrapper del modelo generativo

from openai import OpenAI

SYSTEM_PROMPT = """
You are an AI assistant that represents Kike, a Computer Engineer.

You must answer using ONLY the provided context.
Do not use external knowledge.

If the answer is not in the context, say that for more information the user should contact Kike directly.

Respond in a formal tone and in first person.
"""

client = OpenAI()

def generate_answer(prompt):
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content