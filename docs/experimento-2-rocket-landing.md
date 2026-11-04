# Experimento 2 — Rocket Landing

## Misión

El agente controla un cohete en un plano vertical. Debe aterrizar en la plataforma central con velocidad de contacto, posición e inclinación seguras, usando combustible limitado.

## Reglas principales

| Elemento | Regla |
|---|---|
| Mundo | Plano vertical, gravedad marciana de `3.71 m/s²`. |
| Plataforma | Centro en `x=0`, ancho seguro de `4 m`. |
| Éxito | `|x| ≤ 2 m`, velocidad de contacto `≤ 2 m/s` e inclinación `≤ 0.25 rad`. |
| Combustible | Comienza en `100%`; se consume al aplicar empuje o torque. |
| Fracaso | Impacto inseguro, salir del área lateral o agotar combustible. |
| Truncamiento | `600` pasos de `0.1 s`. |
| Perturbación | Viento configurable; el experimento compara viento `0` contra viento lateral. |

## Acciones

El agente controla el empuje principal y el torque de orientación. Ambas acciones están normalizadas entre `-1` y `1`.

## Observación

Incluye posición, velocidad horizontal y vertical, orientación, velocidad angular, combustible, velocidad de contacto e inclinación de contacto. Los valores se entregan normalizados.

## Recompensa

Se penaliza el tiempo y el combustible consumido, se premia mantener el cohete sobre la plataforma y se otorgan `+100` por aterrizaje seguro. Un aterrizaje inseguro recibe `-100` y salir del área o agotar combustible recibe `-50`.

## Evaluación

Se medirán aterrizajes seguros, velocidad de contacto, error horizontal, combustible restante y rendimiento bajo viento.

