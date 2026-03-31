"""Algoritmos de rutas exactas bajo distancia Manhattan."""

from __future__ import annotations

from itertools import combinations

from .geometry import manhattan_3d
from .types import Point3D, RouteResult


def exact_open_route(points: list[Point3D]) -> RouteResult:
    """Resuelve el TSP abierto exacto con programación dinámica por subconjuntos."""

    n = len(points)
    if n == 0:
        raise ValueError("Se requiere al menos un punto")
    if n == 1:
        return RouteResult(total_cost=0.0, path=[0])

    distances = [[manhattan_3d(points[i], points[j]) for j in range(n)] for i in range(n)]
    dp: dict[tuple[int, int], float] = {}
    parent: dict[tuple[int, int], int | None] = {}

    for end in range(n):
        mask = 1 << end
        dp[(mask, end)] = 0.0
        parent[(mask, end)] = None

    for size in range(2, n + 1):
        for subset in combinations(range(n), size):
            mask = 0
            for vertex in subset:
                mask |= 1 << vertex

            for end in subset:
                prev_mask = mask ^ (1 << end)
                best_cost = float("inf")
                best_prev = None

                for prev in subset:
                    if prev == end:
                        continue
                    candidate_cost = dp[(prev_mask, prev)] + distances[prev][end]
                    if candidate_cost < best_cost:
                        best_cost = candidate_cost
                        best_prev = prev

                dp[(mask, end)] = best_cost
                parent[(mask, end)] = best_prev

    full_mask = (1 << n) - 1
    best_end = min(range(n), key=lambda end: dp[(full_mask, end)])
    best_cost = dp[(full_mask, best_end)]

    path: list[int] = []
    mask = full_mask
    current = best_end
    while current is not None:
        path.append(current)
        previous = parent[(mask, current)]
        mask ^= 1 << current
        current = previous

    path.reverse()
    return RouteResult(total_cost=best_cost, path=path)


def exact_closed_route(points: list[Point3D], start: int = 0) -> RouteResult:
    """Resuelve el TSP cerrado exacto fijando nodo de inicio y retorno."""

    n = len(points)
    if n == 0:
        raise ValueError("Se requiere al menos un punto")
    if n == 1:
        return RouteResult(total_cost=0.0, path=[start, start])

    distances = [[manhattan_3d(points[i], points[j]) for j in range(n)] for i in range(n)]
    dp: dict[tuple[int, int], float] = {}
    parent: dict[tuple[int, int], int | None] = {}

    start_mask = 1 << start
    dp[(start_mask, start)] = 0.0
    parent[(start_mask, start)] = None

    remaining_nodes = [i for i in range(n) if i != start]

    for size in range(1, n):
        for subset in combinations(remaining_nodes, size):
            mask = start_mask
            for vertex in subset:
                mask |= 1 << vertex

            for end in subset:
                prev_mask = mask ^ (1 << end)
                best_cost = float("inf")
                best_prev = None
                prev_candidates = (
                    [start]
                    if prev_mask == start_mask
                    else [candidate for candidate in subset if candidate != end]
                )

                for prev in prev_candidates:
                    if (prev_mask, prev) not in dp:
                        continue
                    candidate_cost = dp[(prev_mask, prev)] + distances[prev][end]
                    if candidate_cost < best_cost:
                        best_cost = candidate_cost
                        best_prev = prev

                dp[(mask, end)] = best_cost
                parent[(mask, end)] = best_prev

    full_mask = (1 << n) - 1
    best_end = min(
        remaining_nodes,
        key=lambda end: dp[(full_mask, end)] + distances[end][start],
    )
    best_cost = dp[(full_mask, best_end)] + distances[best_end][start]

    reverse_path: list[int] = []
    mask = full_mask
    current = best_end
    while current != start:
        reverse_path.append(current)
        previous = parent[(mask, current)]
        mask ^= 1 << current
        current = previous

    path = [start, *reversed(reverse_path), start]
    return RouteResult(total_cost=best_cost, path=path)
