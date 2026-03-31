"""Algoritmos para ubicar bodegas y evaluar redes compartidas."""

from __future__ import annotations

import math
import statistics

import networkx as nx

from .candidates import candidate_warehouses
from .geometry import manhattan_3d
from .types import (
    ArborescenceResult,
    MSTResult,
    Point3D,
    WarehouseArborescenceResult,
    WarehouseLocationResult,
    WarehouseMSTResult,
)


def taxicab_median(points: list[Point3D]) -> WarehouseLocationResult:
    """Calcula la bodega óptima libre en 3D con la mediana por coordenada."""

    if not points:
        raise ValueError("Se requiere al menos un punto")

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    zs = [point[2] for point in points]
    location = (
        statistics.median(xs),
        statistics.median(ys),
        statistics.median(zs),
    )
    distances = [manhattan_3d(point, location) for point in points]
    return WarehouseLocationResult(
        location=location,
        total_distance=sum(distances),
        distances=distances,
    )


def taxicab_median_fixed_y(
    points: list[Point3D],
    fixed_y: float,
) -> WarehouseLocationResult:
    """Calcula la bodega óptima restringida al plano `y = fixed_y`."""

    if not points:
        raise ValueError("Se requiere al menos un punto")

    xs = [point[0] for point in points]
    zs = [point[2] for point in points]
    location = (
        statistics.median(xs),
        fixed_y,
        statistics.median(zs),
    )
    distances = [manhattan_3d(point, location) for point in points]
    return WarehouseLocationResult(
        location=location,
        total_distance=sum(distances),
        distances=distances,
    )


def prim_mst(points: list[Point3D]) -> MSTResult:
    """Construye un árbol recubridor mínimo sobre el grafo completo de puntos."""

    n = len(points)
    if n == 0:
        raise ValueError("Se requiere al menos un punto")
    if n == 1:
        return MSTResult(total_cost=0.0, edges=[])

    in_tree = [False] * n
    min_cost = [math.inf] * n
    parent = [-1] * n
    min_cost[0] = 0.0
    edges: list[tuple[int, int, float]] = []
    total_cost = 0.0

    for _ in range(n):
        current = -1
        best = math.inf
        for i in range(n):
            if not in_tree[i] and min_cost[i] < best:
                best = min_cost[i]
                current = i

        if current == -1:
            raise RuntimeError("No se pudo construir el MST")

        in_tree[current] = True
        total_cost += min_cost[current]

        if parent[current] != -1:
            edges.append((parent[current], current, min_cost[current]))

        for neighbor in range(n):
            if in_tree[neighbor]:
                continue
            distance = manhattan_3d(points[current], points[neighbor])
            if distance < min_cost[neighbor]:
                min_cost[neighbor] = distance
                parent[neighbor] = current

    return MSTResult(total_cost=total_cost, edges=edges)


def best_warehouse_mst(
    points: list[Point3D],
    fixed_y: float = -40.0,
    exact_integer_search_limit: int = 200_000,
) -> WarehouseMSTResult:
    """Busca la bodega que minimiza el costo de una red compartida vía MST."""

    if not points:
        raise ValueError("Se requiere al menos un punto")

    best_result: WarehouseMSTResult | None = None
    for warehouse in candidate_warehouses(points, fixed_y, exact_integer_search_limit):
        mst = prim_mst(points + [warehouse])
        candidate = WarehouseMSTResult(location=warehouse, mst=mst)
        if best_result is None or candidate.mst.total_cost < best_result.mst.total_cost:
            best_result = candidate

    if best_result is None:
        raise RuntimeError("No se encontró una bodega válida")

    return best_result


def monotone_arborescence(
    points: list[Point3D],
    warehouse: Point3D,
) -> ArborescenceResult | None:
    """Construye una arborescencia mínima si la restricción monotónica es factible."""

    all_nodes = points + [warehouse]
    warehouse_idx = len(points)

    for point in points:
        if point[1] < warehouse[1]:
            return None

    graph = nx.DiGraph()
    graph.add_nodes_from(range(len(all_nodes)))

    for parent_idx, parent in enumerate(all_nodes):
        for child_idx, child in enumerate(all_nodes):
            if parent_idx == child_idx or child_idx == warehouse_idx:
                continue
            if parent[1] <= child[1]:
                graph.add_edge(parent_idx, child_idx, weight=manhattan_3d(parent, child))

    for child_idx in range(len(points)):
        if graph.in_degree(child_idx) == 0:
            return None

    if graph.in_degree(warehouse_idx) != 0:
        return None

    try:
        arborescence = nx.minimum_spanning_arborescence(graph, attr="weight")
    except nx.NetworkXException:
        return None

    if set(arborescence.nodes()) != set(graph.nodes()):
        return None
    if arborescence.in_degree(warehouse_idx) != 0:
        return None
    if any(arborescence.in_degree(node) != 1 for node in range(len(points))):
        return None

    edges_to_parent: list[tuple[int, int, float]] = []
    total_cost = 0.0
    for parent_idx, child_idx, data in arborescence.edges(data=True):
        weight = float(data["weight"])
        total_cost += weight
        edges_to_parent.append((child_idx, parent_idx, weight))

    return ArborescenceResult(total_cost=total_cost, edges_to_parent=edges_to_parent)


def best_warehouse_monotone(
    points: list[Point3D],
    fixed_y: float = -40.0,
    exact_integer_search_limit: int = 200_000,
) -> WarehouseArborescenceResult:
    """Busca la bodega factible que minimiza el costo de la red monotónica."""

    if not points:
        raise ValueError("Se requiere al menos un punto")

    best_result: WarehouseArborescenceResult | None = None
    for warehouse in candidate_warehouses(points, fixed_y, exact_integer_search_limit):
        arborescence = monotone_arborescence(points, warehouse)
        if arborescence is None:
            continue
        candidate = WarehouseArborescenceResult(
            location=warehouse,
            arborescence=arborescence,
        )
        if (
            best_result is None
            or candidate.arborescence.total_cost < best_result.arborescence.total_cost
        ):
            best_result = candidate

    if best_result is None:
        raise RuntimeError(
            "No existe solución factible para la restricción monotónica en y"
        )

    return best_result
