# Ambiente v0.1 — Autonomous Rally

## 1. Ambiente

El agente es un vehículo autónomo situado en una pista cerrada de asfalto, con zonas de césped, curvas y obstáculos. Su meta es completar una vuelta, cruzar los checkpoints `1`, `2` y `3` en orden y terminar sin salirse de la pista.

## 2. Mapa

La pista mide `30 m × 20 m`. El límite exterior no se puede atravesar. El vehículo inicia en `S`, debe pasar por los checkpoints numerados y regresar a `G`.

```text
                 30 m
        ┌──────────────────────────────┐
        │       [1]───╮                │
        │   ┌─────────┘                │
        │   │   █ O1          O2 █     │
        │ S─┘                    └─[2] │ 20 m
        │   ┌────── O3 ─────────────┐  │
        │   │                 [3]───┘  │
        │   └───────────────────── G   │
        └──────────────────────────────┘

        S = inicio       G = meta
        [1..3] = checkpoints obligatorios
        O1..O3 = obstáculos fijos
```

La línea de carrera se interpreta como una pista de `4 m` de ancho alrededor del circuito. El dibujo es esquemático y las posiciones exactas se parametrizan antes de ejecutar el episodio.

## 3. Variables con límites

| Variable | Significado | Unidad | Mínimo | Máximo |
|---|---|---:|---:|---:|
| `x` | posición horizontal | m | `0` | `30` |
| `y` | posición vertical | m | `0` | `20` |
| `v` | velocidad lineal | m/s | `0` | `8` |
| `a` | aceleración | m/s² | `-4` | `3` |
| `heading` | orientación | grados | `-180` | `180` |
| `yaw_rate` | velocidad de giro | grados/s | `-90` | `90` |
| `battery` | batería restante | % | `0` | `100` |
| `checkpoint` | último checkpoint válido | índice | `0` | `3` |
| `time` | tiempo transcurrido | s | `0` | `120` |
| `collision_count` | choques acumulados | conteo | `0` | `10` |
| `cargo` | objeto transportado | booleano | `0` | `1` |
| `slip` | factor de poca adherencia | coeficiente | `0` | `1` |

La observación incluye posición relativa al siguiente checkpoint, velocidad, orientación, batería, checkpoint actual, sensores de borde y sensores de obstáculos. `collision_count` y el estado interno exacto de los obstáculos no se muestran directamente.

## 4. Obstáculos

Hay tres bloques fijos: `O1=(12,14)`, `O2=(23,13)` y `O3=(15,5)`, todos de aproximadamente `2 m × 1 m`. También hay un límite físico exterior y zonas de césped fuera de la pista.

Un contacto con un bloque cuenta como choque, aplica `-20` de recompensa y reduce la velocidad. El episodio termina en fracaso si el vehículo atraviesa el límite, acumula `3` choques o queda inmovilizado durante `5 s`. Un roce leve con el borde solo aplica `-5` y permite continuar.

## 5. Clima

La condición base es clima seco, sin viento y con adherencia `slip=0.9`. La perturbación experimental `wet` representa lluvia: la adherencia baja a `slip=0.6`, aumenta la distancia de frenado y añade un desvío lateral aleatorio de hasta `0.25 m` por segundo. El clima se fija al inicio del episodio y el agente no recibe su nombre directamente; debe inferir sus efectos.

## 6. Gravedad

La gravedad es `9.8 m/s²` hacia abajo. En la versión plana no produce movimiento vertical ni cambia la posición del vehículo, pero sí se considera en el modelo de adherencia y en la fuerza normal usada para calcular el agarre. El salto usa esta misma gravedad en la extensión opcional.

## 7. Acciones

Todas las acciones continuas están normalizadas entre `-1` y `1`:

| Acción | Rango | Efecto |
|---|---:|---|
| `move.forward` | `[-1, 1]` | avance/freno; negativo frena o retrocede lentamente, positivo acelera |
| `move.turn` | `[-1, 1]` | giro a izquierda/derecha |
| `jump` | `[-1, 1]` | `1` solicita saltar; solo se acepta cerca de una rampa y a `v ≤ 3 m/s` |
| `grab` | `[-1, 1]` | `1` solicita agarrar/soltar; solo funciona a menos de `1 m` del objeto y a `v ≤ 1 m/s` |

En el rally base no hay objetos agarrables ni rampas, por lo que `jump` y `grab` no producen efecto y reciben `-0.5`. Se conservan para hacer compatible el contrato con futuros mapas.

## 8. Paso (`step`)

Cada paso simula `0.1 s`: el agente recibe la observación, elige acciones, el simulador aplica aceleración, giro, adherencia, gravedad y colisiones, actualiza posición, velocidad, batería y checkpoints, calcula la recompensa y entrega la nueva observación junto con el estado de terminación.

## 9. Truncamiento

El episodio se trunca, sin considerarse éxito ni fracaso, al alcanzar `1.200 pasos` (`120 s`) o cuando la batería llega a `0%`. Cruzar todos los checkpoints y regresar a `G` tiene prioridad y se marca como éxito antes de aplicar el truncamiento.

## 10. Premio y penalización

```text
-0.10                 por cada paso
+0.50 × progreso      por cada metro nuevo hacia el checkpoint
+10                   al cruzar un checkpoint nuevo
+100                  al completar la vuelta y llegar a G
-20                   por choque
-5                    por roce fuerte con el borde
-0.05 × |giro|        por giro brusco
-0.10 × |aceleración|  por aceleración/frenado brusco
-0.50                  por jump/grab inválido
-0.20                  por cada 1% de batería consumido
-100                  por fracaso por salida de pista
```

Cada checkpoint solo otorga premio una vez y debe respetarse el orden `1 → 2 → 3`. El progreso usa la distancia mínima histórica al siguiente checkpoint, evitando ganar puntos avanzando y retrocediendo repetidamente. La meta solo se concede con el orden correcto, regreso a `G` y vehículo dentro de los límites.

