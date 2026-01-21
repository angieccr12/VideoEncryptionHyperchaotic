import numpy as np
from Crypto.Hash import SHA3_256

class SDKGenerator:
    def __init__(self, chaos_generator):
        self.chaos = chaos_generator

    def generate(self) -> bytes:
        x, y, z, w = self.chaos.step()
        chaos_state = np.array([x, y, z, w], dtype=np.float64).tobytes()
        return SHA3_256.new(chaos_state).digest()
