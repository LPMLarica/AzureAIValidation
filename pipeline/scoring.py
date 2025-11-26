def combine_scores(aml_result: dict, features: dict, emb_similarity_score: float = 0.0):
    aml_score = float(aml_result.get('risk_score', aml_result.get('score', 0.0)))
    rule_points = 0.0
    reasons = []
    if features.get('suspicious_terms_count',0) > 0:
        rule_points += 0.2
        reasons.append('Termos suspeitos detectados')
    if features.get('has_signature_word',0) == 0:
        rule_points += 0.2
        reasons.append('Assinatura ausente')
    if features.get('num_fields',0) == 0 and features.get('raw_length',0) > 1000:
        rule_points += 0.15
        reasons.append('Documento longo sem campos extraídos')
    final = 0.55 * aml_score + 0.30 * emb_similarity_score + 0.15 * rule_points
    final = max(0.0, min(1.0, final))
    return {'final_score': final, 'aml_score': aml_score, 'emb_similarity_score': emb_similarity_score, 'reasons': reasons}
