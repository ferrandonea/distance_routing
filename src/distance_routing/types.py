"""Tipos y dataclasses compartidos entre los algoritmos del proyecto."""

from __future__ import annotations

from dataclasses import dataclass


type Point3D = tuple[float, float, float]


@dataclass(frozen=True)
class RouteResult:
    """Representa una ruta Manhattan exacta y su costo total."""

    total_cost: float
    path: list[int]


@dataclass(frozen=True)
class WarehouseLocationResult:
    """Representa una ubicación de bodega y las distancias individuales asociadas."""

    location: Point3D
    total_distance: float
    distances: list[float]


@dataclass(frozen=True)
class MSTResult:
    """Resultado de un árbol recubridor mínimo en el grafo completo de puntos."""

    total_cost: float
    edges: list[tuple[int, int, float]]


@dataclass(frozen=True)
class WarehouseMSTResult:
    """Ubicación de bodega óptima junto con el MST que la conecta a la red."""

    location: Point3D
    mst: MSTResult


@dataclass(frozen=True)
class ArborescenceResult:
    """Resultado de una arborescencia dirigida hacia la bodega."""

    total_cost: float
    edges_to_parent: list[tuple[int, int, float]]


@dataclass(frozen=True)
class WarehouseArborescenceResult:
    """Ubicación de bodega óptima junto con su red dirigida factible."""

    location: Point3D
    arborescence: ArborescenceResult
