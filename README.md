# Fichas-Marte

Proyecto local para diseñar, entrenar y visualizar ambientes autónomos.

## Experimento: Mars Sample Rover

El proyecto contiene el ambiente Gymnasium del rover marciano, entrenamiento, grabaciones de episodios y un visor 3D estilo Mario 64.

El ambiente es una pista discreta con checkpoints ordenados. El agente observa su posición, velocidad y checkpoint actual; las acciones son avanzar, girar a la izquierda o girar a la derecha.

## Estructura

- `docs/ambiente-v0.1.md`: diseño del ambiente.
- `mars_rover/environment.py`: simulador del rover.
- `mars_rover/recording.py`: grabaciones con estados y eventos.
- `docs/mars_rover_visor_3d_estilo_mario64.html`: visor 3D.
- `rally/graphics.py`: motor gráfico opcional con pygame.
- `scripts/setup.sh`: creación del entorno virtual e instalación.
