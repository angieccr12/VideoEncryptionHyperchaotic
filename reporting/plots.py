# reporting/plots.py
"""
plots.py
Funciones de visualización para análisis criptográfico
"""

import matplotlib.pyplot as plt
import numpy as np


def save_histogram(frame, title, path):
    plt.figure()
    plt.hist(frame.flatten(), bins=256, range=(0, 256))
    plt.title(title)
    plt.xlabel("Intensidad")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def save_correlation_plot(frame, title, path):
    x = frame[:, :-1].flatten()
    y = frame[:, 1:].flatten()

    plt.figure()
    plt.scatter(x[:5000], y[:5000], s=1)
    plt.title(title)
    plt.xlabel("Pixel i")
    plt.ylabel("Pixel i+1")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

def save_correlation_plot_mnak(data_array, title, path, sample_size=10000):
    """
    Genera gráfica de correlación para datos MNAK completos (M×N×A×K).
    Muestra correlación entre bytes adyacentes en el archivo cifrado completo.
    
    Args:
        data_array: Array de bytes del archivo .mnak (incluye video + audio + estado caótico)
        title: Título del gráfico
        path: Ruta donde guardar la imagen
        sample_size: Número de muestras a visualizar
    """
    # Bytes en posición i y i+1
    x = data_array[:-1]
    y = data_array[1:]
    
    # Muestreo uniforme y espaciado para mejor visualización
    total_pairs = len(x)
    if total_pairs > sample_size:
        # Muestreo aleatorio uniforme
        np.random.seed(42)  # Reproducibilidad
        indices = np.random.choice(total_pairs, sample_size, replace=False)
        x_sample = x[indices]
        y_sample = y[indices]
    else:
        x_sample = x
        y_sample = y
    
    # Calcular coeficiente de correlación
    correlation_coef = np.corrcoef(x, y)[0, 1]
    
    plt.figure(figsize=(10, 10))
    plt.scatter(x_sample, y_sample, s=0.5, alpha=0.6, c='blue', edgecolors='none')
    plt.title(f"{title}\nCorrelación: {correlation_coef:.6f}", fontsize=12)
    plt.xlabel("Byte en posición i", fontsize=10)
    plt.ylabel("Byte en posición i+1", fontsize=10)
    plt.xlim(-5, 260)
    plt.ylim(-5, 260)
    plt.grid(True, alpha=0.2, linestyle='--')
    
    # Agregar línea de referencia diagonal (correlación perfecta)
    plt.plot([0, 255], [0, 255], 'r--', alpha=0.3, linewidth=0.5, label='Correlación perfecta')
    plt.legend(fontsize=8)
    
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches='tight')
    plt.close()
    
    print(f"  Gráfica de correlación MNAK guardada: {path}")
    print(f"  Total bytes: {len(data_array)}, pares analizados: {total_pairs}, muestras graficadas: {len(x_sample)}")
    print(f"  Coeficiente de correlación: {correlation_coef:.6f} (ideal ≈ 0)")

def save_correlation_heatmap_mnak(data_array, title, path):
    """
    Genera mapa de calor 2D de correlación para datos MNAK completos.
    Muestra la densidad de distribución de bytes adyacentes.
    
    Args:
        data_array: Array de bytes del archivo .mnak
        title: Título del gráfico
        path: Ruta donde guardar la imagen
    """
    x = data_array[:-1]
    y = data_array[1:]
    
    plt.figure(figsize=(10, 10))
    
    # Crear histograma 2D (mapa de calor)
    h, xedges, yedges = np.histogram2d(x, y, bins=256, range=[[0, 256], [0, 256]])
    
    # Normalizar para mejor visualización
    h = h.T  # Transponer para que coincida con la orientación
    
    plt.imshow(h, origin='lower', cmap='hot', interpolation='nearest', 
               extent=[0, 256, 0, 256], aspect='auto')
    plt.colorbar(label='Frecuencia')
    
    plt.title(f"{title}\nMapa de Densidad", fontsize=12)
    plt.xlabel("Byte en posición i", fontsize=10)
    plt.ylabel("Byte en posición i+1", fontsize=10)
    
    # Calcular uniformidad
    mean_freq = np.mean(h)
    std_freq = np.std(h)
    uniformity = std_freq / mean_freq if mean_freq > 0 else 0
    
    plt.text(10, 240, f"Uniformidad: {uniformity:.3f}\n(menor = más uniforme)", 
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8), fontsize=9)
    
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches='tight')
    plt.close()
    
    print(f"  Mapa de calor MNAK guardado: {path}")
    print(f"  Uniformidad: {uniformity:.4f} (ideal < 1.0)")

def save_mnak_distribution_analysis(data_array, title, path_prefix):
    """
    Genera análisis completo de distribución para datos MNAK cifrados.
    Crea múltiples gráficas para verificar uniformidad.
    
    Args:
        data_array: Array de bytes del archivo .mnak cifrado
        title: Título base para las gráficas
        path_prefix: Prefijo de ruta (sin extensión) para guardar gráficas
    """
    # 1. Histograma de frecuencias
    hist, bins = np.histogram(data_array, bins=256, range=(0, 256))
    ideal_freq = len(data_array) / 256
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # Subplot 1: Histograma de distribución de bytes
    axes[0, 0].bar(range(256), hist, width=1.0, color='blue', alpha=0.7)
    axes[0, 0].axhline(y=ideal_freq, color='red', linestyle='--', linewidth=2, label=f'Ideal: {ideal_freq:.1f}')
    axes[0, 0].set_title('Distribución de Valores de Bytes (Histograma)', fontsize=10)
    axes[0, 0].set_xlabel('Valor del byte (0-255)', fontsize=9)
    axes[0, 0].set_ylabel('Frecuencia', fontsize=9)
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(True, alpha=0.3)
    
    # Estadísticas
    mean_freq = hist.mean()
    std_freq = hist.std()
    cv = std_freq / mean_freq if mean_freq > 0 else 0
    chi2 = np.sum((hist - ideal_freq)**2 / ideal_freq)
    
    stats_text = f'Media: {mean_freq:.1f}\nStd: {std_freq:.1f}\nCV: {cv:.4f}\nχ²: {chi2:.1f}'
    axes[0, 0].text(200, hist.max()*0.9, stats_text, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8), fontsize=8)
    
    # Subplot 2: Desviación de la uniformidad
    deviation = hist - ideal_freq
    axes[0, 1].bar(range(256), deviation, width=1.0, color='green', alpha=0.7)
    axes[0, 1].axhline(y=0, color='red', linestyle='-', linewidth=1)
    axes[0, 1].set_title('Desviación de la Distribución Uniforme Ideal', fontsize=10)
    axes[0, 1].set_xlabel('Valor del byte (0-255)', fontsize=9)
    axes[0, 1].set_ylabel('Desviación de la frecuencia ideal', fontsize=9)
    axes[0, 1].grid(True, alpha=0.3)
    
    # Subplot 3: Correlación byte(i) vs byte(i+1) - scatter denso
    x = data_array[:-1]
    y = data_array[1:]
    
    # Histograma 2D para ver densidad real
    h2d, xedges, yedges = np.histogram2d(x, y, bins=256, range=[[0, 256], [0, 256]])
    
    im = axes[1, 0].imshow(h2d.T, origin='lower', cmap='viridis', interpolation='nearest', 
                           extent=[0, 256, 0, 256], aspect='auto', vmin=0)
    axes[1, 0].set_title('Correlación: Byte(i) vs Byte(i+1) - Densidad', fontsize=10)
    axes[1, 0].set_xlabel('Byte en posición i', fontsize=9)
    axes[1, 0].set_ylabel('Byte en posición i+1', fontsize=9)
    plt.colorbar(im, ax=axes[1, 0], label='Frecuencia')
    
    corr_coef = np.corrcoef(x, y)[0, 1]
    axes[1, 0].text(10, 240, f'Corr: {corr_coef:.6f}', 
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8), fontsize=9)
    
    # Subplot 4: Test de runs / autocorrelación visual
    # Tomamos una muestra para ver cambios
    sample = data_array[:10000]
    axes[1, 1].plot(range(len(sample)), sample, linewidth=0.5, alpha=0.8)
    axes[1, 1].set_title('Secuencia de Bytes (primeros 10,000)', fontsize=10)
    axes[1, 1].set_xlabel('Posición', fontsize=9)
    axes[1, 1].set_ylabel('Valor del byte', fontsize=9)
    axes[1, 1].set_ylim(0, 255)
    axes[1, 1].grid(True, alpha=0.3)
    
    # Título general
    fig.suptitle(f'{title}\nAnálisis de Uniformidad y Aleatoriedad', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f"{path_prefix}_analysis.png", dpi=200, bbox_inches='tight')
    plt.close()
    
    print(f"  Análisis completo guardado: {path_prefix}_analysis.png")
    print(f"  Estadísticas: CV={cv:.4f}, χ²={chi2:.2f}, Corr={corr_coef:.6f}")
    
    return {
        'cv': cv,
        'chi2': chi2,
        'correlation': corr_coef,
        'mean_freq': mean_freq,
        'std_freq': std_freq
    }
