from __future__ import annotations

from math import cos, hypot, pi, sin

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class MarsSampleRoverEnv(gym.Env):
    """Ambiente 2-D del rover marciano.

    Acción: [avance, giro, salto, agarrar]. Avance y giro están en [-1, 1];
    salto y agarrar son valores binarios solicitados por el agente.
    """

    metadata = {"render_modes": ["ansi"]}

    def __init__(self, dust_storm=False, map_variant="normal", max_steps=2000, render_mode=None):
        super().__init__()
        self.dust_storm = dust_storm
        self.map_variant = map_variant
        self.max_steps = max_steps
        self.render_mode = render_mode
        self.action_space = spaces.Box(
            low=np.array([-1, -1, 0, 0], dtype=np.float32),
            high=np.array([1, 1, 1, 1], dtype=np.float32),
        )
        # x, y, heading, speed, battery, height, cargo, stage, nearest astronaut,
        # distance and bearing to target, plus seven range sensors.
        self.observation_space = spaces.Box(0, 1, shape=(18,), dtype=np.float32)
        self.base = np.array([4.0, 36.0])
        self.base_samples = [np.array([22.0, 32.0]), np.array([18.0, 5.0])]
        self.asteroids = [(8, 33, 1.5), (17, 24, 1.5), (27, 28, 1.25),
                          (34, 22, 1.0), (13, 13, 1.0), (34, 8, 1.5)]
        self.base_small_rocks = [(11.0, 29.0, 0.4)]
        self.small_rocks = list(self.base_small_rocks)
        self.craters = [(7, 24, 2.5), (31, 35, 2.5), (24, 12, 3.0)]
        self.astronauts = [(16, 30), (32, 15)]

    def _target(self):
        return self.samples[self.stage] if self.stage < 2 else self.base

    def _distance(self, point):
        return float(np.linalg.norm(self.position - point))

    def _observation(self):
        target = self._target()
        delta = target - self.position
        distance = min(40.0, np.linalg.norm(delta))
        bearing = (np.arctan2(delta[1], delta[0]) - self.heading + pi) % (2 * pi) - pi
        nearest_astronaut = min(self._distance(np.array(a)) for a in self.astronauts)
        rays = []
        for offset in np.linspace(-pi / 2, pi / 2, 7):
            angle = self.heading + offset
            rays.append(self._ray_distance(angle))
        raw = [*self.position / 40, (self.heading + pi) / (2 * pi), self.speed / 2,
               self.battery / 100, self.height / 0.8, float(self.cargo), self.stage / 2,
               nearest_astronaut / 40, distance / 40, (bearing + pi) / (2 * pi),
               *[np.clip(r + (self.np_random.uniform(-0.5, 0.5) if self.dust_storm else 0), 0, 40) / 40 for r in rays]]
        return np.asarray(raw, dtype=np.float32)

    def _ray_distance(self, angle):
        # Suficiente para la observación: distancia al borde del mapa y obstáculos.
        direction = np.array([cos(angle), sin(angle)])
        values = []
        for bound in (0, 40):
            if direction[0]: values.append((bound - self.position[0]) / direction[0])
            if direction[1]: values.append((bound - self.position[1]) / direction[1])
        for ox, oy, radius in [*self.asteroids_current, *self.small_rocks]:
            delta = np.array([ox, oy]) - self.position
            projection = float(delta @ direction)
            perpendicular = float(direction[0] * delta[1] - direction[1] * delta[0])
            if projection > 0 and abs(perpendicular) <= radius:
                offset = max(0.0, radius * radius - perpendicular * perpendicular) ** 0.5
                values.append(projection - offset)
        valid = [v for v in values if v >= 0]
        return max(0.0, min(40.0, min(valid) if valid else 40.0))

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        if self.map_variant not in {"normal", "A", "D"}:
            raise ValueError("map_variant debe ser normal, A o D")
        self.asteroids_current = list(self.asteroids)
        self.craters_current = list(self.craters)
        self.small_rocks = list(self.base_small_rocks)
        if self.map_variant == "A":
            # Cruzan el camino directo entre la base y la muestra 1.
            self.small_rocks = [(10.0 + i * 0.85, 34.0, 0.38) for i in range(5)]
        elif self.map_variant == "D":
            self._randomize_map()
        self.samples = []
        for base_sample in self.base_samples:
            for _ in range(100):
                candidate = np.clip(base_sample + self.np_random.uniform(-2, 2, size=2), 1, 39)
                blocked = any(np.linalg.norm(candidate - np.array(o[:2])) <= o[2] + .8 for o in [*self.asteroids_current, *self.craters_current, *self.small_rocks])
                if not blocked and all(np.linalg.norm(candidate - other) > 1.5 for other in self.samples):
                    self.samples.append(candidate)
                    break
            else:
                self.samples.append(np.array(base_sample, dtype=float))
        self.position = self.base.copy()
        self.heading = float(self.np_random.uniform(-pi, pi))
        self.speed = 0.0
        self.battery = 100.0
        self.height = 0.0
        self.cargo = 0
        self.stage = 0
        self.steps = 0
        self.distance_to_target = self._distance(self._target())
        self.events = []
        self.trajectory = []
        self.episode_metadata = {
            "seed": seed,
            "dust_storm": self.dust_storm,
            "map_variant": self.map_variant,
            "samples": [p.tolist() for p in self.samples],
            "asteroids": [list(p) for p in self.asteroids_current],
            "craters": [list(p) for p in self.craters_current],
            "small_rocks": [list(p) for p in self.small_rocks],
        }
        return self._observation(), {"dust_storm": self.dust_storm}

    def _randomize_map(self):
        """Desplaza obstáculos manteniendo separación entre objetos y límites."""
        for _ in range(100):
            moved = []
            for ox, oy, radius in self.asteroids:
                candidate = np.clip(np.array([ox, oy]) + self.np_random.uniform(-2, 2, size=2), 3, 37)
                if all(np.linalg.norm(candidate - np.array(other[:2])) > radius + other[2] + 1.0 for other in moved):
                    moved.append((float(candidate[0]), float(candidate[1]), radius))
            if len(moved) == len(self.asteroids):
                self.asteroids_current = moved
                break

    def step(self, action):
        action = np.asarray(action, dtype=np.float32)
        throttle, turn, jump, grab = np.clip(action, [-1, -1, 0, 0], [1, 1, 1, 1])
        self.steps += 1
        reward = -0.03
        events = []
        if self.dust_storm:
            adhesion = 0.3
            sensor_noise = self.np_random.uniform(-0.5, 0.5)
        else:
            adhesion, sensor_noise = 1.0, 0.0
        old_position = self.position.copy()
        self.heading = (self.heading + float(turn) * 0.2 + pi) % (2 * pi) - pi
        friction = 0.08 if abs(float(throttle)) < 0.05 else 0.0
        self.speed = float(np.clip(self.speed + throttle * 0.18 * adhesion - friction, 0, 2))
        if abs(turn) > 0.8: reward -= 0.2
        was_airborne = self.height > 0
        if jump > 0.5 and self.height == 0 and self.speed <= 2:
            self.height, self.battery = 0.8, max(0, self.battery - 3)
            events.append({"type": "jump", "position": self.position.tolist(), "reward": 0})
        elif jump > 0.5:
            reward -= 0.5
        if self.height > 0:
            self.height = max(0, self.height - 0.8 / 13)
            if was_airborne and self.height == 0:
                events.append({"type": "landing", "position": self.position.tolist(), "reward": 0})
        self.position += np.array([cos(self.heading), sin(self.heading)]) * self.speed * 0.1
        self.battery = max(0, self.battery - 0.03 - 0.03 * (self.speed / 2))
        if self.battery < 10 and self.battery + 0.03 + 0.03 * (self.speed / 2) >= 10:
            events.append({"type": "battery_low", "position": self.position.tolist(), "reward": 0})
        reward -= 0.03 * (self.speed / 2)
        picked = False
        if grab > 0.5:
            if self.stage < 2 and self._distance(self._target()) < 0.8 and self.speed < 0.15:
                sample_number = self.stage + 1
                sample_position = self._target().copy().tolist()
                self.stage += 1; self.cargo = min(1, self.stage); reward += 20; picked = True
                events.append({"type": "sample_collected", "sample": sample_number,
                               "position": self.position.tolist(), "sample_position": sample_position, "reward": 20})
            else:
                reward -= 0.5
                events.append({"type": "invalid_grab", "position": self.position.tolist(), "reward": -0.5})
        previous = self.distance_to_target
        self.distance_to_target = self._distance(self._target())
        if not picked:
            reward += 5 * (previous - self.distance_to_target)
        terminated = False
        if any(self._distance(np.array(c[:2])) <= c[2] for c in self.craters_current):
            terminated, reward = True, reward - 100
            events.append({"type": "crater", "position": self.position.tolist(), "reward": -100})
        if any(self._distance(np.array(a)) <= 1 for a in self.astronauts):
            terminated, reward = True, reward - 100
            events.append({"type": "astronaut", "position": self.position.tolist(), "reward": -100})
        if not (0 <= self.position[0] <= 40 and 0 <= self.position[1] <= 40):
            reward -= 1; self.position = np.clip(self.position, 0, 40)
        collisions = list(self.asteroids_current) if self.height == 0 else [a for a in self.asteroids_current if a[2] > 0.4]
        collisions += self.small_rocks if self.height == 0 else []
        if any(self._distance(np.array(a[:2])) <= a[2] for a in collisions):
            self.position = old_position; self.speed = 0; reward -= 10
            events.append({"type": "asteroid_collision", "position": self.position.tolist(), "reward": -10})
        if not terminated and self.stage == 2 and self._distance(self.base) <= 2:
            terminated, reward = True, reward + 50
            events.append({"type": "victory", "position": self.position.tolist(), "reward": 50})
        if self.battery <= 0:
            terminated, reward = True, reward - 10
            events.append({"type": "battery_empty", "position": self.position.tolist(), "reward": -10})
        truncated = self.steps >= self.max_steps and not terminated
        if truncated:
            events.append({"type": "timeout", "position": self.position.tolist(), "reward": 0})
        for event in events:
            event["step"] = self.steps
        self.events.extend(events)
        self.trajectory.append({"step": self.steps, "position": self.position.tolist(),
                                "heading": self.heading, "speed": self.speed,
                                "height": self.height, "battery": self.battery})
        info = {"battery": self.battery, "stage": self.stage, "sensor_noise": sensor_noise, "events": events}
        return self._observation(), float(reward), terminated, truncated, info

    def render(self):
        return f"Mars Rover pos=({self.position[0]:.1f},{self.position[1]:.1f}) stage={self.stage} battery={self.battery:.1f}%"

