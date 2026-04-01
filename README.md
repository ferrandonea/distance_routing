# distance-routing

Herramientas en Python para optimizacion de rutas y ubicacion de bodegas en 3D usando distancia Manhattan.

El repositorio expone una libreria reusable en `src/distance_routing/`, una CLI unica para ejecutar cada algoritmo y wrappers delgados para mantener compatibilidad con los scripts historicos.

## Capacidades

- ruta abierta minima que visita todos los puntos una vez;
- ruta cerrada minima que vuelve al origen;
- bodega optima libre en 3D por mediana taxicab;
- bodega optima sobre un plano `y` fijo;
- bodega optima minimizando una red compartida via MST;
- bodega optima con red dirigida monotona sobre el eje `y`.

## Estructura del proyecto

```txt
.
├── input/
│   └── puntos.txt
├── output/
├── src/
│   └── distance_routing/
│       ├── __main__.py
│       ├── candidates.py
│       ├── cli.py
│       ├── geometry.py
│       ├── io_utils.py
│       ├── routing.py
│       ├── types.py
│       ├── visualization.py
│       └── warehouse.py
├── tests/
├── min_distance.py
├── opt_taxicab_high_fixed.py
├── opt_taxicab_high_gravity.py
├── opt_taxicab_storage.py
├── opt_taxicab_w_cost.py
├── pyproject.toml
└── README.md
```

## Requisitos

- Python 3.12+
- `networkx` para la variante de arborescencia monotona
- `matplotlib` para generar visualizaciones 3D

## Instalacion

```bash
uv sync
```

## Uso

La interfaz principal es:

```bash
uv run distance-routing <subcomando> [opciones]
```

Alternativamente, sin usar el entry point:

```bash
uv run python -m distance_routing <subcomando> [opciones]
```

### Subcomandos

- `run-all`: ejecuta todos los algoritmos en una sola corrida.
- `open-route`: ruta abierta minima.
- `closed-route`: ruta cerrada minima.
- `warehouse-median`: bodega optima libre en 3D.
- `warehouse-fixed`: bodega optima con `y` fija.
- `warehouse-mst`: bodega optima por red compartida MST.
- `warehouse-monotone`: bodega optima por red dirigida monotona en `y`.

### Argumentos comunes

- `--input`: archivo de entrada. Default `input/puntos.txt`.
- `--output`: archivo de salida cuando aplica.
- `--fixed-y`: default `-40.0` para algoritmos restringidos a un plano.
- `--plot`: imagen de visualizacion 3D para `warehouse-monotone`.
- `--output-dir`: carpeta de salida para `run-all`. Default `output/`.

### Ejemplos

```bash
uv run distance-routing run-all --fixed-y -40
uv run distance-routing open-route
uv run distance-routing closed-route --start 0
uv run distance-routing warehouse-median
uv run distance-routing warehouse-fixed --fixed-y -40
uv run distance-routing warehouse-mst --output output/red_mst.txt
uv run distance-routing warehouse-monotone --fixed-y -40
uv run distance-routing warehouse-monotone --fixed-y -40 --plot output/monotone_3d.png
```

## Formato de entrada

El archivo de entrada debe contener una terna `x y z` por linea:

```txt
-287 2 -736
-286 -4 -729
-271 2 -714
```

Reglas:

- se permiten enteros o decimales;
- las lineas vacias se ignoran;
- cada linea debe tener exactamente 3 valores;
- los algoritmos de red deduplican puntos antes de optimizar.

## Salidas por defecto

- `run-all` escribe `output/ruta_abierta.txt`, `output/ruta_cerrada.txt`, `output/solucion_bodega_mst.txt` y `output/solucion_bodega_monotona_y.txt`
- `open-route` escribe `output/ruta_abierta.txt`
- `closed-route` escribe `output/ruta_cerrada.txt`
- `warehouse-mst` escribe `output/solucion_bodega_mst.txt`
- `warehouse-monotone` escribe `output/solucion_bodega_monotona_y.txt`
- `warehouse-median` y `warehouse-fixed` imprimen por consola y solo escriben archivo si se pasa `--output`
- `warehouse-monotone --plot ...` genera ademas una imagen 3D con puntos, bodega y caminos

La carpeta `output/` se considera runtime y no forma parte de los datos fuente del proyecto.

## Uso como libreria

Los algoritmos principales estan separados por responsabilidad:

- [routing.py](/Users/franciscoerrandonea/code/distance_routing/src/distance_routing/routing.py): rutas exactas abiertas y cerradas.
- [warehouse.py](/Users/franciscoerrandonea/code/distance_routing/src/distance_routing/warehouse.py): ubicacion de bodegas y redes compartidas.
- [geometry.py](/Users/franciscoerrandonea/code/distance_routing/src/distance_routing/geometry.py): distancia Manhattan y deduplicacion.
- [io_utils.py](/Users/franciscoerrandonea/code/distance_routing/src/distance_routing/io_utils.py): lectura de puntos y escritura de reportes.
- [types.py](/Users/franciscoerrandonea/code/distance_routing/src/distance_routing/types.py): dataclasses y tipos compartidos.
- [visualization.py](/Users/franciscoerrandonea/code/distance_routing/src/distance_routing/visualization.py): renderizado 3D del caso monotono.

Esto permite usar la logica desde otros scripts sin depender de la CLI.

## Desarrollo

Ejecutar tests:

```bash
uv run python -m unittest discover -s tests -v
```

Ver ayuda de la CLI:

```bash
uv run distance-routing --help
```

## Compatibilidad

Los scripts historicos en la raiz siguen disponibles:

- `min_distance.py`
- `opt_taxicab_storage.py`
- `opt_taxicab_high_fixed.py`
- `opt_taxicab_w_cost.py`
- `opt_taxicab_high_gravity.py`

Esos archivos ahora son wrappers delgados que delegan a la CLI nueva.
