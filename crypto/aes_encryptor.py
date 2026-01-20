import numpy as np
from Crypto.Cipher import AES
from crypto.sdk_generator import SDKGenerator

class AESCFBFrameEncryptor:
    """
    AES-CFB frame encryption using SDKG-derived dynamic keys
    """

    def __init__(self, chaos_generator):
        self.sdkg = SDKGenerator(chaos_generator)

    def _derive_key_iv(self):
        """
        Split SDKG output into AES key and IV
        """
        key_material = self.sdkg.generate()

        key = key_material[:16]      # AES-128
        iv  = key_material[16:32]    # 128-bit IV

        return key, iv

    def encrypt(self, frame: np.ndarray) -> np.ndarray:
        key, iv = self._derive_key_iv()
        cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=128)

        encrypted = cipher.encrypt(frame.tobytes())
        return np.frombuffer(encrypted, dtype=np.uint8).reshape(frame.shape)

    def decrypt(self, encrypted_frame: np.ndarray) -> np.ndarray:
        key, iv = self._derive_key_iv()
        cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=128)

        decrypted = cipher.decrypt(encrypted_frame.tobytes())
        return np.frombuffer(decrypted, dtype=np.uint8).reshape(encrypted_frame.shape)
