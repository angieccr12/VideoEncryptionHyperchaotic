"""
test.py
Ejecución completa de pruebas criptográficas sobre video MNAK.

Correcciones y mejoras respecto a la versión anterior:
  1. Prueba diferencial correcta: usa differential_test_with_encryptor()
     para comparar E(P) vs E(P') con 1 píxel modificado, no frames consecutivos.
  2. Sensibilidad a la clave: incluida como sección independiente con semilla ε-diferente.
  3. Entropía MNAK: usa entropy_mnak_per_file() para media y std por archivo.
  4. Informe PDF mejorado: pasa system_params al generador del PDF.
  5. Correlación: se calcula sobre los 3 ejes (horizontal, vertical, diagonal).
"""

import os
import sys

# Asegurar que el directorio raíz esté en el path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS — análisis
# ─────────────────────────────────────────────────────────────────────────────
from analysis.video_loader       import load_video, load_mnak_files
from analysis.entropy_tests      import (entropy_global, entropy_per_frame,
                                          entropy_mnak_global, entropy_mnak_per_file)
from analysis.statistical_tests  import correlation, variance
from analysis.quality_tests      import psnr, mse, mad
from analysis.ssim_tests         import ssim
from analysis.robustness_tests   import add_noise, occlusion
from analysis.differential_tests import (npcr, uaci, npcr_mnak, uaci_mnak,
                                          load_two_mnak_versions,
                                          differential_test_with_encryptor)
from analysis.efficiency_tests   import time_per_frame
from analysis.frame_utils        import match_frame_size
from analysis.nist_tests         import monobit_test, block_frequency_test
from analysis.key_sensitivity_tests import full_key_sensitivity_test

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS — encriptador (para pruebas que requieren cifrado en línea)
# ─────────────────────────────────────────────────────────────────────────────
from crypto.chaos_generator  import ChaosKeyGenerator
from crypto.mnk_encryptor    import MNAKFrameEncryptor

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS — reportes
# ─────────────────────────────────────────────────────────────────────────────
from reporting.plots      import (save_histogram, save_correlation_plot,
                                   save_correlation_plot_mnak,
                                   save_mnak_distribution_analysis)
from reporting.pdf_report import generate_pdf_report


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE RUTAS
# ─────────────────────────────────────────────────────────────────────────────
DATA_DIR             = os.path.join(BASE_DIR, "data")
RESULTS_DIR          = os.path.join(BASE_DIR, "results")
PLOTS_DIR            = os.path.join(RESULTS_DIR, "plots")
REPORT_PATH          = os.path.join(RESULTS_DIR, "report.pdf")

ORIGINAL_VIDEO       = os.path.join(DATA_DIR, "video_prueba3.mp4")
ENCRYPTED_VIDEO      = os.path.join(DATA_DIR, "encrypted_video.mp4")
DECRYPTED_VIDEO      = os.path.join(DATA_DIR, "decrypted_video.mp4")
ENCRYPTED_FRAMES_DIR = os.path.join(DATA_DIR, "encrypted_frames")

SEED = 0.1   # semilla del sistema hipercaótico (debe coincidir con main_mnak.py)

os.makedirs(PLOTS_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():

    # ═════════════════════════════════════════════════════════════════════════
    # 1. CARGA DE VIDEOS Y ARCHIVOS MNAK
    # ═════════════════════════════════════════════════════════════════════════
    print("\n" + "═" * 60)
    print("  SISTEMA DE EVALUACIÓN CRIPTOGRÁFICA M×N×A×K")
    print("═" * 60)

    print("\n[1/8] Cargando videos...")
    orig_frames, t_orig = load_video(ORIGINAL_VIDEO,   max_frames=50)
    enc_frames,  t_enc  = load_video(ENCRYPTED_VIDEO,  max_frames=50)
    dec_frames,  t_dec  = load_video(DECRYPTED_VIDEO,  max_frames=50)

    if not orig_frames or not enc_frames or not dec_frames:
        raise RuntimeError("Uno o más videos no pudieron cargarse correctamente.")

    print(f"    Original  : {len(orig_frames)} frames ({t_orig:.2f}s)")
    print(f"    Cifrado   : {len(enc_frames)} frames ({t_enc:.2f}s)")
    print(f"    Descifrado: {len(dec_frames)} frames ({t_dec:.2f}s)")

    print("\n[2/8] Cargando archivos MNAK...")
    try:
        mnak_data, mnak_dims, t_mnak = load_mnak_files(ENCRYPTED_FRAMES_DIR, max_frames=50)
        has_mnak = True
        print(f"    {len(mnak_data)} archivos cargados en {t_mnak:.2f}s")
    except Exception as e:
        print(f"    AVISO: No se pudieron cargar archivos MNAK: {e}")
        has_mnak = False
        mnak_dims = {'M': 0, 'N': 0, 'A': 0, 'K': 32, 'total_frames': 0}

    # ─── Frames de referencia (primer frame de cada video) ────────────────
    f_orig = orig_frames[0]
    f_enc  = match_frame_size(f_orig, enc_frames[0])
    f_dec  = match_frame_size(f_orig, dec_frames[0])

    # ═════════════════════════════════════════════════════════════════════════
    # 2. ENTROPÍA
    # ═════════════════════════════════════════════════════════════════════════
    print("\n[3/8] Calculando entropía...")

    randomness_results = {}

    h_orig  = entropy_global(orig_frames)
    h_enc_v = entropy_global(enc_frames)
    h_pf    = entropy_per_frame(enc_frames)

    randomness_results["H(X) plaintext — global (bits)"]         = h_orig
    randomness_results["H(X) ciphertext — global video (bits)"]  = h_enc_v
    randomness_results["H(X) ciphertext — promedio por frame (bits)"] = h_pf

    print(f"    H plaintext  : {h_orig:.6f} bits")
    print(f"    H ciphertext : {h_enc_v:.6f} bits")
    print(f"    H promedio   : {h_pf:.6f} bits")

    if has_mnak:
        print("\n    Entropía MNAK completa (M×N×A×K):")
        h_mnak = entropy_mnak_global(mnak_data, mnak_dims)
        h_mean, h_std = entropy_mnak_per_file(mnak_data)

        randomness_results["H(X) MNAK completo M×N×A×K (bits)"]          = h_mnak
        randomness_results["H(X) MNAK por archivo — media (bits)"]        = h_mean
        randomness_results["H(X) MNAK por archivo — desviación estándar"] = h_std
        randomness_results["Dimensiones MNAK (texto)"] = (
            f"M={mnak_dims['M']}, N={mnak_dims['N']}, "
            f"A={mnak_dims['A']}, K={mnak_dims['K']}, "
            f"frames={mnak_dims['total_frames']}"
        )
        print(f"    H MNAK global: {h_mnak:.6f} bits")
        print(f"    H por archivo: {h_mean:.6f} ± {h_std:.6f} bits")

    # ═════════════════════════════════════════════════════════════════════════
    # 3. ESTADÍSTICAS DE CORRELACIÓN
    # ═════════════════════════════════════════════════════════════════════════
    print("\n[4/8] Calculando correlaciones...")

    statistical_results = {
        "Correlación horizontal — plaintext":          correlation(f_orig, "horizontal"),
        "Correlación horizontal — ciphertext":         correlation(f_enc,  "horizontal"),
        "Correlación vertical   — ciphertext":         correlation(f_enc,  "vertical"),
        "Correlación diagonal   — ciphertext":         correlation(f_enc,  "diagonal"),
        "Varianza — ciphertext":                       variance(f_enc),
    }

    for k, v in statistical_results.items():
        if isinstance(v, float):
            print(f"    {k}: {v:.6f}")

    # ═════════════════════════════════════════════════════════════════════════
    # 4. CALIDAD DEL DESCIFRADO
    # ═════════════════════════════════════════════════════════════════════════
    print("\n[5/8] Calculando calidad del descifrado...")

    psnr_dec = psnr(f_orig, f_dec)
    mse_dec  = mse(f_orig, f_dec)
    mad_dec  = mad(f_orig, f_dec)
    ssim_dec = ssim(f_orig, f_dec)

    quality_results = {
        "PSNR descifrado (dB)": psnr_dec,
        "MSE  descifrado":      mse_dec,
        "MAD  descifrado":      mad_dec,
        "SSIM descifrado":      ssim_dec,
    }

    print(f"    PSNR: {psnr_dec:.4f} dB  |  MSE: {mse_dec:.4f}")
    print(f"    MAD : {mad_dec:.4f}      |  SSIM: {ssim_dec:.6f}")

    # ═════════════════════════════════════════════════════════════════════════
    # 5. SENSIBILIDAD A LA CLAVE
    # ═════════════════════════════════════════════════════════════════════════
    print("\n[6/8] Prueba de sensibilidad a la clave (ε = 1×10⁻¹⁰)...")

    # Usar frame RGB original (3 canales) para la prueba
    import cv2
    cap_orig = cv2.VideoCapture(ORIGINAL_VIDEO)
    ret, frame_rgb = cap_orig.read()
    cap_orig.release()

    if ret:
        import numpy as np
        frame_rgb = cv2.resize(frame_rgb, (mnak_dims.get('N', 320), mnak_dims.get('M', 240)))
        frame_rgb = cv2.cvtColor(frame_rgb, cv2.COLOR_BGR2RGB)

        key_sens = full_key_sensitivity_test(
            encryptor_class=MNAKFrameEncryptor,
            chaos_class=ChaosKeyGenerator,
            frame=frame_rgb,
            correct_seed=SEED,
            delta=1e-10
        )
        sensitivity_results = key_sens
    else:
        print("    AVISO: No se pudo leer frame para prueba de sensibilidad.")
        sensitivity_results = {
            "PSNR clave incorrecta (dB)": 0.0,
            "SSIM clave incorrecta":      1.0,
            "NPCR clave incorrecta (%)":  0.0,
        }

    for k, v in sensitivity_results.items():
        if isinstance(v, float):
            print(f"    {k}: {v:.5f}")

    # ═════════════════════════════════════════════════════════════════════════
    # 6. PRUEBAS DIFERENCIALES (NPCR / UACI)
    # ═════════════════════════════════════════════════════════════════════════
    print("\n[7/8] Pruebas diferenciales NPCR / UACI...")

    differential_results = {}

    # Prueba diferencial CORRECTA: E(P) vs E(P') con 1 píxel modificado
    if ret:
        print("    Calculando diferencial online E(P) vs E(P' = P + 1 pixel)...")
        diff_online = differential_test_with_encryptor(
            encryptor_class=MNAKFrameEncryptor,
            chaos_class=ChaosKeyGenerator,
            frame=frame_rgb,
            seed=SEED
        )
        differential_results["NPCR online E(P) vs E(P+1px) (%)"] = diff_online["NPCR diferencial (%)"]
        differential_results["UACI online E(P) vs E(P+1px) (%)"] = diff_online["UACI diferencial (%)"]
        print(f"    NPCR online: {diff_online['NPCR diferencial (%)']:.4f}%")
        print(f"    UACI online: {diff_online['UACI diferencial (%)']:.4f}%")
    else:
        differential_results["NPCR online E(P) vs E(P+1px) (%)"] = 0.0
        differential_results["UACI online E(P) vs E(P+1px) (%)"] = 0.0

    # Prueba diferencial sobre video (frames adyacentes — referencia de contenido)
    if len(enc_frames) >= 2:
        f_e1 = enc_frames[0]
        f_e2 = match_frame_size(f_e1, enc_frames[1])
        differential_results["NPCR frames consecutivos — video (%)"] = npcr(f_e1, f_e2)
        differential_results["UACI frames consecutivos — video (%)"] = uaci(f_e1, f_e2)

    # Prueba diferencial sobre archivos .mnak completos (M×N×A×K)
    if has_mnak:
        print("    Calculando diferencial MNAK (frames 0 vs 1)...")
        mnak1, mnak2, ok = load_two_mnak_versions(ENCRYPTED_FRAMES_DIR, frame_index=0)
        if ok:
            n_val = npcr_mnak(mnak1, mnak2)
            u_val = uaci_mnak(mnak1, mnak2)
            differential_results["NPCR MNAK frames 0↔1 M×N×A×K (%)"] = n_val
            differential_results["UACI MNAK frames 0↔1 M×N×A×K (%)"] = u_val
            print(f"    NPCR MNAK: {n_val:.4f}%  |  UACI MNAK: {u_val:.4f}%")
        else:
            print("    AVISO: archivos MNAK insuficientes para diferencial offline.")

    # ─── NIST ────────────────────────────────────────────────────────────────
    import numpy as np
    enc_flat = np.array(f_enc).flatten().astype(np.uint8)
    nist_results = {
        "NIST Monobit test (p-valor)":         monobit_test(enc_flat),
        "NIST Block Frequency test (p-valor)": block_frequency_test(enc_flat),
    }
    for k, v in nist_results.items():
        print(f"    {k}: {v:.6f}")

    # ─── Robustez ─────────────────────────────────────────────────────────────
    noisy_enc    = add_noise(f_enc, sigma=15)
    occluded_enc = occlusion(f_enc, block_size=80)
    robustness_results = {
        "PSNR ciphertext con ruido gaussiano (σ=15)": psnr(f_orig, noisy_enc),
        "PSNR ciphertext con oclusión (80×80 px)":    psnr(f_orig, occluded_enc),
    }

    # ─── Eficiencia ──────────────────────────────────────────────────────────
    efficiency_results = {
        "Tiempo total lectura original (s)":   t_orig,
        "Tiempo total lectura cifrado (s)":    t_enc,
        "Tiempo total lectura descifrado (s)": t_dec,
        "Tiempo por frame — lectura cifrado (s/frame)":
            time_per_frame(t_enc, len(enc_frames)),
    }
    if has_mnak:
        efficiency_results["Tiempo carga MNAK (s)"] = t_mnak
        efficiency_results["Tiempo por archivo MNAK (s/frame)"] = \
            time_per_frame(t_mnak, len(mnak_data))

    # ═════════════════════════════════════════════════════════════════════════
    # 7. GRÁFICAS
    # ═════════════════════════════════════════════════════════════════════════
    print("\n[8/8] Generando gráficas...")

    save_histogram(f_orig, "Histograma — Plaintext (original)",
                   os.path.join(PLOTS_DIR, "hist_original.png"))
    save_histogram(f_enc,  "Histograma — Ciphertext (cifrado)",
                   os.path.join(PLOTS_DIR, "hist_encrypted.png"))
    save_histogram(f_dec,  "Histograma — Plaintext recuperado (descifrado)",
                   os.path.join(PLOTS_DIR, "hist_decrypted.png"))

    save_correlation_plot(f_orig, "Correlación Horizontal — Plaintext",
                          os.path.join(PLOTS_DIR, "corr_original.png"))
    save_correlation_plot(f_enc,  "Correlación Horizontal — Ciphertext (video)",
                          os.path.join(PLOTS_DIR, "corr_encrypted.png"))

    if has_mnak:
        save_correlation_plot_mnak(
            mnak_data[0],
            "Correlación — MNAK Completo (M×N×A×K) — Frame 0",
            os.path.join(PLOTS_DIR, "corr_mnak_frame0.png"),
            sample_size=20000
        )
        save_mnak_distribution_analysis(
            mnak_data[0],
            "MNAK Completo (M×N×A×K) — Frame 0",
            os.path.join(PLOTS_DIR, "mnak_frame0")
        )
        if len(mnak_data) > 10:
            save_mnak_distribution_analysis(
                mnak_data[10],
                "MNAK Completo (M×N×A×K) — Frame 10",
                os.path.join(PLOTS_DIR, "mnak_frame10")
            )

    print("    Gráficas guardadas en:", PLOTS_DIR)

    # ═════════════════════════════════════════════════════════════════════════
    # 8. INFORME PDF
    # ═════════════════════════════════════════════════════════════════════════
    results = {
        "Aleatoriedad (Entropía de Shannon)":     randomness_results,
        "Estadísticas de Correlación":             statistical_results,
        "Calidad del Descifrado":                  quality_results,
        "Sensibilidad a la Clave":                 sensitivity_results,
        "Pruebas Diferenciales (NPCR / UACI)":    differential_results,
        "Robustez ante Perturbaciones":            robustness_results,
        "Pruebas de Aleatoriedad NIST SP 800-22": nist_results,
        "Eficiencia Computacional":                efficiency_results,
    }

    system_params = {
        'M':      mnak_dims.get('M', 'N/A'),
        'N':      mnak_dims.get('N', 'N/A'),
        'A':      mnak_dims.get('A', 0),
        'K':      mnak_dims.get('K', 32),
        'seed':   SEED,
        'frames': len(orig_frames),
    }

    generate_pdf_report(results, PLOTS_DIR, REPORT_PATH, system_params=system_params)

    print("\n" + "═" * 60)
    print("  ANÁLISIS COMPLETADO")
    print(f"  Informe PDF → {REPORT_PATH}")
    print("═" * 60)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()