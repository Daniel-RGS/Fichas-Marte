from __future__ import annotations

import argparse

from .environment import RocketLandingEnv


def rollout():
    env = RocketLandingEnv(); env.reset(seed=7)
    for i in range(5):
        _, reward, terminated, truncated, info = env.step([0.4, 0.0])
        print(f"paso={i + 1} {env.render()} recompensa={reward:.2f} fin={terminated or truncated}")


def main():
    parser = argparse.ArgumentParser(description="CLI del Experimento 2: Rocket Landing")
    parser.add_argument("command", choices=["rollout"])
    args = parser.parse_args()
    if args.command == "rollout": rollout()


if __name__ == "__main__": main()

