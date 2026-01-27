# analysis/ssim_tests.py
import numpy as np
from scipy.ndimage import gaussian_filter

def ssim(img1, img2):
    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)

    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2

    mu1 = gaussian_filter(img1, 1.5)
    mu2 = gaussian_filter(img2, 1.5)

    sigma1 = gaussian_filter(img1 ** 2, 1.5) - mu1 ** 2
    sigma2 = gaussian_filter(img2 ** 2, 1.5) - mu2 ** 2
    sigma12 = gaussian_filter(img1 * img2, 1.5) - mu1 * mu2

    ssim_map = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1 ** 2 + mu2 ** 2 + C1) *
                (sigma1 + sigma2 + C2))

    return float(np.mean(ssim_map))
