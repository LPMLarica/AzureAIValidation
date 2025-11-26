import os
try:
    from config import AZURE_DOCUMENT_KEY as _AZ_DOC_KEY, AZURE_DOCUMENT_ENDPOINT as _AZ_DOC_ENDPOINT
except Exception:
    _AZ_DOC_KEY = None
    _AZ_DOC_ENDPOINT = None

import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentanalysis import DocumentAnalysisClient

AZ_DOC_ENDPOINT = os.getenv("AZ_DOC_ENDPOINT")
AZ_DOC_KEY = os.getenv("AZ_DOC_KEY")
if not AZ_DOC_ENDPOINT or not AZ_DOC_KEY:
    raise Exception("Set AZ_DOC_ENDPOINT and AZ_DOC_KEY in environment or app settings.")

client = DocumentAnalysisClient(AZ_DOC_ENDPOINT, AzureKeyCredential(AZ_DOC_KEY))

def analyze_document_bytes(file_bytes: bytes, model="prebuilt-document"):
    poller = client.begin_analyze_document(model, document=file_bytes)
    result = poller.result()
    # extract text
    full_text = getattr(result, 'content', '') or ''
    if not full_text:
        pages = []
        for p in getattr(result, 'pages', []):
            pages.append(getattr(p, 'content', '') or '')
        full_text = '\n'.join(pages)
    # fields
    fields = {}
    if hasattr(result, 'key_value_pairs') and result.key_value_pairs:
        for kv in result.key_value_pairs:
            k = kv.key.content.strip() if kv.key else None
            v = kv.value.content.strip() if kv.value else None
            if k:
                fields[k] = v
    if hasattr(result, 'documents'):
        for d in result.documents:
            for k, v in d.fields.items():
                try:
                    fields[k] = v.content if hasattr(v, 'content') else str(v)
                except:
                    fields[k] = str(v)
    pages_count = len(getattr(result, 'pages', []))
    return {"raw_text": full_text, "fields": fields, "pages": pages_count}
