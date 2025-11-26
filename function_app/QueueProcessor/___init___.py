import logging
import os
import json
import base64
import dotenv
from dotenv import load_dotenv, find_dotenv
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueMessage
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentanalysis import DocumentAnalysisClient
import requests
from pipeline.features import extract_features_from_doc
from pipeline.embeddings_client import get_embedding
from pipeline.aml_client import call_aml_model
from pipeline.scoring import combine_scores
from pipeline.report import generate_pdf_report


load_dotenv(find_dotenv())

# env
BLOB_CONNSTR = os.getenv('AZURE_BLOB_CONNECTION_STRING')
REPORTS_CONTAINER = os.getenv('AZURE_BLOB_CONTAINER_REPORTS', 'processed-reports')
DOC_ENDPOINT = os.getenv('AZ_DOC_ENDPOINT')
DOC_KEY = os.getenv('AZ_DOC_KEY')

# clients
blob_service = BlobServiceClient.from_connection_string(BLOB_CONNSTR)

doc_client = DocumentAnalysisClient(DOC_ENDPOINT, AzureKeyCredential(DOC_KEY))

def process_blob(container, blob_name):
    container_client = blob_service.get_container_client(container)
    blob_client = container_client.get_blob_client(blob_name)
    data = blob_client.download_blob().readall()
    # analyze with Document Intelligence
    poller = doc_client.begin_analyze_document('prebuilt-document', document=data)
    result = poller.result()
    # build simple doc dict
    raw_text = getattr(result, 'content', '') or ''
    if not raw_text:
        pages = []
        for p in getattr(result, 'pages', []):
            pages.append(getattr(p, 'content','') or '')
        raw_text = '\n'.join(pages)
    fields = {}
    if hasattr(result, 'key_value_pairs') and result.key_value_pairs:
        for kv in result.key_value_pairs:
            k = kv.key.content.strip() if kv.key else None
            v = kv.value.content.strip() if kv.value else None
            if k:
                fields[k] = v
    doc = {'raw_text': raw_text, 'fields': fields, 'pages': len(getattr(result,'pages',[]))}
    # features
    features = extract_features_from_doc(doc)
    # embedding (text snippet)
    emb = get_embedding(raw_text[:2000])
    # call AML model with payload
    payload = {'text': raw_text[:4000], 'features': features, 'embedding': emb}
    aml_result = call_aml_model(payload)
    # compute emb similarity if AML returns one, else 0
    emb_sim = float(aml_result.get('embedding_similarity', 0.0)) if isinstance(aml_result, dict) else 0.0
    scoring = combine_scores(aml_result, features, emb_sim)
    # generate pdf
    pdf_bytes = generate_pdf_report(blob_name, features, scoring, aml_result, fields)
    # upload pdf to reports container
    reports_client = blob_service.get_container_client(REPORTS_CONTAINER)
    reports_client.upload_blob(f"report-{blob_name}.pdf", pdf_bytes, overwrite=True)
    # update metadata on original blob
    meta = {'saifr_score': str(scoring['final_score'])}
    try:
        blob_client.set_blob_metadata(meta)
    except Exception as e:
        logging.warning('Failed setting metadata: %s', e)
    return {'blob': blob_name, 'score': scoring['final_score']}

def main(msg: func.QueueMessage):
    logging.info('Queue trigger function received a message.')
    try:
        body_b64 = msg.get_body().decode()
        # if base64-encoded message from Streamlit, decode first
        try:
            decoded = base64.b64decode(body_b64).decode()
            payload = json.loads(decoded)
        except Exception:
            payload = json.loads(body_b64)
        container = payload.get('container')
        blob_name = payload.get('blob_name')
        res = process_blob(container, blob_name)
        logging.info('Processed: %s', res)
    except Exception as e:
        logging.error('Processing failed: %s', e)
