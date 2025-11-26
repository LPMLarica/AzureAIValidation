import os
import streamlit as st
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient
import uuid
import time
import base64
import json

# Configs
BLOB_CONNSTR = os.getenv("AZURE_BLOB_CONNECTION_STRING") or st.secrets.get("AZURE_BLOB_CONNECTION_STRING", None)
BLOB_CONTAINER_INCOMING = os.getenv("AZURE_BLOB_CONTAINER_INCOMING", st.secrets.get("AZURE_BLOB_CONTAINER_INCOMING", "incoming-docs"))
BLOB_CONTAINER_REPORTS = os.getenv("AZURE_BLOB_CONTAINER_REPORTS", st.secrets.get("AZURE_BLOB_CONTAINER_REPORTS", "processed-reports"))
QUEUE_CONNSTR = os.getenv("AZURE_QUEUE_CONNECTION_STRING") or st.secrets.get("AZURE_QUEUE_CONNECTION_STRING", None)
QUEUE_NAME = os.getenv("AZURE_QUEUE_NAME", st.secrets.get("AZURE_QUEUE_NAME", "doc-processing-queue"))

if not BLOB_CONNSTR or not QUEUE_CONNSTR:
    st.error("Configure AZURE_BLOB_CONNECTION_STRING and AZURE_QUEUE_CONNECTION_STRING in secrets or env.")
    st.stop()

st.set_page_config(layout='wide', page_title="SAIFR Async Fraud Pipeline")
st.title("SAIFR — Async Document Fraud Pipeline (Azure Serverless)")

# Initialize clients
blob_service = BlobServiceClient.from_connection_string(BLOB_CONNSTR)
incoming_container = blob_service.get_container_client(BLOB_CONTAINER_INCOMING)
reports_container = blob_service.get_container_client(BLOB_CONTAINER_REPORTS)

queue_client = QueueClient.from_connection_string(QUEUE_CONNSTR, QUEUE_NAME)

st.sidebar.header("Upload & Settings")
uploaded = st.file_uploader("Envie documento (PDF, PNG, JPG)", type=["pdf","png","jpg","jpeg"])

if uploaded:
    name = uploaded.name
    unique_name = f"{uuid.uuid4()}-{name}"
    bytes_data = uploaded.read()
    if st.button("Enviar para processamento assíncrono"):
        # upload to incoming container
        incoming_container.upload_blob(unique_name, bytes_data, overwrite=True)
        st.success(f"Arquivo enviado: {unique_name}")
        # enqueue a simple JSON 
        msg = json.dumps({"container": BLOB_CONTAINER_INCOMING, "blob_name": unique_name})
        queue_client.send_message(base64.b64encode(msg.encode()).decode())
        st.info("Mensagem enfileirada para processamento. Aguarde alguns segundos e atualize a lista de relatórios.")

st.markdown("---")
st.header("Relatórios processados")
# reports container
try:
    blobs = reports_container.list_blobs()
    rows = []
    for b in blobs:
        rows.append({"name": b.name, "size": b.size, "last_modified": str(b.last_modified)})
    if rows:
        import pandas as pd
        df = pd.DataFrame(rows)
        selected = st.selectbox("Selecione relatório", df['name'].tolist())
        if selected:
            bclient = reports_container.get_blob_client(selected)
            data = bclient.download_blob().readall()
            st.download_button("Download Relatório PDF", data=data, file_name=selected, mime='application/pdf')
    else:
        st.info("Nenhum relatório processado ainda.")
except Exception as e:
    st.error(f"Erro ao listar relatórios: {e}")
