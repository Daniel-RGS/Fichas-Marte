# Ambiente v0.1 — Mars Sample Rover

## 1. Meta y ambiente

El agente es un rover autónomo en una superficie marciana de `40 × 40 m`. Debe recoger dos muestras en orden, esquivar asteroides, cráteres y astronautas, y regresar a la base antes de agotar la batería.

## 2. Mapa

```text
y=40 ┌────────────────────────────────────────┐
     │ ▓▓ pared de cañón ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
     │                          ◆2 (35,32)    │
     │          ●ast           ●ast           │
     │   ◯crát                                 │
     │                   ●ast       👨‍🚀B       │
     │        ◆1 (16,18)                ◯crát │
     │   👨‍🚀A      ●ast                          │
     │ 🚙 → → →                  ◯crát        │
     │[BASE]                                  │
y=0  └────────────────────────────────────────┘
    x=0                                    x=40
```

Leyenda: `🚙` rover, `◆` muestras, `●` asteroides, `◯` cráteres, `👨‍🚀` astronautas.

## 3. Elementos del mundo

| Elemento | Cantidad | Regla |
|---|---:|---|
| Base | 1, en `(0,0)` | Inicio y llegada; zona de `3 × 3 m`. |
| Muestras | 2 | Muestra 1 `(16,18)`, muestra 2 `(35,32)`; se recogen en orden. |
| Asteroides | 5 | Rocas sólidas de `1–3 m` de radio; choque `-1` y velocidad a `0`. |
| Cráteres | 3 | Zona prohibida; caer termina el episodio en fracaso. |
| Astronautas | 2 | Hay que pasar a más de `1 m`; tocarlos aplica `-5` y produce fracaso. |
| Paredes | 4 lados | El choque aplica `-1`. |

## 4. Variables con límites

| Variable | Unidad | Mínimo | Máximo |
|---|---:|---:|---:|
| Posición `x`, `y` | m | `0` | `40` |
| Orientación | grados | `-180` | `180` |
| Velocidad | m/s | `0` | `2` |
| Batería | % | `0` | `100` |
| Altura de salto | m | `0` | `1.5` |
| Carga de muestra | booleano | `0` | `1` |
| Adherencia | coeficiente | `0.3` | `1.0` |
| Distancia al astronauta más cercano | m | `0` | `40` |

## 5. Clima y gravedad

La gravedad es `3.71 m/s²`, la de Marte, y afecta la trayectoria vertical: el rover puede saltar más alto y caer más lentamente que en la Tierra. La condición base es seca, con adherencia `1.0`.

La perturbación experimental `dust_storm` añade ruido de sensores entre `0` y `0.5 m` y reduce la adherencia de `1.0` a `0.3`, haciendo que el rover patine más.

## 6. Acciones

Las acciones de movimiento están normalizadas entre `-1` y `1`:

| Acción | Rango | Regla |
|---|---:|---|
| Mover / avance | `[-1,1]` | Controla avance y frenado. |
| Girar | `[-1,1]` | Controla el giro. |
| Saltar | `0/1` | Solo desde el suelo; permite superar rocas pequeñas y consume `3%` extra de batería. |
| Agarrar | `0/1` | Válido a menos de `0.5 m` de la muestra y con velocidad menor de `0.3 m/s`; en otro caso es inválido. |

## 7. Observación

El agente recibe siete rayos de distancia, dirección y distancia a la muestra actual, distancia al astronauta más cercano, velocidad, giro, batería, indicador de carga y etapa de misión: ir a muestra 1, ir a muestra 2 o volver a la base.

## 8. Paso (`step`)

Un paso simula `0.1 s` y sigue la secuencia: observar → actuar → aplicar física (gravedad, adherencia y choques) → actualizar posición, velocidad, batería y misión → calcular recompensa → entregar nueva observación.

## 9. Truncamiento y fin

El episodio se trunca a los `2000` pasos o cuando la batería llega a `0%`; esto no cuenta como éxito ni fracaso. Hay éxito cuando las muestras 1 y 2 fueron recogidas en orden y el rover regresó a la base. Hay fracaso al caer en un cráter o chocar con un astronauta.

## 10. Premios y penalizaciones

| Evento | Valor |
|---|---:|
| Acercarse a la muestra actual | `+0.1` |
| Primera recogida de cada muestra | `+10` |
| Regresar a la base con las 2 muestras | `+20` |
| Cada paso | `-0.01` |
| Choque con asteroide o pared | `-1` |
| Giro brusco | `-0.05` |
| Salto innecesario | `-0.5` |
| Agarre inválido | `-0.5` |
| Tocar un astronauta | `-5` |

La recogida solo entrega premio la primera vez. El progreso solo se calcula hacia la muestra actual, respetando el orden, para impedir repetir muestras. Un salto sin una roca pequeña cerca se considera innecesario y no permite obtener progreso adicional.

## 11. Evaluación

Se registran misiones completas, muestras recogidas, batería restante, choques y distancia recorrida. El experimento de robustez activa `dust_storm` y compara si el modelo continúa completando la misión bajo ruido de sensores y menor adherencia.

