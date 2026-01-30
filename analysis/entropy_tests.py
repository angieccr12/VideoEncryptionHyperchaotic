# analysis/entropy_tests.py
import numpy as np
from scipy.stats import entropy

def entropy_global(frames):
    data = np.concatenate([f.flatten() for f in frames])
    hist, _ = np.histogram(data, bins=256, range=(0, 256), density=True)
    return entropy(hist + 1e-12)

def entropy_per_frame(frames):
    values = []
    for f in frames:
        hist, _ = np.histogram(f.flatten(), bins=256, range=(0, 256), density=True)
        values.append(entropy(hist + 1e-12))
    return float(np.mean(values))
