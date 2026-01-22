"""
plots.py
Funciones de visualización para análisis criptográfico
"""

import matplotlib.pyplot as plt
import numpy as np


def save_histogram(frame, title, path):
    plt.figure()
    plt.hist(frame.flatten(), bins=256, range=(0, 256))
    plt.title(title)
    plt.xlabel("Intensidad")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def save_correlation_plot(frame, title, path):
    x = frame[:, :-1].flatten()
    y = frame[:, 1:].flatten()

    plt.figure()
    plt.scatter(x[:5000], y[:5000], s=1)
    plt.title(title)
    plt.xlabel("Pixel i")
    plt.ylabel("Pixel i+1")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
