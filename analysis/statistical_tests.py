import numpy as np
from scipy.stats import pearsonr

def correlation(frame, mode="horizontal"):
    if mode == "horizontal":
        x, y = frame[:, :-1], frame[:, 1:]
    elif mode == "vertical":
        x, y = frame[:-1, :], frame[1:, :]
    else:  # diagonal
        x, y = frame[:-1, :-1], frame[1:, 1:]

    return pearsonr(x.flatten(), y.flatten())[0]

def variance(frame):
    return float(np.var(frame))
