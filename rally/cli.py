from __future__ import annotations

import argparse
from pathlib import Path

from .agent import QLearningAgent
from .environment import AutonomousRallyEnv

MODEL = Path("artifacts/rally-qlearning.pkl")


def train(episodes):
    env, agent = AutonomousRallyEnv(), QLearningAgent()
    successes = 0
    for _ in range(episodes):
        state, _ = env.reset()
        done = False
        while not done:
            action = agent.act(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            agent.update(state, action, reward, next_state, done)
            state = next_state
        successes += int(terminated)
        agent.epsilon = max(0.05, agent.epsilon * 0.999)
    agent.save(MODEL)
    print(f"modelo guardado en {MODEL} | episodios={episodes} | éxitos={successes}")


def evaluate(episodes):
    agent = QLearningAgent.load(MODEL)
    env = AutonomousRallyEnv()
    for i in range(episodes):
        state, _ = env.reset()
        total, done = 0.0, False
        while not done:
            state, reward, terminated, truncated, _ = env.step(agent.act(state, explore=False))
            total += reward
            done = terminated or truncated
        print(f"episodio={i + 1} éxito={terminated} recompensa={total:.1f} pasos={env.steps}")


def rollout():
    env = AutonomousRallyEnv()
    state, _ = env.reset()
    for i in range(5):
        action = i % 3
        next_state, reward, terminated, truncated, _ = env.step(action)
        print(f"{i + 1}: obs={state.tolist()} acción={action} nuevo_estado={next_state.tolist()} recompensa={reward:.1f} fin={terminated or truncated}")
        state = next_state


def main():
    parser = argparse.ArgumentParser(description="CLI del experimento Autonomous Rally")
    sub = parser.add_subparsers(dest="command", required=True)
    t = sub.add_parser("train"); t.add_argument("--episodes", type=int, default=5000)
    e = sub.add_parser("evaluate"); e.add_argument("--episodes", type=int, default=3)
    sub.add_parser("rollout"); sub.add_parser("render")
    args = parser.parse_args()
    if args.command == "train": train(args.episodes)
    elif args.command == "evaluate": evaluate(args.episodes)
    elif args.command == "rollout": rollout()
    else:
        from .graphics import run
        run()


if __name__ == "__main__":
    main()

