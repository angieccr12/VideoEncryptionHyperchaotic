import numpy as np
from Crypto.Hash import SHA3_256

class SDKGenerator:
    """
    Synchronized Dynamic Key Generator (SDKG)
    Chaos → SHA3-256 → 256-bit key material
    """

    def __init__(self, chaos_generator):
        self.chaos = chaos_generator

    def generate(self) -> bytes:
        """
        Returns 32 bytes (256 bits) of dynamic key material
        """
        # Step chaotic system once
        x, y, z, w = self.chaos.step()

        # Convert chaos state to bytes (IEEE-754)
        chaos_state = np.array([x, y, z, w], dtype=np.float64).tobytes()

        # SHA3-256 avalanche
        digest = SHA3_256.new(chaos_state).digest()

        return digest
