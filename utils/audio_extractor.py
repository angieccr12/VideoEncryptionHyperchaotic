"""
audio_extractor.py
Extrae y sincroniza audio frame por frame (dimensión A)
"""
import numpy as np
import wave
import subprocess
import os
from scipy.io import wavfile


class AudioExtractor:
    """
    Extrae audio de video y lo sincroniza frame a frame
    """
    
    def __init__(self, video_path, fps=30):
        """
        Args:
            video_path: Ruta al archivo de video
            fps: Frames por segundo del video
        """
        self.video_path = video_path
        self.fps = fps
        self.audio_data = None
        self.sample_rate = None
        self.samples_per_frame = 0
        
    def extract_audio_to_wav(self, output_wav="data/temp_audio.wav"):
        """
        Extrae audio del video a formato WAV usando moviepy
        
        Returns:
            str: Ruta al archivo WAV o None si no hay audio
        """
        try:
            from moviepy.editor import VideoFileClip
            
            video = VideoFileClip(self.video_path)
            
            if video.audio is None:
                print("⚠️ El video no tiene audio")
                video.close()
                return None
            
            # Extraer audio a WAV
            video.audio.write_audiofile(output_wav, verbose=False, logger=None)
            video.close()
            
            print(f"✅ Audio extraído: {output_wav}")
            return output_wav
            
        except Exception as e:
            print(f"❌ Error extrayendo audio: {e}")
            return None
    
    def load_audio_data(self, wav_path):
        """
        Carga datos de audio desde archivo WAV
        
        Args:
            wav_path: Ruta al archivo WAV
            
        Returns:
            bool: True si se cargó correctamente
        """
        try:
            self.sample_rate, self.audio_data = wavfile.read(wav_path)
            
            # Si es estéreo, convertir a mono (promedio de canales)
            if len(self.audio_data.shape) > 1:
                self.audio_data = np.mean(self.audio_data, axis=1).astype(self.audio_data.dtype)
            
            # Calcular muestras por frame
            self.samples_per_frame = int(self.sample_rate / self.fps)
            
            print(f"📊 Audio cargado:")
            print(f"   - Sample rate: {self.sample_rate} Hz")
            print(f"   - Muestras totales: {len(self.audio_data)}")
            print(f"   - Muestras por frame: {self.samples_per_frame}")
            print(f"   - Duración: {len(self.audio_data) / self.sample_rate:.2f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Error cargando audio: {e}")
            return False
    
    def get_audio_chunk_for_frame(self, frame_index):
        """
        Obtiene el chunk de audio correspondiente a un frame específico
        
        Args:
            frame_index: Índice del frame (0-based)
            
        Returns:
            numpy.ndarray: Array de muestras de audio (dimensión A) o None
        """
        if self.audio_data is None:
            return None
        
        start_sample = frame_index * self.samples_per_frame
        end_sample = start_sample + self.samples_per_frame
        
        # Si nos pasamos del final, rellenar con ceros
        if start_sample >= len(self.audio_data):
            return np.zeros(self.samples_per_frame, dtype=self.audio_data.dtype)
        
        if end_sample > len(self.audio_data):
            # Rellenar con ceros al final
            chunk = self.audio_data[start_sample:]
            padding = np.zeros(end_sample - len(self.audio_data), dtype=self.audio_data.dtype)
            return np.concatenate([chunk, padding])
        
        return self.audio_data[start_sample:end_sample]
    
    def reconstruct_audio_from_chunks(self, audio_chunks, output_wav="data/reconstructed_audio.wav"):
        """
        Reconstruye un archivo de audio desde chunks frame a frame
        
        Args:
            audio_chunks: Lista de numpy arrays (uno por frame)
            output_wav: Ruta de salida
            
        Returns:
            str: Ruta al archivo WAV reconstruido
        """
        try:
            # Concatenar todos los chunks
            full_audio = np.concatenate([chunk for chunk in audio_chunks if chunk is not None])
            
            # Guardar como WAV
            wavfile.write(output_wav, self.sample_rate, full_audio.astype(np.int16))
            
            print(f"✅ Audio reconstruido: {output_wav}")
            return output_wav
            
        except Exception as e:
            print(f"❌ Error reconstruyendo audio: {e}")
            return None
    
    def get_dimensions(self):
        """
        Retorna las dimensiones de audio (A)
        
        Returns:
            dict: Información de dimensiones
        """
        return {
            'A': self.samples_per_frame,
            'sample_rate': self.sample_rate,
            'total_samples': len(self.audio_data) if self.audio_data is not None else 0
        }
