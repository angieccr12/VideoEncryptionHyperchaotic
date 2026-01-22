import numpy as np
from collections import deque

class ChaosKeyGenerator:
    """
    Hyperchaotic time-delay system
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

        # Initial conditions
        self.x = seed
        self.y = seed * 1.2
        self.z = seed * 1.5
        self.w = seed * 2.0

        # Delay buffers
        self.x_delay = deque([self.x] * (self.delay1 + 1), maxlen=self.delay1 + 1)
        self.y_delay = deque([self.y] * (self.delay2 + 1), maxlen=self.delay2 + 1)
        self.z_delay = deque([self.z] * (self.delay3 + 1), maxlen=self.delay3 + 1)

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
