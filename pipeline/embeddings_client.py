import os
import requests

AZ_OPENAI_ENDPOINT = os.getenv("AZ_OPENAI_ENDPOINT")  
AZ_OPENAI_KEY = os.getenv("AZ_OPENAI_KEY")
AZ_OPENAI_EMBED_MODEL = os.getenv("AZ_OPENAI_EMBED_MODEL", "text-embedding-3-small")

def get_embedding(text: str):
    if not AZ_OPENAI_ENDPOINT or not AZ_OPENAI_KEY:
        raise Exception("Configure AZ_OPENAI_ENDPOINT and AZ_OPENAI_KEY")
    url = f"{AZ_OPENAI_ENDPOINT}/openai/deployments/{AZ_OPENAI_EMBED_MODEL}/embeddings?api-version=2024-10-01"
    headers = {"Content-Type": "application/json", "api-key": AZ_OPENAI_KEY}
    payload = {"input": text}
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    resp = r.json()
    return resp["data"][0]["embedding"]
