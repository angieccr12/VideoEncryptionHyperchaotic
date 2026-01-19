import cv2
import numpy as np

def show_frames(original, encrypted, decrypted, info):
    combined = np.hstack((original, encrypted, decrypted))
    cv2.putText(
        combined,
        info,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )
    cv2.imshow("Original | Encrypted | Decrypted", combined)
