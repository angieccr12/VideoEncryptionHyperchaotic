import numpy as np
import wave
import subprocess
import os
from scipy.io import wavfile


class AudioExtractor:
    
    def __init__(self, video_path, fps=30):
        self.video_path = video_path
        self.fps = fps
        self.audio_data = None
        self.sample_rate = None
        self.samples_per_frame = 0
        
    def extract_audio_to_wav(self, output_wav="data/temp_audio.wav"):
        try:
            from moviepy.editor import VideoFileClip
            
            video = VideoFileClip(self.video_path)
            
            if video.audio is None:
                print("El video no tiene audio")
                video.close()
                return None
            
            video.audio.write_audiofile(output_wav, verbose=False, logger=None)
            video.close()
            
            print(f"Audio extraido: {output_wav}")
            return output_wav
            
        except Exception as e:
            print(f"Error extrayendo audio: {e}")
            return None
    
    def load_audio_data(self, wav_path):
        try:
            self.sample_rate, self.audio_data = wavfile.read(wav_path)
            
            if len(self.audio_data.shape) > 1:
                self.audio_data = np.mean(self.audio_data, axis=1).astype(self.audio_data.dtype)
            
            self.samples_per_frame = int(self.sample_rate / self.fps)
            
            print(f"Audio cargado: {self.sample_rate}Hz, {self.samples_per_frame} muestras/frame")
            
            return True
            
        except Exception as e:
            print(f"Error cargando audio: {e}")
            return False
    
    def get_audio_chunk_for_frame(self, frame_index):
        if self.audio_data is None:
            return None
        
        start_sample = frame_index * self.samples_per_frame
        end_sample = start_sample + self.samples_per_frame
        
        if start_sample >= len(self.audio_data):
            return np.zeros(self.samples_per_frame, dtype=self.audio_data.dtype)
        
        if end_sample > len(self.audio_data):
            chunk = self.audio_data[start_sample:]
            padding = np.zeros(end_sample - len(self.audio_data), dtype=self.audio_data.dtype)
            return np.concatenate([chunk, padding])
        
        return self.audio_data[start_sample:end_sample]
    
    def reconstruct_audio_from_chunks(self, audio_chunks, output_wav="data/reconstructed_audio.wav"):
        try:
            full_audio = np.concatenate([chunk for chunk in audio_chunks if chunk is not None])
            wavfile.write(output_wav, self.sample_rate, full_audio.astype(np.int16))
            print(f"Audio reconstruido: {output_wav}")
            return output_wav
        except Exception as e:
            print(f"Error reconstruyendo audio: {e}")
            return None
    
    def get_dimensions(self):
        return {
            'A': self.samples_per_frame,
            'sample_rate': self.sample_rate,
            'total_samples': len(self.audio_data) if self.audio_data is not None else 0
        }
