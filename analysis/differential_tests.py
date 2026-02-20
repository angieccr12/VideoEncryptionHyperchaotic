"""
differential_tests.py
Pruebas diferenciales NPCR y UACI
"""

import numpy as np
import os

def modify_one_pixel(frame):
    """
    Modifica un solo píxel del frame (escenario diferencial).
    Maneja correctamente uint8 sin overflow.
    """
    import numpy as np

    modified = frame.copy()
    x, y = 0, 0

    value = int(modified[x, y])
    modified[x, y] = np.uint8((value + 1) % 256)

    return modified

def load_two_mnak_versions(directory, frame_index=0):
    """
    Carga dos versiones de archivos .mnak para comparación diferencial:
    - Versión original cifrada
    - Versión con 1 píxel modificado cifrada
    
    Args:
        directory: Directorio con archivos .mnak
        frame_index: Índice del frame a comparar
    
    Returns:
        data1: Array de bytes de la versión original cifrada
        data2: Array de bytes de la versión modificada cifrada
        success: Bool indicando si se cargaron correctamente
    """
    # Buscar archivos consecutivos (asumiendo que se cifraron con y sin modificación)
    file1 = os.path.join(directory, f"frame_{frame_index:06d}.mnak")
    file2 = os.path.join(directory, f"frame_{frame_index + 1:06d}.mnak")
    
    if not os.path.exists(file1) or not os.path.exists(file2):
        return None, None, False
    
    # Leer ambos archivos completos
    with open(file1, 'rb') as f:
        data1 = np.frombuffer(f.read(), dtype=np.uint8)
    
    with open(file2, 'rb') as f:
        data2 = np.frombuffer(f.read(), dtype=np.uint8)
    
    # Verificar que tengan el mismo tamaño
    if len(data1) != len(data2):
        return None, None, False
    
    return data1, data2, True


def npcr(img1, img2):
    if img1.shape != img2.shape:
        raise ValueError("NPCR requiere imágenes del mismo tamaño")
    diff = img1 != img2
    return 100.0 * np.sum(diff) / diff.size

def uaci(img1, img2):
    if img1.shape != img2.shape:
        raise ValueError("UACI requiere imágenes del mismo tamaño")
    return 100.0 * np.mean(np.abs(img1.astype(int) - img2.astype(int)) / 255.0)

def npcr_mnak(data1, data2):
    """
    Calcula NPCR para archivos MNAK completos según fórmula [6]:
    NPCR = (Σ D(i,j,a,k)) / (M×N×A×K) × 100%
    
    Donde D(i,j,a,k) = 1 si C1 ≠ C2, 0 en caso contrario
    
    Args:
        data1: Array de bytes del primer archivo .mnak cifrado
        data2: Array de bytes del segundo archivo .mnak cifrado
    
    Returns:
        NPCR en porcentaje
    """
    if len(data1) != len(data2):
        raise ValueError("NPCR requiere archivos del mismo tamaño")
    
    # Comparación elemento por elemento: D(i,j,a,k)
    D = (data1 != data2).astype(int)
    
    # NPCR = Σ D / Total × 100%
    npcr_value = 100.0 * np.sum(D) / len(data1)
    
    return npcr_value

def uaci_mnak(data1, data2):
    """
    Calcula UACI para archivos MNAK completos según:
    UACI = (1/(M×N×A×K)) × Σ |C1(i,j,a,k) - C2(i,j,a,k)| / 255 × 100%
    
    Args:
        data1: Array de bytes del primer archivo .mnak cifrado
        data2: Array de bytes del segundo archivo .mnak cifrado
    
    Returns:
        UACI en porcentaje
    """
    if len(data1) != len(data2):
        raise ValueError("UACI requiere archivos del mismo tamaño")
    
    # Diferencia absoluta normalizada
    diff = np.abs(data1.astype(int) - data2.astype(int))
    
    # UACI = promedio de diferencias / 255 × 100%
    uaci_value = 100.0 * np.mean(diff / 255.0)
    
    return uaci_value
