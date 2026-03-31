"""Optimiza una red dirigida hacia una bodega con restricción monotónica en `y`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional
import math

import networkx as nx


Point3D = Tuple[float, float, float]


@dataclass
class ArborescenceResult:
    """Resultado de una arborescencia mínima dirigida hacia la bodega."""
    total_cost: float
    edges_to_parent: List[Tuple[int, int, float]]
    # cada tupla es: (child, parent, cost)


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


def deduplicate_points(points: List[Point3D], ndigits: int = 9) -> List[Point3D]:
    """Elimina puntos duplicados redondeando coordenadas para estabilizar floats."""
    seen = set()
    unique: List[Point3D] = []

    for p in points:
        key = (round(p[0], ndigits), round(p[1], ndigits), round(p[2], ndigits))
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return unique


def manhattan_3d(a: Point3D, b: Point3D) -> float:
    """Calcula la distancia Manhattan entre dos puntos 3D."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def all_integers(values: List[float], tol: float = 1e-9) -> bool:
    """Indica si todos los valores son enteros dentro de una tolerancia."""
    return all(abs(v - round(v)) <= tol for v in values)


def candidate_warehouses(
    points: List[Point3D],
    fixed_y: float,
    exact_integer_search_limit: int = 200_000,
) -> List[Point3D]:
    """Genera ubicaciones candidatas para la bodega sobre el plano `y = fixed_y`."""
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


def evaluate_warehouse_monotone_y(
    points: List[Point3D],
    warehouse: Point3D,
) -> Optional[ArborescenceResult]:
    """
    Construye una red compartida mínima hacia la bodega bajo la restricción:
    en cada salto debe cumplirse y_parent <= y_child.

    Implementación:
    - grafo original conceptual: child -> parent
    - para usar minimum_spanning_arborescence construimos el grafo invertido:
      parent -> child
    - la bodega queda como raíz del árbol
    """
    all_nodes = points + [warehouse]
    warehouse_idx = len(points)

    # Factibilidad básica:
    # si algún punto está por debajo de la bodega, no puede llegar "solo bajando"
    for p in points:
        if p[1] < warehouse[1]:
            return None

    G = nx.DiGraph()

    for i in range(len(all_nodes)):
        G.add_node(i)

    # En el grafo invertido agregamos parent -> child
    # donde child puede bajar hacia parent en el modelo original
    for parent_idx, parent in enumerate(all_nodes):
        for child_idx, child in enumerate(all_nodes):
            if parent_idx == child_idx:
                continue

            # La bodega debe ser la raíz, así que no permitimos arcos que entren a ella
            if child_idx == warehouse_idx:
                continue

            # Restricción monotónica:
            # en original child -> parent solo si parent.y <= child.y
            if parent[1] <= child[1]:
                cost = manhattan_3d(parent, child)
                G.add_edge(parent_idx, child_idx, weight=cost)

    # Si algún nodo no bodega no tiene ningún padre posible, es infactible
    for child_idx in range(len(points)):
        if G.in_degree(child_idx) == 0:
            return None

    # La bodega debe ser la raíz
    if G.in_degree(warehouse_idx) != 0:
        return None

    try:
        A = nx.minimum_spanning_arborescence(G, attr="weight")
    except nx.NetworkXException:
        return None

    # Validación estructural
    if set(A.nodes()) != set(G.nodes()):
        return None

    if A.in_degree(warehouse_idx) != 0:
        return None

    for node in range(len(points)):
        if A.in_degree(node) != 1:
            return None

    # Convertimos a formato child -> parent
    edges_to_parent: List[Tuple[int, int, float]] = []
    total_cost = 0.0

    for parent_idx, child_idx, data in A.edges(data=True):
        w = float(data["weight"])
        total_cost += w
        edges_to_parent.append((child_idx, parent_idx, w))

    return ArborescenceResult(
        total_cost=total_cost,
        edges_to_parent=edges_to_parent,
    )


def find_best_warehouse_monotone_y(
    points: List[Point3D],
    fixed_y: float = -40.0,
    exact_integer_search_limit: int = 200_000,
) -> Tuple[Point3D, ArborescenceResult]:
    """Busca la bodega factible con menor costo total bajo restricción monotónica."""
    candidates = candidate_warehouses(
        points=points,
        fixed_y=fixed_y,
        exact_integer_search_limit=exact_integer_search_limit,
    )

    best_warehouse: Optional[Point3D] = None
    best_result: Optional[ArborescenceResult] = None

    for warehouse in candidates:
        result = evaluate_warehouse_monotone_y(points, warehouse)
        if result is None:
            continue

        if best_result is None or result.total_cost < best_result.total_cost:
            best_warehouse = warehouse
            best_result = result

    if best_warehouse is None or best_result is None:
        raise RuntimeError(
            "No existe solución factible. Revisa si hay puntos con y < -40 "
            "o si la restricción hace imposible conectar todo."
        )

    return best_warehouse, best_result


def format_node_name(index: int, num_original_points: int) -> str:
    """Etiqueta un índice como punto original o como bodega."""
    if index < num_original_points:
        return f"P{index}"
    return "BODEGA"


def save_solution(
    path: str,
    points: List[Point3D],
    warehouse: Point3D,
    result: ArborescenceResult,
) -> None:
    """Guarda la solución dirigida en un archivo de texto legible."""
    num_original_points = len(points)
    all_nodes = points + [warehouse]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write("SOLUCIÓN\n")
        f.write(f"Bodega óptima: {warehouse}\n")
        f.write(f"Costo total de la red compartida: {result.total_cost}\n")
        f.write("\nNodos:\n")

        for i, p in enumerate(points):
            f.write(f"P{i}: {p}\n")
        f.write(f"BODEGA: {warehouse}\n")

        f.write("\nAristas dirigidas hacia la bodega:\n")
        for child, parent, cost in result.edges_to_parent:
            child_name = format_node_name(child, num_original_points)
            parent_name = format_node_name(parent, num_original_points)
            child_point = all_nodes[child]
            parent_point = all_nodes[parent]

            f.write(
                f"{child_name} {child_point} -> "
                f"{parent_name} {parent_point} | costo={cost}\n"
            )


def main() -> None:
    """Ejecuta la optimización dirigida y exporta la solución encontrada."""
    base_dir = Path(__file__).resolve().parent
    input_file = base_dir / "input" / "puntos.txt"
    output_file = base_dir / "output" / "solucion_bodega_monotona_y.txt"
    fixed_y = -40.0

    points = read_points_txt(input_file)
    original_count = len(points)
    points = deduplicate_points(points)

    print(f"Puntos originales: {original_count}")
    print(f"Puntos únicos: {len(points)}")

    warehouse, result = find_best_warehouse_monotone_y(
        points=points,
        fixed_y=fixed_y,
        exact_integer_search_limit=200_000,
    )

    print("\nBodega óptima:", warehouse)
    print("Costo total de la red compartida:", result.total_cost)
    print("\nAristas child -> parent:")
    for child, parent, cost in result.edges_to_parent:
        print(f"{child} -> {parent}   costo={cost}")

    save_solution(output_file, points, warehouse, result)
    print(f"\nResultado guardado en: {output_file}")


if __name__ == "__main__":
    main()
