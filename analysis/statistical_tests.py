"""
statistical_tests.py
Pruebas estadísticas de correlación y dispersión para frames de video.

La correlación se calcula en escala de grises para frames 2D o promediando
canales para frames 3D (RGB), asegurando compatibilidad con ambos formatos.
"""

import numpy as np
from scipy.stats import pearsonr


def _to_gray(frame):
    """Convierte frame RGB a escala de grises si es necesario."""
    if frame.ndim == 3:
        return np.mean(frame, axis=2).astype(np.float64)
    return frame.astype(np.float64)


def correlation(frame, mode="horizontal"):
    """
    Calcula el coeficiente de correlación de Pearson entre píxeles adyacentes.

    Args:
        frame: ndarray uint8, 2D o 3D (RGB)
        mode:  'horizontal', 'vertical' o 'diagonal'
    Returns:
        coeficiente de correlación de Pearson (float en [-1, 1])
    """
    f = _to_gray(frame)

    if mode == "horizontal":
        x, y = f[:, :-1], f[:, 1:]
    elif mode == "vertical":
        x, y = f[:-1, :], f[1:, :]
    elif mode == "diagonal":
        x, y = f[:-1, :-1], f[1:, 1:]
    else:
        raise ValueError(f"Modo desconocido: {mode}. Use 'horizontal', 'vertical' o 'diagonal'.")

    xf = x.flatten()
    yf = y.flatten()

    # pearsonr puede fallar si la varianza es 0 (imagen constante)
    if np.std(xf) < 1e-10 or np.std(yf) < 1e-10:
        return 0.0

    return float(pearsonr(xf, yf)[0])


def variance(frame):
    """
    Calcula la varianza de los píxeles del frame.

    Args:
        frame: ndarray uint8, 2D o 3D
    Returns:
        varianza (float)
    """
    return float(np.var(_to_gray(frame)))