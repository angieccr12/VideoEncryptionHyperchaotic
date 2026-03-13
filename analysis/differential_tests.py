"""
differential_tests.py
Pruebas diferenciales NPCR y UACI

METODOLOGÍA CORRECTA:
  La prueba diferencial auténtica compara E(P) vs E(P') donde P' es P con
  exactamente 1 píxel modificado (Δ = 1 en el LSB). Esta es la definición
  establecida en la literatura de criptografía de imágenes.

  NO se deben comparar dos frames consecutivos del video como aproximación:
  eso mide variación de contenido, no sensibilidad del cifrado.

Referencias:
  [1] Wu Y. et al., "NPCR and UACI randomness tests for image encryption",
      Journal of Selected Areas in Telecommunications, 2011.
  [2] Pak C. & Huang L., "A new color image encryption using combination of
      the 1D chaotic map", Signal Processing, 2017.
"""

import numpy as np
import os
import glob


# ─────────────────────────────────────────────────────────────────────────────
# Utilidades de modificación de imagen
# ─────────────────────────────────────────────────────────────────────────────

def modify_one_pixel(frame):
    """
    Modifica el LSB del primer píxel (posición [0,0]) del frame.
    Para frames RGB, modifica el canal R del píxel [0,0].
    Maneja correctamente uint8 sin overflow.

    Args:
        frame: ndarray uint8, forma (H, W) o (H, W, C)
    Returns:
        frame modificado (copia)
    """
    modified = frame.copy()

    if modified.ndim == 2:
        val = int(modified[0, 0])
        modified[0, 0] = np.uint8((val + 1) % 256)
    else:
        val = int(modified[0, 0, 0])
        modified[0, 0, 0] = np.uint8((val + 1) % 256)

    return modified


# ─────────────────────────────────────────────────────────────────────────────
# NPCR / UACI sobre arrays 2D / 3D (frames de video)
# ─────────────────────────────────────────────────────────────────────────────

def npcr(img1, img2):
    """
    Number of Pixels Change Rate.
    NPCR = (Σ D(i,j)) / (M×N) × 100%
    donde D(i,j) = 1 si C1(i,j) ≠ C2(i,j), 0 en caso contrario.

    Valor ideal para cifrado seguro: > 99.6%
    """
    if img1.shape != img2.shape:
        raise ValueError("NPCR requiere imágenes del mismo tamaño")
    diff = img1 != img2
    return 100.0 * np.sum(diff) / diff.size


def uaci(img1, img2):
    """
    Unified Average Changing Intensity.
    UACI = (1/(M×N)) × Σ |C1(i,j) - C2(i,j)| / 255 × 100%

    Valor ideal para cifrado seguro: 33.46% ± 0.5%
    """
    if img1.shape != img2.shape:
        raise ValueError("UACI requiere imágenes del mismo tamaño")
    return 100.0 * np.mean(np.abs(img1.astype(np.int32) - img2.astype(np.int32)) / 255.0)


# ─────────────────────────────────────────────────────────────────────────────
# NPCR / UACI sobre archivos .mnak completos (M×N×A×K)
# ─────────────────────────────────────────────────────────────────────────────

def npcr_mnak(data1, data2):
    """
    Calcula NPCR para archivos MNAK completos según:
    NPCR = (Σ D(i)) / (M×N×A×K) × 100%
    donde D(i) = 1 si C1[i] ≠ C2[i], 0 en caso contrario.

    Args:
        data1: ndarray uint8 del primer archivo .mnak cifrado
        data2: ndarray uint8 del segundo archivo .mnak cifrado
    Returns:
        NPCR en porcentaje
    """
    if len(data1) != len(data2):
        raise ValueError("NPCR MNAK requiere archivos del mismo tamaño")
    D = (data1 != data2).astype(np.int32)
    return 100.0 * np.sum(D) / len(data1)


def uaci_mnak(data1, data2):
    """
    Calcula UACI para archivos MNAK completos según:
    UACI = (1/(M×N×A×K)) × Σ |C1[i] - C2[i]| / 255 × 100%

    Args:
        data1: ndarray uint8 del primer archivo .mnak cifrado
        data2: ndarray uint8 del segundo archivo .mnak cifrado
    Returns:
        UACI en porcentaje
    """
    if len(data1) != len(data2):
        raise ValueError("UACI MNAK requiere archivos del mismo tamaño")
    diff = np.abs(data1.astype(np.int32) - data2.astype(np.int32))
    return 100.0 * np.mean(diff / 255.0)


# ─────────────────────────────────────────────────────────────────────────────
# Prueba diferencial correcta: E(P) vs E(P') con encriptador real
# ─────────────────────────────────────────────────────────────────────────────

def differential_test_with_encryptor(encryptor_class, chaos_class, frame,
                                      seed=0.1, audio_chunk=None):
    """
    Prueba diferencial NPCR/UACI correcta:
      Cifra el frame P → C1 = E(P)
      Cifra P' = P con 1 píxel modificado → C2 = E(P')
      Ambos con la MISMA clave (misma semilla), por tanto mismos generadores
      en el mismo estado (se instancian freshly con la misma semilla).

    Args:
        encryptor_class: clase MNAKFrameEncryptor
        chaos_class:     clase ChaosKeyGenerator
        frame:           ndarray (M, N, 3) uint8
        seed:            semilla del generador caótico
        audio_chunk:     audio sincronizado o None
    Returns:
        dict con NPCR y UACI calculados sobre los bytes del ciphertext completo
    """
    # Cifrado de P con generador fresco (mismo estado inicial)
    gen1 = chaos_class(seed=seed)
    enc1 = encryptor_class(gen1)
    c1   = enc1.encrypt(frame, audio_chunk)
    c1_arr = np.frombuffer(c1, dtype=np.uint8)

    # Modificar exactamente 1 píxel
    frame_prime = modify_one_pixel(frame)

    # Cifrado de P' con generador fresco (idéntico estado inicial)
    gen2 = chaos_class(seed=seed)
    enc2 = encryptor_class(gen2)
    c2   = enc2.encrypt(frame_prime, audio_chunk)
    c2_arr = np.frombuffer(c2, dtype=np.uint8)

    # Asegurar mismo tamaño para comparación
    min_len = min(len(c1_arr), len(c2_arr))
    c1_arr  = c1_arr[:min_len]
    c2_arr  = c2_arr[:min_len]

    npcr_val = npcr_mnak(c1_arr, c2_arr)
    uaci_val = uaci_mnak(c1_arr, c2_arr)

    return {
        "NPCR diferencial (%)": npcr_val,
        "UACI diferencial (%)": uaci_val,
        "bytes_comparados":     min_len,
        "pixels_modificados":   1,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Carga de archivos .mnak para comparación diferencial (modo offline)
# ─────────────────────────────────────────────────────────────────────────────

def load_two_mnak_versions(directory, frame_index=0):
    """
    Carga dos archivos .mnak consecutivos para comparación diferencial offline.

    NOTA: En el modo offline (análisis post-cifrado), si los frames consecutivos
    son de escenas distintas, el NPCR/UACI medirá variación de contenido, no
    sensibilidad del cifrador. Para resultados rigurosos, usar
    differential_test_with_encryptor() con el mismo frame.

    Args:
        directory:   directorio con archivos .mnak
        frame_index: índice del primer frame
    Returns:
        data1, data2: ndarray uint8 o None si no se encuentran
        success:      bool
    """
    file1 = os.path.join(directory, f"frame_{frame_index:06d}.mnak")
    file2 = os.path.join(directory, f"frame_{frame_index + 1:06d}.mnak")

    if not os.path.exists(file1) or not os.path.exists(file2):
        return None, None, False

    with open(file1, 'rb') as f:
        data1 = np.frombuffer(f.read(), dtype=np.uint8)
    with open(file2, 'rb') as f:
        data2 = np.frombuffer(f.read(), dtype=np.uint8)

    if len(data1) != len(data2):
        # Truncar al mínimo común
        min_len = min(len(data1), len(data2))
        data1 = data1[:min_len]
        data2 = data2[:min_len]

    return data1, data2, True