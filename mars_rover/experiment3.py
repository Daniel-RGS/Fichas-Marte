"""Experimento 3: línea base y aumento controlado de dificultad."""
from __future__ import annotations

import argparse
from collections import Counter

import numpy as np

from .environment import MarsSampleRoverEnv
from .recording import manual_policy


def failure_cause(env, terminated, truncated):
    if env.stage == 2 and np.linalg.norm(env.position - env.base) <= 2:
        return "victoria"
    types = [event["type"] for event in env.events]
    for name in ("crater", "astronaut", "asteroid_collision", "battery_empty", "timeout"):
        if name in types:
            return {"asteroid_collision": "choque", "battery_empty": "bateria"}.get(name, name)
    return "tiempo" if truncated else "no_llego"


def run_policy(variant, policy_factory, seeds=50):
    rows = []
    for seed in range(seeds):
        env = MarsSampleRoverEnv(map_variant=variant)
        obs, _ = env.reset(seed=seed)
        policy = policy_factory()
        total = 0.0
        while True:
            obs, reward, terminated, truncated, _ = env.step(policy(env, obs))
            total += reward
            if terminated or truncated:
                break
        rows.append({
            "success": failure_cause(env, terminated, truncated) == "victoria",
            "battery": env.battery,
            "steps": env.steps,
            "cause": failure_cause(env, terminated, truncated),
            "reward": total,
        })
    return rows


def print_report(variant, rows):
    successes = sum(row["success"] for row in rows)
    print(f"variante={variant} misiones={successes}/{len(rows)} "
          f"bateria_media={np.mean([r['battery'] for r in rows]):.1f}% "
          f"pasos_medios={np.mean([r['steps'] for r in rows]):.1f}")
    print("causas=" + ", ".join(f"{key}:{value}" for key, value in sorted(Counter(r["cause"] for r in rows).items())))


def main():
    parser = argparse.ArgumentParser(description="Evaluación del Experimento 3")
    parser.add_argument("--seeds", type=int, default=50)
    parser.add_argument("--variant", choices=["normal", "A", "D", "all"], default="all")
    args = parser.parse_args()
    variants = ["normal", "A", "D"] if args.variant == "all" else [args.variant]
    for variant in variants:
        print_report(variant, run_policy(variant, manual_policy, args.seeds))


if __name__ == "__main__":
    main()
