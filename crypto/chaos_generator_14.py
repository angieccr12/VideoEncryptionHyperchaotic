import numpy as np

class ChaosKeyGenerator:
    """
    4D Hyperchaotic system (NHS) based on:
    Méndez-Ramírez et al., Electronics 2021, 10, 1793
    Discretized via Euler method (Eq. 14 of paper)
    """
    def __init__(self, seed=0.1234):
        # Initial conditions — paper uses x0=y0=z0=w0=1
        self.x = seed
        self.y = seed * 2
        self.z = seed * 3
        self.w = seed * 4

        # System parameters (hyperchaotic regime)
        self.a = 2.0
        self.b = 2.0
        self.c = 0.5
        self.d = 14.5

        # Step size — paper uses τ=0.005 for simulation, τ=0.02 for embedded
        self.tau = 0.005

        # Warm up the system to leave transient behavior
        for _ in range(1000):
            self._euler_step()

    def _euler_step(self):
        """Euler discretization of the NHS (Eq. 14 in paper)"""
        a, b, c, d, tau = self.a, self.b, self.c, self.d, self.tau
        x, y, z, w = self.x, self.y, self.z, self.w

        self.x = x + tau * (-a*x - b*y*z)
        self.y = y + tau * (-x + c*y + c*w)
        self.z = z + tau * (d - y**2 - z)
        self.w = w + tau * (x - w)

    def step(self):
        self._euler_step()
        return self.x, self.y, self.z, self.w

    def generate_key(self, shape):
        self._euler_step()
        chaos = np.array([self.x, self.y, self.z, self.w])
        # Normalize to [0, 255]
        chaos = np.abs(np.sin(chaos * 1e4))  # escala para más variación
        key = np.tile(chaos.mean(), shape)
        return (key * 255).astype(np.uint8)