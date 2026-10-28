from __future__ import annotations

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class AutonomousRallyEnv(gym.Env):
    metadata = {"render_modes": ["ansi"]}

    def __init__(self, track_length: int = 30, max_steps: int = 80, render_mode=None):
        super().__init__()
        self.track_length = track_length
        self.max_steps = max_steps
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.MultiDiscrete([track_length, 3, 4, max_steps + 1])
        self.render_mode = render_mode

    def _obs(self):
        return np.array([self.position, self.speed, self.checkpoint, self.steps], dtype=np.int64)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.position, self.speed, self.checkpoint, self.steps = 0, 1, 0, 0
        return self._obs(), {"checkpoint": self.checkpoint}

    def step(self, action):
        action = int(action)
        self.steps += 1
        reward = -0.1
        if action == 0:
            self.speed = min(2, self.speed + 1)
        else:
            self.speed = max(0, self.speed - 1)
            reward -= 1.0
        self.position += self.speed
        if self.position >= self.track_length:
            self.position = self.track_length - 1
        target = (self.checkpoint + 1) * (self.track_length // 4)
        if self.checkpoint < 3 and self.position >= target:
            self.checkpoint += 1
            reward += 10.0
        terminated = self.checkpoint == 3
        if terminated:
            reward += 100.0
        truncated = self.steps >= self.max_steps and not terminated
        return self._obs(), reward, terminated, truncated, {"checkpoint": self.checkpoint}

    def render(self):
        track = ["."] * self.track_length
        for i in range(1, 4):
            track[min(i * (self.track_length // 4), self.track_length - 1)] = str(i)
        track[self.position] = "A"
        return "|" + "".join(track) + f"| step={self.steps} checkpoint={self.checkpoint}"

