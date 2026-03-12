# gui/viewer.py
import cv2
import numpy as np

window_created = False

MAX_WIDTH = 1280
MAX_HEIGHT = 720


def show_frames(original, encrypted, decrypted, info):
    global window_created

    # Crear cuadro vacío
    empty = np.zeros_like(encrypted)

    # Grid 2x2
    top_row = np.hstack((original, encrypted))
    bottom_row = np.hstack((decrypted, empty))
    combined = np.vstack((top_row, bottom_row))

    cv2.putText(
        combined,
        info,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    h, w = combined.shape[:2]

    # calcular factor de escala
    scale = min(MAX_WIDTH / w, MAX_HEIGHT / h, 1)

    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(combined, (new_w, new_h))

    # crear ventana solo una vez
    if not window_created:
        cv2.namedWindow("Viewer", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Viewer", new_w, new_h)
        window_created = True

    cv2.imshow("Viewer", resized)