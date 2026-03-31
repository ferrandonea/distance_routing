# distance-routing

Herramientas en Python para optimización de rutas y ubicación de bodegas en 3D usando distancia Manhattan.

El repositorio expone una librería reusable en `src/distance_routing/`, una CLI única para ejecutar cada algoritmo y wrappers delgados para mantener compatibilidad con los scripts históricos.

## Capacidades

- ruta abierta mínima que visita todos los puntos una vez;
- ruta cerrada mínima que vuelve al origen;
- bodega óptima libre en 3D por mediana taxicab;
- bodega óptima sobre un plano `y` fijo;
- bodega óptima minimizando una red compartida vía MST;
- bodega óptima con red dirigida monotónica sobre el eje `y`.

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
- `networkx` para la variante de arborescencia monotónica

## Instalación

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

- `open-route`: ruta abierta mínima.
- `closed-route`: ruta cerrada mínima.
- `warehouse-median`: bodega óptima libre en 3D.
- `warehouse-fixed`: bodega óptima con `y` fija.
- `warehouse-mst`: bodega óptima por red compartida MST.
- `warehouse-monotone`: bodega óptima por red dirigida monotónica en `y`.

### Argumentos comunes

- `--input`: archivo de entrada. Default `input/puntos.txt`.
- `--output`: archivo de salida cuando aplica.
- `--fixed-y`: default `-40.0` para algoritmos restringidos a un plano.

### Ejemplos

```bash
uv run distance-routing open-route
uv run distance-routing closed-route --start 0
uv run distance-routing warehouse-median
uv run distance-routing warehouse-fixed --fixed-y -40
uv run distance-routing warehouse-mst --output output/red_mst.txt
uv run distance-routing warehouse-monotone --fixed-y -40
```

## Formato de entrada

El archivo de entrada debe contener una terna `x y z` por línea:

```txt
-287 2 -736
-286 -4 -729
-271 2 -714
```

Reglas:

- se permiten enteros o decimales;
- las líneas vacías se ignoran;
- cada línea debe tener exactamente 3 valores;
- los algoritmos de red deduplican puntos antes de optimizar.

## Salidas por defecto

- `open-route` escribe `output/ruta_abierta.txt`
- `closed-route` escribe `output/ruta_cerrada.txt`
- `warehouse-mst` escribe `output/solucion_bodega_mst.txt`
- `warehouse-monotone` escribe `output/solucion_bodega_monotona_y.txt`
- `warehouse-median` y `warehouse-fixed` imprimen por consola y sólo escriben archivo si se pasa `--output`

La carpeta `output/` se considera runtime y no forma parte de los datos fuente del proyecto.

## Uso como librería

Los algoritmos principales están separados por responsabilidad:

- [routing.py](/Users/franciscoerrandonea/code/distance_routing/src/distance_routing/routing.py): rutas exactas abiertas y cerradas.
- [warehouse.py](/Users/franciscoerrandonea/code/distance_routing/src/distance_routing/warehouse.py): ubicación de bodegas y redes compartidas.
- [geometry.py](/Users/franciscoerrandonea/code/distance_routing/src/distance_routing/geometry.py): distancia Manhattan y deduplicación.
- [io_utils.py](/Users/franciscoerrandonea/code/distance_routing/src/distance_routing/io_utils.py): lectura de puntos y escritura de reportes.
- [types.py](/Users/franciscoerrandonea/code/distance_routing/src/distance_routing/types.py): dataclasses y tipos compartidos.

Esto permite usar la lógica desde otros scripts sin depender de la CLI.

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

Los scripts históricos en la raíz siguen disponibles:

- `min_distance.py`
- `opt_taxicab_storage.py`
- `opt_taxicab_high_fixed.py`
- `opt_taxicab_w_cost.py`
- `opt_taxicab_high_gravity.py`

Esos archivos ahora son wrappers delgados que delegan a la CLI nueva.
