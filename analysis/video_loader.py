# analysis/video_loader.py
import cv2
import time
import os
import glob
import struct
import numpy as np

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

def load_mnak_files(directory, max_frames=50):
    """
    Carga archivos .mnak completos (M×N×A×K) para análisis de entropía.
    
    Args:
        directory: Directorio con archivos .mnak
        max_frames: Número máximo de frames a cargar
    
    Returns:
        data_arrays: Lista de arrays de bytes cifrados (cada uno contiene M×N×A×K)
        dimensions: Dict con dimensiones promedio {M, N, A, K}
        elapsed: Tiempo de carga
    """
    start = time.time()
    
    # Importar dimensiones de configuración
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.settings import FRAME_WIDTH, FRAME_HEIGHT
    
    M = FRAME_WIDTH
    N = FRAME_HEIGHT
    K_size = 32  # 4 float64 = 32 bytes (estado caótico)
    header_size = 48  # Header MNAK
    
    # Buscar archivos .mnak
    pattern = os.path.join(directory, "frame_*.mnak")
    mnak_files = sorted(glob.glob(pattern))[:max_frames]
    
    if not mnak_files:
        raise FileNotFoundError(f"No se encontraron archivos .mnak en {directory}")
    
    data_arrays = []
    file_sizes = []
    
    for filepath in mnak_files:
        with open(filepath, 'rb') as f:
            # Leer archivo completo cifrado
            encrypted_data = f.read()
            file_sizes.append(len(encrypted_data))
            
            # Guardar todo el contenido cifrado como un array
            data_array = np.frombuffer(encrypted_data, dtype=np.uint8)
            data_arrays.append(data_array)
    
    # Calcular dimensión A (audio) desde el tamaño del archivo
    # Formato: Header(48) + Frame(M×N×3) + Audio(A×2)
    avg_file_size = np.mean(file_sizes)
    frame_bytes = M * N * 3
    audio_bytes = avg_file_size - header_size - frame_bytes
    A = int(audio_bytes / 2) if audio_bytes > 0 else 0  # int16 = 2 bytes por muestra
    
    dimensions = {
        'M': M,
        'N': N,
        'A': max(0, A),
        'K': K_size,
        'total_frames': len(data_arrays),
        'avg_file_size': avg_file_size
    }
    
    elapsed = time.time() - start
    
    print(f"Cargados {len(data_arrays)} archivos .mnak")
    print(f"Dimensiones: M={dimensions['M']}, N={dimensions['N']}, A={dimensions['A']}, K={dimensions['K']}")
    print(f"Tamaño promedio por archivo: {avg_file_size:.0f} bytes")
    
    return data_arrays, dimensions, elapsed
