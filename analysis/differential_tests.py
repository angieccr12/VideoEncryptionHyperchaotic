"""
differential_tests.py
Pruebas diferenciales NPCR y UACI
"""

import numpy as np


def modify_one_pixel(frame):
    """
    Modifica un solo píxel del frame (escenario diferencial).
    Evita overflow en uint8.
    """
    modified = frame.copy()
    x, y = 0, 0

    value = int(modified[x, y])
    modified[x, y] = np.uint8((value + 1) % 256)

    return modified


def npcr(img1, img2):
    """
    Number of Pixel Change Rate (NPCR)
    """
    if img1.shape != img2.shape:
        raise ValueError("NPCR requiere imágenes del mismo tamaño")

    diff = img1 != img2
    return 100.0 * np.sum(diff) / diff.size


def uaci(img1, img2):
    """
    Unified Average Changing Intensity (UACI)
    """
    if img1.shape != img2.shape:
        raise ValueError("UACI requiere imágenes del mismo tamaño")

    return 100.0 * np.mean(np.abs(img1.astype(np.int16) - img2.astype(np.int16)) / 255.0)
