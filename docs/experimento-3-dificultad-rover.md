# Experimento 3: dificultad progresiva del rover

Este experimento compara el mapa normal con dos cambios controlados:

- **A — salto útil:** una fila de rocas pequeñas cruza el camino corto hacia la muestra 1. Saltar permite conservar la ruta directa; el salto no entrega recompensa por sí mismo.
- **3D — mapa variable:** en cada episodio se desplazan muestras, asteroides, cráteres y astronautas, manteniendo límites, separaciones y una ruta comprobable.
- **3E — terreno:** añade tres zonas de arena y una franja de pendiente con consumo y velocidad modificados; el salto no entrega recompensa.

La evaluación se hace sobre 50 semillas por variante y registra misiones completas, batería restante, pasos usados y causa de fallo. La política manual se usa como control de que cada variante es resoluble antes de interpretar PPO.

Orden experimental:

1. Evaluar PPO en el mapa normal.
2. Evaluar la política manual en normal, 3D y 3E.
3. Entrenar PPO en el mapa normal y en mapas aleatorios con semillas separadas.
4. Si PPO no aprende desde cero en 3D o 3E, continuar desde el modelo normal y ajustar progresivamente la dificultad.

El resultado de cada episodio queda resumido por `mars_rover.experiment3`. Las causas distinguen choque, cráter, astronauta, batería, tiempo agotado y victoria.
