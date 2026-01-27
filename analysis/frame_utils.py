# analysis/frame_utils.py
import cv2

def match_frame_size(reference, target):
    """
    Ajusta el frame target al tamaño del frame reference
    """
    h, w = reference.shape
    return cv2.resize(target, (w, h), interpolation=cv2.INTER_LINEAR)
