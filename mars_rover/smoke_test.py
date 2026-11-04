"""Pruebas físicas mínimas que deben pasar antes de entrenar."""
from __future__ import annotations

import numpy as np

from .environment import MarsSampleRoverEnv


def run():
    env = MarsSampleRoverEnv(map_variant="normal")
    obs, _ = env.reset(seed=0)
    assert env.observation_space.contains(obs)
    before = env.battery
    env.step([0, 0, 0, 0])
    assert abs((before - env.battery) - 0.03) < 1e-6, env.battery
    assert env._terrain_reading(env.position) == (0.0, 0.5)
    env.position = np.array([39.9, 20.0]); env.heading = 0.0; env.speed = 2.0
    env.step([1, 0, 0, 0])
    assert env.speed == 0.0
    for variant in ("normal", "A", "D", "3E"):
        check = MarsSampleRoverEnv(map_variant=variant)
        obs, _ = check.reset(seed=10)
        assert check.observation_space.contains(obs)
    print("smoke_test=ok consumo_parado=0.03 pared_frena=si terreno_normal=si")


if __name__ == "__main__":
    run()
