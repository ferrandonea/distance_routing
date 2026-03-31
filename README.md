# Distance Routing

Scripts en Python para resolver variantes simples de optimización geométrica en 3D usando distancia Manhattan (taxicab).

El proyecto trabaja sobre un conjunto de puntos en un archivo de texto y calcula:

- una ruta mínima abierta que visita todos los puntos una vez;
- una ruta mínima cerrada que vuelve al origen;
- una bodega óptima libre en 3D minimizando suma de distancias;
- una bodega óptima con `y` fija;
- una bodega con `y` fija minimizando el costo de una red compartida modelada como MST.

## Requisitos

- Python 3.12 o superior
- No hay dependencias externas

## Formato de entrada

El archivo `puntos.txt` debe contener una terna `x y z` por línea:

```txt
-287 2 -736
-286 -4 -729
-271 2 -714
```

Notas:

- Se permiten enteros o decimales.
- Las líneas vacías se ignoran.
- Cada línea debe tener exactamente 3 valores.

## Scripts

### `min_distance.py`

Calcula rutas mínimas exactas con distancia Manhattan:

- ruta abierta: visita todos los puntos sin volver al inicio;
- ruta cerrada: parte en el punto `0`, visita todos los puntos y vuelve al inicio.

Usa programación dinámica por subconjuntos, por lo que sirve bien para instancias pequeñas.

Salida:

- imprime resultados en consola;
- genera `ruta_abierta.txt`;
- genera `ruta_cerrada.txt`.

Ejecutar:

```bash
python min_distance.py
```

### `opt_taxicab_storage.py`

Calcula la bodega óptima libre en 3D para minimizar la suma de distancias Manhattan desde todos los puntos hacia una sola ubicación.

La solución usa la mediana por coordenada.

Ejecutar:

```bash
python opt_taxicab_storage.py
```

### `opt_taxicab_high_fixed.py`

Calcula la bodega óptima restringida al plano `y = -40` minimizando la suma de distancias Manhattan.

La solución usa la mediana en `x` y `z`, manteniendo `y` fija.

Ejecutar:

```bash
python opt_taxicab_high_fixed.py
```

### `opt_taxicab_w_cost.py`

Busca una bodega en el plano `y = -40` minimizando el costo total de una red compartida. Para cada candidato:

- agrega la bodega como un nodo más;
- construye un árbol recubridor mínimo (MST) con distancia Manhattan;
- compara el costo total de la red.

El script además elimina puntos duplicados antes de optimizar.

Salida:

- imprime la solución en consola;
- genera `solucion_bodega_mst.txt`.

Ejecutar:

```bash
python opt_taxicab_w_cost.py
```

## Archivos relevantes

- `puntos.txt`: entrada principal.
- `ruta_abierta.txt`: salida de la ruta abierta.
- `ruta_cerrada.txt`: salida de la ruta cerrada.
- `solucion_bodega_mst.txt`: salida de la optimización con costo de red.

## Estructura del proyecto

```txt
.
├── min_distance.py
├── opt_taxicab_high_fixed.py
├── opt_taxicab_storage.py
├── opt_taxicab_w_cost.py
├── puntos.txt
└── README.md
```

## Observaciones

- `min_distance.py` resuelve el problema de forma exacta y su costo computacional crece rápido con el número de puntos.
- `opt_taxicab_storage.py` y `opt_taxicab_high_fixed.py` son métodos cerrados y muy baratos computacionalmente.
- `opt_taxicab_w_cost.py` mezcla búsqueda de candidatos con evaluación exacta por MST; puede crecer si el espacio de búsqueda es grande.
