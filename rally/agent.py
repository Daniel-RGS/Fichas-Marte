from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np


class QLearningAgent:
    def __init__(self, n_actions=3, alpha=0.2, gamma=0.98, epsilon=1.0, seed=7):
        self.q = {}
        self.n_actions, self.alpha, self.gamma, self.epsilon = n_actions, alpha, gamma, epsilon
        self.rng = np.random.default_rng(seed)

    def values(self, state):
        key = tuple(int(x) for x in state)
        return self.q.setdefault(key, np.zeros(self.n_actions, dtype=float))

    def act(self, state, explore=True):
        if explore and self.rng.random() < self.epsilon:
            return int(self.rng.integers(self.n_actions))
        return int(np.argmax(self.values(state)))

    def update(self, state, action, reward, next_state, done):
        values = self.values(state)
        target = reward if done else reward + self.gamma * np.max(self.values(next_state))
        values[action] += self.alpha * (target - values[action])

    def save(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, "rb") as f:
            return pickle.load(f)

