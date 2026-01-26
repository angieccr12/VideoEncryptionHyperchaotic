# 📐 Sistema de Encriptación M×N×A×K

## 🎯 Descripción General

Sistema de encriptación de video que trabaja con una estructura multidimensional **M×N×A×K**:

- **M**: Ancho del frame (píxeles) - Dimensión espacial horizontal
- **N**: Alto del frame (píxeles) - Dimensión espacial vertical  
- **A**: Audio sincronizado (muestras por frame) - Dimensión temporal de audio
- **K**: Estado del sistema hipercaótico - Dimensión de clave dinámica

## 📊 Estructura de Dimensiones

### Representación Matemática

```
Video = {Frame₁, Frame₂, ..., Frameₜ}

Donde cada Frameᵢ:
  Frameᵢ = (Vᵢ, Aᵢ, Kᵢ)
  
  Vᵢ: Video    → M × N × 3 (RGB)
  Aᵢ: Audio    → A (muestras de audio)
  Kᵢ: Caos     → (xᵢ, yᵢ, zᵢ, wᵢ) ∈ ℝ⁴
```

### Dimensiones por Defecto

```python
M = 426  # píxeles (ancho)
N = 320  # píxeles (alto)
A = 1600 # muestras (para 48kHz audio @ 30fps: 48000/30 = 1600)
K = ℝ⁴   # espacio de estados (x, y, z, w)
```

## 🔐 Dimensión K: Sistema Hipercaótico

### Definición

K representa el **estado del sistema caótico** en el tiempo:

```
K(t) = (x(t), y(t), z(t), w(t)) ∈ ℝ⁴
```

### Sistema de Ecuaciones con Retardos

```
dx/dt = -a·x(t-τ₁) - b·y(t)·z(t)
dy/dt = -x(t) + c·y(t-τ₂) + c·w(t)
dz/dt = d - y²(t) - z(t-τ₃)
dw/dt = x(t) - w(t)
```

Donde:
- **a = 2.0, b = 2.0, c = 0.5, d = 14.5** (parámetros del sistema)
- **τ₁ = 0.12, τ₂ = 0.25, τ₃ = 0.38** (retardos temporales)

### Evolución Temporal

Para cada frame i, el sistema evoluciona:

```
K₀ → K₁ → K₂ → ... → Kᵢ → ...

Kᵢ₊₁ = f(Kᵢ, Kᵢ₋τ₁, Kᵢ₋τ₂, Kᵢ₋τ₃)
```

Esto genera una **secuencia única** de claves AES, una por frame.

## 🎵 Dimensión A: Audio Sincronizado

### Extracción Frame-Sincronizada

Para video a `fps` frames por segundo y audio a `sample_rate` Hz:

```
A = sample_rate / fps

Ejemplo: 48000 Hz / 30 fps = 1600 muestras/frame
```

### Sincronización

```python
Frame₀: samples[0:1600]
Frame₁: samples[1600:3200]
Frame₂: samples[3200:4800]
...
Frameᵢ: samples[i*A : (i+1)*A]
```

### Formato

- **Tipo**: `int16` (audio PCM de 16 bits)
- **Canales**: Mono (convertido si es estéreo)
- **Tamaño**: A muestras × 2 bytes = 3200 bytes/frame (para A=1600)

## 📦 Formato de Datos Encriptados (.mnak)

### Estructura del Archivo

```
┌─────────────────────────────────────┐
│ HEADER (48 bytes)                   │
├─────────────────────────────────────┤
│ Magic: 'MNAK' (4 bytes)            │
│ M: uint32 (4 bytes)                │
│ N: uint32 (4 bytes)                │
│ A: uint32 (4 bytes)                │
│ K: float64[4] (32 bytes)           │
│   - x: float64 (8 bytes)           │
│   - y: float64 (8 bytes)           │
│   - z: float64 (8 bytes)           │
│   - w: float64 (8 bytes)           │
├─────────────────────────────────────┤
│ VIDEO DATA                          │
│ M × N × 3 bytes                     │
│ (frame RGB serializado)             │
├─────────────────────────────────────┤
│ AUDIO DATA                          │
│ A × 2 bytes                         │
│ (audio int16 serializado)           │
└─────────────────────────────────────┘

Total por frame:
  48 + (M×N×3) + (A×2) bytes
  = 48 + 408,960 + 3,200
  = 412,208 bytes (ejemplo: 426×320, A=1600)
```

### Encriptación

Todo el contenido (header + video + audio) se encripta con **AES-256-CFB**:

```python
clave_AES = SHA3-256(K || frame_counter)
iv_AES = SHA3-256(K || frame_counter)[16:32]

encrypted = AES-CFB(plaintext, clave_AES, iv_AES)
```

## 🚀 Uso del Sistema

### Ejecución Básica

```bash
python main_mnak.py
```

### Proceso Automático

1. **Extrae audio** → Dimensión A
2. **Inicializa sistema caótico** → Dimensión K
3. **Procesa cada frame**:
   - Toma frame i (M×N×3)
   - Toma audio chunk i (A)
   - Genera estado caótico Kᵢ
   - Encripta todo junto → archivo .mnak
   - Desencripta para verificación
4. **Reconstruye audio** desde chunks desencriptados
5. **Combina video + audio** → resultado final

### Archivos Generados

```
data/
├── encrypted_video.mp4          # Video cifrado (visual, sin audio)
├── decrypted_video.mp4          # Video descifrado (con audio)
└── encrypted_frames/            # Frames encriptados individuales
    ├── frame_000000.mnak        # Frame 0 (M×N×A×K encriptado)
    ├── frame_000001.mnak        # Frame 1
    └── ...
```

## 🔍 Verificación de Dimensiones

### Script de Análisis

```bash
python verify_mnak_dimensions.py
```

Verifica:
- ✅ Dimensiones M, N correctas
- ✅ Dimensión A sincronizada
- ✅ Evolución de dimensión K
- ✅ Integridad de encriptación/desencriptación

## 🔐 Seguridad

### Espacios de Claves

```
Espacio total = M × N × A × K

M: 426 píxeles
N: 320 píxeles  
A: 1600 muestras
K: ℝ⁴ (continuo, 4D)
```

### Características de Seguridad

1. **Clave dinámica K**:
   - Cada frame usa una clave AES diferente
   - Derivada del estado caótico hipercaótico
   - Imposible predecir sin conocer K₀ y parámetros

2. **Sincronización A**:
   - Audio encriptado junto con video
   - Imposible separar sin desencriptar

3. **Integridad**:
   - Estado K almacenado en cada frame
   - Permite verificación de sincronización

## 📈 Comparación con Sistema Original

| Característica | Sistema Original | Sistema M×N×A×K |
|----------------|------------------|-----------------|
| **Video** | M × N × 3 | M × N × 3 |
| **Audio** | ❌ Separado | ✅ Integrado (A) |
| **Clave** | ❌ Implícita | ✅ Explícita (K) |
| **Formato** | .mp4 estándar | .mnak custom |
| **Verificación** | ❌ No incluida | ✅ Estado K guardado |
| **Seguridad** | Alta | Muy alta |

## 🎓 Información Técnica

### Complejidad Computacional

- **Encriptación**: O(M·N + A) por frame
- **AES-CFB**: Lineal en tamaño de datos
- **Sistema caótico**: O(1) por iteración

### Rendimiento Típico

```
Video: 426×320 @ 30fps
Audio: 48kHz, 16-bit mono
Hardware: CPU moderno

Velocidad: ~15-25 frames/s
Tiempo: ~4-6 minutos para video de 2 minutos
```

## ⚠️ Notas Importantes

1. **Sincronización crítica**: Encriptador y desencriptador deben usar:
   - Misma semilla K₀
   - Mismo número de iteraciones de warmup
   - Mismo orden de procesamiento de frames

2. **Archivos .mnak**: Formato propietario, no reproducible en players estándar

3. **Audio**: Solo el video desencriptado final (.mp4) tiene audio audible

## 📚 Referencias

- Sistema hipercaótico: Basado en sistemas de Lorenz con retardos
- AES-CFB: NIST FIPS 197
- SHA3-256: NIST FIPS 202
