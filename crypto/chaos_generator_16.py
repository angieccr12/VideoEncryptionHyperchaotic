import numpy as np

class ChaosKeyGenerator:
    """
    4D Hyperchaotic Lorenz-Stenflo system with Euler discretization
    """
    def __init__(self, seed=0.1234):
        self.x = seed
        self.y = seed * 2
        self.z = seed * 3
        self.w = seed * 4

        self.a = 40.0
        self.b = 2.0
        self.c = 22.0
        self.d = 0.0
        self.e = 0.5
        self.tau = 0.001  # paso pequeño, este sistema diverge fácil

        # Warm up
        for _ in range(1000):
            self._euler_step()

    def _euler_step(self):
        a, b, c, d, e, tau = self.a, self.b, self.c, self.d, self.e, self.tau
        x, y, z, w = self.x, self.y, self.z, self.w

        self.x = x + tau * (a * (y - x))
        self.y = y + tau * (c * y - x * z + w)
        self.z = z + tau * (-b * z + y**2)
        self.w = w + tau * (-e * (x + y))

    def step(self):
        self._euler_step()
        return self.x, self.y, self.z, self.w

    def generate_key(self, shape):
        self._euler_step()
        chaos = np.array([self.x, self.y, self.z, self.w])
        chaos = np.abs(np.sin(chaos * 1e4))
        key = np.tile(chaos.mean(), shape)
        return (key * 255).astype(np.uint8)