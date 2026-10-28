from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np


class RoverQAgent:
    ACTIONS = np.array([
        [-1, -1, 0, 0], [-1, 0, 0, 0], [-1, 1, 0, 0],
        [0, -1, 0, 0], [0, 0, 0, 0], [0, 1, 0, 0],
        [1, -1, 0, 0], [1, 0, 0, 0], [1, 1, 0, 0],
    ], dtype=np.float32)

    def __init__(self, seed=7, alpha=.12, gamma=.98, epsilon=1.0):
        self.q = {}
        self.alpha, self.gamma, self.epsilon = alpha, gamma, epsilon
        self.rng = np.random.default_rng(seed)

    def key(self, obs):
        # Discretización compacta para un baseline reproducible.
        return tuple(np.clip((np.asarray(obs) * 10).astype(int), 0, 10))

    def values(self, obs):
        return self.q.setdefault(self.key(obs), np.zeros(len(self.ACTIONS)))

    def act(self, obs, explore=True):
        if explore and self.rng.random() < self.epsilon:
            return int(self.rng.integers(len(self.ACTIONS)))
        return int(np.argmax(self.values(obs)))

    def update(self, obs, action, reward, next_obs, done):
        target = reward if done else reward + self.gamma * np.max(self.values(next_obs))
        values = self.values(obs)
        values[action] += self.alpha * (target - values[action])

    def save(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as handle: pickle.dump(self, handle)

    @staticmethod
    def load(path):
        with open(path, "rb") as handle: return pickle.load(handle)

