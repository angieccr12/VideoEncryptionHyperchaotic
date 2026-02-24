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

    def _derive_key_nonce_from_chaos(self, chaos_state):
        """
        Deriva una clave AES-128 (16 bytes) y un nonce de 8 bytes para AES-CTR.
        AES-CTR en PyCryptodome con nonce de 8 bytes usa un contador de 64 bits,
        lo que da un keystream máximo de 2^64 bloques (suficiente para cualquier frame).
        """
        chaos_bytes = np.array(chaos_state, dtype=np.float64).tobytes()
        frame_bytes = struct.pack('<Q', self.frame_count)
        hash_material = chaos_bytes + frame_bytes
        key_material = SHA3_256.new(hash_material).digest()
        key   = key_material[:16]   # 128-bit key
        nonce = key_material[16:24] # 64-bit nonce (el resto lo usa como contador inicial = 0)
        return key, nonce

    # ── Permutación de píxeles ─────────────────────────────────────────────────

    def _derive_permutation(self, chaos_state, n_pixels):
        """Genera un índice de permutación determinista a partir del estado caótico."""
        seed_bytes = np.array(chaos_state, dtype=np.float64).tobytes()
        seed_int = int.from_bytes(SHA3_256.new(seed_bytes).digest(), 'little')
        rng = np.random.default_rng(seed_int % (2**32))
        return rng.permutation(n_pixels)

    def _permute_pixels(self, frame, chaos_state):
        """Aplana el frame, permuta los píxeles y reconstruye la forma original."""
        M, N, C = frame.shape
        flat = frame.reshape(M * N, C)
        perm = self._derive_permutation(chaos_state, M * N)
        return flat[perm].reshape(M, N, C)

    def _unpermute_pixels(self, frame, chaos_state):
        """Invierte la permutación aplicada por _permute_pixels."""
        M, N, C = frame.shape
        flat = frame.reshape(M * N, C)
        perm = self._derive_permutation(chaos_state, M * N)
        inv_perm = np.empty_like(perm)
        inv_perm[perm] = np.arange(M * N)
        return flat[inv_perm].reshape(M, N, C)

    # ── Serialización / deserialización MNAK ──────────────────────────────────

    def _serialize_mnak(self, frame, audio_chunk, chaos_state):
        M, N, channels = frame.shape
        A = len(audio_chunk) if audio_chunk is not None else 0
        header = bytearray()
        header.extend(b'MNAK')
        header.extend(struct.pack('<I', M))
        header.extend(struct.pack('<I', N))
        header.extend(struct.pack('<I', A))
        header.extend(np.array(chaos_state, dtype=np.float64).tobytes())
        frame_bytes = frame.tobytes()
        audio_bytes = audio_chunk.tobytes() if (audio_chunk is not None and len(audio_chunk) > 0) else b''
        return bytes(header) + frame_bytes + audio_bytes

    def _deserialize_mnak(self, data_bytes):
        magic = data_bytes[0:4]
        if magic != b'MNAK':
            raise ValueError(f"Magic number inválido: {magic}")
        M = struct.unpack('<I', data_bytes[4:8])[0]
        N = struct.unpack('<I', data_bytes[8:12])[0]
        A = struct.unpack('<I', data_bytes[12:16])[0]
        chaos_state = tuple(np.frombuffer(data_bytes[16:48], dtype=np.float64))
        frame_size  = M * N * 3
        frame_start = 48
        frame_end   = frame_start + frame_size
        frame = np.frombuffer(data_bytes[frame_start:frame_end], dtype=np.uint8).reshape((M, N, 3))
        if A > 0:
            audio_bytes = data_bytes[frame_end:frame_end + A * 2]
            audio_chunk = np.frombuffer(audio_bytes, dtype=np.int16)
        else:
            audio_chunk = None
        return frame, audio_chunk, chaos_state, M, N, A

    # ── Cifrado / descifrado ───────────────────────────────────────────────────

    def encrypt(self, frame, audio_chunk=None):
        chaos_state = self._get_chaos_state()

        # Permutar píxeles antes de serializar
        permuted_frame = self._permute_pixels(frame, chaos_state)

        plaintext = self._serialize_mnak(permuted_frame, audio_chunk, chaos_state)

        key, nonce = self._derive_key_nonce_from_chaos(chaos_state)
        # AES-CTR: nonce de 8 bytes → contador de 64 bits, initial_value=0
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        return cipher.encrypt(plaintext)

    def decrypt(self, ciphertext):
        chaos_state = self._get_chaos_state()

        key, nonce = self._derive_key_nonce_from_chaos(chaos_state)
        # Mismo nonce y clave → mismo keystream
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)

        frame, audio_chunk, stored_chaos_state, M, N, A = self._deserialize_mnak(plaintext)

        # Revertir permutación tras deserializar
        frame = self._unpermute_pixels(frame, chaos_state)

        # Verificación de integridad del estado caótico
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