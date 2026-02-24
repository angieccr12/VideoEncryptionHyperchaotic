import numpy as np
from collections import deque
import hashlib

class ChaosKeyGenerator:
    """
    Hyperchaotic time-delay system - genuinely 4D
    """

    def __init__(self, seed=0.1, dt=0.01):
        # Parameters
        self.a = 2.0
        self.b = 2.0
        self.c = 0.5
        self.d = 14.5

        self.dt = dt

        # Delays
        self.tau1 = 0.12
        self.tau2 = 0.25
        self.tau3 = 0.38

        self.delay1 = int(self.tau1 / dt)
        self.delay2 = int(self.tau2 / dt)
        self.delay3 = int(self.tau3 / dt)

        # Derivar 4 condiciones iniciales independientes desde seed
        x0, y0, z0, w0 = self._derive_initial_conditions(seed)

        self.x = x0
        self.y = y0
        self.z = z0
        self.w = w0

        # Delay buffers
        self.x_delay = deque([self.x] * (self.delay1 + 1), maxlen=self.delay1 + 1)
        self.y_delay = deque([self.y] * (self.delay2 + 1), maxlen=self.delay2 + 1)
        self.z_delay = deque([self.z] * (self.delay3 + 1), maxlen=self.delay3 + 1)

    def _derive_initial_conditions(self, seed):
        
        # Convertir seed a bytes de forma determinista
        seed_bytes = str(seed).encode('utf-8')

        # Generar 4 hashes distintos usando salts diferentes
        def hash_to_float(data, salt):
            h = hashlib.sha256(data + salt).digest()
            # Convertir primeros 8 bytes a float en (-2, 2)
            raw = int.from_bytes(h[:8], 'big')
            normalized = raw / (2**64 - 1)  # [0, 1]
            return normalized * 4.0 - 2.0   # [-2, 2]

        x0 = hash_to_float(seed_bytes, b'x_dimension')
        y0 = hash_to_float(seed_bytes, b'y_dimension')
        z0 = hash_to_float(seed_bytes, b'z_dimension')
        w0 = hash_to_float(seed_bytes, b'w_dimension')

        return x0, y0, z0, w0

    def step(self):
        x_tau = self.x_delay[0]
        y_tau = self.y_delay[0]
        z_tau = self.z_delay[0]

        dx = -self.a * x_tau - self.b * self.y * self.z
        dy = -self.x + self.c * y_tau + self.c * self.w
        dz = self.d - self.y**2 - z_tau
        dw = self.x - self.w

        self.x += dx * self.dt
        self.y += dy * self.dt
        self.z += dz * self.dt
        self.w += dw * self.dt

        self.x_delay.append(self.x)
        self.y_delay.append(self.y)
        self.z_delay.append(self.z)

        return self.x, self.y, self.z, self.w