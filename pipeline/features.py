def extract_features_from_doc(doc: dict):
    raw = doc.get('raw_text','') or ''
    fields = doc.get('fields',{}) or {}
    pages = doc.get('pages',0)
    features = {}
    features['num_fields'] = len(fields)
    features['num_pages'] = pages
    features['raw_length'] = len(raw)
    features['has_signature_word'] = int(('assinatura' in raw.lower()) or ('signature' in raw.lower()))
    suspicious_terms = ['rasura','alterado','forged','void','canceled','cancela']
    features['suspicious_terms_count'] = sum(raw.lower().count(t) for t in suspicious_terms)
    features['has_amount'] = int(any('valor' in k.lower() or 'amount' in k.lower() for k in fields.keys()))
    return features
