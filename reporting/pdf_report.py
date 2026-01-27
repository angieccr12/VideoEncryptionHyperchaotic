"""
pdf_report.py
Generación de informe PDF académico interpretado
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os


def interpret_metric(key, value):
    if "NPCR" in key:
        return " (Adecuado)" if value > 99 else " (Débil)"
    if "UACI" in key:
        return " (Esperado)" if 30 <= value <= 35 else " (Atípico)"
    if "SSIM" in key and value < 0.1:
        return " (Alta sensibilidad)"
    if "Monobit" in key:
        return " (Balance adecuado)" if value < 0.01 else " (Desbalance)"
    return ""


def generate_pdf_report(results, plots_dir, output_path):

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    y = height - 50

    # -------- TÍTULO --------
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Informe de Análisis de Cifrado de Video")
    y -= 30

    c.setFont("Helvetica", 11)
    c.drawString(50, y, "Evaluación criptográfica offline (no streaming)")
    y -= 40

    # -------- RESULTADOS --------
    for section, metrics in results.items():

        c.setFont("Helvetica-Bold", 13)
        c.drawString(50, y, section)
        y -= 20

        c.setFont("Helvetica", 10)

        for key, value in metrics.items():
            label = interpret_metric(key, value)
            text = f"{key}: {value:.5f}{label}" if isinstance(value, float) else f"{key}: {value}"
            c.drawString(70, y, text)
            y -= 15

        y -= 10

        if y < 120:
            c.showPage()
            y = height - 50

    # -------- GRÁFICOS --------
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Visualización de resultados")

    y = height - 100

    for img in [
        "hist_original.png",
        "hist_encrypted.png",
        "hist_decrypted.png",
        "corr_original.png",
        "corr_encrypted.png",
    ]:
        path = os.path.join(plots_dir, img)
        if os.path.exists(path):
            c.drawImage(path, 70, y - 180, width=220, height=150)
            y -= 190

            if y < 120:
                c.showPage()
                y = height - 50

    c.save()
