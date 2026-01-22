"""
pdf_report.py
Generación de informe PDF académico
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os


def generate_pdf_report(results, plots_dir, output_path):

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    y = height - 50

    # ---- Título ----
    c.setFont("Helvetica-Bold", 15)
    c.drawString(50, y, "Informe de Análisis de Cifrado de Video")
    y -= 40

    c.setFont("Helvetica", 11)

    # ---- Resultados numéricos ----
    for section, metrics in results.items():
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, section)
        y -= 20

        c.setFont("Helvetica", 10)
        for key, value in metrics.items():
            c.drawString(70, y, f"{key}: {value:.5f}" if isinstance(value, float) else f"{key}: {value}")
            y -= 15

        y -= 10

        if y < 120:
            c.showPage()
            y = height - 50

    # ---- Gráficos ----
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
            c.drawImage(path, 70, y - 200, width=200, height=150)
            y -= 200

            if y < 120:
                c.showPage()
                y = height - 50

    c.save()
