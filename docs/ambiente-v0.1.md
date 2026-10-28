# Ambiente v0.1 — Autonomous Rally

## Misión y mapa

Una pista cerrada de longitud `N` con tres checkpoints que deben cruzarse en orden. El agente debe completar una vuelta sin salirse.

## Variables y unidades

| Variable | Unidad | Rango | Visible |
|---|---|---:|---|
| posición | celda | `0..N-1` | sí |
| velocidad | celdas/turno | `0..2` | sí |
| checkpoint actual | índice | `0..3` | sí |
| tiempo | turnos | `0..T` | sí |
| salidas/choques | conteo | `0..T` | no |

## Observaciones y acciones

Observación: `(posición, velocidad, checkpoint, tiempo)`. Acciones: `0=avanzar`, `1=girar izquierda`, `2=girar derecha`. En esta primera versión los giros reducen velocidad y representan maniobras de control.

## Dinámica

Cada acción actualiza velocidad, posición y tiempo. Cruzar el siguiente checkpoint incrementa el progreso. Salirse de la pista produce fracaso; cruzar los tres checkpoints y completar la vuelta produce éxito.

## Recompensa

`+10` por checkpoint nuevo, `+100` por éxito, `-20` por salida, `-0.1` por paso y `-1` por giro.

## Éxito, fracaso y límite de tiempo

Éxito: completar todos los checkpoints. Fracaso: salida de pista. Truncamiento: alcanzar `T=80` turnos.

## Métricas e incidente

Métricas: tasa de éxito, pasos por episodio y salidas de pista. Perturbación: reducir la adherencia, modelada como mayor probabilidad de salida al avanzar rápido.

## Cinco transiciones

Se registran automáticamente mediante `rally.cli rollout`.

## Posibles trampas y decisiones pendientes

Evitar recompensar repetidamente el mismo checkpoint. Pendiente: mapa continuo, sensores y física detallada.

