# analysis/entropy_tests.py
import numpy as np

def entropy_global(frames, audio_dim=None, key_dim=None):
    """
    Calcula la entropía de Shannon global según la fórmula:
    H(X) = -Σ(ni/(M×N×A×K)) * log2(ni/(M×N×A×K))
    
    Args:
        frames: Lista de frames (M×N cada uno)
        audio_dim: Dimensión A del audio sincronizado (opcional)
        key_dim: Dimensión K de la clave dinámica/parámetros (opcional)
    
    Returns:
        Entropía en bits
    """
    # Concatenar todos los frames en un solo array
    data = np.concatenate([f.flatten() for f in frames])
    
    # M×N×frames (total de píxeles)
    total_elements = len(data)
    
    # Multiplicar por dimensiones adicionales si se proporcionan
    denominator = total_elements
    if audio_dim is not None and audio_dim > 0:
        denominator *= audio_dim
    if key_dim is not None and key_dim > 0:
        denominator *= key_dim
    
    # Contar frecuencias absolutas (ni) para cada valor xi
    unique_values, counts = np.unique(data, return_counts=True)
    
    # Calcular entropía usando log2 según fórmula [4]
    # H(X) = -Σ P(xi) * log2(P(xi)) donde P(xi) = ni/(M×N×A×K)
    H = 0.0
    for ni in counts:
        P_xi = ni / denominator  # P(xi) = ni/(M×N×A×K)
        if P_xi > 0:
            H -= P_xi * np.log2(P_xi)
    
    return H

def entropy_per_frame(frames, audio_dim=None, key_dim=None):
    """
    Calcula la entropía promedio por frame usando la misma fórmula de Shannon.
    
    Args:
        frames: Lista de frames
        audio_dim: Dimensión A del audio (opcional)
        key_dim: Dimensión K de la clave dinámica (opcional)
    
    Returns:
        Entropía promedio en bits
    """
    values = []
    for f in frames:
        data = f.flatten()
        
        # M×N (píxeles del frame)
        total_elements = len(data)
        
        # Multiplicar por dimensiones adicionales
        denominator = total_elements
        if audio_dim is not None and audio_dim > 0:
            denominator *= audio_dim
        if key_dim is not None and key_dim > 0:
            denominator *= key_dim
        
        # Frecuencias absolutas
        unique_values, counts = np.unique(data, return_counts=True)
        
        # Calcular entropía con log2
        H = 0.0
        for ni in counts:
            P_xi = ni / denominator
            if P_xi > 0:
                H -= P_xi * np.log2(P_xi)
        
        values.append(H)
    
    return float(np.mean(values))

def entropy_mnak_global(data_arrays, dimensions):
    """
    Calcula la entropía de Shannon para archivos MNAK completos (M×N×A×K).
    Incluye todos los datos cifrados: frames, audio y estado caótico.
    
    Args:
        data_arrays: Lista de arrays de bytes cifrados (del archivo .mnak completo)
        dimensions: Dict con dimensiones {M, N, A, K, total_frames}
    
    Returns:
        Entropía en bits calculada sobre el volumen total M×N×A×K
    """
    # Concatenar todos los archivos .mnak en un solo array
    all_data = np.concatenate([arr for arr in data_arrays])
    
    # Total de bytes cifrados
    total_bytes = len(all_data)
    
    # Contar frecuencias absolutas (ni) de cada valor (0-255)
    unique_values, counts = np.unique(all_data, return_counts=True)
    
    # Calcular entropía con log2 según fórmula [4]
    # H(X) = -Σ(ni/Total) * log2(ni/Total)
    # donde Total = M×N×A×K para todos los frames
    H = 0.0
    for ni in counts:
        P_xi = ni / total_bytes
        if P_xi > 0:
            H -= P_xi * np.log2(P_xi)
    
    # Información adicional sobre las dimensiones
    M = dimensions.get('M', 0)
    N = dimensions.get('N', 0)
    A = dimensions.get('A', 0)
    K = dimensions.get('K', 0)
    frames = dimensions.get('total_frames', 1)
    
    theoretical_total = M * N * 3 * frames  # píxeles RGB
    if A > 0:
        theoretical_total += A * 2 * frames  # audio int16
    theoretical_total += K * frames  # estado caótico
    theoretical_total += 48 * frames  # headers
    
    print(f"  Total bytes analizados: {total_bytes}")
    print(f"  Volumen teórico M×N×A×K: {theoretical_total}")
    print(f"  Composición: {frames} frames × (M={M}, N={N}, A={A}, K={K})")
    
    return H
