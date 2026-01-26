"""
test.py
Ejecución completa de pruebas criptográficas sobre video
Proyecto: VideoEncryptionHyperchaotic
"""

import os

# Análisis
from analysis.video_loader import load_video
from analysis.entropy_tests import entropy_global, entropy_per_frame
from analysis.statistical_tests import correlation, variance
from analysis.quality_tests import psnr, mse, mad
from analysis.ssim_tests import ssim
from analysis.robustness_tests import add_noise, occlusion
from analysis.differential_tests import modify_one_pixel, npcr, uaci
from analysis.efficiency_tests import time_per_frame
from analysis.frame_utils import match_frame_size

# Reportes 
from reporting.plots import save_histogram, save_correlation_plot
from reporting.pdf_report import generate_pdf_report


# CONFIGURACIÓN

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ORIGINAL_VIDEO = r"C:\Users\accal\Documentos\VideoEncryptionHyperchaotic\data\video_prueba3.mp4"
ENCRYPTED_VIDEO = r"C:\Users\accal\Documentos\VideoEncryptionHyperchaotic\data\encrypted_video.mp4"
DECRYPTED_VIDEO = r"C:\Users\accal\Documentos\VideoEncryptionHyperchaotic\data\decrypted_video.mp4"

RESULTS_DIR = os.path.join(BASE_DIR, "results")
PLOTS_DIR = os.path.join(RESULTS_DIR, "plots")
REPORT_PATH = os.path.join(RESULTS_DIR, "report.pdf")

os.makedirs(PLOTS_DIR, exist_ok=True)


# MAIN

def main():

    # CARGA DE VIDEOS 
    orig_frames, t_orig = load_video(ORIGINAL_VIDEO)
    enc_frames, t_enc = load_video(ENCRYPTED_VIDEO)
    dec_frames, t_dec = load_video(DECRYPTED_VIDEO)

    # TOMA DE FRAMES DE EJEMPLO
    f_orig = orig_frames[0]
    f_enc = enc_frames[0]
    f_dec = dec_frames[0]

    # NORMALIZACIÓN DE TAMAÑOS
    f_enc = match_frame_size(f_orig, f_enc)
    f_dec = match_frame_size(f_orig, f_dec)

    # ALEATORIEDAD 
    randomness_results = {
        "Entropía global (Original)": entropy_global(orig_frames),
        "Entropía global (Cifrado)": entropy_global(enc_frames),
        "Entropía promedio por frame (Cifrado)": entropy_per_frame(enc_frames),
    }

    # ESTADÍSTICAS 
    statistical_results = {
        "Correlación horizontal (Original)": correlation(f_orig, "horizontal"),
        "Correlación horizontal (Cifrado)": correlation(f_enc, "horizontal"),
        "Correlación vertical (Cifrado)": correlation(f_enc, "vertical"),
        "Correlación diagonal (Cifrado)": correlation(f_enc, "diagonal"),
        "Varianza (Cifrado)": variance(f_enc),
    }

    # CALIDAD DE DESCIFRADO
    quality_results = {
        "PSNR (dB)": psnr(f_orig, f_dec),
        "MSE": mse(f_orig, f_dec),
        "MAD": mad(f_orig, f_dec),
        "SSIM": ssim(f_orig, f_dec),
    }

    # ROBUSTEZ 
    noisy_enc = add_noise(f_enc, sigma=15)
    occluded_enc = occlusion(f_enc, block_size=80)

    robustness_results = {
        "PSNR con ruido": psnr(f_orig, noisy_enc),
        "PSNR con oclusión": psnr(f_orig, occluded_enc),
    }

    # PRUEBAS DIFERENCIALES
    modified_orig = modify_one_pixel(f_orig)

    encrypted_modified = f_enc.copy()

    differential_results = {
        "NPCR (%)": npcr(f_enc, encrypted_modified),
        "UACI (%)": uaci(f_enc, encrypted_modified),
    }

    # EFICIENCIA
    efficiency_results = {
        "Tiempo lectura original (s)": t_orig,
        "Tiempo lectura cifrado (s)": t_enc,
        "Tiempo lectura descifrado (s)": t_dec,
        "Tiempo por frame (cifrado)": time_per_frame(t_enc, len(enc_frames)),
    }

    # GRÁFICOS
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

    # CONSOLIDACIÓN
    results = {
        "Aleatoriedad": randomness_results,
        "Estadísticas": statistical_results,
        "Calidad del descifrado": quality_results,
        "Robustez": robustness_results,
        "Pruebas diferenciales": differential_results,
        "Eficiencia": efficiency_results,
    }

    generate_pdf_report(results, PLOTS_DIR, REPORT_PATH)

    print("Análisis finalizado correctamente")
    print("Informe generado en:", REPORT_PATH)


# EJECUCIÓN
if __name__ == "__main__":
    main()
