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

        self.delay1 = round(self.tau1 / dt)
        self.delay2 = round(self.tau2 / dt)
        self.delay3 = round(self.tau3 / dt)

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

    def _derivatives(self, x, y, z, w, x_tau, y_tau, z_tau):
        """
        Compute the derivatives of the hyperchaotic system.
        
        Args:
            x, y, z, w: Current state variables
            x_tau, y_tau, z_tau: Delayed state variables
            
        Returns:
            Tuple of (dx/dt, dy/dt, dz/dt, dw/dt)
        """
        dx = -self.a * x_tau - self.b * y * z
        dy = -x + self.c * y_tau + self.c * w
        dz = self.d - y**2 - z_tau
        dw = x - w
        return dx, dy, dz, dw

    def step(self):
        """
        Advance the system one time step using Runge-Kutta 4th order (RK4).
        RK4 provides much better numerical accuracy for chaotic systems
        compared to explicit Euler method.
        """
        # Get delayed values (these remain constant during the RK4 sub-steps)
        x_tau = self.x_delay[0]
        y_tau = self.y_delay[0]
        z_tau = self.z_delay[0]

        # RK4: k1 = f(t_n, y_n)
        k1_x, k1_y, k1_z, k1_w = self._derivatives(
            self.x, self.y, self.z, self.w,
            x_tau, y_tau, z_tau
        )

        # RK4: k2 = f(t_n + dt/2, y_n + k1*dt/2)
        k2_x, k2_y, k2_z, k2_w = self._derivatives(
            self.x + k1_x * self.dt / 2,
            self.y + k1_y * self.dt / 2,
            self.z + k1_z * self.dt / 2,
            self.w + k1_w * self.dt / 2,
            x_tau, y_tau, z_tau
        )

        # RK4: k3 = f(t_n + dt/2, y_n + k2*dt/2)
        k3_x, k3_y, k3_z, k3_w = self._derivatives(
            self.x + k2_x * self.dt / 2,
            self.y + k2_y * self.dt / 2,
            self.z + k2_z * self.dt / 2,
            self.w + k2_w * self.dt / 2,
            x_tau, y_tau, z_tau
        )

        # RK4: k4 = f(t_n + dt, y_n + k3*dt)
        k4_x, k4_y, k4_z, k4_w = self._derivatives(
            self.x + k3_x * self.dt,
            self.y + k3_y * self.dt,
            self.z + k3_z * self.dt,
            self.w + k3_w * self.dt,
            x_tau, y_tau, z_tau
        )

        # Update state: y_{n+1} = y_n + (k1 + 2*k2 + 2*k3 + k4) * dt / 6
        self.x += (k1_x + 2*k2_x + 2*k3_x + k4_x) * self.dt / 6
        self.y += (k1_y + 2*k2_y + 2*k3_y + k4_y) * self.dt / 6
        self.z += (k1_z + 2*k2_z + 2*k3_z + k4_z) * self.dt / 6
        self.w += (k1_w + 2*k2_w + 2*k3_w + k4_w) * self.dt / 6

        # Update delay buffers with new values
        self.x_delay.append(self.x)
        self.y_delay.append(self.y)
        self.z_delay.append(self.z)

        return self.x, self.y, self.z, self.w