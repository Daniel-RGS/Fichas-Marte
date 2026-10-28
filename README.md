# MLOps Autonomous Lab

Proyecto local para diseñar, entrenar y visualizar ambientes autónomos.

## Experimento 1: Autonomous Rally

```bash
./scripts/setup.sh
source .venv/bin/activate
python -m rally.cli train --episodes 5000
python -m rally.cli evaluate --episodes 3
python -m rally.cli render --episodes 1
```

El ambiente es una pista discreta con checkpoints ordenados. El agente observa su posición, velocidad y checkpoint actual; las acciones son avanzar, girar a la izquierda o girar a la derecha.

## Estructura

- `docs/ambiente-v0.1.md`: diseño del ambiente.
- `rally/environment.py`: ambiente Gymnasium.
- `rally/agent.py`: agente tabular Q-learning.
- `rally/cli.py`: interfaz de línea de comandos.
- `rally/graphics.py`: motor gráfico opcional con pygame.
- `scripts/setup.sh`: creación del entorno virtual e instalación.

