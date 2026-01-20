import numpy as np
from collections import deque

class ChaosKeyGenerator:
    """
    Hyperchaotic time-delay system (4D)
    """

    def __init__(self, seed=0.1234, dt=0.01):
        # Parámetros del sistema
        self.a = 2.0
        self.b = 2.0
        self.c = 0.5
        self.d = 14.5

        self.tau1 = 0.12
        self.tau2 = 0.25
        self.tau3 = 0.38

        self.dt = dt

        # Estados iniciales
        self.x = seed
        self.y = seed * 2
        self.z = seed * 3
        self.w = seed * 4

        # Longitud de memoria para retardos
        self.n1 = int(self.tau1 / dt)
        self.n2 = int(self.tau2 / dt)
        self.n3 = int(self.tau3 / dt)

        # Buffers de historial
        self.x_hist = deque([self.x] * (self.n1 + 1), maxlen=self.n1 + 1)
        self.y_hist = deque([self.y] * (self.n2 + 1), maxlen=self.n2 + 1)
        self.z_hist = deque([self.z] * (self.n3 + 1), maxlen=self.n3 + 1)

    def step(self):
        # Valores retardados
        x_tau1 = self.x_hist[0]
        y_tau2 = self.y_hist[0]
        z_tau3 = self.z_hist[0]

        # Ecuaciones diferenciales discretizadas (Euler)
        dx = -self.a * x_tau1 - self.b * self.y * self.z
        dy = -self.x + self.c * y_tau2 + self.c * self.w
        dz = self.d - self.y**2 - z_tau3
        dw = self.x - self.w

        # Actualización de estados
        self.x += self.dt * dx
        self.y += self.dt * dy
        self.z += self.dt * dz
        self.w += self.dt * dw

        # Actualizar historial
        self.x_hist.append(self.x)
        self.y_hist.append(self.y)
        self.z_hist.append(self.z)

        return self.x, self.y, self.z, self.w

    def generate_key(self, shape, discard=100):
        # Transitorio
        for _ in range(discard):
            self.step()

        self.step()
        chaos = np.array([self.x, self.y, self.z, self.w])
        chaos = np.abs(np.sin(chaos))
        key = np.tile(chaos.mean(), shape)

        return (key * 255).astype(np.uint8)
