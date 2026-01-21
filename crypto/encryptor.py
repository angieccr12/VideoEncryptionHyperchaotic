# crypto/encryptor.py
import numpy as np

class FrameEncryptor:
    def __init__(self, key_generator):
        self.keygen = key_generator

    def encrypt(self, frame):
        key = self.keygen.generate_key(frame.shape)
        return np.bitwise_xor(frame, key)

    def decrypt(self, encrypted_frame):
        key = self.keygen.generate_key(encrypted_frame.shape)
        return np.bitwise_xor(encrypted_frame, key)
