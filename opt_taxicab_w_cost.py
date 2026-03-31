"""Ubica una bodega en un plano fijo minimizando el costo de una red Manhattan compartida."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional
import math


Point3D = Tuple[float, float, float]


@dataclass
class MSTResult:
    """Resultado de un árbol recubridor mínimo sobre el grafo completo."""
    total_cost: float
    edges: List[Tuple[int, int, float]]


def read_points_txt(path: str) -> List[Point3D]:
    """Lee puntos 3D desde un archivo de texto y valida su formato."""
    points: List[Point3D] = []

    with open(path, "r", encoding="utf-8") as f:
        for line_num, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) != 3:
                raise ValueError(
                    f"Línea {line_num}: se esperaban 3 valores y llegaron {len(parts)}"
                )

            try:
                x, y, z = map(float, parts)
            except ValueError as exc:
                raise ValueError(
                    f"Línea {line_num}: no se pudo convertir a número"
                ) from exc

            points.append((x, y, z))

    if not points:
        raise ValueError("El archivo no contiene puntos")

    return points


def manhattan_3d(a: Point3D, b: Point3D) -> float:
    """Calcula la distancia Manhattan entre dos puntos 3D."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def prim_mst(points: List[Point3D]) -> MSTResult:
    """Construye un MST con Prim sobre el grafo completo inducido por los puntos."""
    n = len(points)
    if n == 1:
        return MSTResult(total_cost=0.0, edges=[])

    in_tree = [False] * n
    min_cost = [math.inf] * n
    parent = [-1] * n

    min_cost[0] = 0.0
    total_cost = 0.0
    edges: List[Tuple[int, int, float]] = []

    for _ in range(n):
        u = -1
        best = math.inf

        for i in range(n):
            if not in_tree[i] and min_cost[i] < best:
                best = min_cost[i]
                u = i

        if u == -1:
            raise RuntimeError("No se pudo construir el MST")

        in_tree[u] = True
        total_cost += min_cost[u]

        if parent[u] != -1:
            edges.append((parent[u], u, min_cost[u]))

        # El grafo es completo: al entrar un nodo al árbol, reevalúa a todos los demás.
        for v in range(n):
            if not in_tree[v]:
                d = manhattan_3d(points[u], points[v])
                if d < min_cost[v]:
                    min_cost[v] = d
                    parent[v] = u

    return MSTResult(total_cost=total_cost, edges=edges)


def all_integers(values: List[float], tol: float = 1e-9) -> bool:
    """Indica si todos los valores son enteros dentro de una tolerancia."""
    return all(abs(v - round(v)) <= tol for v in values)


def candidate_warehouses(
    points: List[Point3D],
    fixed_y: float,
    exact_integer_search_limit: int = 200_000,
) -> List[Point3D]:
    """
    Genera candidatos para la bodega en y = fixed_y.

    Si todas las coordenadas x y z son enteras y el rango no explota,
    busca exacto en toda la caja entera.

    Si no, usa candidatos tipo rejilla inducida por x y z observados.
    Eso es una heurística muy razonable y suele funcionar bien.
    """
    xs = [p[0] for p in points]
    zs = [p[2] for p in points]

    xs_unique = sorted(set(xs))
    zs_unique = sorted(set(zs))

    xs_are_int = all_integers(xs)
    zs_are_int = all_integers(zs)

    if xs_are_int and zs_are_int:
        min_x = int(round(min(xs)))
        max_x = int(round(max(xs)))
        min_z = int(round(min(zs)))
        max_z = int(round(max(zs)))

        grid_size = (max_x - min_x + 1) * (max_z - min_z + 1)

        if grid_size <= exact_integer_search_limit:
            return [
                (float(x), fixed_y, float(z))
                for x in range(min_x, max_x + 1)
                for z in range(min_z, max_z + 1)
            ]

    return [(x, fixed_y, z) for x in xs_unique for z in zs_unique]


def evaluate_warehouse(points: List[Point3D], warehouse: Point3D) -> MSTResult:
    """Evalúa el costo de conectar todos los puntos y la bodega vía MST."""
    augmented = points + [warehouse]
    return prim_mst(augmented)


def find_best_warehouse(
    points: List[Point3D],
    fixed_y: float = -40.0,
    exact_integer_search_limit: int = 200_000,
) -> Tuple[Point3D, MSTResult]:
    """Explora candidatos y devuelve la bodega con menor costo total de red."""
    candidates = candidate_warehouses(
        points=points,
        fixed_y=fixed_y,
        exact_integer_search_limit=exact_integer_search_limit,
    )

    best_warehouse: Optional[Point3D] = None
    best_result: Optional[MSTResult] = None

    for warehouse in candidates:
        result = evaluate_warehouse(points, warehouse)

        if best_result is None or result.total_cost < best_result.total_cost:
            best_warehouse = warehouse
            best_result = result

    if best_warehouse is None or best_result is None:
        raise RuntimeError("No se encontró una bodega válida")

    return best_warehouse, best_result


def format_node_name(index: int, num_original_points: int) -> str:
    """Etiqueta un nodo como punto original o como la bodega agregada."""
    if index < num_original_points:
        return f"P{index}"
    return "BODEGA"


def save_solution(
    path: str,
    points: List[Point3D],
    warehouse: Point3D,
    mst: MSTResult,
) -> None:
    """Persistе la solución en un archivo de texto legible."""
    num_original_points = len(points)
    all_nodes = points + [warehouse]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write("SOLUCIÓN\n")
        f.write(f"Bodega óptima: {warehouse}\n")
        f.write(f"Costo total de red compartida: {mst.total_cost}\n")
        f.write("\nNodos:\n")

        for i, p in enumerate(points):
            f.write(f"P{i}: {p}\n")
        f.write(f"BODEGA: {warehouse}\n")

        f.write("\nAristas del MST:\n")
        for u, v, w in mst.edges:
            name_u = format_node_name(u, num_original_points)
            name_v = format_node_name(v, num_original_points)
            pu = all_nodes[u]
            pv = all_nodes[v]
            f.write(f"{name_u} {pu} <-> {name_v} {pv} | costo={w}\n")


def deduplicate_points(points, tol=1e-9):
    """Elimina puntos duplicados usando redondeo tolerante para floats."""
    seen = set()
    unique = []

    for p in points:
        key = (
            round(p[0] / tol) * tol,
            round(p[1] / tol) * tol,
            round(p[2] / tol) * tol,
        )
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique


def main() -> None:
    """Ejecuta el flujo completo de búsqueda de bodega y exporta la solución."""
    base_dir = Path(__file__).resolve().parent
    input_file = base_dir / "input" / "puntos.txt"
    output_file = base_dir / "output" / "solucion_bodega_mst.txt"
    fixed_y = -40.0

    points = read_points_txt(input_file)
    # Se deduplican puntos para no sesgar el costo ni repetir nodos en la salida.
    points = deduplicate_points(points)

    warehouse, mst = find_best_warehouse(
        points=points,
        fixed_y=fixed_y,
        exact_integer_search_limit=200_000,
    )

    print("Bodega óptima:", warehouse)
    print("Costo total de la red compartida:", mst.total_cost)
    print("Aristas:")
    for u, v, w in mst.edges:
        print(f"  {u} <-> {v}   costo={w}")

    save_solution(output_file, points, warehouse, mst)
    print(f"\nResultado guardado en: {output_file}")


if __name__ == "__main__":
    main()
