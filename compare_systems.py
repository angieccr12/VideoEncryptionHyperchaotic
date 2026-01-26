"""
compare_systems.py
Comparación entre sistema original y sistema M×N×A×K
"""
import os
import sys

# Importar settings solo si está disponible
try:
    from config.settings import FRAME_WIDTH, FRAME_HEIGHT
except ImportError:
    FRAME_WIDTH = 426
    FRAME_HEIGHT = 320


def print_comparison_table():
    """
    Muestra una tabla comparativa de ambos sistemas
    """
    print("="*90)
    print(" "*25 + "COMPARACIÓN DE SISTEMAS")
    print("="*90)
    
    print(f"\n{'Característica':<25} {'Sistema Original':<30} {'Sistema M×N×A×K':<30}")
    print("-"*90)
    
    # Estructura de datos
    print(f"{'ESTRUCTURA DE DATOS':<25}")
    print(f"{'  Video':<25} {'M×N×3 (frame RGB)':<30} {'M×N×3 (frame RGB)':<30}")
    print(f"{'  Audio':<25} {'Separado (no encriptado)':<30} {'✅ Integrado A muestras':<30}")
    print(f"{'  Clave':<25} {'❌ Implícita':<30} {'✅ Explícita K=(x,y,z,w)':<30}")
    
    print(f"\n{'DIMENSIONES':<25}")
    print(f"{'  M (Ancho)':<25} {str(FRAME_WIDTH) + ' píxeles':<30} {str(FRAME_WIDTH) + ' píxeles':<30}")
    print(f"{'  N (Alto)':<25} {str(FRAME_HEIGHT) + ' píxeles':<30} {str(FRAME_HEIGHT) + ' píxeles':<30}")
    print(f"{'  A (Audio/frame)':<25} {'N/A':<30} {'~1600 muestras':<30}")
    print(f"{'  K (Clave)':<25} {'Implícita (evolución)':<30} {'Explícita ℝ⁴':<30}")
    
    print(f"\n{'FORMATO DE SALIDA':<25}")
    print(f"{'  Video encriptado':<25} {'.mp4 estándar':<30} {'.mp4 + .mnak':<30}")
    print(f"{'  Audio en cifrado':<25} {'❌ No incluido':<30} {'✅ Incluido':<30}")
    print(f"{'  Metadata K':<25} {'❌ No guardada':<30} {'✅ En cada frame':<30}")
    
    print(f"\n{'SEGURIDAD':<25}")
    print(f"{'  Clave por frame':<25} {'✅ Sí (AES derivado)':<30} {'✅ Sí (AES derivado)':<30}")
    print(f"{'  Verificación':<25} {'❌ No integrada':<30} {'✅ Estado K guardado':<30}")
    print(f"{'  Encriptación audio':<25} {'❌ No':<30} {'✅ Sí':<30}")
    
    print(f"\n{'PROCESAMIENTO':<25}")
    print(f"{'  Archivos main':<25} {'main.py':<30} {'main_mnak.py':<30}")
    print(f"{'  Encriptador':<25} {'AESCFBFrameEncryptor':<30} {'MNAKFrameEncryptor':<30}")
    print(f"{'  Post-proceso':<25} {'Combinar audio después':<30} {'Audio integrado':<30}")
    
    # Calcular tamaños
    frame_size_original = FRAME_WIDTH * FRAME_HEIGHT * 3
    frame_size_mnak = 48 + (FRAME_WIDTH * FRAME_HEIGHT * 3) + (1600 * 2)  # header + video + audio
    
    print(f"\n{'TAMAÑOS':<25}")
    print(f"{'  Frame sin encriptar':<25} {f'{frame_size_original:,} bytes':<30} {f'{frame_size_original:,} bytes':<30}")
    print(f"{'  Frame encriptado':<25} {f'{frame_size_original:,} bytes':<30} {f'{frame_size_mnak:,} bytes':<30}")
    print(f"{'  Overhead':<25} {'0 bytes':<30} {f'{frame_size_mnak - frame_size_original:,} bytes':<30}")
    
    print(f"\n{'USO RECOMENDADO':<25}")
    print(f"{'  Original':<25} {'Videos sin audio o audio no crítico':<55}")
    print(f"{'  M×N×A×K':<25} {'Videos con audio que debe ser encriptado':<55}")
    
    print("\n" + "="*90)


def demonstrate_dimensions():
    """
    Demuestra visualmente las dimensiones M×N×A×K
    """
    print("\n" + "="*90)
    print(" "*30 + "DIMENSIONES M×N×A×K")
    print("="*90)
    
    M = FRAME_WIDTH   # 426
    N = FRAME_HEIGHT  # 320
    A = 1600  # muestras de audio por frame (ejemplo: 48kHz / 30fps)
    K = 4     # dimensión del espacio de estados (x, y, z, w)
    
    print(f"""
    ┌───────────────────────────────────────────────────────────┐
    │                   ESTRUCTURA M×N×A×K                      │
    └───────────────────────────────────────────────────────────┘
    
    Para cada FRAME i:
    
    ┌─────────────────────────────────────────────────────────┐
    │  DIMENSIÓN M (Ancho): {M} píxeles                        │
    │  DIMENSIÓN N (Alto):  {N} píxeles                        │
    │  DIMENSIÓN A (Audio): {A} muestras                       │
    │  DIMENSIÓN K (Caos):  4D = (x, y, z, w) ∈ ℝ⁴            │
    └─────────────────────────────────────────────────────────┘
    
    Representación visual:
    
    ┌─── M = {M} píxeles ───────────────────────────┐
    │ ╔═══════════════════════════════════════════╗ │ ┐
    │ ║                                           ║ │ │
    │ ║                                           ║ │ │
    │ ║          FRAME (RGB)                      ║ │ │
    │ ║          M × N × 3                        ║ │ N = {N}
    │ ║                                           ║ │ │ píxeles
    │ ║                                           ║ │ │
    │ ╚═══════════════════════════════════════════╝ │ ┘
    └───────────────────────────────────────────────┘
             ↓
         Combinado con
             ↓
    ┌───── AUDIO (A = {A}) ────────────────────────┐
    │  [s₁, s₂, s₃, ..., s₁₆₀₀]                    │
    │  Muestras de audio para este frame           │
    └───────────────────────────────────────────────┘
             ↓
         Encriptado con clave
             ↓
    ┌───── CLAVE K (Sistema Caótico) ──────────────┐
    │  K = (x, y, z, w)                            │
    │  x = estado de variable x                    │
    │  y = estado de variable y                    │
    │  z = estado de variable z                    │
    │  w = estado de variable w                    │
    │                                               │
    │  Evoluciona cada frame:                      │
    │  K₀ → K₁ → K₂ → ... → Kᵢ                    │
    └───────────────────────────────────────────────┘
    
    TAMAÑOS EN BYTES:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Header (metadata):       48 bytes
    Video (M×N×3):      {M * N * 3:,} bytes
    Audio (A×2):         {A * 2:,} bytes
    ────────────────────────────────────────────────
    TOTAL por frame:    {48 + M*N*3 + A*2:,} bytes
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    EVOLUCIÓN TEMPORAL:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Frame 0: (V₀, A₀, K₀)  →  Encriptar  →  .mnak
    Frame 1: (V₁, A₁, K₁)  →  Encriptar  →  .mnak
    Frame 2: (V₂, A₂, K₂)  →  Encriptar  →  .mnak
    ...
    Frame t: (Vₜ, Aₜ, Kₜ)  →  Encriptar  →  .mnak
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    print("="*90)


def show_file_structure():
    """
    Muestra la estructura de archivos de ambos sistemas
    """
    print("\n" + "="*90)
    print(" "*30 + "ESTRUCTURA DE ARCHIVOS")
    print("="*90)
    
    print("""
    SISTEMA ORIGINAL:
    ─────────────────
    crypto/
      ├── chaos_generator.py      (Sistema caótico)
      ├── aes_encryptor.py        (Encriptador AES básico)
      └── sdk_generator.py        (Derivación de claves)
    
    main.py                        (Procesa video)
      ↓
    data/
      ├── encrypted_video.mp4     (Video cifrado, SIN audio)
      └── decrypted_video.mp4     (Video descifrado + audio original)
    
    
    SISTEMA M×N×A×K:
    ────────────────
    crypto/
      ├── chaos_generator.py      (Sistema caótico - igual)
      ├── mnk_encryptor.py        (✨ NUEVO: Encriptador M×N×A×K)
      └── sdk_generator.py        (Derivación de claves - igual)
    
    utils/
      └── audio_extractor.py      (✨ NUEVO: Extractor sincronizado)
    
    main_mnak.py                   (✨ NUEVO: Procesa con M×N×A×K)
      ↓
    data/
      ├── encrypted_video.mp4     (Video cifrado para visualización)
      ├── encrypted_frames/       (✨ NUEVO: Frames .mnak)
      │   ├── frame_000000.mnak   (Frame 0: M×N×A×K encriptado)
      │   ├── frame_000001.mnak   (Frame 1: M×N×A×K encriptado)
      │   └── ...
      └── decrypted_video.mp4     (Video + audio desencriptados)
    
    
    ARCHIVOS DE ANÁLISIS:
    ─────────────────────
    verify_mnak_dimensions.py      (✨ Verifica dimensiones M×N×A×K)
    compare_systems.py             (✨ Este archivo - comparación)
    MNAK_DOCUMENTATION.md          (✨ Documentación completa)
    """)
    
    print("="*90)


def main():
    """
    Función principal
    """
    print("\n")
    print("╔" + "═"*88 + "╗")
    print("║" + " "*20 + "COMPARACIÓN: SISTEMA ORIGINAL vs M×N×A×K" + " "*27 + "║")
    print("╚" + "═"*88 + "╝")
    
    # Tabla comparativa
    print_comparison_table()
    
    # Demostración visual de dimensiones
    demonstrate_dimensions()
    
    # Estructura de archivos
    show_file_structure()
    
    # Recomendaciones
    print("\n" + "="*90)
    print(" "*35 + "RECOMENDACIONES")
    print("="*90)
    
    print("""
    📝 CUÁNDO USAR CADA SISTEMA:
    
    ✅ USA SISTEMA ORIGINAL (main.py) si:
       • El video no tiene audio
       • El audio no necesita ser encriptado
       • Necesitas formato .mp4 estándar
       • Prioridad: simplicidad y compatibilidad
    
    ✅ USA SISTEMA M×N×A×K (main_mnak.py) si:
       • El video tiene audio que debe encriptarse
       • Necesitas verificación de integridad (estado K)
       • Quieres análisis detallado de dimensiones
       • Prioridad: máxima seguridad y control
    
    🔬 PARA ANÁLISIS ACADÉMICO:
       • Sistema M×N×A×K proporciona estructura más completa
       • Permite análisis dimensional explícito
       • Facilita estudios de sincronización audio-video
       • Incluye metadata del estado caótico para investigación
    
    💡 AMBOS SISTEMAS:
       • Usan el mismo generador caótico hipercaótico
       • Tienen la misma seguridad criptográfica (AES-256)
       • Generan videos desencriptados idénticos al original
       • Son compatibles con test.py para análisis
    """)
    
    print("="*90)
    
    # Instrucciones de uso
    print("\n" + "="*90)
    print(" "*38 + "CÓMO USAR")
    print("="*90)
    
    print("""
    🚀 EJECUTAR SISTEMA ORIGINAL:
       python main.py
    
    🚀 EJECUTAR SISTEMA M×N×A×K:
       python main_mnak.py
    
    🔍 VERIFICAR DIMENSIONES:
       python verify_mnak_dimensions.py
    
    📊 ANÁLISIS CRIPTOGRÁFICO:
       python test.py
    """)
    
    print("="*90 + "\n")


if __name__ == "__main__":
    main()
