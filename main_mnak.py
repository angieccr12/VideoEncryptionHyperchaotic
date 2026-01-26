"""
main_mnak.py
Sistema de encriptación M×N×A×K
M: Ancho del frame (píxeles)
N: Alto del frame (píxeles)
A: Audio sincronizado por frame
K: Estado del sistema hipercaótico (clave dinámica)
"""
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

print("="*70)
print("🎬 SISTEMA DE ENCRIPTACIÓN M×N×A×K - VIDEO HIPERCAÓTICO")
print("="*70)
print()
print("Dimensiones:")
print(f"  M (Ancho):  {FRAME_WIDTH} píxeles")
print(f"  N (Alto):   {FRAME_HEIGHT} píxeles")
print(f"  A (Audio):  Sincronizado frame a frame")
print(f"  K (Caos):   Sistema hipercaótico 4D con retardos")
print("="*70)

# ============================================================================
# PASO 1: EXTRAER Y CARGAR AUDIO (DIMENSIÓN A)
# ============================================================================
print("\n📢 Paso 1: Extrayendo y sincronizando audio (dimensión A)...")

audio_extractor = AudioExtractor(VIDEO_INPUT, fps=FPS)
wav_path = audio_extractor.extract_audio_to_wav("data/temp_audio_mnak.wav")

if wav_path and audio_extractor.load_audio_data(wav_path):
    has_audio = True
    audio_dims = audio_extractor.get_dimensions()
    print(f"✅ Dimensión A = {audio_dims['A']} muestras/frame")
else:
    has_audio = False
    print("ℹ️  No hay audio, A = 0")

# ============================================================================
# PASO 2: CONFIGURAR SISTEMA CAÓTICO (DIMENSIÓN K)
# ============================================================================
print(f"\n🔐 Paso 2: Inicializando sistema hipercaótico (dimensión K)...")

seed = 0.1
warmup = 1000

print(f"   - Semilla inicial: {seed}")
print(f"   - Warmup: {warmup} iteraciones")
print(f"   - Retardos: τ₁=0.12, τ₂=0.25, τ₃=0.38")

keygen_enc = ChaosKeyGenerator(seed=seed)
keygen_dec = ChaosKeyGenerator(seed=seed)

# Warmup del sistema caótico
for _ in range(warmup):
    keygen_enc.step()
    keygen_dec.step()

print("✅ Sistema caótico inicializado (K = espacio ℝ⁴)")

# ============================================================================
# PASO 3: CREAR ENCRIPTADORES M×N×A×K
# ============================================================================
print(f"\n🔧 Paso 3: Creando encriptadores M×N×A×K...")

samples_per_frame = audio_extractor.samples_per_frame if has_audio else 0

encryptor = MNAKFrameEncryptor(keygen_enc, audio_samples_per_frame=samples_per_frame)
decryptor = MNAKFrameEncryptor(keygen_dec, audio_samples_per_frame=samples_per_frame)

print(f"✅ Encriptadores configurados")

# ============================================================================
# PASO 4: PROCESAR VIDEO (ENCRIPTAR/DESENCRIPTAR)
# ============================================================================
print(f"\n🎥 Paso 4: Procesando video frame a frame...")

cap = open_video(VIDEO_INPUT)
writer_enc = create_writer(VIDEO_ENCRYPTED, FPS, (FRAME_WIDTH, FRAME_HEIGHT))

# Video temporal para frames desencriptados (sin audio todavía)
VIDEO_DECRYPTED_TEMP = "data/decrypted_video_no_audio_mnak.mp4"
writer_dec = create_writer(VIDEO_DECRYPTED_TEMP, FPS, (FRAME_WIDTH, FRAME_HEIGHT))

timer = Timer()
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_id = 0

# Lista para almacenar chunks de audio desencriptados
decrypted_audio_chunks = []

# Directorio para datos encriptados
os.makedirs("data/encrypted_frames", exist_ok=True)

print(f"📊 Total de frames a procesar: {total_frames}")
print("   Encriptando con estructura M×N×A×K...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Redimensionar frame a M×N
    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

    # Obtener chunk de audio para este frame (dimensión A)
    if has_audio:
        audio_chunk = audio_extractor.get_audio_chunk_for_frame(frame_id)
    else:
        audio_chunk = None

    # ENCRIPTAR: M×N×A×K → Ciphertext
    encrypted_data = encryptor.encrypt(frame, audio_chunk)
    
    # Guardar datos encriptados (binarios)
    encrypted_file = f"data/encrypted_frames/frame_{frame_id:06d}.mnak"
    with open(encrypted_file, 'wb') as f:
        f.write(encrypted_data)

    # DESENCRIPTAR: Ciphertext → M×N×A×K
    decrypted_frame, decrypted_audio = decryptor.decrypt(encrypted_data)
    
    # Guardar audio desencriptado para reconstrucción posterior
    if decrypted_audio is not None:
        decrypted_audio_chunks.append(decrypted_audio)

    # Para visualización: crear frame encriptado visible (ruido)
    # (los datos reales encriptados están en formato binario)
    encrypted_visual = np.frombuffer(encrypted_data[:frame.size], dtype=np.uint8)
    encrypted_visual = encrypted_visual[:FRAME_HEIGHT*FRAME_WIDTH*3]
    encrypted_visual = encrypted_visual.reshape((FRAME_HEIGHT, FRAME_WIDTH, 3))

    # Escribir frames de video (sin audio)
    writer_enc.write(encrypted_visual)
    writer_dec.write(decrypted_frame)

    # Mostrar progreso
    progress = (frame_id / total_frames) * 100
    info = f"Frame {frame_id}/{total_frames} | {progress:.1f}% | {timer.elapsed():.1f}s | M×N×A×K"

    show_frames(frame, encrypted_visual, decrypted_frame, info)

    frame_id += 1
    if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
        break

cap.release()
writer_enc.release()
writer_dec.release()
cv2.destroyAllWindows()

print(f"\n✅ Procesamiento completado: {frame_id} frames")

# ============================================================================
# PASO 5: RECONSTRUIR AUDIO Y COMBINAR CON VIDEO
# ============================================================================
print(f"\n🎵 Paso 5: Reconstruyendo audio desde dimensión A...")

if has_audio and len(decrypted_audio_chunks) > 0:
    # Reconstruir audio desde chunks
    reconstructed_wav = audio_extractor.reconstruct_audio_from_chunks(
        decrypted_audio_chunks,
        "data/reconstructed_audio_mnak.wav"
    )
    
    if reconstructed_wav:
        # Combinar video desencriptado con audio reconstruido
        print("🎵 Combinando video con audio reconstruido...")
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
            print(f"✅ Video con audio guardado: {VIDEO_DECRYPTED}")
        except Exception as e:
            print(f"❌ Error combinando audio: {e}")
        
        # Limpiar archivos temporales
        if os.path.exists(VIDEO_DECRYPTED_TEMP):
            os.remove(VIDEO_DECRYPTED_TEMP)
        if os.path.exists(reconstructed_wav):
            os.remove(reconstructed_wav)
        if os.path.exists(wav_path):
            os.remove(wav_path)
        
        print("✅ Audio reconstruido y combinado")
else:
    # Sin audio, simplemente renombrar
    if os.path.exists(VIDEO_DECRYPTED_TEMP):
        os.rename(VIDEO_DECRYPTED_TEMP, VIDEO_DECRYPTED)
    print("ℹ️  Video sin audio procesado")

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "="*70)
print("✅ PROCESO M×N×A×K COMPLETADO")
print("="*70)
print(f"\n📊 Estructura procesada:")
print(f"   M (Ancho):        {FRAME_WIDTH} píxeles")
print(f"   N (Alto):         {FRAME_HEIGHT} píxeles")
print(f"   A (Audio/frame):  {audio_extractor.samples_per_frame if has_audio else 0} muestras")
print(f"   K (Estado caos):  4D (x, y, z, w) ∈ ℝ⁴")
print(f"\n📁 Archivos generados:")
print(f"   - Video cifrado:      {VIDEO_ENCRYPTED}")
print(f"   - Video descifrado:   {VIDEO_DECRYPTED}")
print(f"   - Frames encriptados: data/encrypted_frames/ ({frame_id} archivos .mnak)")
print(f"\n⏱️  Tiempo total: {timer.elapsed():.2f}s")
print(f"⚡  Velocidad: {frame_id/timer.elapsed():.2f} frames/s")
print("\n" + "="*70)
print("🔐 Dimensión K (claves por frame): {frame_id} estados caóticos únicos")
print("="*70)
