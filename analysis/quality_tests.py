# analysis/quality_tests.py
import numpy as np
import math

def mse(a, b):
    return float(np.mean((a - b) ** 2))

def psnr(a, b):
    m = mse(a, b)
    if m == 0:
        return float("inf")
    return 20 * math.log10(255 / math.sqrt(m))

def mad(a, b):
    return float(np.mean(np.abs(a - b)))
