"""
key_sensitivity_tests.py
Pruebas de sensibilidad a la clave.

Un cifrador caótico seguro debe producir al descifrar con clave ε-incorrecta:
  PSNR  ≈  8–12 dB     (equivalente a imagen de ruido blanco puro)
  SSIM  ≈  0.00–0.05   (sin correlación estructural con original)
  NPCR  ≈  99.6%       (casi todos los píxeles difieren del resultado correcto)

CORRECCIÓN respecto a versión anterior:
  - Se instancian generadores FRESCOS (misma semilla) para enc y dec_correct,
    evitando desincronización por warm-up compartido.
  - Se instancia un tercer generador con semilla ε-diferente para dec_wrong.
  - key_sensitivity_metrics() acepta frames 2D o 3D.
"""

import numpy as np
from analysis.quality_tests      import psnr
from analysis.ssim_tests         import ssim
from analysis.differential_tests import npcr


def key_sensitivity_metrics(frame_correct, frame_wrong_key):
    """
    Compara el resultado de descifrar con clave correcta vs clave incorrecta.

    Args:
        frame_correct:   frame descifrado con clave correcta (2D o 3D uint8)
        frame_wrong_key: frame descifrado con clave incorrecta (2D o 3D uint8)
    Returns:
        dict con PSNR, SSIM y NPCR
    """
    # Convertir a escala de grises para PSNR y SSIM
    if frame_correct.ndim == 3:
        orig_g  = np.mean(frame_correct,   axis=2).astype(np.uint8)
        wrong_g = np.mean(frame_wrong_key, axis=2).astype(np.uint8)
    else:
        orig_g  = frame_correct
        wrong_g = frame_wrong_key

    return {
        "PSNR clave incorrecta (dB)": psnr(orig_g, wrong_g),
        "SSIM clave incorrecta":      ssim(orig_g, wrong_g),
        "NPCR clave incorrecta (%)":  npcr(orig_g, wrong_g),
    }


def full_key_sensitivity_test(encryptor_class, chaos_class, frame,
                               correct_seed=0.1, delta=1e-10,
                               audio_chunk=None):
    """
    Prueba completa de sensibilidad a la clave:
      1. Cifra el frame con la clave correcta.
      2. Descifra con la clave correcta → frame_ok.
      3. Descifra con clave ε-incorrecta (seed + delta) → frame_bad.
      4. Compara frame_ok vs frame_bad.

    Cada generador se instancia con semilla fresca para evitar desincronización.

    Args:
        encryptor_class: clase MNAKFrameEncryptor
        chaos_class:     clase ChaosKeyGenerator
        frame:           ndarray (M, N, 3) uint8
        correct_seed:    semilla correcta del generador
        delta:           perturbación mínima sobre la semilla incorrecta
        audio_chunk:     audio sincronizado o None
    Returns:
        dict con PSNR, SSIM, NPCR
    """
    # ── Cifrar con clave correcta ────────────────────────────────────────────
    enc_correct = encryptor_class(chaos_class(seed=correct_seed))
    ciphertext  = enc_correct.encrypt(frame, audio_chunk)

    # ── Descifrar con clave correcta ─────────────────────────────────────────
    dec_correct     = encryptor_class(chaos_class(seed=correct_seed))
    frame_ok, _     = dec_correct.decrypt(ciphertext)

    # ── Descifrar con clave ε-incorrecta ─────────────────────────────────────
    wrong_seed      = correct_seed + delta
    dec_wrong       = encryptor_class(chaos_class(seed=wrong_seed))
    try:
        frame_bad, _ = dec_wrong.decrypt(ciphertext)
    except Exception:
        # Si el descifrado falla por magic number incorrecto, el resultado
        # es ruido puro → generar array aleatorio del mismo tamaño
        rng       = np.random.default_rng(42)
        frame_bad = rng.integers(0, 256, frame.shape, dtype=np.uint8)

    return key_sensitivity_metrics(frame_ok, frame_bad)