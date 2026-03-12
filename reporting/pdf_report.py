"""
pdf_report.py
Generación de informe PDF académico con estilo profesional
Inspirado en el formato del informe de referencia con tablas, badges de estado y secciones visuales
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus.flowables import Flowable
from datetime import datetime
import os


# =========================
# PALETA DE COLORES
# =========================
COLOR_PRIMARY      = colors.HexColor("#1a3a5c")   # Azul oscuro – encabezados principales
COLOR_SECONDARY    = colors.HexColor("#2e6da4")   # Azul medio – encabezados de sección
COLOR_ACCENT       = colors.HexColor("#e8f0f7")   # Azul muy claro – fondo de encabezados de tabla
COLOR_ROW_ALT      = colors.HexColor("#f5f8fb")   # Azul casi blanco – filas alternas
COLOR_PASS         = colors.HexColor("#1a7a3a")   # Verde – aprobado
COLOR_FAIL         = colors.HexColor("#b00020")   # Rojo – fallido
COLOR_WARN         = colors.HexColor("#8a5e00")   # Ámbar – marginal
COLOR_PASS_BG      = colors.HexColor("#e6f4ea")
COLOR_FAIL_BG      = colors.HexColor("#fce8eb")
COLOR_WARN_BG      = colors.HexColor("#fff8e1")
COLOR_BORDER       = colors.HexColor("#b8cfe0")
COLOR_HEADER_TEXT  = colors.white
COLOR_BODY_TEXT    = colors.HexColor("#1c1c1c")
COLOR_SUBTITLE     = colors.HexColor("#4a6580")


# =========================
# ESTILOS DE PÁRRAFO
# =========================

def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "doc_title": ParagraphStyle(
            "doc_title",
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=COLOR_PRIMARY,
            spaceAfter=4,
            leading=26,
        ),
        "doc_subtitle": ParagraphStyle(
            "doc_subtitle",
            fontName="Helvetica",
            fontSize=11,
            textColor=COLOR_SUBTITLE,
            spaceAfter=2,
        ),
        "doc_date": ParagraphStyle(
            "doc_date",
            fontName="Helvetica-Oblique",
            fontSize=9,
            textColor=COLOR_SUBTITLE,
            spaceAfter=0,
        ),
        "section_title": ParagraphStyle(
            "section_title",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=COLOR_SECONDARY,
            spaceBefore=14,
            spaceAfter=6,
        ),
        "subsection_title": ParagraphStyle(
            "subsection_title",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=COLOR_PRIMARY,
            spaceBefore=10,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=9,
            textColor=COLOR_BODY_TEXT,
            leading=13,
            spaceAfter=4,
        ),
        "table_header": ParagraphStyle(
            "table_header",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            textColor=COLOR_HEADER_TEXT,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            fontName="Helvetica",
            fontSize=8,
            textColor=COLOR_BODY_TEXT,
            leading=11,
        ),
        "table_cell_mono": ParagraphStyle(
            "table_cell_mono",
            fontName="Courier",
            fontSize=7.5,
            textColor=COLOR_BODY_TEXT,
            leading=11,
        ),
        "pass_badge": ParagraphStyle(
            "pass_badge",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=COLOR_PASS,
        ),
        "fail_badge": ParagraphStyle(
            "fail_badge",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=COLOR_FAIL,
        ),
        "warn_badge": ParagraphStyle(
            "warn_badge",
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=COLOR_WARN,
        ),
        "caption": ParagraphStyle(
            "caption",
            fontName="Helvetica-Oblique",
            fontSize=8,
            textColor=COLOR_SUBTITLE,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "verdict_pass": ParagraphStyle(
            "verdict_pass",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=COLOR_PASS,
        ),
        "verdict_fail": ParagraphStyle(
            "verdict_fail",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=COLOR_FAIL,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica-Oblique",
            fontSize=7.5,
            textColor=COLOR_SUBTITLE,
            alignment=TA_CENTER,
        ),
    }
    return styles


# =========================
# CLASIFICACIÓN DE MÉTRICAS
# =========================

THRESHOLDS = {
    "NPCR": ("pass",   lambda v: v > 99),
    "UACI": ("check",  lambda v: 30 <= v <= 35),
    "SSIM descifrado": ("fail", lambda v: v < 0.9),
    "SSIM clave":      ("pass", lambda v: v < 0.1),
    "Monobit":         ("pass", lambda v: v >= 0.01),
    "Block Frequency": ("pass", lambda v: v >= 0.01),
    "PSNR descifrado": ("check", lambda v: v > 30),
    "Correlación horizontal — ciphertext": ("check", lambda v: abs(v) < 0.1),
    "Correlación vertical — ciphertext":   ("check", lambda v: abs(v) < 0.1),
    "Correlación diagonal — ciphertext":   ("check", lambda v: abs(v) < 0.1),
}


def classify_metric(key, value):
    """Retorna (status_str, badge_label) según la clave y valor."""
    if not isinstance(value, (int, float)):
        return "neutral", "—"

    key_lower = key.lower()

    if "npcr" in key_lower:
        ok = value > 99
        return ("pass", "✓ APROBADO") if ok else ("fail", "✗ FALLIDO")

    if "uaci" in key_lower:
        ok = 30 <= value <= 35
        return ("pass", "✓ APROBADO") if ok else ("fail", "✗ FALLIDO")

    if "ssim" in key_lower:
        if "clave" in key_lower or "incorrecta" in key_lower:
            ok = value < 0.1
            return ("pass", "✓ APROBADO") if ok else ("fail", "✗ FALLIDO")
        else:
            ok = value > 0.9
            return ("pass", "✓ APROBADO") if ok else ("fail", "✗ FALLIDO")

    if "psnr" in key_lower:
        if "clave" in key_lower or "ruido" in key_lower or "oclus" in key_lower:
            ok = value < 15
            return ("pass", "✓ APROBADO") if ok else ("fail", "✗ FALLIDO")
        else:
            ok = value > 30
            return ("pass", "✓ APROBADO") if ok else ("fail", "✗ FALLIDO")

    if "monobit" in key_lower:
        ok = value >= 0.01
        return ("pass", "✓ APROBADO") if ok else ("fail", "✗ FALLIDO")

    if "block frequency" in key_lower or "bloque" in key_lower:
        ok = value >= 0.01
        return ("pass", "✓ APROBADO") if ok else ("fail", "✗ FALLIDO")

    if "correlación horizontal" in key_lower and "cipher" in key_lower:
        if abs(value) < 0.1:
            return "pass", "✓ APROBADO"
        elif abs(value) < 0.3:
            return "warn", "~ MARGINAL"
        else:
            return "fail", "✗ FALLIDO"

    if "correlación vertical" in key_lower or "correlación diagonal" in key_lower:
        if abs(value) < 0.1:
            return "pass", "✓ APROBADO"
        elif abs(value) < 0.3:
            return "warn", "~ MARGINAL"
        else:
            return "fail", "✗ FALLIDO"

    return "neutral", "—"


def interpret_metric(key, value):
    """Texto interpretativo breve."""
    if not isinstance(value, (int, float)):
        return str(value)

    key_lower = key.lower()

    if "npcr" in key_lower:
        return f"{value:.4f}% — {'alta sensibilidad al cambio de un píxel' if value > 99 else 'sensibilidad insuficiente'}"
    if "uaci" in key_lower:
        ideal = "intensidad de cambio adecuada (ideal: 33.46%)" if 30 <= value <= 35 else "valor atípico"
        return f"{value:.4f}% — {ideal}"
    if "ssim" in key_lower:
        if "clave" in key_lower or "incorrecta" in key_lower:
            return f"SSIM={value:.5f} — {'sin estructura recuperable con clave incorrecta' if value < 0.1 else 'estructura detectable con clave incorrecta'}"
        return f"SSIM={value:.5f} — {'calidad de descifrado suficiente' if value > 0.9 else 'calidad de descifrado insuficiente'}"
    if "psnr" in key_lower:
        if "clave" in key_lower or "ruido" in key_lower or "oclus" in key_lower:
            return f"{value:.2f} dB — cifrado produce apariencia de ruido"
        return f"{value:.2f} dB — {'reconstrucción perfecta' if value > 40 else 'pérdida significativa en descifrado'}"
    if "monobit" in key_lower:
        return f"p={value:.5f} — {'balance adecuado' if value >= 0.01 else 'desbalance de bits detectado (p < 0.01)'}"
    if "block frequency" in key_lower or "bloque" in key_lower:
        return f"p={value:.5f} — {'distribución de bloques uniforme' if value >= 0.01 else 'bloques no uniformes'}"
    if "correlación" in key_lower:
        label = "correlación significativa (patrón detectable)" if abs(value) > 0.1 else "correlación despreciable"
        return f"r={value:.6f} — {label}"
    if "entropía" in key_lower or "entropy" in key_lower:
        return f"{value:.6f} bits"

    return f"{value:.5f}"


# =========================
# VALORES ESPERADOS POR MÉTRICA
# Para un cifrador de video con audio hipercaótico (M×N×A×K)
# =========================

def expected_value(key):
    """
    Retorna el string con el rango/valor esperado para cada métrica,
    contextualizado para un cifrador de video+audio hipercaótico.
    """
    k = key.lower()

    # ── Entropía ──────────────────────────────────────────────────────
    if "entropía" in k or "entropy" in k:
        if "plaintext" in k or "original" in k:
            return "5.0 – 7.5 bits\n(contenido visual natural)"
        if "mnak" in k and ("media" in k or "promedio" in k or "por archivo" in k):
            return "≥ 7.99 bits\n(payload cifrado completo)"
        if "mnak" in k and "desviación" in k:
            return "< 0.001\n(uniformidad entre frames)"
        if "mnak" in k:
            return "≈ 8.000 bits\n(máxima entropía teórica)"
        if "global" in k and "cifrad" in k:
            return "≥ 7.9 bits\n(ciphertext de video)"
        if "promedio" in k or "frame" in k:
            return "≥ 7.9 bits\n(por frame cifrado)"
        return "≥ 7.9 bits"

    # ── Correlación ───────────────────────────────────────────────────
    if "correlación" in k or "correlacion" in k:
        if "plaintext" in k or "original" in k:
            return "> 0.90\n(alta correlación natural)"
        if "horizontal" in k:
            return "|r| < 0.01\n(destrucción espacial horizontal)"
        if "vertical" in k:
            return "|r| < 0.01\n(destrucción espacial vertical)"
        if "diagonal" in k:
            return "|r| < 0.01\n(destrucción espacial diagonal)"
        return "|r| ≈ 0"

    # ── Varianza ──────────────────────────────────────────────────────
    if "varianza" in k:
        return "≈ 5500 – 6500\n(distribución uniforme [0,255])"

    # ── PSNR ──────────────────────────────────────────────────────────
    if "psnr" in k:
        if "descifrad" in k:
            return "≥ 40 dB\n(reconstrucción perfecta)\no ∞ si lossless"
        if "clave" in k or "incorrecta" in k:
            return "< 15 dB\n(ruido puro con clave errónea)"
        if "ruido" in k:
            return "< 15 dB\n(cifrado robusto ante ruido)"
        if "oclus" in k:
            return "< 15 dB\n(cifrado robusto ante oclusión)"
        return "< 15 dB (ciphertext)\no ≥ 40 dB (descifrado)"

    # ── MSE ───────────────────────────────────────────────────────────
    if "mse" in k:
        return "< 1.0\n(descifrado lossless ideal: 0)"

    # ── MAD ───────────────────────────────────────────────────────────
    if "mad" in k:
        return "< 1.0\n(descifrado lossless ideal: 0)"

    # ── SSIM ──────────────────────────────────────────────────────────
    if "ssim" in k:
        if "descifrad" in k:
            return "≥ 0.99\n(fidelidad casi perfecta)"
        if "clave" in k or "incorrecta" in k:
            return "< 0.05\n(sin estructura con clave errónea)"
        return "≥ 0.99 (descifrado)\n< 0.05 (clave incorrecta)"

    # ── NPCR ──────────────────────────────────────────────────────────
    if "npcr" in k:
        return "> 99.60%\n(ideal: 99.6094% para 8 bits)"

    # ── UACI ──────────────────────────────────────────────────────────
    if "uaci" in k:
        return "33.46% ± 0.5%\n(ideal teórico: 33.4635%)"

    # ── NIST Monobit ──────────────────────────────────────────────────
    if "monobit" in k:
        return "p ≥ 0.01\n(balance de 0s y 1s)"

    # ── NIST Block Frequency ──────────────────────────────────────────
    if "block" in k or "bloque" in k or "frequency" in k or "frecuencia" in k:
        return "p ≥ 0.01\n(bloques uniformes)"

    # ── Tiempos / Eficiencia ──────────────────────────────────────────
    if "tiempo" in k or "time" in k:
        if "frame" in k:
            return "< 0.033 s/frame\n(≥ 30 fps en tiempo real)"
        if "mnak" in k:
            return "< 0.010 s/frame\n(lectura eficiente de .mnak)"
        return "Referencia comparativa"

    # ── Dimensiones MNAK ─────────────────────────────────────────────
    if "dimensiones" in k or "dimension" in k:
        return "Según configuración\ndel sistema"

    return "—"


# =========================
# CONSTRUCCIÓN DE TABLA DE MÉTRICAS
# =========================

def build_metrics_table(metrics, styles):
    """
    Construye una tabla estilizada con 5 columnas:
    Métrica | Valor obtenido | Valor esperado | Estado | Interpretación
    """

    # Ancho útil ≈ 170 mm → distribuir entre 5 columnas
    col_widths = [120, 55, 75, 55, 165]

    header_row = [
        Paragraph("Métrica",         styles["table_header"]),
        Paragraph("Valor obtenido",  styles["table_header"]),
        Paragraph("Valor esperado",  styles["table_header"]),
        Paragraph("Estado",          styles["table_header"]),
        Paragraph("Interpretación",  styles["table_header"]),
    ]

    data = [header_row]

    for i, (key, value) in enumerate(metrics.items()):
        status, badge = classify_metric(key, value)

        # Valor formateado
        if isinstance(value, float):
            val_str = f"{value:.5f}"
        elif isinstance(value, int):
            val_str = str(value)
        else:
            val_str = str(value)

        # Badge con color
        badge_style = {
            "pass":    styles["pass_badge"],
            "fail":    styles["fail_badge"],
            "warn":    styles["warn_badge"],
            "neutral": styles["table_cell"],
        }.get(status, styles["table_cell"])

        expected = expected_value(key)
        interp   = interpret_metric(key, value)

        row = [
            Paragraph(key,      styles["table_cell"]),
            Paragraph(val_str,  styles["table_cell_mono"]),
            Paragraph(expected, styles["table_cell"]),
            Paragraph(badge,    badge_style),
            Paragraph(interp,   styles["table_cell"]),
        ]
        data.append(row)

    ts = TableStyle([
        # Encabezado
        ("BACKGROUND",    (0, 0), (-1, 0), COLOR_SECONDARY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), COLOR_HEADER_TEXT),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 8.5),
        # Bordes
        ("BOX",           (0, 0), (-1, -1), 0.6, COLOR_BORDER),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, COLOR_BORDER),
        # Padding
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        # Columna "Valor esperado" en cursiva gris
        ("FONTNAME",      (2, 1), (2, -1), "Helvetica-Oblique"),
        ("TEXTCOLOR",     (2, 1), (2, -1), COLOR_SUBTITLE),
        ("FONTSIZE",      (2, 1), (2, -1), 7.5),
    ])

    # Filas alternas + colores de estado
    for i, (key, value) in enumerate(metrics.items(), start=1):
        status, _ = classify_metric(key, value)
        if status == "pass":
            bg = COLOR_PASS_BG
        elif status == "fail":
            bg = COLOR_FAIL_BG
        elif status == "warn":
            bg = COLOR_WARN_BG
        else:
            bg = COLOR_ROW_ALT if i % 2 == 0 else colors.white
        ts.add("BACKGROUND", (0, i), (-1, i), bg)

    return Table(data, colWidths=col_widths, style=ts, repeatRows=1)


# =========================
# TABLA DE RESUMEN EJECUTIVO
# =========================

def build_summary_table(results, styles):
    """Cuenta aprobados, marginales y fallidos en todos los resultados."""
    total = passed = failed = marginal = 0

    for section, metrics in results.items():
        for key, value in metrics.items():
            if not isinstance(value, (int, float)):
                continue
            total += 1
            status, _ = classify_metric(key, value)
            if status == "pass":
                passed += 1
            elif status == "fail":
                failed += 1
            elif status == "warn":
                marginal += 1

    pct_pass = f"{100*passed/total:.1f}%" if total else "—"
    pct_fail = f"{100*failed/total:.1f}%" if total else "—"
    pct_marg = f"{100*marginal/total:.1f}%" if total else "—"

    col_widths = [160, 80, 80]
    header = [
        Paragraph("Categoría", styles["table_header"]),
        Paragraph("Cantidad", styles["table_header"]),
        Paragraph("Porcentaje", styles["table_header"]),
    ]
    rows = [
        header,
        [Paragraph("✓ Métricas aprobadas", styles["pass_badge"]),
         Paragraph(str(passed), styles["table_cell"]),
         Paragraph(pct_pass,    styles["table_cell"])],
        [Paragraph("~ Métricas marginales", styles["warn_badge"]),
         Paragraph(str(marginal), styles["table_cell"]),
         Paragraph(pct_marg,     styles["table_cell"])],
        [Paragraph("✗ Métricas fallidas", styles["fail_badge"]),
         Paragraph(str(failed), styles["table_cell"]),
         Paragraph(pct_fail,    styles["table_cell"])],
        [Paragraph("Total evaluadas", styles["table_cell"]),
         Paragraph(str(total), styles["table_cell"]),
         Paragraph("100%",     styles["table_cell"])],
    ]

    ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), COLOR_SECONDARY),
        ("BOX",           (0, 0), (-1, -1), 0.6, COLOR_BORDER),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, COLOR_BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("BACKGROUND",    (0, 1), (-1, 1), COLOR_PASS_BG),
        ("BACKGROUND",    (0, 2), (-1, 2), COLOR_WARN_BG),
        ("BACKGROUND",    (0, 3), (-1, 3), COLOR_FAIL_BG),
        ("BACKGROUND",    (0, 4), (-1, 4), COLOR_ROW_ALT),
        ("FONTNAME",      (0, 4), (-1, 4), "Helvetica-Bold"),
    ])

    return Table(rows, colWidths=col_widths, style=ts), passed, total


# =========================
# HEADER / FOOTER DE PÁGINA
# =========================

def on_page(canvas, doc, styles):
    width, height = A4

    # Barra superior
    canvas.saveState()
    canvas.setFillColor(COLOR_PRIMARY)
    canvas.rect(0, height - 18*mm, width, 18*mm, fill=1, stroke=0)

    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(colors.white)
    canvas.drawString(20*mm, height - 11*mm, "Evaluación Criptográfica — Sistema de Cifrado de Video Hipercaótico 4D")

    # Número de página
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - 20*mm, height - 11*mm, f"Página {doc.page}")

    # Barra inferior
    canvas.setFillColor(COLOR_ACCENT)
    canvas.rect(0, 0, width, 10*mm, fill=1, stroke=0)
    canvas.setFillColor(COLOR_SUBTITLE)
    canvas.setFont("Helvetica-Oblique", 7.5)
    canvas.drawCentredString(width/2, 3.5*mm,
        "Informe generado automáticamente por el módulo de evaluación criptográfica del sistema M×N×A×K — Cifrado hipercaótico de video 4D.")
    canvas.restoreState()


# =========================
# GENERACIÓN DEL REPORTE
# =========================

def generate_pdf_report(results, plots_dir, output_path,
                        system_params=None):
    """
    results     : dict { section_name: { metric_name: value, ... }, ... }
    plots_dir   : directorio con los PNG generados
    output_path : ruta del PDF de salida
    system_params : dict opcional con parámetros del sistema (M, N, A, K, etc.)
    """

    styles = build_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=25*mm,
        bottomMargin=18*mm,
        title="Informe de Evaluación Criptográfica",
        author="Sistema M×N×A×K",
    )

    story = []
    width = A4[0] - 40*mm   # ancho útil

    def hr(color=COLOR_BORDER, thickness=0.8):
        return HRFlowable(width="100%", thickness=thickness,
                          color=color, spaceAfter=4, spaceBefore=2)

    # ── PORTADA / ENCABEZADO ──────────────────────────────────────────
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("Informe de Evaluación Criptográfica", styles["doc_title"]))
    story.append(Paragraph(
        "Sistema de Cifrado de Video con Caos Hipercaótico 4D (M×N×A×K)",
        styles["doc_subtitle"]))
    story.append(Paragraph(
        f"Generado: {datetime.now().strftime('%d de %B de %Y, %H:%M')}",
        styles["doc_date"]))
    story.append(hr(COLOR_PRIMARY, 1.5))
    story.append(Spacer(1, 4*mm))

    # ── PARÁMETROS DEL SISTEMA ────────────────────────────────────────
    if system_params:
        story.append(Paragraph("Parámetros del Sistema", styles["section_title"]))

        param_data = [[
            Paragraph("Parámetro", styles["table_header"]),
            Paragraph("Valor", styles["table_header"]),
            Paragraph("Descripción", styles["table_header"]),
        ]]
        for pname, (pval, pdesc) in system_params.items():
            param_data.append([
                Paragraph(pname, styles["table_cell"]),
                Paragraph(str(pval), styles["table_cell_mono"]),
                Paragraph(pdesc, styles["table_cell"]),
            ])

        param_ts = TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), COLOR_SECONDARY),
            ("BOX",           (0, 0), (-1, -1), 0.6, COLOR_BORDER),
            ("INNERGRID",     (0, 0), (-1, -1), 0.3, COLOR_BORDER),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 7),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
        ] + [
            ("BACKGROUND", (0, i), (-1, i), COLOR_ROW_ALT if i % 2 == 0 else colors.white)
            for i in range(1, len(param_data))
        ])

        param_table = Table(param_data,
                            colWidths=[90, 90, width - 180],
                            style=param_ts, repeatRows=1)
        story.append(param_table)
        story.append(Spacer(1, 4*mm))

    # ── SECCIONES DE MÉTRICAS ─────────────────────────────────────────
    SECTION_DESCRIPTIONS = {
        "Aleatoriedad": (
            "Entropía de Shannon",
            "La entropía mide el grado de aleatoriedad de los datos. Un cifrador ideal produce "
            "entropía próxima a 8 bits/byte, indicando distribución uniforme y ausencia de patrones "
            "predecibles en el texto cifrado."
        ),
        "Estadísticas": (
            "Estadísticas de Correlación",
            "La correlación entre píxeles adyacentes debe ser despreciable (|r| ≈ 0) en el texto "
            "cifrado. Valores altos en el plaintext son normales; el cifrador debe destruir esa "
            "estructura espacial."
        ),
        "Calidad del descifrado": (
            "Calidad del Descifrado",
            "Evalúa la fidelidad de la reconstrucción. PSNR > 30 dB y SSIM > 0.9 indican descifrado "
            "perfecto o casi perfecto. Valores bajos señalan pérdida de información o bugs en el pipeline."
        ),
        "Robustez": (
            "Robustez ante Perturbaciones",
            "Se simulan ataques de ruido gaussiano y oclusión de bloques sobre el ciphertext. "
            "Un buen cifrador produce apariencia de ruido incluso bajo perturbaciones (PSNR bajo, "
            "sin estructura visual recuperable)."
        ),
        "Pruebas diferenciales": (
            "Pruebas Diferenciales (NPCR / UACI)",
            "NPCR mide el porcentaje de píxeles que cambian al alterar un único píxel del plaintext. "
            "UACI mide la intensidad media del cambio. Valores ideales: NPCR > 99%, UACI ≈ 33.46%."
        ),
        "Pruebas NIST": (
            "Pruebas de Aleatoriedad NIST SP 800-22",
            "Pruebas estadísticas estándar para evaluar la calidad del generador pseudoaleatorio. "
            "El p-valor debe ser ≥ 0.01 para aprobar cada prueba."
        ),
        "Eficiencia": (
            "Eficiencia Computacional",
            "Tiempos de lectura y procesamiento por frame. Valores más bajos indican mayor eficiencia "
            "del pipeline de cifrado/descifrado."
        ),
    }

    for section, metrics in results.items():
        if not metrics:
            continue

        short_title, description = SECTION_DESCRIPTIONS.get(
            section, (section, "")
        )

        story.append(Paragraph(short_title, styles["section_title"]))
        story.append(hr())

        if description:
            story.append(Paragraph(description, styles["body"]))
            story.append(Spacer(1, 2*mm))

        tbl = build_metrics_table(metrics, styles)
        story.append(KeepTogether([tbl]))
        story.append(Spacer(1, 5*mm))

    # ── RESUMEN EJECUTIVO ─────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Resumen Ejecutivo", styles["section_title"]))
    story.append(hr(COLOR_PRIMARY, 1.2))
    story.append(Spacer(1, 2*mm))

    summary_table, passed, total = build_summary_table(results, styles)
    story.append(summary_table)
    story.append(Spacer(1, 6*mm))

    # Veredicto
    pct = (passed / total * 100) if total else 0
    if pct >= 80:
        veredicto_style = styles["verdict_pass"]
        veredicto = f"SISTEMA SEGURO — {pct:.1f}% de las métricas superan los umbrales mínimos."
    elif pct >= 60:
        veredicto_style = styles["fail_badge"]
        veredicto = (f"SISTEMA INSUFICIENTE — Solo {pct:.1f}% de las métricas superan los umbrales mínimos. "
                     "Se requieren mejoras en el pipeline de cifrado.")
    else:
        veredicto_style = styles["fail_badge"]
        veredicto = (f"SISTEMA NO SEGURO — Solo {pct:.1f}% de las métricas aprueban. "
                     "El sistema presenta vulnerabilidades críticas.")

    story.append(Paragraph("Veredicto de Seguridad", styles["subsection_title"]))

    verdict_box_data = [[Paragraph(veredicto, veredicto_style)]]
    verdict_box_ts = TableStyle([
        ("BOX",          (0, 0), (-1, -1), 1.2, COLOR_FAIL if pct < 80 else COLOR_PASS),
        ("BACKGROUND",   (0, 0), (-1, -1), COLOR_FAIL_BG if pct < 80 else COLOR_PASS_BG),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ])
    verdict_box = Table(verdict_box_data, colWidths=[width], style=verdict_box_ts)
    story.append(verdict_box)

    # ── TABLA DE REFERENCIA: UMBRALES ESPERADOS ──────────────────────
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("Umbrales de Referencia para Cifrado de Video con Audio", styles["subsection_title"]))
    story.append(Paragraph(
        "La siguiente tabla resume los valores objetivo establecidos en la literatura para sistemas de "
        "cifrado de video con audio basados en caos hipercaótico (M×N×A×K). Estos umbrales son los "
        "criterios utilizados para clasificar cada métrica como aprobada, marginal o fallida en este informe.",
        styles["body"]))
    story.append(Spacer(1, 3*mm))

    ref_col_widths = [110, 75, width - 185]
    ref_header_row = [
        Paragraph("Métrica",        styles["table_header"]),
        Paragraph("Umbral / Rango esperado", styles["table_header"]),
        Paragraph("Justificación",  styles["table_header"]),
    ]
    ref_raw = [
        ("Entropía — ciphertext (video/audio)",
         "≥ 7.9 bits/byte\n(ideal: 8.000)",
         "Distribución uniforme de bytes indica máxima aleatoriedad. Cualquier valor < 7.9 revela patrones explotables por un atacante."),
        ("Entropía — MNAK completo (M×N×A×K)",
         "≈ 8.000 bits/byte\n(desv. estándar < 0.001)",
         "El payload completo (frame + audio + estado K) debe alcanzar entropía máxima. Desviación < 0.001 confirma uniformidad entre frames."),
        ("Correlación entre píxeles — ciphertext\n(horizontal, vertical, diagonal)",
         "|r| < 0.01",
         "El cifrador debe destruir toda correlación espacial. Valores |r| > 0.1 indican que el contenido original es parcialmente recuperable."),
        ("PSNR — descifrado correcto",
         "≥ 40 dB\n(lossless ideal: ∞ / MSE = 0)",
         "Un descifrado perfecto reproduce el frame original bit a bit. PSNR < 30 dB señala pérdida de información en el pipeline de descifrado."),
        ("MSE / MAD — descifrado correcto",
         "≈ 0.0\n(ideal exacto: 0)",
         "Error cuadrático medio y desviación absoluta media deben ser nulos para un descifrado lossless perfecto."),
        ("SSIM — descifrado correcto",
         "≥ 0.99\n(ideal: 1.0)",
         "Índice de similitud estructural. Valores < 0.9 indican degradación visual perceptible por el usuario final."),
        ("PSNR / SSIM — clave incorrecta",
         "PSNR < 15 dB\nSSIM < 0.05",
         "Con clave errónea el resultado debe ser indistinguible de ruido. SSIM > 0.1 con clave incorrecta constituye una vulnerabilidad grave."),
        ("NPCR — sensibilidad diferencial",
         "> 99.60%\n(ideal teórico: 99.6094%)",
         "Cambiar 1 píxel en el plaintext debe alterar >99.6% del ciphertext. Valor teórico para distribución uniforme de 8 bits: 99.6094%."),
        ("UACI — intensidad diferencial",
         "33.46% ± 0.5%\n(ideal: 33.4635%)",
         "Intensidad media del cambio diferencial. Desviaciones > 1% del ideal indican no uniformidad del keystream hipercaótico."),
        ("PSNR ciphertext bajo ataques\n(ruido gaussiano / oclusión)",
         "< 15 dB",
         "El ciphertext perturbado no debe revelar contenido visual. PSNR bajo confirma ocultamiento de estructura incluso bajo ataques pasivos."),
        ("NIST Monobit test (p-valor)",
         "p ≥ 0.01",
         "Verifica balance entre bits 0 y 1 en el keystream generado por el sistema hipercaótico. Fallo indica sesgo estadístico explotable."),
        ("NIST Block Frequency test (p-valor)",
         "p ≥ 0.01",
         "Verifica uniformidad en bloques de bits del keystream. Fallo indica patrones periódicos en el generador pseudoaleatorio."),
        ("Tiempo por frame — cifrado/descifrado",
         "< 0.033 s/frame\n(≥ 30 fps en tiempo real)",
         "Para video en tiempo real se requieren ≥ 30 frames/s. Para cifrado offline el umbral es flexible; se reporta como referencia comparativa."),
        ("Tiempo por archivo .mnak",
         "< 0.010 s/frame",
         "Lectura e interpretación del payload completo M×N×A×K debe ser eficiente para no ser el cuello de botella del pipeline."),
    ]

    exp_style = ParagraphStyle("exp_cell", fontName="Helvetica-Oblique",
                               fontSize=7.5, textColor=COLOR_SUBTITLE, leading=11)
    ref_data = [ref_header_row]
    for i, (metric, expected_val, justif) in enumerate(ref_raw, start=1):
        ref_data.append([
            Paragraph(metric,       styles["table_cell"]),
            Paragraph(expected_val, exp_style),
            Paragraph(justif,       styles["table_cell"]),
        ])

    ref_ts = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), COLOR_PRIMARY),
        ("BOX",           (0, 0), (-1, -1), 0.6, COLOR_BORDER),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, COLOR_BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ] + [
        ("BACKGROUND", (0, i), (-1, i), COLOR_ROW_ALT if i % 2 == 0 else colors.white)
        for i in range(1, len(ref_data))
    ])

    ref_table = Table(ref_data, colWidths=ref_col_widths, style=ref_ts, repeatRows=1)
    story.append(ref_table)

    # ── VISUALIZACIÓN DE RESULTADOS ───────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Visualización de Resultados", styles["section_title"]))
    story.append(hr(COLOR_PRIMARY, 1.2))

    # ---- Histogramas ----
    story.append(Paragraph("Distribución de Intensidades (Histogramas)", styles["subsection_title"]))
    story.append(Paragraph(
        "Los histogramas muestran la distribución de valores de píxeles. El plaintext (original) "
        "concentra valores según el contenido visual. El ciphertext ideal presenta distribución "
        "uniforme en [0, 255], evidenciando máxima entropía y ausencia de patrones.",
        styles["body"]))
    story.append(Spacer(1, 3*mm))

    hist_images = [
        ("hist_original.png",   "Histograma del plaintext (video original)"),
        ("hist_encrypted.png",  "Histograma del ciphertext (video cifrado)"),
        ("hist_decrypted.png",  "Histograma del plaintext recuperado (descifrado)"),
    ]

    # Par lado a lado
    pair_rows = []
    pair_captions = []
    row_imgs = []
    row_caps = []

    for fname, caption in hist_images:
        fpath = os.path.join(plots_dir, fname)
        if os.path.exists(fpath):
            row_imgs.append(Image(fpath, width=85*mm, height=55*mm))
            row_caps.append(caption)
        if len(row_imgs) == 2:
            pair_rows.append(row_imgs[:])
            pair_captions.append(row_caps[:])
            row_imgs.clear()
            row_caps.clear()

    if row_imgs:     # imagen suelta
        pair_rows.append(row_imgs + [Spacer(85*mm, 55*mm)])
        pair_captions.append(row_caps + [""])

    img_ts = TableStyle([
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ])

    for imgs, caps in zip(pair_rows, pair_captions):
        story.append(Table([imgs], colWidths=[width/2, width/2], style=img_ts))
        cap_row = [Paragraph(c, styles["caption"]) for c in caps]
        story.append(Table([cap_row], colWidths=[width/2, width/2], style=img_ts))
        story.append(Spacer(1, 3*mm))

    # ---- Correlación ----
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("Correlación entre Píxeles Adyacentes", styles["subsection_title"]))
    story.append(Paragraph(
        "Las gráficas de dispersión comparan píxeles adyacentes horizontales. En el plaintext se "
        "observa correlación alta (puntos agrupados en diagonal). En el ciphertext seguro la nube "
        "de puntos debe ser uniforme y dispersa (correlación ≈ 0), indicando que la relación "
        "espacial ha sido destruida.",
        styles["body"]))
    story.append(Spacer(1, 3*mm))

    corr_images = [
        ("corr_original.png",   "Correlación horizontal — plaintext"),
        ("corr_encrypted.png",  "Correlación horizontal — ciphertext (video)"),
    ]

    corr_imgs = []
    corr_caps = []
    for fname, caption in corr_images:
        fpath = os.path.join(plots_dir, fname)
        if os.path.exists(fpath):
            corr_imgs.append(Image(fpath, width=85*mm, height=55*mm))
            corr_caps.append(caption)

    if corr_imgs:
        while len(corr_imgs) < 2:
            corr_imgs.append(Spacer(85*mm, 55*mm))
            corr_caps.append("")
        story.append(Table([corr_imgs], colWidths=[width/2, width/2], style=img_ts))
        story.append(Table(
            [[Paragraph(c, styles["caption"]) for c in corr_caps]],
            colWidths=[width/2, width/2], style=img_ts))

    # ── BUILD ─────────────────────────────────────────────────────────
    doc.build(
        story,
        onFirstPage=lambda c, d: on_page(c, d, styles),
        onLaterPages=lambda c, d: on_page(c, d, styles),
    )