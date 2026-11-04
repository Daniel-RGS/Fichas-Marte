from __future__ import annotations

import math

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class RocketLandingEnv(gym.Env):
    """Ambiente 2-D de aterrizaje vertical con combustible y viento."""

    def __init__(self, wind=0.0, max_steps=600, render_mode=None):
        super().__init__()
        self.wind = float(wind)
        self.max_steps = max_steps
        self.render_mode = render_mode
        self.action_space = spaces.Box(-1.0, 1.0, shape=(2,), dtype=np.float32)
        # x, y, vx, vy, angle, angular_velocity, fuel, contact_speed, contact_angle
        self.observation_space = spaces.Box(-1.0, 1.0, shape=(9,), dtype=np.float32)
        self.platform = np.array([0.0, 0.0])

    def _obs(self):
        return np.array([
            np.clip(self.x / 20, -1, 1), np.clip(self.y / 20, 0, 1),
            np.clip(self.vx / 10, -1, 1), np.clip(self.vy / 10, -1, 1),
            np.clip(self.angle / math.pi, -1, 1), np.clip(self.angular_velocity / 4, -1, 1),
            self.fuel / 100, np.clip(self.contact_speed / 5, -1, 1),
            np.clip(self.contact_angle / math.pi, -1, 1),
        ], dtype=np.float32)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.x = float(self.np_random.uniform(-8, 8)); self.y = 18.0
        self.vx = float(self.np_random.uniform(-1, 1)); self.vy = 0.0
        self.angle = float(self.np_random.uniform(-0.15, 0.15)); self.angular_velocity = 0.0
        self.fuel = 100.0; self.steps = 0; self.contact_speed = 0.0; self.contact_angle = 0.0
        return self._obs(), {"wind": self.wind}

    def step(self, action):
        throttle, torque = np.clip(action, -1, 1)
        self.steps += 1; reward = -0.05
        fuel_used = abs(float(throttle)) * 0.35 + abs(float(torque)) * 0.12
        self.fuel = max(0.0, self.fuel - fuel_used)
        thrust = max(0.0, float(throttle)) * 7.5
        self.vx += math.sin(self.angle) * thrust * 0.1 + self.wind * 0.03
        self.vy += (math.cos(self.angle) * thrust - 3.71) * 0.1
        self.angular_velocity += float(torque) * 0.15 - self.angle * 0.02
        self.angle += self.angular_velocity * 0.1
        self.x += self.vx * 0.1; self.y += self.vy * 0.1
        terminated = False; truncated = self.steps >= self.max_steps
        if self.y <= 0:
            self.y = 0; self.contact_speed = abs(self.vy); self.contact_angle = abs(self.angle)
            safe = abs(self.x) <= 2.0 and self.contact_speed <= 2.0 and self.contact_angle <= 0.25
            terminated = True
            if safe:
                reward += 100.0 + 20.0 * self.fuel / 100
            else:
                reward -= 100.0
        elif abs(self.x) > 20 or self.fuel <= 0:
            terminated = True; reward -= 50.0
        else:
            reward += max(0.0, 1.0 - abs(self.x) / 20) * 0.05
        return self._obs(), float(reward), terminated, truncated and not terminated, {"fuel": self.fuel, "safe_landing": terminated and reward > 0}

    def render(self):
        return f"Rocket x={self.x:.1f} y={self.y:.1f} vx={self.vx:.1f} vy={self.vy:.1f} fuel={self.fuel:.1f}%"

