"""Generación de ubicaciones candidatas para bodegas en plano fijo."""

from __future__ import annotations

from .geometry import all_integers
from .types import Point3D


def candidate_warehouses(
    points: list[Point3D],
    fixed_y: float,
    exact_integer_search_limit: int = 200_000,
) -> list[Point3D]:
    """Genera candidatos sobre el plano `y = fixed_y` a partir de los puntos observados."""

    xs = [point[0] for point in points]
    zs = [point[2] for point in points]

    xs_unique = sorted(set(xs))
    zs_unique = sorted(set(zs))

    if all_integers(xs) and all_integers(zs):
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
