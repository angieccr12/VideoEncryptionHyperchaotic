# 🎬 Sistema de Encriptación de Video M×N×A×K

## 📐 Descripción de Dimensiones

Este proyecto implementa un sistema de encriptación de video con estructura multidimensional **M×N×A×K**:

- **M**: Ancho del frame (426 píxeles)
- **N**: Alto del frame (320 píxeles)
- **A**: Audio sincronizado (~1600 muestras por frame)
- **K**: Estado del sistema hipercaótico 4D (x, y, z, w) ∈ ℝ⁴

## 🚀 Inicio Rápido

### Sistema Original (sin dimensión A y K explícitas)
```bash
python main.py
```
- Encripta solo video
- Audio se maneja separadamente
- Formato estándar .mp4

### Sistema M×N×A×K (dimensiones completas)
```bash
python main_mnak.py
```
- Encripta video + audio integrado
- Incluye estado caótico K explícito
- Genera archivos .mnak con estructura completa

## 📊 Comparación de Sistemas

```bash
python compare_systems.py
```

Muestra tabla comparativa completa entre ambos sistemas.

## 🔍 Verificación de Dimensiones

```bash
python verify_mnak_dimensions.py
```

Analiza y verifica:
- Dimensiones M, N del video
- Dimensión A del audio sincronizado
- Evolución de dimensión K (sistema caótico)
- Integridad de archivos .mnak

## 📁 Estructura del Proyecto

```
VideoEncryptionHyperchaotic/
├── main.py                      # Sistema original
├── main_mnak.py                 # ✨ Sistema M×N×A×K
├── compare_systems.py           # ✨ Comparación
├── verify_mnak_dimensions.py    # ✨ Verificación
│
├── crypto/
│   ├── chaos_generator.py       # Sistema hipercaótico
│   ├── aes_encryptor.py         # Encriptador básico
│   ├── mnk_encryptor.py         # ✨ Encriptador M×N×A×K
│   └── sdk_generator.py         # Derivación de claves
│
├── utils/
│   ├── audio_extractor.py       # ✨ Extracción sincronizada
│   ├── audio_handler.py         # Manejo de audio
│   └── timer.py                 # Utilidades
│
├── analysis/                    # Scripts de análisis
├── config/                      # Configuración
└── docs/
    ├── MNAK_DOCUMENTATION.md    # ✨ Documentación completa
    └── AUDIO_README.md          # Guía de audio
```

## 🔐 Dimensión K: Sistema Hipercaótico

### Ecuaciones con Retardos Temporales

```
dx/dt = -a·x(t-τ₁) - b·y(t)·z(t)
dy/dt = -x(t) + c·y(t-τ₂) + c·w(t)
dz/dt = d - y²(t) - z(t-τ₃)
dw/dt = x(t) - w(t)
```

**Parámetros:**
- a = 2.0, b = 2.0, c = 0.5, d = 14.5
- τ₁ = 0.12, τ₂ = 0.25, τ₃ = 0.38

**Características:**
- Genera secuencia única de claves por frame
- Cada frame usa K diferente
- Imposible predecir sin conocer estado inicial

## 🎵 Dimensión A: Audio Sincronizado

```
A = sample_rate / fps
Ejemplo: 48000 Hz / 30 fps = 1600 muestras/frame
```

**Sincronización:**
- Frame 0: muestras [0:1600]
- Frame 1: muestras [1600:3200]
- Frame i: muestras [i×A : (i+1)×A]

## 📦 Formato .mnak

```
┌─────────────────────────┐
│ Header (48 bytes)       │
│  - Magic: 'MNAK'        │
│  - M, N, A (uint32)     │
│  - K (4× float64)       │
├─────────────────────────┤
│ Video (M×N×3 bytes)     │
├─────────────────────────┤
│ Audio (A×2 bytes)       │
└─────────────────────────┘

Total: 412,208 bytes/frame
(para M=426, N=320, A=1600)
```

## 💻 Requisitos

```bash
pip install -r requirments.txt
```

Principales dependencias:
- opencv-python
- numpy
- pycryptodome
- moviepy
- scipy
- matplotlib

## 📊 Análisis Criptográfico

```bash
python test.py
```

Genera análisis completo:
- Entropía (aleatoriedad)
- Correlación (estadísticas)
- PSNR, SSIM (calidad)
- NPCR, UACI (análisis diferencial)
- Reporte PDF con resultados

## 🎯 Casos de Uso

### Sistema Original (`main.py`)
✅ Videos sin audio  
✅ Audio no crítico  
✅ Compatibilidad estándar  

### Sistema M×N×A×K (`main_mnak.py`)
✅ Audio debe ser encriptado  
✅ Investigación académica  
✅ Análisis dimensional  
✅ Máxima seguridad  

## 📚 Documentación

- **[MNAK_DOCUMENTATION.md](MNAK_DOCUMENTATION.md)**: Documentación técnica completa
- **[AUDIO_README.md](AUDIO_README.md)**: Guía de manejo de audio
- **[compare_systems.py](compare_systems.py)**: Comparación interactiva

## 🔬 Para Investigadores

El sistema M×N×A×K proporciona:
- ✅ Estructura dimensional explícita
- ✅ Metadata del estado caótico
- ✅ Sincronización audio-video verificable
- ✅ Formato para análisis académico

## ⚙️ Configuración

Edita `config/settings.py`:
```python
VIDEO_INPUT = "data/video_prueba.mp4"
FRAME_WIDTH = 426
FRAME_HEIGHT = 320
FPS = 30
```

## 🛡️ Seguridad

- **AES-256-CFB**: Encriptación simétrica
- **SHA3-256**: Derivación de claves
- **Sistema hipercaótico**: Generación de claves únicas por frame
- **Warmup**: 1000 iteraciones para estabilización

## 📈 Rendimiento

```
Video: 426×320 @ 30fps
Hardware: CPU moderno
Velocidad: ~15-25 frames/s
```

## 🤝 Contribuciones

Este es un proyecto académico de investigación en encriptación de video con sistemas caóticos.

## 📄 Licencia

Proyecto de Grado - VideoEncryptionHyperchaotic

---

**Autor**: Proyecto de Grado  
**Fecha**: 2026  
**Versión**: 2.0 (Sistema M×N×A×K)
