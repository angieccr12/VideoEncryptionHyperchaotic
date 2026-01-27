# analysis/video_loader.py
import cv2
import time

def load_video(path, max_frames=50):
    cap = cv2.VideoCapture(path)
    frames = []
    start = time.time()

    while len(frames) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frames.append(gray)

    cap.release()
    elapsed = time.time() - start
    return frames, elapsed
