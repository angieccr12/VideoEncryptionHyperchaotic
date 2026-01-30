"""
key_sensitivity_tests.py
Prueba de sensibilidad a la clave
"""

from analysis.quality_tests import psnr
from analysis.ssim_tests import ssim

def key_sensitivity_metrics(original_frame, decrypted_wrong_key_frame):
    """
    Evalúa la sensibilidad a la clave usando PSNR y SSIM.
    Un sistema seguro debe producir valores muy bajos.
    """
    return {
        "PSNR con clave incorrecta (dB)": psnr(original_frame, decrypted_wrong_key_frame),
        "SSIM con clave incorrecta": ssim(original_frame, decrypted_wrong_key_frame),
    }
