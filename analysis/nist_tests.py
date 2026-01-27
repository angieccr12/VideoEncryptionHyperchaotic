"""
nist_tests.py
Pruebas básicas de aleatoriedad tipo NIST (offline)
"""

import numpy as np

def monobit_test(data):
    bits = np.unpackbits(data.astype(np.uint8))
    ones = np.sum(bits)
    zeros = len(bits) - ones
    return abs(int(ones) - int(zeros)) / len(bits)

def block_frequency_test(data, block_size=128):
    bits = np.unpackbits(data.astype(np.uint8))
    n_blocks = len(bits) // block_size
    blocks = bits[:n_blocks * block_size].reshape(n_blocks, block_size)
    proportions = np.mean(blocks, axis=1)
    return float(np.mean(np.abs(proportions - 0.5)))
