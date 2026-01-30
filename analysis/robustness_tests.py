# analysis/robustness_tests.py
import numpy as np
import cv2

def add_noise(frame, sigma=10):
    noise = np.random.normal(0, sigma, frame.shape)
    noisy = frame + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)

def occlusion(frame, block_size=50):
    h, w = frame.shape
    x = np.random.randint(0, w - block_size)
    y = np.random.randint(0, h - block_size)
    occluded = frame.copy()
    occluded[y:y+block_size, x:x+block_size] = 0
    return occluded
