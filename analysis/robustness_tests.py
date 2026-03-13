"""
robustness_tests.py
Simulación de ataques físicos sobre el ciphertext.

Las pruebas verifican que pequeñas perturbaciones sobre el ciphertext
no comprometan la seguridad global del sistema (el plaintext recuperado
con clave correcta sigue siendo ruido).
"""

import numpy as np
import cv2


def add_noise(frame, sigma=10):
    """
    Añade ruido gaussiano al frame (simula interferencia en el canal de transmisión).

    Args:
        frame: ndarray uint8, 2D o 3D
        sigma: desviación estándar del ruido (intensidad)
    Returns:
        frame con ruido, recortado a [0, 255] uint8
    """
    noise = np.random.normal(0, sigma, frame.shape)
    noisy = frame.astype(np.float64) + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)


def occlusion(frame, block_size=50):
    """
    Aplica oclusión rectangular al frame (simula pérdida de paquetes / daño físico).

    La posición del bloque se elige aleatoriamente dentro de los límites del frame.

    Args:
        frame:      ndarray uint8, 2D o 3D
        block_size: lado del bloque cuadrado en píxeles
    Returns:
        frame con bloque ocluido (píxeles puestos a 0), uint8
    """
    occluded = frame.copy()

    if frame.ndim == 2:
        h, w = frame.shape
    else:
        h, w = frame.shape[:2]

    # Asegurar que el bloque cabe en el frame
    bh = min(block_size, h - 1)
    bw = min(block_size, w - 1)

    y = np.random.randint(0, max(1, h - bh))
    x = np.random.randint(0, max(1, w - bw))

    occluded[y:y + bh, x:x + bw] = 0
    return occluded