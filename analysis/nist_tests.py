"""
nist_tests.py
Pruebas básicas de aleatoriedad tipo NIST (offline)
"""

import numpy as np
from scipy.stats import norm, chi2


def monobit_test(data):
    """
    Prueba Monobit NIST (SP 800-22, Sección 2.1)
    Retorna p-valor: pasa si p > 0.01
    """
    bits = np.unpackbits(data.astype(np.uint8))
    n = len(bits)
    ones = int(np.sum(bits))
    zeros = n - ones

    # Estadístico S_obs según especificación NIST
    s_obs = abs(ones - zeros) / np.sqrt(n)

    # P-valor mediante función de error complementaria
    p_value = float(2 * (1 - norm.cdf(s_obs)))

    return p_value


def block_frequency_test(data, block_size=128):
    """
    Prueba Block Frequency NIST (SP 800-22, Sección 2.2)
    Retorna p-valor: pasa si p > 0.01
    """
    bits = np.unpackbits(data.astype(np.uint8))
    n_blocks = len(bits) // block_size

    if n_blocks == 0:
        return 0.0

    blocks = bits[:n_blocks * block_size].reshape(n_blocks, block_size)
    proportions = np.mean(blocks, axis=1)

    # Estadístico chi-cuadrado según especificación NIST
    chi_sq = float(4 * block_size * np.sum((proportions - 0.5) ** 2))

    # P-valor con grados de libertad = número de bloques
    p_value = float(chi2.sf(chi_sq, df=n_blocks))

    return p_value