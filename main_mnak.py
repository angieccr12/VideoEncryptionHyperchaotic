import cv2
import os
import numpy as np
from config.settings import *
from crypto.chaos_generator import ChaosKeyGenerator
from crypto.mnk_encryptor import MNAKFrameEncryptor
from video.video_io import open_video, create_writer
from gui.viewer import show_frames
from utils.timer import Timer
from utils.audio_extractor import AudioExtractor
from moviepy.editor import VideoFileClip, AudioFileClip

print("Sistema de encriptacion M×N×A×K")
print(f"M={FRAME_WIDTH}, N={FRAME_HEIGHT}")

audio_extractor = AudioExtractor(VIDEO_INPUT, fps=FPS)
wav_path = audio_extractor.extract_audio_to_wav("data/temp_audio_mnak.wav")

if wav_path and audio_extractor.load_audio_data(wav_path):
    has_audio = True
    audio_dims = audio_extractor.get_dimensions()
    print(f"Audio: A={audio_dims['A']} muestras/frame")
else:
    has_audio = False
    print("Sin audio")

seed = 0.1
warmup = 1000

keygen_enc = ChaosKeyGenerator(seed=seed)
keygen_dec = ChaosKeyGenerator(seed=seed)

for _ in range(warmup):
    keygen_enc.step()
    keygen_dec.step()

samples_per_frame = audio_extractor.samples_per_frame if has_audio else 0
encryptor = MNAKFrameEncryptor(keygen_enc, audio_samples_per_frame=samples_per_frame)
decryptor = MNAKFrameEncryptor(keygen_dec, audio_samples_per_frame=samples_per_frame)

cap = open_video(VIDEO_INPUT)
writer_enc = create_writer(VIDEO_ENCRYPTED, FPS, (FRAME_WIDTH, FRAME_HEIGHT))

VIDEO_DECRYPTED_TEMP = "data/decrypted_video_no_audio_mnak.mp4"
writer_dec = create_writer(VIDEO_DECRYPTED_TEMP, FPS, (FRAME_WIDTH, FRAME_HEIGHT))

timer = Timer()
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_id = 0
decrypted_audio_chunks = []

os.makedirs("data/encrypted_frames", exist_ok=True)
print(f"Procesando {total_frames} frames...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

    if has_audio:
        audio_chunk = audio_extractor.get_audio_chunk_for_frame(frame_id)
    else:
        audio_chunk = None

    encrypted_data = encryptor.encrypt(frame, audio_chunk)
    
    encrypted_file = f"data/encrypted_frames/frame_{frame_id:06d}.mnak"
    with open(encrypted_file, 'wb') as f:
        f.write(encrypted_data)

    decrypted_frame, decrypted_audio = decryptor.decrypt(encrypted_data)
    
    if decrypted_audio is not None:
        decrypted_audio_chunks.append(decrypted_audio)

    encrypted_visual = np.frombuffer(encrypted_data[:frame.size], dtype=np.uint8)
    encrypted_visual = encrypted_visual[:FRAME_HEIGHT*FRAME_WIDTH*3]
    encrypted_visual = encrypted_visual.reshape((FRAME_HEIGHT, FRAME_WIDTH, 3))

    writer_enc.write(encrypted_visual)
    writer_dec.write(decrypted_frame)

    progress = (frame_id / total_frames) * 100
    info = f"Frame {frame_id}/{total_frames} | {progress:.1f}% | {timer.elapsed():.1f}s"

    show_frames(frame, encrypted_visual, decrypted_frame, info)

    frame_id += 1
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
writer_enc.release()
writer_dec.release()
cv2.destroyAllWindows()

print(f"Procesado {frame_id} frames")

if has_audio and len(decrypted_audio_chunks) > 0:
    reconstructed_wav = audio_extractor.reconstruct_audio_from_chunks(
        decrypted_audio_chunks,
        "data/reconstructed_audio_mnak.wav"
    )
    
    if reconstructed_wav:
        try:
            video = VideoFileClip(VIDEO_DECRYPTED_TEMP)
            audio = AudioFileClip(reconstructed_wav)
            video_with_audio = video.set_audio(audio)
            video_with_audio.write_videofile(
                VIDEO_DECRYPTED,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            video.close()
            audio.close()
            video_with_audio.close()
        except Exception as e:
            print(f"Error combinando audio: {e}")
        
        if os.path.exists(VIDEO_DECRYPTED_TEMP):
            os.remove(VIDEO_DECRYPTED_TEMP)
        if os.path.exists(reconstructed_wav):
            os.remove(reconstructed_wav)
        if os.path.exists(wav_path):
            os.remove(wav_path)
else:
    if os.path.exists(VIDEO_DECRYPTED_TEMP):
        os.rename(VIDEO_DECRYPTED_TEMP, VIDEO_DECRYPTED)

print(f"M={FRAME_WIDTH}, N={FRAME_HEIGHT}, A={audio_extractor.samples_per_frame if has_audio else 0}")
print(f"Tiempo: {timer.elapsed():.2f}s")
print(f"Velocidad: {frame_id/timer.elapsed():.2f} fps")
