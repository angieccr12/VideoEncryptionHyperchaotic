# config/settings.py
import cv2

VIDEO_INPUT = "data/video_prueba3.mp4"
VIDEO_ENCRYPTED = "data/encrypted_video.mp4"
VIDEO_DECRYPTED = "data/decrypted_video.mp4"

cap = cv2.VideoCapture(VIDEO_INPUT)

FRAME_WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
FRAME_HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
FPS = cap.get(cv2.CAP_PROP_FPS)

cap.release()