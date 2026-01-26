"""
verify_mnak_dimensions.py
Script para verificar y analizar las dimensiones M×N×A×K del sistema
"""
import os
import struct
import numpy as np
from crypto.chaos_generator import ChaosKeyGenerator
from utils.audio_extractor import AudioExtractor
from config.settings import *


def analyze_mnak_file(filepath):
    """
    Analiza un archivo .mnak y muestra sus dimensiones
    
    Args:
        filepath: Ruta al archivo .mnak
    """
    print(f"\n📄 Analizando: {os.path.basename(filepath)}")
    print("-" * 60)
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Tamaño total
    total_size = len(data)
    print(f"Tamaño total: {total_size:,} bytes ({total_size/1024:.2f} KB)")
    
    # Leer header
    magic = data[0:4]
    print(f"\nMagic number: {magic}")
    
    if magic != b'MNAK':
        print("❌ Archivo no es formato MNAK válido")
        return None
    
    M = struct.unpack('<I', data[4:8])[0]
    N = struct.unpack('<I', data[8:12])[0]
    A = struct.unpack('<I', data[12:16])[0]
    
    chaos_state = np.frombuffer(data[16:48], dtype=np.float64)
    x, y, z, w = chaos_state
    
    print(f"\n📊 DIMENSIONES:")
    print(f"  M (Ancho):  {M} píxeles")
    print(f"  N (Alto):   {N} píxeles")
    print(f"  A (Audio):  {A} muestras/frame")
    print(f"  K (Caos):   4D = ({x:.6f}, {y:.6f}, {z:.6f}, {w:.6f})")
    
    # Calcular tamaños esperados
    header_size = 48
    video_size = M * N * 3
    audio_size = A * 2  # int16 = 2 bytes
    expected_size = header_size + video_size + audio_size
    
    print(f"\n📦 ESTRUCTURA:")
    print(f"  Header:     {header_size} bytes")
    print(f"  Video:      {video_size:,} bytes (M×N×3)")
    print(f"  Audio:      {audio_size:,} bytes (A×2)")
    print(f"  Esperado:   {expected_size:,} bytes")
    print(f"  Real:       {total_size:,} bytes")
    
    if total_size == expected_size:
        print("  ✅ Estructura correcta")
    else:
        print(f"  ⚠️  Diferencia: {total_size - expected_size} bytes")
    
    return {
        'M': M,
        'N': N,
        'A': A,
        'K': (x, y, z, w),
        'sizes': {
            'header': header_size,
            'video': video_size,
            'audio': audio_size,
            'total': total_size
        }
    }


def verify_chaos_evolution(seed=0.1, warmup=1000, num_steps=10):
    """
    Verifica la evolución del sistema caótico (dimensión K)
    
    Args:
        seed: Semilla inicial
        warmup: Iteraciones de calentamiento
        num_steps: Pasos a mostrar
    """
    print(f"\n🔐 VERIFICACIÓN DE DIMENSIÓN K (Sistema Caótico)")
    print("="*60)
    print(f"Configuración:")
    print(f"  - Semilla: {seed}")
    print(f"  - Warmup: {warmup} iteraciones")
    print(f"  - Pasos a mostrar: {num_steps}")
    
    chaos = ChaosKeyGenerator(seed=seed)
    
    # Warmup
    print(f"\n⏳ Aplicando warmup...")
    for _ in range(warmup):
        chaos.step()
    
    print(f"\n📈 Evolución de K (post-warmup):")
    print(f"{'Step':<8} {'x':<15} {'y':<15} {'z':<15} {'w':<15}")
    print("-"*68)
    
    states = []
    for i in range(num_steps):
        x, y, z, w = chaos.step()
        states.append((x, y, z, w))
        print(f"{i:<8} {x:<15.6f} {y:<15.6f} {z:<15.6f} {w:<15.6f}")
    
    # Análisis de la evolución
    states_array = np.array(states)
    means = np.mean(states_array, axis=0)
    stds = np.std(states_array, axis=0)
    
    print(f"\n📊 Estadísticas de K:")
    print(f"  Media:  x={means[0]:.6f}, y={means[1]:.6f}, z={means[2]:.6f}, w={means[3]:.6f}")
    print(f"  Desv:   x={stds[0]:.6f}, y={stds[1]:.6f}, z={stds[2]:.6f}, w={stds[3]:.6f}")
    
    # Verificar comportamiento caótico
    is_chaotic = np.all(stds > 0.1)  # Desviación suficiente
    print(f"\n{'✅' if is_chaotic else '❌'} Sistema muestra comportamiento caótico")
    
    return states


def verify_audio_dimensions(video_path, fps=30):
    """
    Verifica las dimensiones de audio (A)
    
    Args:
        video_path: Ruta al video
        fps: Frames por segundo
    """
    print(f"\n🎵 VERIFICACIÓN DE DIMENSIÓN A (Audio)")
    print("="*60)
    
    if not os.path.exists(video_path):
        print(f"❌ Video no encontrado: {video_path}")
        return None
    
    extractor = AudioExtractor(video_path, fps=fps)
    wav_path = extractor.extract_audio_to_wav("data/temp_verify_audio.wav")
    
    if not wav_path:
        print("ℹ️  Video sin audio, A = 0")
        return None
    
    extractor.load_audio_data(wav_path)
    dims = extractor.get_dimensions()
    
    print(f"\n📊 Dimensiones de Audio:")
    print(f"  A = {dims['A']} muestras/frame")
    print(f"  Sample rate = {dims['sample_rate']} Hz")
    print(f"  FPS = {fps}")
    print(f"  Cálculo: {dims['sample_rate']} Hz / {fps} fps = {dims['A']} muestras/frame")
    
    # Verificar consistencia
    expected_A = dims['sample_rate'] // fps
    if dims['A'] == expected_A:
        print(f"  ✅ Dimensión A correcta")
    else:
        print(f"  ⚠️  Esperado: {expected_A}, obtenido: {dims['A']}")
    
    # Limpiar
    if os.path.exists(wav_path):
        os.remove(wav_path)
    
    return dims


def verify_video_dimensions(video_path):
    """
    Verifica las dimensiones de video (M×N)
    
    Args:
        video_path: Ruta al video
    """
    print(f"\n🎥 VERIFICACIÓN DE DIMENSIONES M×N (Video)")
    print("="*60)
    
    if not os.path.exists(video_path):
        print(f"❌ Video no encontrado: {video_path}")
        return None
    
    import cv2
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("❌ No se pudo abrir el video")
        return None
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    cap.release()
    
    print(f"\n📊 Dimensiones del Video:")
    print(f"  M (Ancho):  {width} píxeles")
    print(f"  N (Alto):   {height} píxeles")
    print(f"  Canales:    3 (RGB)")
    print(f"  FPS:        {fps}")
    print(f"  Frames:     {frame_count}")
    print(f"  Duración:   {frame_count/fps:.2f}s")
    
    # Verificar contra configuración
    if width == FRAME_WIDTH and height == FRAME_HEIGHT:
        print(f"  ✅ Dimensiones coinciden con configuración")
    else:
        print(f"  ⚠️  Configuración: {FRAME_WIDTH}×{FRAME_HEIGHT}")
        print(f"     Real: {width}×{height}")
    
    return {
        'M': width,
        'N': height,
        'fps': fps,
        'frames': frame_count
    }


def main():
    """
    Función principal de verificación
    """
    print("="*70)
    print("🔍 VERIFICACIÓN DE DIMENSIONES M×N×A×K")
    print("="*70)
    
    # Verificar dimensiones del video original
    print("\n" + "="*70)
    print("PARTE 1: Dimensiones del Video Original")
    print("="*70)
    video_dims = verify_video_dimensions(VIDEO_INPUT)
    
    # Verificar dimensiones de audio
    print("\n" + "="*70)
    print("PARTE 2: Dimensiones de Audio")
    print("="*70)
    audio_dims = verify_audio_dimensions(VIDEO_INPUT, fps=FPS)
    
    # Verificar evolución del sistema caótico
    print("\n" + "="*70)
    print("PARTE 3: Evolución del Sistema Caótico (K)")
    print("="*70)
    chaos_states = verify_chaos_evolution(seed=0.1, warmup=1000, num_steps=10)
    
    # Analizar archivos .mnak si existen
    print("\n" + "="*70)
    print("PARTE 4: Análisis de Archivos .mnak")
    print("="*70)
    
    mnak_dir = "data/encrypted_frames"
    if os.path.exists(mnak_dir):
        mnak_files = [f for f in os.listdir(mnak_dir) if f.endswith('.mnak')]
        
        if mnak_files:
            print(f"\n📁 Encontrados {len(mnak_files)} archivos .mnak")
            
            # Analizar los primeros 3
            for i, filename in enumerate(sorted(mnak_files)[:3]):
                filepath = os.path.join(mnak_dir, filename)
                analyze_mnak_file(filepath)
                
                if i < 2:  # No imprimir separador después del último
                    print()
        else:
            print("\nℹ️  No hay archivos .mnak. Ejecuta main_mnak.py primero.")
    else:
        print(f"\nℹ️  Directorio {mnak_dir} no existe. Ejecuta main_mnak.py primero.")
    
    # Resumen final
    print("\n" + "="*70)
    print("✅ RESUMEN DE VERIFICACIÓN")
    print("="*70)
    
    if video_dims:
        print(f"\n📐 Estructura M×N×A×K:")
        print(f"  M (Ancho):        {video_dims['M']} píxeles")
        print(f"  N (Alto):         {video_dims['N']} píxeles")
        if audio_dims:
            print(f"  A (Audio/frame):  {audio_dims['A']} muestras")
        else:
            print(f"  A (Audio/frame):  0 (sin audio)")
        print(f"  K (Estado caos):  4D ∈ ℝ⁴")
        
        # Calcular tamaño total por frame
        M, N = video_dims['M'], video_dims['N']
        A = audio_dims['A'] if audio_dims else 0
        
        header_size = 48
        video_size = M * N * 3
        audio_size = A * 2
        total_size = header_size + video_size + audio_size
        
        print(f"\n💾 Tamaño por frame encriptado:")
        print(f"  Header:   {header_size} bytes")
        print(f"  Video:    {video_size:,} bytes")
        print(f"  Audio:    {audio_size:,} bytes")
        print(f"  TOTAL:    {total_size:,} bytes ({total_size/1024:.2f} KB)")
        
        if video_dims.get('frames'):
            total_video_size = total_size * video_dims['frames']
            print(f"\n📦 Tamaño estimado video completo:")
            print(f"  {video_dims['frames']} frames × {total_size:,} bytes")
            print(f"  = {total_video_size:,} bytes")
            print(f"  = {total_video_size/1024/1024:.2f} MB")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
