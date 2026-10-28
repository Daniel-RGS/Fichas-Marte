from __future__ import annotations

import argparse
from pathlib import Path

from .agent import RoverQAgent
from .environment import MarsSampleRoverEnv

MODEL = Path("artifacts/mars-rover-q.pkl")


def train(episodes):
    env, agent = MarsSampleRoverEnv(), RoverQAgent()
    successes = 0
    for episode in range(episodes):
        obs, _ = env.reset(seed=episode)
        done = False
        while not done:
            action = agent.act(obs)
            next_obs, reward, terminated, truncated, _ = env.step(agent.ACTIONS[action])
            done = terminated or truncated
            agent.update(obs, action, reward, next_obs, done)
            obs = next_obs
        successes += int(terminated and env.stage == 2 and env._distance(env.base) <= 2)
        agent.epsilon = max(.05, agent.epsilon * .997)
    agent.save(MODEL)
    print(f"modelo={MODEL} episodios={episodes} éxitos={successes} epsilon={agent.epsilon:.3f}")


def evaluate(episodes, dust_storm=False):
    agent = RoverQAgent.load(MODEL)
    results = []
    for episode in range(episodes):
        env = MarsSampleRoverEnv(dust_storm=dust_storm)
        obs, _ = env.reset(seed=10000 + episode)
        total, done = 0.0, False
        while not done:
            obs, reward, terminated, truncated, info = env.step(agent.ACTIONS[agent.act(obs, False)])
            total += reward; done = terminated or truncated
        success = terminated and env.stage == 2 and env._distance(env.base) <= 2
        results.append(success)
        print(f"episodio={episode + 1} éxito={success} etapa={env.stage} batería={info['battery']:.1f}% recompensa={total:.1f}")
    print(f"tasa_de_éxito={sum(results)}/{episodes}")


def rollout():
    env = MarsSampleRoverEnv(); obs, _ = env.reset(seed=7)
    for i in range(5):
        action = RoverQAgent.ACTIONS[i % len(RoverQAgent.ACTIONS)]
        next_obs, reward, terminated, truncated, _ = env.step(action)
        print(f"{i + 1}: etapa={env.stage} pos=({env.position[0]:.1f},{env.position[1]:.1f}) acción={action.tolist()} recompensa={reward:.2f} fin={terminated or truncated}")
        obs = next_obs


def render():
    env = MarsSampleRoverEnv(); env.reset(seed=7)
    print("Mapa ANSI: rover", env.render())


def main():
    parser = argparse.ArgumentParser(description="CLI de Mars Sample Rover")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("train"); p.add_argument("--episodes", type=int, default=1000)
    p = sub.add_parser("evaluate"); p.add_argument("--episodes", type=int, default=3); p.add_argument("--dust-storm", action="store_true")
    sub.add_parser("rollout"); sub.add_parser("render")
    args = parser.parse_args()
    if args.command == "train": train(args.episodes)
    elif args.command == "evaluate": evaluate(args.episodes, args.dust_storm)
    elif args.command == "rollout": rollout()
    else: render()


if __name__ == "__main__": main()

