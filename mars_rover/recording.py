from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .environment import MarsSampleRoverEnv


def save_episode(path, policy, seed=7, dust_storm=False):
    env = MarsSampleRoverEnv(dust_storm=dust_storm)
    obs, _ = env.reset(seed=seed)
    done = False
    while not done:
        action = policy(env, obs)
        obs, _, terminated, truncated, _ = env.step(np.asarray(action, dtype=np.float32))
        done = terminated or truncated
    recording = {
        "metadata": env.episode_metadata,
        "states": env.trajectory,
        "events": env.events,
        "result": {"terminated": terminated, "truncated": truncated,
                    "success": env.stage == 2 and env._distance(env.base) <= 2,
                    "steps": env.steps, "battery": env.battery},
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(recording, indent=2), encoding="utf-8")
    return recording


def manual_policy():
    waypoint = {"index": 0}

    def policy(env, _obs):
        if env.stage < 2:
            target = env._target(); slow = True
        else:
            points = [np.array([12., 26.]), np.array([6., 30.]), env.base]
            target = points[waypoint["index"]]; slow = waypoint["index"] == 2
            if np.linalg.norm(target - env.position) < 1.5 and waypoint["index"] < 2:
                waypoint["index"] += 1; target = points[waypoint["index"]]; slow = False
        delta = target - env.position
        distance = np.linalg.norm(delta)
        desired = np.arctan2(delta[1], delta[0])
        error = (desired - env.heading + np.pi) % (2 * np.pi) - np.pi
        turn = float(np.clip(error / .2, -1, 1))
        if slow and distance < .8:
            throttle = -1 if env.speed > .15 else .15
        elif slow and distance < 3:
            throttle = -1 if env.speed > .5 else .2
        else:
            throttle = .65 if abs(error) < .8 else .05
        grab = float(env.stage < 2 and np.linalg.norm(env._target() - env.position) < .8 and env.speed < .15)
        return [throttle, turn, 0, grab]

    return policy
