"""Utilidades geométricas y de normalización para puntos en 3D."""

from __future__ import annotations

from typing import Iterable

from .types import Point3D


def manhattan_3d(a: Point3D, b: Point3D) -> float:
    """Calcula la distancia Manhattan entre dos puntos 3D."""

    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def all_integers(values: Iterable[float], tol: float = 1e-9) -> bool:
    """Indica si todos los valores son enteros dentro de una tolerancia."""

    return all(abs(value - round(value)) <= tol for value in values)


def deduplicate_points(points: list[Point3D], tol: float = 1e-9) -> list[Point3D]:
    """Elimina puntos duplicados usando redondeo tolerante para floats."""

    seen: set[Point3D] = set()
    unique: list[Point3D] = []

    for point in points:
        key = (
            round(point[0] / tol) * tol,
            round(point[1] / tol) * tol,
            round(point[2] / tol) * tol,
        )
        if key not in seen:
            seen.add(key)
            unique.append(point)

    return unique
