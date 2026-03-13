"""
quality_tests.py
Métricas de calidad de imagen para evaluación del descifrado.

MSE  = Error cuadrático medio          (0 = perfecto)
PSNR = Peak Signal-to-Noise Ratio (dB) (∞ = perfecto, >40 = excelente)
MAD  = Mean Absolute Difference        (0 = perfecto)
"""

import numpy as np
import math


def _flatten(a, b):
    """Convierte ambos arrays a float64 aplanado, compatibles con 2D y 3D."""
    return a.astype(np.float64).flatten(), b.astype(np.float64).flatten()


def mse(a, b):
    """Error cuadrático medio entre dos imágenes del mismo tamaño."""
    af, bf = _flatten(a, b)
    return float(np.mean((af - bf) ** 2))


def psnr(a, b):
    """
    Peak Signal-to-Noise Ratio en dB.
    PSNR = 20 · log10(255 / √MSE)
    Retorna float('inf') si MSE = 0 (imágenes idénticas).
    """
    m = mse(a, b)
    if m < 1e-12:
        return float("inf")
    return float(20.0 * math.log10(255.0 / math.sqrt(m)))


def mad(a, b):
    """Mean Absolute Difference entre dos imágenes del mismo tamaño."""
    af, bf = _flatten(a, b)
    return float(np.mean(np.abs(af - bf)))