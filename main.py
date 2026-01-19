import cv2
from config.settings import *
from crypto.chaos_generator import ChaosKeyGenerator
from crypto.encryptor import FrameEncryptor
from video.video_io import open_video, create_writer
from gui.viewer import show_frames
from utils.timer import Timer

cap = open_video(VIDEO_INPUT)
writer_enc = create_writer(VIDEO_ENCRYPTED, FPS, (FRAME_WIDTH, FRAME_HEIGHT))
writer_dec = create_writer(VIDEO_DECRYPTED, FPS, (FRAME_WIDTH, FRAME_HEIGHT))

keygen = ChaosKeyGenerator()
encryptor = FrameEncryptor(keygen)
timer = Timer()

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_id = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
    encrypted = encryptor.encrypt(frame)
    decrypted = encryptor.decrypt(encrypted)

    writer_enc.write(encrypted)
    writer_dec.write(decrypted)

    progress = (frame_id / total_frames) * 100
    info = f"Frame {frame_id}/{total_frames} | {progress:.1f}% | {timer.elapsed():.1f}s"

    show_frames(frame, encrypted, decrypted, info)

    frame_id += 1
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
writer_enc.release()
writer_dec.release()
cv2.destroyAllWindows()
