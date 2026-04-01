"""Visualizaciones 3D para soluciones geométricas del proyecto."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from .io_utils import ensure_parent_dir
from .types import Point3D, WarehouseArborescenceResult


def _manhattan_polyline(child: Point3D, parent: Point3D) -> list[Point3D]:
    """Construye una polilinea ortogonal que representa un camino Manhattan."""

    bend_x = (parent[0], child[1], child[2])
    bend_z = (parent[0], child[1], parent[2])
    return [child, bend_x, bend_z, parent]


def plot_monotone_3d(
    path: str | Path,
    points: list[Point3D],
    result: WarehouseArborescenceResult,
) -> Path:
    """Genera una imagen 3D usando `z` como altura visual de la escena."""

    path = ensure_parent_dir(Path(path))
    warehouse_index = len(points)
    all_nodes = points + [result.location]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    ax.scatter(
        [point[0] for point in points],
        [point[2] for point in points],
        [point[1] for point in points],
        c="#1f77b4",
        s=40,
        label="Puntos",
    )
    ax.scatter(
        [result.location[0]],
        [result.location[2]],
        [result.location[1]],
        c="#d62728",
        s=120,
        marker="^",
        label="Bodega",
    )

    for index, point in enumerate(points):
        ax.text(point[0], point[2], point[1], f"P{index}", fontsize=8)
    ax.text(
        result.location[0],
        result.location[2],
        result.location[1],
        "BODEGA",
        fontsize=9,
        fontweight="bold",
    )

    for child_idx, parent_idx, _cost in result.arborescence.edges_to_parent:
        child = all_nodes[child_idx]
        parent = all_nodes[parent_idx]
        polyline = _manhattan_polyline(child, parent)
        ax.plot(
            [point[0] for point in polyline],
            [point[2] for point in polyline],
            [point[1] for point in polyline],
            color="#2ca02c" if parent_idx != warehouse_index else "#ff7f0e",
            linewidth=2,
            alpha=0.9,
        )

    ax.set_title("Red monotona hacia la bodega")
    ax.set_xlabel("X")
    ax.set_ylabel("Z (altura)")
    ax.set_zlabel("Y")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path
