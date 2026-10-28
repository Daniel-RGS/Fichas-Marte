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
| Base | 1, en `(4,36)` | Inicio y llegada; zona de `4 × 4 m`. |
| Muestras | 2 | Muestra 1 `(22,32)`, muestra 2 `(18,5)`; se recogen en orden. |
| Asteroides | 6 | Rocas sólidas de `1–1.5 m` de radio; choque `-1` y velocidad a `0`. |
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
| Altura de salto | m | `0` | `0.8` |
| Carga de muestra | booleano | `0` | `1` |
| Adherencia | coeficiente | `0.3` | `1.0` |
| Distancia al astronauta más cercano | m | `0` | `40` |

## 5. Clima y gravedad

La gravedad es `3.71 m/s²`, la de Marte, y afecta la trayectoria vertical. El salto parte de una velocidad vertical de `2.4 m/s`, alcanza aproximadamente `0.8 m` y dura cerca de `1.3 s`. La condición base es seca, con adherencia `1.0`.

La perturbación experimental `dust_storm` añade ruido de sensores entre `0` y `0.5 m` y reduce la adherencia de `1.0` a `0.3`, haciendo que el rover patine más.

## 6. Acciones

Las acciones de movimiento están normalizadas entre `-1` y `1`:

| Acción | Rango | Regla |
|---|---:|---|
| Mover / avance | `[-1,1]` | Controla avance y frenado. |
| Girar | `[-1,1]` | Controla el giro. |
| Saltar | `0/1` | Solo desde el suelo; permite superar rocas pequeñas, usa `2.4 m/s` verticales y consume `3%` extra de batería. |
| Agarrar | `0/1` | Válido a menos de `0.5 m` de la muestra y con velocidad menor de `0.3 m/s`; en otro caso es inválido. |

## 7. Observación

El agente recibe siete rayos de distancia, dirección y distancia a la muestra actual, distancia al astronauta más cercano, velocidad, giro, batería, indicador de carga y etapa de misión: ir a muestra 1, ir a muestra 2 o volver a la base.

## 8. Paso (`step`)

Un paso simula `0.1 s` y sigue la secuencia: observar → actuar → aplicar física (gravedad, adherencia y choques) → actualizar posición, velocidad, batería y misión → calcular recompensa → entregar nueva observación.

## 9. Truncamiento y fin

El episodio se trunca únicamente al alcanzar `2000` pasos. La batería en `0%` es una derrota suave: termina el episodio como fracaso con una penalización adicional de `-10`. Hay éxito cuando las muestras 1 y 2 fueron recogidas en orden y el rover regresó a la base. Hay fracaso al caer en un cráter, chocar con un astronauta o quedarse sin batería.

## 10. Premios y penalizaciones

| Evento | Valor |
|---|---:|
| Progreso hacia la muestra actual | `5 × (distancia anterior − distancia actual)` |
| Primera recogida de cada muestra | `+10` |
| Regresar a la base con las 2 muestras | `+20` |
| Cada paso | `-0.03` |
| Consumo por movimiento a velocidad máxima | `-0.03` por paso |
| Choque con asteroide o pared | `-1` |
| Giro brusco | `-0.2` |
| Salto innecesario | `-0.5` |
| Agarre inválido | `-0.5` |
| Tocar un astronauta | `-5` |
| Batería agotada | `-10` |

El progreso es diferencial: acercarse da positivo y alejarse da negativo. Como alternativa equivalente de implementación se puede guardar la mejor distancia de la etapa y premiar solo una mejora real. La recogida solo entrega premio la primera vez y el progreso solo se calcula hacia la muestra actual, respetando el orden. Un salto sin una roca pequeña cerca se considera innecesario y no permite obtener progreso adicional.

Para evitar memorizar una única ruta, cada episodio usa una semilla: el mapa base conserva estas coordenadas, pero las muestras pueden desplazarse hasta `±2 m` y la orientación inicial puede variar. Los obstáculos deben seguir siendo válidos y no solaparse con la base ni con las muestras.

## 11. Evaluación

Se registran misiones completas, muestras recogidas, batería restante, choques y distancia recorrida. El experimento de robustez activa `dust_storm` y compara si el modelo continúa completando la misión bajo ruido de sensores y menor adherencia.

## 12. Rangos de observación y parámetros

| Observación o parámetro | Unidad | Rango |
|---|---:|---:|
| Posición `x,y` | m | `0–40` |
| Orientación | radianes | `-π–π` |
| Velocidad | m/s | `0–2` |
| Altura | m | `0–0.8` |
| Batería | % | `0–100` |
| Rayos de distancia | m | `0–40` más ruido `±0.5` en tormenta |
| Distancia a objetivo | m | `0–40` |
| Distancia a astronauta | m | `0–40` |
| Etapa de misión | índice | `0–2` |
| Adherencia | coeficiente | `0.3–1.0` |

## 13. Cinco transiciones de ejemplo

1. El rover observa la muestra 1 a su derecha, avanza y reduce su distancia; recibe progreso positivo.
2. Se aproxima a la muestra con velocidad menor de `0.15 m/s`, ejecuta agarrar y recibe `+20`, sin cobrar progreso adicional en ese mismo paso.
3. Detecta un asteroide en la trayectoria, gira y se aleja; el cambio de distancia produce la recompensa diferencial correspondiente.
4. Pasa sobre la roca pequeña con salto activo; la gravedad lo hace subir y volver al suelo en aproximadamente `13 pasos`, con consumo extra de batería.
5. Tras recoger ambas muestras, vuelve a la zona de base; si no tocó un astronauta en ese paso, recibe `+50` y termina con éxito.

## 14. Respuesta al reto del equipo

La trampa principal era acercarse y alejarse repetidamente para cobrar progreso. Se evita usando la diferencia entre distancia anterior y actual: acercarse es positivo y alejarse es negativo. Además, cada muestra solo puede recogerse una vez y el progreso solo se calcula hacia la muestra de la etapa actual.

