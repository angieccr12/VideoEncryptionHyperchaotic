import numpy as np
from Crypto.Cipher import AES
from Crypto.Hash import SHA3_256
import struct


class MNAKFrameEncryptor:
    def __init__(self, chaos_generator, audio_samples_per_frame=0):
        self.chaos = chaos_generator
        self.audio_samples_per_frame = audio_samples_per_frame
        self.frame_count = 0
        
    def _get_chaos_state(self):
        x, y, z, w = self.chaos.step()
        self.frame_count += 1
        return (x, y, z, w)
    
    def _derive_key_iv_from_chaos(self, chaos_state):
        # Serializar estado caótico a bytes
        chaos_bytes = np.array(chaos_state, dtype=np.float64).tobytes()
        
        # Agregar contador de frame para mayor entropía
        frame_bytes = struct.pack('<Q', self.frame_count)
        
        # Hash SHA3-256 del estado caótico + contador
        hash_material = chaos_bytes + frame_bytes
        key_material = SHA3_256.new(hash_material).digest()
        
        # Primeros 16 bytes = key, siguientes 16 bytes = IV
        return key_material[:16], key_material[16:32]
    
    def _serialize_mnak(self, frame, audio_chunk, chaos_state):
        # Dimensiones
        M, N, channels = frame.shape
        A = len(audio_chunk) if audio_chunk is not None else 0
        # header (4 + 4 + 4 + 4 + 32 bytes)  
        header = bytearray()
        header.extend(b'MNAK')  # Magic number
        header.extend(struct.pack('<I', M))
        header.extend(struct.pack('<I', N))
        header.extend(struct.pack('<I', A))
        header.extend(np.array(chaos_state, dtype=np.float64).tobytes())
        
        # Datos del frame (M×N×3 bytes)
        frame_bytes = frame.tobytes()
        
        # Datos de audio (A bytes si audio es int16, o A*4 si float32)
        if audio_chunk is not None and len(audio_chunk) > 0:
            audio_bytes = audio_chunk.tobytes()
        else:
            audio_bytes = b''
        
        # Concatenar todo
        return bytes(header) + frame_bytes + audio_bytes
    
    def _deserialize_mnak(self, data_bytes):

        # Leer header (48 bytes)
        magic = data_bytes[0:4]
        if magic != b'MNAK':
            raise ValueError(f"Magic number inválido: {magic}")
        
        M = struct.unpack('<I', data_bytes[4:8])[0]
        N = struct.unpack('<I', data_bytes[8:12])[0]
        A = struct.unpack('<I', data_bytes[12:16])[0]
        
        chaos_state = np.frombuffer(data_bytes[16:48], dtype=np.float64)
        chaos_state = tuple(chaos_state)
        
        # Leer frame (después del header)
        frame_size = M * N * 3
        frame_start = 48
        frame_end = frame_start + frame_size
        frame_bytes = data_bytes[frame_start:frame_end]
        frame = np.frombuffer(frame_bytes, dtype=np.uint8).reshape((M, N, 3))
        
        # Leer audio (después del frame)
        if A > 0:
            audio_start = frame_end
            audio_end = audio_start + A * 2  # int16 = 2 bytes por muestra
            audio_bytes = data_bytes[audio_start:audio_end]
            audio_chunk = np.frombuffer(audio_bytes, dtype=np.int16)
        else:
            audio_chunk = None
        
        return frame, audio_chunk, chaos_state, M, N, A
    
    def encrypt(self, frame, audio_chunk=None):

        # Obtener estado caótico actual (dimensión K)
        chaos_state = self._get_chaos_state()
        
        # Serializar M×N×A×K a bytes
        plaintext = self._serialize_mnak(frame, audio_chunk, chaos_state)
        
        # Derivar clave e IV desde K
        key, iv = self._derive_key_iv_from_chaos(chaos_state)
        
        # Encriptar con AES-CFB
        cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=128)
        ciphertext = cipher.encrypt(plaintext)
        
        return ciphertext
    
    def decrypt(self, ciphertext):

        # Obtener estado caótico actual (debe estar sincronizado con encriptación)
        chaos_state = self._get_chaos_state()
        
        # Derivar la misma clave e IV
        key, iv = self._derive_key_iv_from_chaos(chaos_state)
        
        # Desencriptar
        cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=128)
        plaintext = cipher.decrypt(ciphertext)
        
        # Deserializar M×N×A×K
        frame, audio_chunk, stored_chaos_state, M, N, A = self._deserialize_mnak(plaintext)
        
        # Verificar que el estado caótico coincida (validación de integridad)
        chaos_diff = np.array(chaos_state) - np.array(stored_chaos_state)
        if np.max(np.abs(chaos_diff)) > 1e-6:
            print(f"Advertencia: Estado caótico no coincide en frame {self.frame_count}")
            print(f"Esperado: {chaos_state}")
            print(f"Obtenido: {stored_chaos_state}")
        
        return frame, audio_chunk
    
    def get_state_info(self):
        return {
            'frame_count': self.frame_count,
            'audio_samples_per_frame': self.audio_samples_per_frame,
            'chaos_state': self.chaos.step() if hasattr(self.chaos, 'step') else None
        }
