"""
pdf_report.py
Generación de informe PDF académico con formato estructurado.

Estructura del informe:
  - Portada con título y parámetros del sistema
  - Tabla de resultados por sección con resultado esperado e interpretación automática
  - Comparativa de métricas vs valores de referencia bibliográfica
  - Conclusión automática de seguridad
  - Sección de gráficas con leyendas
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os
import datetime


# ─────────────────────────────────────────────────────────────────────────────
# Valores de referencia bibliográfica
# ─────────────────────────────────────────────────────────────────────────────

REFERENCE_VALUES = {
    "Entropía": {
        "ideal":    8.0,
        "min_pass": 7.99,
        "unidad":   "bits",
        "criterio": ">= 7.99",
        "fuente":   "Shannon (1948)"
    },
    "NPCR": {
        "ideal":    99.6096,
        "min_pass": 99.0,
        "unidad":   "%",
        "criterio": "> 99.0%",
        "fuente":   "Wu et al. (2011)"
    },
    "UACI": {
        "ideal":    33.4635,
        "min_pass": 32.0,
        "max_pass": 35.0,
        "unidad":   "%",
        "criterio": "33.46 ± 1.5%",
        "fuente":   "Wu et al. (2011)"
    },
    "Correlación": {
        "ideal":    0.0,
        "max_pass": 0.1,
        "unidad":   "",
        "criterio": "|r| < 0.1",
        "fuente":   "Gonzalez-Olvera et al. (2020)"
    },
    "MSE (cifrado)": {
        "ideal":    "> 9 555",
        "min_pass": 9555,
        "unidad":   "",
        "criterio": "> 9 555 (alta distorsión)",
        "fuente":   "Ahmad & Hwang (2016)"
    },
    "MAD (cifrado)": {
        "ideal":    "máximo",
        "min_pass": 60.0,
        "unidad":   "",
        "criterio": "> 60 (alta distorsión media)",
        "fuente":   "Alvarez & Li (2006)"
    },
    "Varianza histograma (cifrado)": {
        "ideal":    0,
        "max_pass": 5000,
        "unidad":   "",
        "criterio": "Mínima (≈ 0 ideal)",
        "fuente":   "Enayatifar et al. (2019); MDPI Entropy"
    },
    "PSNR cifrado": {
        "ideal":    8.0,
        "min_pass": 7.0,
        "max_pass": 12.0,
        "unidad":   "dB",
        "criterio": "8–12 dB (ruido puro)",
        "fuente":   "Parametro estándar"
    },
    "SSIM clave incorrecta": {
        "ideal":    0.0,
        "max_pass": 0.05,
        "unidad":   "",
        "criterio": "< 0.05",
        "fuente":   "Wang et al. (2004)"
    },
    "PSNR descifrado": {
        "ideal":    "inf",
        "min_pass": 40.0,
        "unidad":   "dB",
        "criterio": "> 40 dB (lossless)",
        "fuente":   "Estándar de calidad"
    },
    "SSIM descifrado": {
        "ideal":    1.0,
        "min_pass": 0.99,
        "unidad":   "",
        "criterio": "> 0.99",
        "fuente":   "Wang et al. (2004)"
    },
    "Monobit (NIST)": {
        "ideal":    "p ≥ 0.05",
        "min_pass": 0.01,
        "unidad":   "p-value",
        "criterio": "p > 0.01",
        "fuente":   "NIST SP 800-22 (2010)"
    },
    "Block Frequency (NIST)": {
        "ideal":    "p ≥ 0.05",
        "min_pass": 0.01,
        "unidad":   "p-value",
        "criterio": "p > 0.01",
        "fuente":   "NIST SP 800-22 (2010)"
    },
    "Tiempo por frame": {
        "ideal":    "< 0.033 s",
        "min_pass": 0.033,
        "unidad":   "s",
        "criterio": "< 0.033 s para 30 fps",
        "fuente":   "Req. tiempo real"
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Resultados esperados por métrica (para columna "Resultado Esperado")
# ─────────────────────────────────────────────────────────────────────────────

EXPECTED_RESULTS = {
    # ── Aleatoriedad ──────────────────────────────────────────────────────────
    "Entropía de Shannon (ciphertext)": {
        "valor":    "≥ 7.99 bits",
        "ideal":    "8.0 bits",
        "fuente":   "Shannon (1948)",
        "nota":     "Máxima entropía indica distribución uniforme de bytes"
    },
    "Entropía de Shannon (MNAK)": {
        "valor":    "≥ 7.99 bits",
        "ideal":    "8.0 bits",
        "fuente":   "Shannon (1948)",
        "nota":     "Incluye frame + audio + estado caótico serializado"
    },
    # ── Estadísticas / Correlación ────────────────────────────────────────────
    "Correlación horizontal (ciphertext)": {
        "valor":    "|r| < 0.1",
        "ideal":    "r ≈ 0.0",
        "fuente":   "Gonzalez-Olvera et al. (2020)",
        "nota":     "Sin correlación estadística entre píxeles adyacentes"
    },
    "Correlación vertical (ciphertext)": {
        "valor":    "|r| < 0.1",
        "ideal":    "r ≈ 0.0",
        "fuente":   "Gonzalez-Olvera et al. (2020)",
        "nota":     "Difusión espacial completa en dirección vertical"
    },
    "Correlación diagonal (ciphertext)": {
        "valor":    "|r| < 0.1",
        "ideal":    "r ≈ 0.0",
        "fuente":   "Gonzalez-Olvera et al. (2020)",
        "nota":     "Difusión espacial completa en dirección diagonal"
    },
    "Correlación horizontal (MNAK)": {
        "valor":    "|r| < 0.1",
        "ideal":    "r ≈ 0.0",
        "fuente":   "Gonzalez-Olvera et al. (2020)",
        "nota":     "Correlación nula en archivo MNAK completo"
    },
    "Correlación vertical (MNAK)": {
        "valor":    "|r| < 0.1",
        "ideal":    "r ≈ 0.0",
        "fuente":   "Gonzalez-Olvera et al. (2020)",
        "nota":     "Correlación nula en archivo MNAK completo"
    },
    "Correlación diagonal (MNAK)": {
        "valor":    "|r| < 0.1",
        "ideal":    "r ≈ 0.0",
        "fuente":   "Gonzalez-Olvera et al. (2020)",
        "nota":     "Correlación nula en archivo MNAK completo"
    },
    # ── Varianza de histograma ────────────────────────────────────────────────
    "Varianza (Cifrado)": {
        "valor":    "Mínima posible",
        "ideal":    "≈ 0 (histograma uniforme)",
        "fuente":   "Enayatifar et al., MDPI Entropy (2019)",
        "nota":     "Histograma uniforme → varianza mínima → máxima aleatoriedad"
    },
    "Varianza (Original)": {
        "valor":    "Alta (contenido visual)",
        "ideal":    "Refleja contenido del video",
        "fuente":   "Referencia comparativa",
        "nota":     "Varianza alta en plaintext es esperable (contenido estructurado)"
    },
    # ── Calidad del descifrado ────────────────────────────────────────────────
    "PSNR (dB)": {
        "valor":    "7 – 12 dB (cifrado)",
        "ideal":    "≈ 8 dB (ruido puro)",
        "fuente":   "Ahmad & Hwang (2016); Parámetro estándar",
        "nota":     "PSNR bajo entre original y cifrado indica alta distorsión (seguro)"
    },
    "MSE": {
        "valor":    "> 9 555",
        "ideal":    "> 10 000",
        "fuente":   "Ahmad & Hwang (2016); Tandfonline (2021)",
        "nota":     "MSE alto entre plaintext y ciphertext confirma alta distorsión"
    },
    "MAD": {
        "valor":    "> 60",
        "ideal":    "> 80",
        "fuente":   "Alvarez & Li (2006); PMC (2022)",
        "nota":     "Error absoluto medio alto indica gran diferencia pixel a pixel"
    },
    "SSIM": {
        "valor":    "> 0.99 (descifrado)",
        "ideal":    "1.0",
        "fuente":   "Wang et al. (2004)",
        "nota":     "SSIM para calidad de descifrado; 1.0 = imagen idéntica al original"
    },
    # ── Sensibilidad a la clave ───────────────────────────────────────────────
    "PSNR (clave incorrecta)": {
        "valor":    "7 – 12 dB",
        "ideal":    "≈ 8 dB (ruido)",
        "fuente":   "Parámetro estándar de cifrado",
        "nota":     "Clave errónea debe producir imagen de ruido puro"
    },
    "SSIM (clave incorrecta)": {
        "valor":    "< 0.05",
        "ideal":    "≈ 0.0",
        "fuente":   "Wang et al. (2004)",
        "nota":     "Sin estructura recuperable con clave incorrecta"
    },
    # ── Pruebas diferenciales ─────────────────────────────────────────────────
    "NPCR": {
        "valor":    "> 99.0 %",
        "ideal":    "99.6096 %",
        "fuente":   "Wu et al. (2011)",
        "nota":     "Cambio de 1 píxel en plaintext altera ~100% del ciphertext"
    },
    "UACI": {
        "valor":    "33.46 ± 1.5 %",
        "ideal":    "33.4635 %",
        "fuente":   "Wu et al. (2011)",
        "nota":     "Intensidad promedio de cambio entre dos ciphertexts"
    },
    # ── Robustez ──────────────────────────────────────────────────────────────
    "PSNR con ruido": {
        "valor":    "> 25 dB",
        "ideal":    "≥ 30 dB",
        "fuente":   "Scientific Reports (2025); Parámetro estándar",
        "nota":     "Degradación mínima ante ruido gaussiano moderado"
    },
    "PSNR con oclusión": {
        "valor":    "> 20 dB",
        "ideal":    "≥ 25 dB",
        "fuente":   "Scientific Reports (2025); Parámetro estándar",
        "nota":     "Tolerancia a pérdida parcial del ciphertext (1/4 de imagen)"
    },
    # ── Pruebas NIST ──────────────────────────────────────────────────────────
    "Monobit test (p-value)": {
        "valor":    "p > 0.01",
        "ideal":    "p ≥ 0.05",
        "fuente":   "NIST SP 800-22 (2010)",
        "nota":     "Balance entre bits 0 y 1 en la secuencia cifrada"
    },
    "Block Frequency test (p-value)": {
        "valor":    "p > 0.01",
        "ideal":    "p ≥ 0.05",
        "fuente":   "NIST SP 800-22 (2010)",
        "nota":     "Uniformidad en bloques de 128 bits"
    },
    # ── Dimensiones / parámetros MNAK ────────────────────────────────────────
    "Dimensiones MNAK": {
        "valor":    "Según configuración",
        "ideal":    "M×N×A×K definidos por el video",
        "fuente":   "Parámetro de sistema M×N×A×K",
        "nota":     "M=ancho, N=alto, A=muestras audio/frame, K=bytes estado caótico"
    },
    # ── Eficiencia ────────────────────────────────────────────────────────────
    "Tiempo lectura original (s)": {
        "valor":    "Referencial (I/O)",
        "ideal":    "< 0.5 s (lectura disco)",
        "fuente":   "Depende del hardware y codec",
        "nota":     "Tiempo de lectura del video sin cifrar del disco"
    },
    "Tiempo lectura cifrado (s)": {
        "valor":    "Referencial (I/O)",
        "ideal":    "< 0.5 s (lectura disco)",
        "fuente":   "Depende del hardware",
        "nota":     "Tiempo de lectura del archivo .mnak cifrado"
    },
    "Tiempo lectura descifrado (s)": {
        "valor":    "Referencial (I/O)",
        "ideal":    "< 0.5 s (lectura disco)",
        "fuente":   "Depende del hardware",
        "nota":     "Tiempo de lectura tras descifrado completo"
    },
    "Tiempo por frame (cifrado)": {
        "valor":    "< 0.033 s (30 fps)",
        "ideal":    "< 0.033 s",
        "fuente":   "Requisito de tiempo real (30 fps)",
        "nota":     "< 0.033 s/frame habilita cifrado en tiempo real a 30 fps"
    },
    "Tiempo de cifrado por frame (s)": {
        "valor":    "< 0.1 s",
        "ideal":    "< 0.033 s (30 fps)",
        "fuente":   "Requisito de tiempo real",
        "nota":     "< 0.033 s permite cifrado en tiempo real a 30 fps"
    },
    "Tiempo total de cifrado (s)": {
        "valor":    "Proporcional a frames",
        "ideal":    "Lineal con K frames",
        "fuente":   "Depende del hardware",
        "nota":     "Escala linealmente con el número de frames procesados"
    },
    "Frames procesados": {
        "valor":    "Según parámetro K",
        "ideal":    "Todos los frames del video",
        "fuente":   "Parámetro de configuración",
        "nota":     "Número de frames evaluados en el análisis de rendimiento"
    },
}

# Función auxiliar: obtener resultado esperado formateado para una métrica
def _get_expected(key):
    """
    Busca el resultado esperado para una métrica dada por coincidencia parcial
    en el diccionario EXPECTED_RESULTS.
    Devuelve una cadena con 'valor (fuente)' o un texto inferido.
    """
    k_low = key.lower()
    # Búsqueda exacta primero
    if key in EXPECTED_RESULTS:
        e = EXPECTED_RESULTS[key]
        return f"{e['valor']}\nIdeal: {e['ideal']}\n[{e['fuente']}]"

    # Búsqueda por coincidencia parcial
    for ref_key, e in EXPECTED_RESULTS.items():
        if ref_key.lower() in k_low or k_low in ref_key.lower():
            return f"{e['valor']}\nIdeal: {e['ideal']}\n[{e['fuente']}]"

    # Inferencia desde REFERENCE_VALUES por palabras clave
    if "entropía" in k_low or "entropy" in k_low:
        r = REFERENCE_VALUES["Entropía"]
        return f"{r['criterio']} {r['unidad']}\nIdeal: {r['ideal']} {r['unidad']}\n[{r['fuente']}]"
    if "npcr" in k_low:
        r = REFERENCE_VALUES["NPCR"]
        return f"{r['criterio']}\nIdeal: {r['ideal']} {r['unidad']}\n[{r['fuente']}]"
    if "uaci" in k_low:
        r = REFERENCE_VALUES["UACI"]
        return f"{r['criterio']}\nIdeal: {r['ideal']} {r['unidad']}\n[{r['fuente']}]"
    if "correlación" in k_low or "correlacion" in k_low:
        r = REFERENCE_VALUES["Correlación"]
        return f"{r['criterio']}\nIdeal: {r['ideal']}\n[{r['fuente']}]"
    if "mse" in k_low:
        return "> 9 555 (alta distorsión)\nIdeal: > 10 000\n[Ahmad & Hwang (2016)]"
    if "mad" in k_low:
        return "> 60\nIdeal: > 80\n[Alvarez & Li (2006)]"
    if "varianza" in k_low or "variance" in k_low:
        return "Mínima posible\nIdeal: ≈ 0 (histograma uniforme)\n[Enayatifar et al. (2019)]"
    if "dimensiones" in k_low or "mnak" in k_low:
        return "Según configuración\nIdeal: M×N×A×K del video\n[Parámetro de sistema]"
    if "psnr" in k_low:
        if "descifrad" in k_low or "dec" in k_low:
            r = REFERENCE_VALUES["PSNR descifrado"]
            return f"{r['criterio']}\nIdeal: {r['ideal']} {r['unidad']}\n[{r['fuente']}]"
        else:
            r = REFERENCE_VALUES["PSNR cifrado"]
            return f"{r['criterio']}\nIdeal: {r['ideal']} {r['unidad']}\n[{r['fuente']}]"
    if "ssim" in k_low:
        if "incorrecta" in k_low or "wrong" in k_low:
            r = REFERENCE_VALUES["SSIM clave incorrecta"]
            return f"{r['criterio']}\nIdeal: {r['ideal']}\n[{r['fuente']}]"
        else:
            r = REFERENCE_VALUES["SSIM descifrado"]
            return f"{r['criterio']}\nIdeal: {r['ideal']}\n[{r['fuente']}]"
    if "monobit" in k_low:
        return "p > 0.01\nIdeal: p ≥ 0.05\n[NIST SP 800-22 (2010)]"
    if "block frequency" in k_low or "bloque" in k_low:
        return "p > 0.01\nIdeal: p ≥ 0.05\n[NIST SP 800-22 (2010)]"
    if "tiempo" in k_low or "time" in k_low:
        if "frame" in k_low:
            return "< 0.033 s/frame (30 fps)\nIdeal: < 0.033 s\n[Req. tiempo real]"
        else:
            return "< 0.5 s (I/O disco)\nIdeal: Referencial\n[Depende del hardware]"
    if "frames" in k_low:
        return "Todos los frames del video\nIdeal: K frames completos\n[Parámetro de sistema]"

    return "Ver bibliografía\nde referencia"


# ─────────────────────────────────────────────────────────────────────────────
# Interpretación automática de métricas
# ─────────────────────────────────────────────────────────────────────────────

def _classify_metric(key, value):
    """
    Clasifica una métrica como APROBADA, MARGINAL o FALLIDA.
    Devuelve (estado, color, interpretación_texto).
    """
    k_low = key.lower()

    # Entropía
    if "entropía" in k_low or "entropy" in k_low:
        if isinstance(value, float):
            if value >= 7.99:
                return "✓ APROBADO", colors.HexColor("#1a7a1a"), \
                       f"H={value:.4f} bits — distribución casi uniforme (ideal: 8.0)"
            elif value >= 7.90:
                return "~ MARGINAL", colors.HexColor("#b86f00"), \
                       f"H={value:.4f} bits — aceptable, pero por debajo del ideal"
            else:
                return "✗ FALLIDO", colors.HexColor("#9b0000"), \
                       f"H={value:.4f} bits — insuficiente (mín. recomendado: 7.99)"

    # NPCR
    if "npcr" in k_low:
        if isinstance(value, float):
            if value >= 99.0:
                return "✓ APROBADO", colors.HexColor("#1a7a1a"), \
                       f"{value:.4f}% — alta sensibilidad al cambio de un píxel"
            elif value >= 95.0:
                return "~ MARGINAL", colors.HexColor("#b86f00"), \
                       f"{value:.4f}% — sensibilidad moderada (ideal: >99.6%)"
            else:
                return "✗ FALLIDO", colors.HexColor("#9b0000"), \
                       f"{value:.4f}% — sensibilidad insuficiente"

    # UACI
    if "uaci" in k_low:
        if isinstance(value, float):
            if 30.0 <= value <= 36.0:
                return "✓ APROBADO", colors.HexColor("#1a7a1a"), \
                       f"{value:.4f}% — intensidad de cambio adecuada (ideal: 33.46%)"
            elif 25.0 <= value <= 40.0:
                return "~ MARGINAL", colors.HexColor("#b86f00"), \
                       f"{value:.4f}% — fuera del rango óptimo pero funcional"
            else:
                return "✗ FALLIDO", colors.HexColor("#9b0000"), \
                       f"{value:.4f}% — valor atípico"

    # Correlación
    if "correlación" in k_low or "correlacion" in k_low:
        if isinstance(value, float):
            if abs(value) < 0.1:
                return "✓ APROBADO", colors.HexColor("#1a7a1a"), \
                       f"r={value:.6f} — sin correlación estadística entre píxeles"
            elif abs(value) < 0.3:
                return "~ MARGINAL", colors.HexColor("#b86f00"), \
                       f"r={value:.6f} — correlación baja pero detectada"
            else:
                return "✗ FALLIDO", colors.HexColor("#9b0000"), \
                       f"r={value:.6f} — correlación significativa (patrón detectable)"

    # PSNR — contexto depende del uso (cifrado vs descifrado)
    if "psnr" in k_low:
        if isinstance(value, float):
            if "descifrad" in k_low or "dec" in k_low:
                if value == float('inf') or value > 60.0:
                    return "✓ APROBADO", colors.HexColor("#1a7a1a"), \
                           "Descifrado perfecto (lossless)"
                elif value > 40.0:
                    return "✓ APROBADO", colors.HexColor("#1a7a1a"), \
                           f"{value:.2f} dB — calidad de descifrado excelente"
                elif value > 30.0:
                    return "~ MARGINAL", colors.HexColor("#b86f00"), \
                           f"{value:.2f} dB — calidad aceptable con pérdidas menores"
                else:
                    return "✗ FALLIDO", colors.HexColor("#9b0000"), \
                           f"{value:.2f} dB — pérdida significativa en descifrado"
            else:
                if 7.0 <= value <= 12.0:
                    return "✓ APROBADO", colors.HexColor("#1a7a1a"), \
                           f"{value:.2f} dB — cifrado produce apariencia de ruido"
                elif value < 7.0:
                    return "~ MARGINAL", colors.HexColor("#b86f00"), \
                           f"{value:.2f} dB — muy bajo, verificar implementación"
                else:
                    return "~ MARGINAL", colors.HexColor("#b86f00"), \
                           f"{value:.2f} dB — cifrado visible (>12 dB)"

    # SSIM
    if "ssim" in k_low:
        if isinstance(value, float):
            if "incorrecta" in k_low or "wrong" in k_low:
                if value < 0.05:
                    return "✓ APROBADO", colors.HexColor("#1a7a1a"), \
                           f"SSIM={value:.5f} — sin estructura recuperable con clave incorrecta"
                elif value < 0.15:
                    return "~ MARGINAL", colors.HexColor("#b86f00"), \
                           f"SSIM={value:.5f} — estructura residual mínima"
                else:
                    return "✗ FALLIDO", colors.HexColor("#9b0000"), \
                           f"SSIM={value:.5f} — estructura visible con clave incorrecta"
            else:
                if value > 0.99:
                    return "✓ APROBADO", colors.HexColor("#1a7a1a"), \
                           f"SSIM={value:.5f} — descifrado perfectamente fiel"
                elif value > 0.95:
                    return "~ MARGINAL", colors.HexColor("#b86f00"), \
                           f"SSIM={value:.5f} — pequeñas discrepancias"
                else:
                    return "✗ FALLIDO", colors.HexColor("#9b0000"), \
                           f"SSIM={value:.5f} — calidad de descifrado insuficiente"

    # Monobit / NIST
    if "monobit" in k_low:
        if isinstance(value, float):
            if value > 0.01:
                return "✓ APROBADO", colors.HexColor("#1a7a1a"), \
                       f"p={value:.5f} — balance de bits adecuado (H0 no rechazada)"
            else:
                return "✗ FALLIDO", colors.HexColor("#9b0000"), \
                       f"p={value:.5f} — desbalance de bits detectado (p < 0.01)"

    if "block frequency" in k_low or "bloque" in k_low:
        if isinstance(value, float):
            if value > 0.01:
                return "✓ APROBADO", colors.HexColor("#1a7a1a"), \
                       f"p={value:.5f} — distribución de bloques uniforme"
            else:
                return "✗ FALLIDO", colors.HexColor("#9b0000"), \
                       f"p={value:.5f} — bloques no uniformes detectados"

    # Genérico
    return "—", colors.black, str(value)


# ─────────────────────────────────────────────────────────────────────────────
# Descripción por sección
# ─────────────────────────────────────────────────────────────────────────────

SECTION_DESCRIPTIONS = {
    "Aleatoriedad": (
        "La entropía de Shannon mide la uniformidad de la distribución de bytes en el "
        "ciphertext. Un valor cercano al máximo teórico de 8.0 bits indica que el cifrador "
        "produce salidas estadísticamente indistinguibles de ruido aleatorio uniforme."
    ),
    "Estadísticas": (
        "Las pruebas de correlación verifican que los píxeles adyacentes del ciphertext "
        "no presenten dependencia lineal. Coeficientes próximos a cero indican alta "
        "difusión: el cifrador elimina efectivamente la estructura espacial del plaintext."
    ),
    "Calidad del descifrado": (
        "Mide la fidelidad de la recuperación del plaintext a partir del ciphertext. "
        "Un PSNR = ∞ dB y SSIM = 1.0 indican descifrado perfecto (lossless). Valores "
        "inferiores señalan pérdida de información o error de sincronización."
    ),
    "Sensibilidad a la clave": (
        "Evalúa la propiedad de efecto avalancha ante variaciones mínimas en la clave. "
        "Con semilla ε=1×10⁻¹⁰ diferente, el ciphertext descifrado debe ser "
        "indistinguible de ruido aleatorio (PSNR ≈ 8–12 dB, SSIM ≈ 0)."
    ),
    "Pruebas diferenciales": (
        "Mide el cambio en el ciphertext ante la modificación de exactamente 1 píxel "
        "del plaintext. NPCR > 99.6% indica que casi todos los bytes del ciphertext "
        "cambian (efecto avalancha), y UACI ≈ 33.46% verifica la intensidad promedio "
        "del cambio. Estas métricas se calculan sobre el ciphertext completo M×N×A×K."
    ),
    "Robustez": (
        "Simula ataques físicos sobre el ciphertext: adición de ruido gaussiano y "
        "oclusión de bloques. Un cifrador robusto debe degradar mínimamente la "
        "calidad del plaintext recuperado ante perturbaciones moderadas del ciphertext."
    ),
    "Pruebas NIST": (
        "Subconjunto de las pruebas estadísticas de aleatoriedad NIST SP 800-22. "
        "El test Monobit verifica el balance entre bits 0 y 1. El Block Frequency "
        "test verifica uniformidad en bloques de 128 bits. p > 0.01 indica que la "
        "hipótesis de aleatoriedad no puede rechazarse."
    ),
    "Eficiencia": (
        "Métricas de rendimiento del sistema de cifrado. El tiempo por frame determina "
        "la viabilidad del sistema para aplicaciones en tiempo real o near-real-time."
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Constructor del informe
# ─────────────────────────────────────────────────────────────────────────────

def generate_pdf_report(results, plots_dir, output_path, system_params=None):
    """
    Genera el informe PDF académico completo.

    Args:
        results:       dict { sección: { métrica: valor } }
        plots_dir:     directorio con las imágenes de gráficas
        output_path:   ruta del PDF de salida
        system_params: dict opcional con parámetros del sistema
                       { 'M', 'N', 'A', 'K', 'seed', 'frames' }
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
    )

    styles = getSampleStyleSheet()
    W      = A4[0] - 5.0 * cm   # ancho útil

    # ── Estilos personalizados ────────────────────────────────────────────────
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        textColor=colors.HexColor("#1a2e4a"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    style_subtitle = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor("#4a4a4a"),
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    style_section = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor("#1a2e4a"),
        spaceBefore=14,
        spaceAfter=4,
        borderPad=4,
    )
    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor("#333333"),
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    style_caption = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor("#666666"),
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    style_footer = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=7.5,
        textColor=colors.HexColor("#888888"),
        alignment=TA_CENTER,
    )

    # Estilo de celda reutilizable
    def cell_style(size=8, align=TA_LEFT, bold=False):
        return ParagraphStyle(
            'cell',
            fontSize=size,
            leading=11,
            alignment=align,
            fontName='Helvetica-Bold' if bold else 'Helvetica',
        )

    story = []

    # ═══════════════════════════════════════════════════════════════════════════
    # PORTADA
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(
        "Informe de Evaluación Criptográfica", style_title
    ))
    story.append(Paragraph(
        "Sistema de Cifrado de Video con Caos Hipercaótico 4D (M×N×A×K)",
        style_subtitle
    ))
    story.append(HRFlowable(width="100%", thickness=1.5,
                             color=colors.HexColor("#1a2e4a"), spaceAfter=8))

    fecha = datetime.datetime.now().strftime("%d de %B de %Y, %H:%M")
    story.append(Paragraph(f"Generado: {fecha}", style_caption))

    # Parámetros del sistema
    if system_params:
        params_data = [
            ["Parámetro", "Valor", "Descripción"],
            ["M × N", f"{system_params.get('M','—')} × {system_params.get('N','—')}",
             "Resolución del frame (ancho × alto)"],
            ["A", str(system_params.get('A', '—')), "Muestras de audio por frame"],
            ["K", str(system_params.get('K', '—')), "Dimensión del estado caótico (bytes)"],
            ["Semilla", str(system_params.get('seed', 0.1)), "Condición inicial del generador"],
            ["Frames", str(system_params.get('frames', '—')), "Frames procesados en el análisis"],
        ]
        params_table = Table(params_data, colWidths=[W * 0.25, W * 0.25, W * 0.50])
        params_table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0),  colors.HexColor("#1a2e4a")),
            ('TEXTCOLOR',    (0, 0), (-1, 0),  colors.white),
            ('FONTNAME',     (0, 0), (-1, 0),  'Helvetica-Bold'),
            ('FONTSIZE',     (0, 0), (-1, -1), 8.5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.HexColor("#f0f4f8"), colors.white]),
            ('GRID',         (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
            ('ALIGN',        (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING',   (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
            ('LEFTPADDING',  (0, 0), (-1, -1), 8),
        ]))
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph("Parámetros del Sistema", style_section))
        story.append(params_table)

    story.append(Spacer(1, 0.5 * cm))

    # ── Descripción del pipeline ──────────────────────────────────────────────
    story.append(Paragraph("Pipeline de Cifrado", style_section))
    story.append(Paragraph(
        "El sistema implementa un cifrador de video multicapa basado en un sistema "
        "hipercaótico con retardo de tiempo de 4 dimensiones (x, y, z, w). El pipeline "
        "de cifrado por frame consta de tres capas independientes: "
        "(1) <b>Arnold Cat Map</b> con parámetros derivados del estado caótico — permutación "
        "espacial determinista de los píxeles del frame RGB; "
        "(2) <b>XOR Caótico</b> — operación XOR byte a byte entre el frame permutado y un "
        "keystream expandido desde el estado caótico vía SHA3-256 en modo contador; "
        "(3) <b>AES-CTR</b> — cifrado final del payload MNAK serializado completo (frame + "
        "audio + estado caótico), con clave e IV derivados del mismo estado caótico. "
        "El estado caótico almacenado en el header sirve para verificación de integridad.",
        style_body
    ))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # SECCIONES DE RESULTADOS
    # ═══════════════════════════════════════════════════════════════════════════
    pass_count   = 0
    fail_count   = 0
    margin_count = 0

    for section, metrics in results.items():
        story.append(Paragraph(section, style_section))
        story.append(HRFlowable(width="100%", thickness=0.5,
                                 color=colors.HexColor("#aaaaaa"), spaceAfter=4))

        # Descripción de la sección
        if section in SECTION_DESCRIPTIONS:
            story.append(Paragraph(SECTION_DESCRIPTIONS[section], style_body))

        # ── Tabla de métricas con columna "Resultado Esperado" ────────────────
        # Anchos: Métrica | Valor obtenido | Resultado esperado | Estado | Interpretación
        col_widths = [W * 0.22, W * 0.10, W * 0.22, W * 0.11, W * 0.35]

        table_data = [[
            Paragraph("<b>Métrica</b>",           cell_style(8, TA_LEFT,   True)),
            Paragraph("<b>Valor\nobt.</b>",        cell_style(8, TA_CENTER, True)),
            Paragraph("<b>Resultado esperado</b>", cell_style(8, TA_LEFT,   True)),
            Paragraph("<b>Estado</b>",             cell_style(8, TA_CENTER, True)),
            Paragraph("<b>Interpretación</b>",     cell_style(8, TA_LEFT,   True)),
        ]]

        for key, value in metrics.items():
            # ── Valor formateado ──────────────────────────────────────────────
            if isinstance(value, float):
                if value == float('inf'):
                    val_str = "∞"
                elif abs(value) < 1e-4 and value != 0.0:
                    val_str = f"{value:.2e}"
                else:
                    val_str = f"{value:.5f}"
            else:
                val_str = str(value)

            # ── Clasificación ─────────────────────────────────────────────────
            status, status_color, interpretation = _classify_metric(key, value)

            # Contadores globales
            if "✓" in status:
                pass_count += 1
            elif "✗" in status:
                fail_count += 1
            elif "~" in status:
                margin_count += 1

            # ── Resultado esperado ────────────────────────────────────────────
            expected_text = _get_expected(key)

            # Color de fondo de la celda "Resultado esperado" según estado
            # (se aplica inline vía TableStyle por índice de fila más abajo)

            table_data.append([
                Paragraph(key,              cell_style(8,   TA_LEFT)),
                Paragraph(val_str,          cell_style(8,   TA_CENTER)),
                Paragraph(
                    expected_text.replace("\n", "<br/>"),
                    cell_style(7.5, TA_LEFT)
                ),
                Paragraph(
                    f'<font color="{status_color.hexval() if hasattr(status_color, "hexval") else "#000000"}">'
                    f'<b>{status}</b></font>',
                    cell_style(7.5, TA_CENTER)
                ),
                Paragraph(interpretation,   cell_style(7.5, TA_LEFT)),
            ])

        # ── Construir tabla ───────────────────────────────────────────────────
        t = Table(table_data, colWidths=col_widths)

        base_style = [
            # Encabezado
            ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor("#2c5282")),
            ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
            ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, 0),  8.5),
            # Filas alternas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.HexColor("#eef2f7"), colors.white]),
            # Columna "Resultado esperado" — fondo diferenciado sutil
            ('BACKGROUND',    (2, 1), (2, -1),  colors.HexColor("#fafaf0")),
            # Rejilla
            ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
            # Borde de separación en columna de resultado esperado
            ('LINEAFTER',     (2, 0), (2, -1),  0.8, colors.HexColor("#2c5282")),
            # Alineación y padding
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('ALIGN',         (1, 0), (1, -1),  'CENTER'),
            ('ALIGN',         (3, 0), (3, -1),  'CENTER'),
            ('TOPPADDING',    (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ]
        t.setStyle(TableStyle(base_style))
        story.append(t)
        story.append(Spacer(1, 0.3 * cm))

    # ═══════════════════════════════════════════════════════════════════════════
    # TABLA DE REFERENCIA BIBLIOGRÁFICA
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("Valores de Referencia Bibliográfica", style_section))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#aaaaaa"), spaceAfter=4))
    story.append(Paragraph(
        "La siguiente tabla consolida los umbrales mínimos y valores ideales de cada "
        "métrica criptográfica según la bibliografía especializada. Estos valores son "
        "utilizados como base de comparación en cada sección del informe.",
        style_body
    ))

    ref_header = [
        Paragraph("<b>Métrica</b>",           cell_style(8, TA_LEFT,   True)),
        Paragraph("<b>Criterio de paso</b>",  cell_style(8, TA_CENTER, True)),
        Paragraph("<b>Valor ideal</b>",        cell_style(8, TA_CENTER, True)),
        Paragraph("<b>Unidad</b>",             cell_style(8, TA_CENTER, True)),
        Paragraph("<b>Fuente bibliográfica</b>", cell_style(8, TA_LEFT, True)),
    ]
    ref_rows = [ref_header]
    for metric_name, ref in REFERENCE_VALUES.items():
        ideal_str = str(ref.get("ideal", "—"))
        ref_rows.append([
            Paragraph(metric_name,               cell_style(8, TA_LEFT)),
            Paragraph(ref.get("criterio", "—"),  cell_style(7.5, TA_CENTER)),
            Paragraph(ideal_str,                 cell_style(7.5, TA_CENTER)),
            Paragraph(ref.get("unidad", ""),     cell_style(7.5, TA_CENTER)),
            Paragraph(ref.get("fuente", ""),     cell_style(7.5, TA_LEFT)),
        ])

    ref_col_widths = [W * 0.25, W * 0.25, W * 0.12, W * 0.10, W * 0.28]
    ref_table = Table(ref_rows, colWidths=ref_col_widths)
    ref_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor("#2c5282")),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0),  8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.HexColor("#eef2f7"), colors.white]),
        ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN',         (1, 0), (3, -1),  'CENTER'),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
    ]))
    story.append(ref_table)
    story.append(Spacer(1, 0.4 * cm))

    # ═══════════════════════════════════════════════════════════════════════════
    # RESUMEN EJECUTIVO
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("Resumen Ejecutivo", style_section))
    story.append(HRFlowable(width="100%", thickness=1.0,
                             color=colors.HexColor("#1a2e4a"), spaceAfter=6))

    total_metrics = pass_count + fail_count + margin_count
    if total_metrics > 0:
        pct_pass = 100.0 * pass_count / total_metrics
    else:
        pct_pass = 0.0

    summary_data = [
        ["Categoría", "Cantidad", "Porcentaje"],
        ["✓ Métricas aprobadas", str(pass_count),
         f"{100.0 * pass_count / max(total_metrics, 1):.1f}%"],
        ["~ Métricas marginales", str(margin_count),
         f"{100.0 * margin_count / max(total_metrics, 1):.1f}%"],
        ["✗ Métricas fallidas", str(fail_count),
         f"{100.0 * fail_count / max(total_metrics, 1):.1f}%"],
        ["Total evaluadas", str(total_metrics), "100%"],
    ]
    summary_table = Table(summary_data, colWidths=[W * 0.50, W * 0.25, W * 0.25])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),   colors.HexColor("#1a2e4a")),
        ('TEXTCOLOR',     (0, 0), (-1, 0),   colors.white),
        ('FONTNAME',      (0, 0), (-1, 0),   'Helvetica-Bold'),
        ('BACKGROUND',    (0, 1), (-1, 1),   colors.HexColor("#d4edda")),  # verde
        ('BACKGROUND',    (0, 2), (-1, 2),   colors.HexColor("#fff3cd")),  # amarillo
        ('BACKGROUND',    (0, 3), (-1, 3),   colors.HexColor("#f8d7da")),  # rojo
        ('FONTNAME',      (0, 4), (-1, 4),   'Helvetica-Bold'),
        ('GRID',          (0, 0), (-1, -1),  0.3, colors.HexColor("#cccccc")),
        ('FONTSIZE',      (0, 0), (-1, -1),  9),
        ('ALIGN',         (1, 0), (-1, -1),  'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1),  'MIDDLE'),
        ('TOPPADDING',    (0, 0), (-1, -1),  6),
        ('BOTTOMPADDING', (0, 0), (-1, -1),  6),
        ('LEFTPADDING',   (0, 0), (-1, -1),  8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.4 * cm))

    # Veredicto
    if pct_pass >= 85.0:
        verdict_color = colors.HexColor("#1a7a1a")
        verdict = (
            f"SISTEMA SEGURO — {pct_pass:.0f}% de las métricas superan los umbrales "
            "de referencia bibliográfica. El esquema de cifrado hipercaótico M×N×A×K "
            "cumple los criterios de seguridad para cifrado de video."
        )
    elif pct_pass >= 60.0:
        verdict_color = colors.HexColor("#b86f00")
        verdict = (
            f"SISTEMA PARCIALMENTE SEGURO — {pct_pass:.0f}% de las métricas son "
            "aceptables. Se recomienda revisar las métricas marginales o fallidas "
            "antes de su publicación académica."
        )
    else:
        verdict_color = colors.HexColor("#9b0000")
        verdict = (
            f"SISTEMA INSUFICIENTE — Solo {pct_pass:.0f}% de las métricas superan "
            "los umbrales mínimos. Se requieren mejoras en el pipeline de cifrado."
        )

    verdict_data = [["Veredicto de Seguridad"], [verdict]]
    verdict_table = Table(verdict_data, colWidths=[W])
    verdict_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor("#1a2e4a")),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0),  10),
        ('BACKGROUND',    (0, 1), (-1, 1),  colors.HexColor("#f8f9fa")),
        ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor("#1a2e4a")),
        ('FONTSIZE',      (0, 1), (-1, 1),  9),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
    ]))
    story.append(verdict_table)

    # ═══════════════════════════════════════════════════════════════════════════
    # GRÁFICAS
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("Visualización de Resultados", style_section))
    story.append(HRFlowable(width="100%", thickness=1.0,
                             color=colors.HexColor("#1a2e4a"), spaceAfter=8))

    graph_groups = [
        {
            "title": "Distribución de Intensidades (Histogramas)",
            "description": (
                "Los histogramas muestran la distribución de valores de píxeles. "
                "El plaintext (original) concentra valores según el contenido visual. "
                "El ciphertext ideal presenta distribución uniforme en [0, 255], "
                "evidenciando máxima entropía y ausencia de patrones."
            ),
            "images": [
                ("hist_original.png",   "Histograma del plaintext (video original)"),
                ("hist_encrypted.png",  "Histograma del ciphertext (video cifrado)"),
                ("hist_decrypted.png",  "Histograma del plaintext recuperado (descifrado)"),
            ]
        },
        {
            "title": "Correlación entre Píxeles Adyacentes",
            "description": (
                "Las gráficas de dispersión comparan píxeles adyacentes horizontales. "
                "En el plaintext se observa correlación alta (puntos agrupados en diagonal). "
                "En el ciphertext seguro la nube de puntos debe ser uniforme y dispersa "
                "(correlación ≈ 0), indicando que la relación espacial ha sido destruida."
            ),
            "images": [
                ("corr_original.png",           "Correlación horizontal — plaintext"),
                ("corr_encrypted.png",          "Correlación horizontal — ciphertext (video)"),
                ("corr_mnak_frame0.png",        "Correlación — MNAK completo (M×N×A×K)"),
            ]
        },
        {
            "title": "Análisis de Uniformidad MNAK Completo",
            "description": (
                "Análisis de la distribución de bytes en el archivo .mnak completo, "
                "que incluye frame cifrado, audio cifrado y estado caótico serializado. "
                "La distribución uniforme en el histograma y la dispersión uniforme en "
                "el mapa de densidad de correlación confirman la calidad criptográfica "
                "del cifrado sobre el volumen total M×N×A×K."
            ),
            "images": [
                ("mnak_frame0_analysis.png",  "Análisis completo de uniformidad — Frame 0"),
                ("mnak_frame10_analysis.png", "Análisis completo de uniformidad — Frame 10"),
            ]
        },
    ]

    for group in graph_groups:
        story.append(Paragraph(group["title"], style_section))
        story.append(Paragraph(group["description"], style_body))

        images_found = []
        for fname, caption in group["images"]:
            fpath = os.path.join(plots_dir, fname)
            if os.path.exists(fpath):
                images_found.append((fpath, caption))

        if not images_found:
            story.append(Paragraph(
                "<i>Gráficas no disponibles para esta sección.</i>", style_body
            ))
            continue

        # Mostrar imágenes en filas de 2
        for i in range(0, len(images_found), 2):
            row_imgs  = images_found[i:i+2]
            img_width = W / len(row_imgs) - 0.3 * cm

            row_cells = []
            for fpath, caption in row_imgs:
                try:
                    img = Image(fpath, width=img_width, height=img_width * 0.72)
                    cell_content = [img,
                                    Paragraph(caption, style_caption)]
                    row_cells.append(cell_content)
                except Exception:
                    row_cells.append([Paragraph(
                        f"<i>[Error cargando {os.path.basename(fpath)}]</i>",
                        style_caption
                    )])

            if len(row_cells) == 1:
                row_cells.append([Spacer(1, 1)])

            img_table = Table([row_cells],
                              colWidths=[W / 2 - 0.15 * cm] * 2)
            img_table.setStyle(TableStyle([
                ('VALIGN',  (0, 0), (-1, -1), 'TOP'),
                ('ALIGN',   (0, 0), (-1, -1), 'CENTER'),
                ('LEFTPADDING',  (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(img_table)

        story.append(Spacer(1, 0.3 * cm))

    # ── Pie de página final ───────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#cccccc"), spaceAfter=4))
    story.append(Paragraph(
        "Informe generado automáticamente por el módulo de evaluación criptográfica "
        "del sistema M×N×A×K — Cifrado hipercaótico de video 4D.",
        style_footer
    ))

    doc.build(story)
    print(f"\n[PDF] Informe generado: {output_path}")
    print(f"      Métricas evaluadas : {total_metrics}")
    print(f"      Aprobadas          : {pass_count} ({pct_pass:.1f}%)")
    print(f"      Marginales         : {margin_count}")
    print(f"      Fallidas           : {fail_count}")