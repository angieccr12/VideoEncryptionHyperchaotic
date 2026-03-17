import numpy as np

class ChaosKeyGenerator:
    """
    Discrete Lorenz–Stenflo inspired chaotic system
    """
    def __init__(self, seed=0.1234):
        self.x, self.y, self.z, self.w = seed, seed*2, seed*3, seed*4

    def step(self):
        a, b, c, d = 11.0, 2.9, 5.0, 23.0
        self.x = a * (self.y - self.x) + self.z
        self.y = d * self.x - self.y - self.x * self.w
        self.z = -c * self.x - self.z
        self.w = self.x * self.y - b * self.w
        return self.x, self.y, self.z, self.w

    def generate_key(self, shape):
        self.step()
        chaos = np.array([self.x, self.y, self.z, self.w])
        chaos = np.abs(np.sin(chaos))
        key = np.tile(chaos.mean(), shape)
        return (key * 255).astype(np.uint8)
