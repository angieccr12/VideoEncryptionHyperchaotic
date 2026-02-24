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
            self._rk4_step()

    def _derivatives(self, x, y, z, w):
        """Compute derivatives of the Lorenz-Stenflo system"""
        a, b, c, d, e = self.a, self.b, self.c, self.d, self.e
        dx = a * (y - x)
        dy = c * y - x * z + w
        dz = -b * z + y**2
        dw = -e * (x + y)
        return dx, dy, dz, dw

    def _rk4_step(self):
        """Runge-Kutta 4th order integration for better numerical accuracy"""
        tau = self.tau
        
        # k1 = f(t_n, y_n)
        k1_x, k1_y, k1_z, k1_w = self._derivatives(self.x, self.y, self.z, self.w)
        
        # k2 = f(t_n + tau/2, y_n + k1*tau/2)
        k2_x, k2_y, k2_z, k2_w = self._derivatives(
            self.x + k1_x * tau / 2,
            self.y + k1_y * tau / 2,
            self.z + k1_z * tau / 2,
            self.w + k1_w * tau / 2
        )
        
        # k3 = f(t_n + tau/2, y_n + k2*tau/2)
        k3_x, k3_y, k3_z, k3_w = self._derivatives(
            self.x + k2_x * tau / 2,
            self.y + k2_y * tau / 2,
            self.z + k2_z * tau / 2,
            self.w + k2_w * tau / 2
        )
        
        # k4 = f(t_n + tau, y_n + k3*tau)
        k4_x, k4_y, k4_z, k4_w = self._derivatives(
            self.x + k3_x * tau,
            self.y + k3_y * tau,
            self.z + k3_z * tau,
            self.w + k3_w * tau
        )
        
        # y_{n+1} = y_n + (k1 + 2*k2 + 2*k3 + k4) * tau / 6
        self.x = self.x + (k1_x + 2*k2_x + 2*k3_x + k4_x) * tau / 6
        self.y = self.y + (k1_y + 2*k2_y + 2*k3_y + k4_y) * tau / 6
        self.z = self.z + (k1_z + 2*k2_z + 2*k3_z + k4_z) * tau / 6
        self.w = self.w + (k1_w + 2*k2_w + 2*k3_w + k4_w) * tau / 6

    def step(self):
        self._rk4_step()
        return self.x, self.y, self.z, self.w

    def generate_key(self, shape):
        self._rk4_step()
        chaos = np.array([self.x, self.y, self.z, self.w])
        chaos = np.abs(np.sin(chaos * 1e4))
        key = np.tile(chaos.mean(), shape)
        return (key * 255).astype(np.uint8)