"""
test.py
Ejecución completa de pruebas criptográficas sobre video
Proyecto: VideoEncryptionHyperchaotic
Cifrado por archivos (offline)
"""

import os

# =========================
# IMPORTS
# =========================

# Análisis
from analysis.video_loader import load_video
from analysis.entropy_tests import entropy_global, entropy_per_frame
from analysis.statistical_tests import correlation, variance
from analysis.quality_tests import psnr, mse, mad
from analysis.ssim_tests import ssim
from analysis.robustness_tests import add_noise, occlusion
from analysis.differential_tests import npcr, uaci
from analysis.efficiency_tests import time_per_frame
from analysis.frame_utils import match_frame_size
from analysis.nist_tests import monobit_test, block_frequency_test

# Reportes
from reporting.plots import save_histogram, save_correlation_plot
from reporting.pdf_report import generate_pdf_report


# =========================
# CONFIGURACIÓN DE RUTAS
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
PLOTS_DIR = os.path.join(RESULTS_DIR, "plots")
REPORT_PATH = os.path.join(RESULTS_DIR, "report.pdf")

ORIGINAL_VIDEO = os.path.join(DATA_DIR, "video_prueba3.mp4")
ENCRYPTED_VIDEO = os.path.join(DATA_DIR, "encrypted_video.mp4")
DECRYPTED_VIDEO = os.path.join(DATA_DIR, "decrypted_video.mp4")

os.makedirs(PLOTS_DIR, exist_ok=True)


# =========================
# MAIN
# =========================

def main():

    # =========================
    # CARGA DE VIDEOS
    # =========================
    orig_frames, t_orig = load_video(ORIGINAL_VIDEO)
    enc_frames, t_enc = load_video(ENCRYPTED_VIDEO)
    dec_frames, t_dec = load_video(DECRYPTED_VIDEO)

    if len(orig_frames) == 0 or len(enc_frames) == 0 or len(dec_frames) == 0:
        raise RuntimeError("Uno o más videos no pudieron cargarse correctamente")

    # =========================
    # FRAMES DE REFERENCIA
    # =========================
    f_orig = orig_frames[0]
    f_enc = match_frame_size(f_orig, enc_frames[0])
    f_dec = match_frame_size(f_orig, dec_frames[0])

    # =========================
    # ALEATORIEDAD (ENTROPÍA)
    # =========================
    randomness_results = {
        "Entropía global (Original)": entropy_global(orig_frames),
        "Entropía global (Cifrado)": entropy_global(enc_frames),
        "Entropía promedio por frame (Cifrado)": entropy_per_frame(enc_frames),
    }

    # =========================
    # PRUEBAS ESTADÍSTICAS
    # =========================
    statistical_results = {
        "Correlación horizontal (Original)": correlation(f_orig, "horizontal"),
        "Correlación horizontal (Cifrado)": correlation(f_enc, "horizontal"),
        "Correlación vertical (Cifrado)": correlation(f_enc, "vertical"),
        "Correlación diagonal (Cifrado)": correlation(f_enc, "diagonal"),
        "Varianza (Cifrado)": variance(f_enc),
    }

    # =========================
    # CALIDAD DEL DESCIFRADO
    # =========================
    quality_results = {
        "PSNR (dB)": psnr(f_orig, f_dec),
        "MSE": mse(f_orig, f_dec),
        "MAD": mad(f_orig, f_dec),
        "SSIM": ssim(f_orig, f_dec),
    }

    # =========================
    # ROBUSTEZ (ATAQUES SIMULADOS)
    # =========================
    noisy_enc = add_noise(f_enc, sigma=15)
    occluded_enc = occlusion(f_enc, block_size=80)

    robustness_results = {
        "PSNR con ruido": psnr(f_orig, noisy_enc),
        "PSNR con oclusión": psnr(f_orig, occluded_enc),
    }

    # =========================
    # PRUEBAS DIFERENCIALES (OFFLINE)
    # =========================
    if len(enc_frames) >= 2:
        f_enc_1 = enc_frames[0]
        f_enc_2 = match_frame_size(f_enc_1, enc_frames[1])

        differential_results = {
            "NPCR (%)": npcr(f_enc_1, f_enc_2),
            "UACI (%)": uaci(f_enc_1, f_enc_2),
        }
    else:
        differential_results = {
            "NPCR (%)": 0.0,
            "UACI (%)": 0.0,
        }

    # =========================
    # PRUEBAS NIST (OFFLINE)
    # =========================
    nist_results = {
        "Monobit Test": monobit_test(f_enc),
        "Block Frequency Test": block_frequency_test(f_enc),
    }

    # =========================
    # EFICIENCIA
    # =========================
    efficiency_results = {
        "Tiempo lectura original (s)": t_orig,
        "Tiempo lectura cifrado (s)": t_enc,
        "Tiempo lectura descifrado (s)": t_dec,
        "Tiempo por frame (cifrado)": time_per_frame(t_enc, len(enc_frames)),
    }

    # =========================
    # GRÁFICOS
    # =========================
    save_histogram(f_orig, "Histograma - Original",
                   os.path.join(PLOTS_DIR, "hist_original.png"))

    save_histogram(f_enc, "Histograma - Cifrado",
                   os.path.join(PLOTS_DIR, "hist_encrypted.png"))

    save_histogram(f_dec, "Histograma - Descifrado",
                   os.path.join(PLOTS_DIR, "hist_decrypted.png"))

    save_correlation_plot(f_orig, "Correlación - Original",
                          os.path.join(PLOTS_DIR, "corr_original.png"))

    save_correlation_plot(f_enc, "Correlación - Cifrado",
                          os.path.join(PLOTS_DIR, "corr_encrypted.png"))

    # =========================
    # CONSOLIDACIÓN DE RESULTADOS
    # =========================
    results = {
        "Aleatoriedad": randomness_results,
        "Estadísticas": statistical_results,
        "Calidad del descifrado": quality_results,
        "Robustez": robustness_results,
        "Pruebas diferenciales": differential_results,
        "Pruebas NIST": nist_results,
        "Eficiencia": efficiency_results,
    }

    generate_pdf_report(results, PLOTS_DIR, REPORT_PATH)

    print("Análisis finalizado correctamente")
    print("Informe generado en:", REPORT_PATH)


# =========================
# EJECUCIÓN
# =========================

if __name__ == "__main__":
    main()
