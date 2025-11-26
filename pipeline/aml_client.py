import os
import requests
import json

AZUREML_ENDPOINT_URL = os.getenv("AZUREML_ENDPOINT_URL")  
AZUREML_ENDPOINT_KEY = os.getenv("AZUREML_ENDPOINT_KEY")

def call_aml_model(payload: dict):
    if not AZUREML_ENDPOINT_URL or not AZUREML_ENDPOINT_KEY:
        raise Exception("Set AZUREML_ENDPOINT_URL and AZUREML_ENDPOINT_KEY")
    headers = {
        "Authorization": f"Bearer {AZUREML_ENDPOINT_KEY}",
        "Content-Type": "application/json"
    }
    r = requests.post(AZUREML_ENDPOINT_URL, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()
