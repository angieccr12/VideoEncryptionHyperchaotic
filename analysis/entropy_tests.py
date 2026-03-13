"""
entropy_tests.py
Cálculo de entropía de Shannon para frames y archivos MNAK.

Fórmula de Shannon (base 2):
  H(X) = -Σ P(xi) · log2 P(xi)
donde P(xi) = ni / N_total, ni = frecuencia absoluta del valor xi.

El valor máximo teórico para datos de 8 bits es H_max = log2(256) = 8.0 bits.
Un cifrador ideal produce H ≈ 7.999 bits (distribución casi uniforme).
"""

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# Entropía sobre frames de video (arrays 2D)
# ─────────────────────────────────────────────────────────────────────────────

def entropy_global(frames):
    """
    Entropía de Shannon global calculada sobre TODOS los frames concatenados.
    El denominador es el total de bytes (píxeles) analizados.

    Args:
        frames: lista de ndarrays uint8 (pueden ser 2D o 3D)
    Returns:
        H en bits (máximo teórico: 8.0)
    """
    data = np.concatenate([f.flatten() for f in frames]).astype(np.uint8)
    N    = len(data)

    _, counts = np.unique(data, return_counts=True)

    H = 0.0
    for ni in counts:
        p = ni / N
        if p > 0:
            H -= p * np.log2(p)
    return float(H)


def entropy_per_frame(frames):
    """
    Entropía de Shannon promedio calculada frame a frame.

    Args:
        frames: lista de ndarrays uint8
    Returns:
        H promedio en bits
    """
    values = []
    for f in frames:
        data = f.flatten().astype(np.uint8)
        N    = len(data)
        _, counts = np.unique(data, return_counts=True)

        H = 0.0
        for ni in counts:
            p = ni / N
            if p > 0:
                H -= p * np.log2(p)
        values.append(H)

    return float(np.mean(values))


# ─────────────────────────────────────────────────────────────────────────────
# Entropía sobre archivos .mnak completos (M×N×A×K)
# ─────────────────────────────────────────────────────────────────────────────

def entropy_mnak_global(data_arrays, dimensions):
    """
    Entropía de Shannon para archivos MNAK completos (M×N×A×K).
    Incluye frame, audio y estado caótico serializado en cada archivo.

    El cálculo se realiza sobre TODOS los bytes cifrados concatenados,
    que representan el volumen total M×N×A×K del esquema de cifrado.

    Args:
        data_arrays: lista de ndarrays uint8 (contenido completo de cada .mnak)
        dimensions:  dict con dimensiones {M, N, A, K, total_frames}
    Returns:
        H en bits (valor ideal: ≥ 7.99)
    """
    # Concatenar todos los archivos cifrados
    all_data   = np.concatenate(data_arrays).astype(np.uint8)
    total_bytes = len(all_data)

    # Frecuencias absolutas para los 256 posibles valores de byte
    counts_full = np.zeros(256, dtype=np.int64)
    unique_vals, unique_counts = np.unique(all_data, return_counts=True)
    counts_full[unique_vals] = unique_counts

    # Entropía de Shannon
    H = 0.0
    for ni in counts_full:
        if ni > 0:
            p = ni / total_bytes
            H -= p * np.log2(p)

    # Información de diagnóstico
    M      = dimensions.get('M', 0)
    N      = dimensions.get('N', 0)
    A      = dimensions.get('A', 0)
    K      = dimensions.get('K', 0)
    frames = dimensions.get('total_frames', 1)

    print(f"  [Entropía MNAK] Total bytes analizados : {total_bytes:,}")
    print(f"  [Entropía MNAK] Frames incluidos       : {frames}")
    print(f"  [Entropía MNAK] Dimensiones M×N×A×K   : {M}×{N}×{A}×{K}")
    print(f"  [Entropía MNAK] H(X) calculado         : {H:.6f} bits")
    print(f"  [Entropía MNAK] H_max teórico          : 8.000000 bits")
    print(f"  [Entropía MNAK] Diferencia             : {8.0 - H:.6f} bits")

    return float(H)


def entropy_mnak_per_file(data_arrays):
    """
    Entropía de Shannon por archivo .mnak individual, devuelve media y std.

    Args:
        data_arrays: lista de ndarrays uint8
    Returns:
        (mean_H, std_H): entropía media y desviación estándar en bits
    """
    values = []
    for arr in data_arrays:
        data = arr.astype(np.uint8)
        N    = len(data)
        _, counts = np.unique(data, return_counts=True)

        H = 0.0
        for ni in counts:
            p = ni / N
            if p > 0:
                H -= p * np.log2(p)
        values.append(H)

    arr_values = np.array(values)
    return float(np.mean(arr_values)), float(np.std(arr_values))