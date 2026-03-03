# Wrapper del modelo de embeddings
from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-3-large"
    )
    return [item.embedding for item in response.data]