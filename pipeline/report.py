import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_pdf_report(document_name: str, features: dict, scoring_result: dict, aml_result: dict, fields: dict):
    buf = io.BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    x, y = 40, h - 40
    p.setFont('Helvetica-Bold', 14)
    p.drawString(x, y, f'Relatório de Risco - {document_name}')
    y -= 24
    p.setFont('Helvetica', 10)
    p.drawString(x, y, f'Gerado em: {datetime.utcnow().isoformat()} UTC')
    y -= 18
    p.setFont('Helvetica-Bold', 12)
    p.drawString(x, y, 'Scores')
    y -= 14
    p.setFont('Helvetica', 10)
    p.drawString(x, y, f"AML score: {scoring_result['aml_score']:.3f}")
    y -= 12
    p.drawString(x, y, f"Similarity score: {scoring_result['emb_similarity_score']:.3f}")
    y -= 12
    p.drawString(x, y, f"Final score: {scoring_result['final_score']:.3f}")
    y -= 18
    p.setFont('Helvetica-Bold', 12)
    p.drawString(x, y, 'Razões / Evidências')
    y -= 14
    p.setFont('Helvetica', 10)
    for r in scoring_result['reasons']:
        if y < 80:
            p.showPage(); y = h - 40
        p.drawString(x + 8, y, f"- {r}")
        y -= 12
    y -= 10
    p.setFont('Helvetica-Bold', 12)
    p.drawString(x, y, 'Campos extraídos')
    y -= 14
    p.setFont('Helvetica', 9)
    for k, v in fields.items():
        if y < 80:
            p.showPage(); y = h - 40
        val = str(v)
        if len(val) > 120: val = val[:117] + '...'
        p.drawString(x + 8, y, f"{k}: {val}")
        y -= 12
    p.showPage()
    p.save()
    buf.seek(0)
    return buf.read()
