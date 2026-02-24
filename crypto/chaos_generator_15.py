import numpy as np

class ChaosKeyGenerator:
    """
    Discrete Lorenz–Stenflo inspired chaotic system
    """
    def __init__(self, seed=0.1234):
        self.x, self.y, self.z, self.w = seed, seed*2, seed*3, seed*4

    def step(self):
        a, b, c, d, r, q, k = 20, 32, 3, 1, -1, 1, -1
        self.x = a * (self.y - self.x) + r * self.w
        self.y = b * self.x - self.x * self.z - self.y * q
        self.z = self.x * self.y - c * self.z
        self.w = d * self.x * self.y - k * self.w
        return self.x, self.y, self.z, self.w

    def generate_key(self, shape):
        self.step()
        chaos = np.array([self.x, self.y, self.z, self.w])
        chaos = np.abs(np.sin(chaos))
        key = np.tile(chaos.mean(), shape)
        return (key * 255).astype(np.uint8)
