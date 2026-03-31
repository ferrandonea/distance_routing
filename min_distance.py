"""Calcula rutas mínimas abiertas y cerradas con distancia Manhattan en 3D."""

from itertools import combinations
from pathlib import Path


def read_points_txt(path):
    """Lee un archivo de puntos con formato `x y z`, una terna por línea."""
    points = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Línea {line_num}: esperaba 3 valores, encontré {len(parts)}")
            x, y, z = map(float, parts)
            points.append((x, y, z))
    return points


def manhattan_3d(a, b):
    """Devuelve la distancia Manhattan entre dos puntos 3D."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def tsp_manhattan_open(points):
    """Resuelve el TSP abierto exacto usando programación dinámica por subconjuntos."""
    n = len(points)
    dist = [[manhattan_3d(points[i], points[j]) for j in range(n)] for i in range(n)]

    dp = {}
    parent = {}

    for j in range(n):
        mask = 1 << j
        dp[(mask, j)] = 0
        parent[(mask, j)] = None

    # dp[(mask, j)] guarda el costo mínimo de visitar `mask` y terminar en `j`.
    for size in range(2, n + 1):
        for subset in combinations(range(n), size):
            mask = 0
            for v in subset:
                mask |= 1 << v

            for j in subset:
                prev_mask = mask ^ (1 << j)
                best = float("inf")
                best_prev = None

                for k in subset:
                    if k == j:
                        continue
                    cost = dp[(prev_mask, k)] + dist[k][j]
                    if cost < best:
                        best = cost
                        best_prev = k

                dp[(mask, j)] = best
                parent[(mask, j)] = best_prev

    full_mask = (1 << n) - 1

    best_cost = float("inf")
    best_end = None
    for j in range(n):
        if dp[(full_mask, j)] < best_cost:
            best_cost = dp[(full_mask, j)]
            best_end = j

    path = []
    mask = full_mask
    j = best_end
    while j is not None:
        path.append(j)
        prev_j = parent[(mask, j)]
        mask ^= 1 << j
        j = prev_j

    path.reverse()
    return best_cost, path


def tsp_manhattan_cycle(points, start=0):
    """Resuelve el TSP cerrado exacto fijando un nodo inicial y final."""
    n = len(points)
    dist = [[manhattan_3d(points[i], points[j]) for j in range(n)] for i in range(n)]

    dp = {}
    parent = {}

    start_mask = 1 << start
    dp[(start_mask, start)] = 0
    parent[(start_mask, start)] = None

    nodes = [i for i in range(n) if i != start]

    for size in range(1, n):
        for subset in combinations(nodes, size):
            mask = start_mask
            for v in subset:
                mask |= 1 << v

            for j in subset:
                prev_mask = mask ^ (1 << j)
                best = float("inf")
                best_prev = None

                # Cuando el subconjunto previo sólo contiene al origen, la transición
                # válida es salir directamente desde `start`.
                prev_candidates = [start] if prev_mask == start_mask else [k for k in subset if k != j]

                for k in prev_candidates:
                    if (prev_mask, k) in dp:
                        cost = dp[(prev_mask, k)] + dist[k][j]
                        if cost < best:
                            best = cost
                            best_prev = k

                dp[(mask, j)] = best
                parent[(mask, j)] = best_prev

    full_mask = (1 << n) - 1

    best_cost = float("inf")
    best_end = None
    for j in nodes:
        cost = dp[(full_mask, j)] + dist[j][start]
        if cost < best_cost:
            best_cost = cost
            best_end = j

    path = [start]
    reverse_path = []

    mask = full_mask
    j = best_end
    while j != start:
        reverse_path.append(j)
        prev_j = parent[(mask, j)]
        mask ^= 1 << j
        j = prev_j

    path.extend(reversed(reverse_path))
    path.append(start)

    return best_cost, path


def save_route(path_out, points, route, total_cost):
    """Guarda una ruta calculada en un archivo de texto legible."""
    path_out.parent.mkdir(parents=True, exist_ok=True)
    with open(path_out, "w", encoding="utf-8") as f:
        f.write(f"Distancia total: {total_cost}\n")
        f.write("Orden de visita:\n")
        for idx in route:
            x, y, z = points[idx]
            f.write(f"{idx}: {x} {y} {z}\n")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    input_file = base_dir / "input" / "puntos.txt"
    open_output_file = base_dir / "output" / "ruta_abierta.txt"
    closed_output_file = base_dir / "output" / "ruta_cerrada.txt"

    points = read_points_txt(input_file)

    if len(points) == 0:
        raise ValueError("El archivo no contiene puntos")
    if len(points) == 1:
        print("Solo hay un punto:", points[0])
    else:
        open_cost, open_route = tsp_manhattan_open(points)
        print("Ruta abierta mínima")
        print("Distancia total:", open_cost)
        print("Orden índices:", open_route)
        print("Puntos:")
        for i in open_route:
            print(points[i])

        save_route(open_output_file, points, open_route, open_cost)

        cycle_cost, cycle_route = tsp_manhattan_cycle(points, start=0)
        print("\nRuta cerrada mínima")
        print("Distancia total:", cycle_cost)
        print("Orden índices:", cycle_route)
        print("Puntos:")
        for i in cycle_route:
            print(points[i])

        save_route(closed_output_file, points, cycle_route, cycle_cost)
