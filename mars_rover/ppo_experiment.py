"""Entrenamiento y evaluación reproducible de PPO para el rover."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

from .environment import MarsSampleRoverEnv

ROOT = Path("artifacts/ppo-rover")


def make_env(dust_storm=False, seed_offset=0):
    def factory():
        env = Monitor(MarsSampleRoverEnv(dust_storm=dust_storm, map_variant="normal"))
        env.reset(seed=seed_offset)
        return env
    return factory


def train(total_steps):
    ROOT.mkdir(parents=True, exist_ok=True)
    env = DummyVecEnv([make_env(seed_offset=i) for i in range(8)])
    env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=10.0)
    callback = CheckpointCallback(save_freq=max(1024 // 8, 1), save_path=str(ROOT / "checkpoints"), name_prefix="ppo")
    model = PPO("MlpPolicy", env, seed=7, verbose=1, n_steps=256, batch_size=256,
                learning_rate=3e-4, gamma=.99, device="cpu")
    model.learn(total_timesteps=total_steps, callback=callback)
    model.save(ROOT / "model")
    env.save(ROOT / "vecnormalize.pkl")
    env.close()
    print(f"guardado={ROOT / 'model'} pasos={total_steps}")


def cause(env, terminated, truncated):
    if env.stage == 2 and np.linalg.norm(env.position - env.base) <= 2:
        return "victoria"
    for name in ("crater", "astronaut", "asteroid_collision", "battery_empty", "timeout"):
        if any(e["type"] == name for e in env.events):
            return {"asteroid_collision": "choque", "battery_empty": "bateria"}.get(name, name)
    return "tiempo" if truncated else "no_llego"


def evaluate(episodes):
    eval_env = DummyVecEnv([make_env()])
    eval_env = VecNormalize.load(ROOT / "vecnormalize.pkl", eval_env)
    eval_env.training = False
    eval_env.norm_reward = False
    model = PPO.load(ROOT / "model", env=eval_env, device="cpu")
    for storm in (False, True):
        results = []
        for i in range(episodes):
            env = MarsSampleRoverEnv(dust_storm=storm, map_variant="normal")
            obs, _ = env.reset(seed=10000 + i)
            jumps = collisions = stationary = 0
            headings = []
            while True:
                normalized = eval_env.normalize_obs(obs[None, ...])
                action, _ = model.predict(normalized, deterministic=True)
                obs, _, terminated, truncated, info = env.step(action[0])
                jumps += sum(e["type"] == "jump" for e in info.get("events", []))
                collisions = info.get("collision_count", collisions)
                stationary += int(env.speed < .03)
                headings.append(env.heading)
                if terminated or truncated:
                    break
            turns = int(np.sum(np.abs(np.diff(np.unwrap(headings))) > .1)) if len(headings) > 1 else 0
            results.append((cause(env, terminated, truncated), env.battery, env.steps, jumps, collisions, stationary, turns))
        wins = sum(r[0] == "victoria" for r in results)
        print(f"tormenta={storm} misiones={wins}/{episodes} bateria_media={np.mean([r[1] for r in results]):.1f}% pasos_medios={np.mean([r[2] for r in results]):.1f} saltos={np.mean([r[3] for r in results]):.1f} choques={np.mean([r[4] for r in results]):.1f} quietud={np.mean([r[5] for r in results]):.1f} giros={np.mean([r[6] for r in results]):.1f}")
        counts = {}
        for r in results: counts[r[0]] = counts.get(r[0], 0) + 1
        print("causas=" + ", ".join(f"{k}:{v}" for k, v in sorted(counts.items())))
    eval_env.close()


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    t = sub.add_parser("train"); t.add_argument("--steps", type=int, default=1_000_000)
    e = sub.add_parser("evaluate"); e.add_argument("--episodes", type=int, default=50)
    args = parser.parse_args()
    train(args.steps) if args.command == "train" else evaluate(args.episodes)


if __name__ == "__main__":
    main()
