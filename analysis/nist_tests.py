"""
nist_tests.py
Pruebas básicas de aleatoriedad tipo NIST SP 800-22 (offline)

Pruebas implementadas:
  1. Monobit (Frequency) Test    — Sección 2.1
  2. Block Frequency Test        — Sección 2.2
  3. Runs Test                   — Sección 2.3

Criterio de aprobación: p-valor > 0.01 para cada prueba.
"""

import numpy as np
from scipy.stats import norm, chi2
from scipy.special import erfc


def monobit_test(data):
    """
    Prueba Monobit NIST (SP 800-22, Sección 2.1).
    Verifica el balance entre la cantidad de unos y ceros en la secuencia.

    Hipótesis nula: la secuencia es aleatoria (|ones - zeros| ≈ 0).
    p-valor > 0.01 → no se rechaza H0 (secuencia aleatoria).

    Args:
        data: ndarray uint8
    Returns:
        p-valor (float)
    """
    bits  = np.unpackbits(data.astype(np.uint8))
    n     = len(bits)
    ones  = int(np.sum(bits))
    zeros = n - ones

    s_obs   = abs(ones - zeros) / np.sqrt(n)
    p_value = float(erfc(s_obs / np.sqrt(2)))

    return p_value


def block_frequency_test(data, block_size=128):
    """
    Prueba Block Frequency NIST (SP 800-22, Sección 2.2).
    Verifica que la proporción de unos en bloques de `block_size` bits
    sea cercana a 0.5.

    Args:
        data:       ndarray uint8
        block_size: tamaño de bloque en bits (default: 128)
    Returns:
        p-valor (float)
    """
    bits     = np.unpackbits(data.astype(np.uint8))
    n_blocks = len(bits) // block_size

    if n_blocks == 0:
        return 0.0

    blocks      = bits[:n_blocks * block_size].reshape(n_blocks, block_size)
    proportions = np.mean(blocks, axis=1)

    chi_sq  = float(4 * block_size * np.sum((proportions - 0.5) ** 2))
    p_value = float(chi2.sf(chi_sq, df=n_blocks))

    return p_value


def runs_test(data):
    """
    Prueba Runs NIST (SP 800-22, Sección 2.3).
    Verifica que el número de «runs» (secuencias ininterrumpidas de 0s o 1s)
    sea consistente con una secuencia aleatoria.

    Args:
        data: ndarray uint8
    Returns:
        p-valor (float)
    """
    bits = np.unpackbits(data.astype(np.uint8))
    n    = len(bits)

    pi = float(np.sum(bits)) / n

    # Si la proporción de unos está muy lejos de 0.5, el test no es aplicable
    if abs(pi - 0.5) >= (2.0 / np.sqrt(n)):
        return 0.0

    # Contar runs: cambios entre bits adyacentes
    runs   = int(np.sum(bits[:-1] != bits[1:])) + 1
    num    = abs(runs - 2 * n * pi * (1 - pi))
    denom  = 2 * np.sqrt(2 * n) * pi * (1 - pi)

    if denom == 0:
        return 0.0

    p_value = float(erfc(num / denom))
    return p_value