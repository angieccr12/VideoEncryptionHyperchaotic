import cv2

def open_video(path):
    return cv2.VideoCapture(path)

def create_writer(path, fps, size):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    return cv2.VideoWriter(path, fourcc, fps, size)
