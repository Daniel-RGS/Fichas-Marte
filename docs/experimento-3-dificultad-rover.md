# Experimento 3: dificultad progresiva del rover

Este experimento compara el mapa normal con dos cambios controlados:

- **A — salto útil:** una fila de rocas pequeñas cruza el camino corto hacia la muestra 1. Saltar permite conservar la ruta directa; el salto no entrega recompensa por sí mismo.
- **D — mapa variable:** en cada episodio se desplazan las muestras y los asteroides, manteniendo límites y separaciones para que ningún objeto aparezca dentro de otro.

La evaluación se hace sobre 50 semillas por variante y registra misiones completas, batería restante, pasos usados y causa de fallo. La política manual se usa como control de que cada variante es resoluble antes de interpretar PPO.

Orden experimental:

1. Evaluar PPO en el mapa normal.
2. Evaluar la política manual en normal, A y D.
3. Entrenar PPO en el mapa normal.
4. Si PPO no aprende desde cero en A o D, continuar desde el modelo normal y ajustar progresivamente la dificultad.

El resultado de cada episodio queda resumido por `mars_rover.experiment3`. Las causas distinguen choque, cráter, astronauta, batería, tiempo agotado y victoria.
