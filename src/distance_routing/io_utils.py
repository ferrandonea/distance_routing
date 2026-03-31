"""Lectura de datos de entrada y escritura de reportes de salida."""

from __future__ import annotations

from pathlib import Path

from .types import (
    ArborescenceResult,
    MSTResult,
    Point3D,
    RouteResult,
    WarehouseArborescenceResult,
    WarehouseLocationResult,
    WarehouseMSTResult,
)


def project_root() -> Path:
    """Devuelve la raíz del repositorio asumiendo layout `src/`."""

    return Path(__file__).resolve().parents[2]


def default_input_path() -> Path:
    """Devuelve la ruta de entrada por defecto."""

    return project_root() / "input" / "puntos.txt"


def default_output_path(filename: str) -> Path:
    """Devuelve una ruta de salida en la carpeta `output/` del proyecto."""

    return project_root() / "output" / filename


def ensure_parent_dir(path: Path) -> Path:
    """Crea la carpeta padre de una ruta antes de escribir en ella."""

    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def read_points_txt(path: str | Path) -> list[Point3D]:
    """Lee puntos 3D desde un archivo y valida que cada línea tenga tres valores."""

    path = Path(path)
    points: list[Point3D] = []

    with path.open("r", encoding="utf-8") as file_obj:
        for line_num, raw_line in enumerate(file_obj, start=1):
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


def write_route_report(
    path: str | Path,
    points: list[Point3D],
    result: RouteResult,
) -> Path:
    """Escribe una ruta exacta y el orden de visita en un archivo de texto."""

    path = ensure_parent_dir(Path(path))
    with path.open("w", encoding="utf-8") as file_obj:
        file_obj.write(f"Distancia total: {result.total_cost}\n")
        file_obj.write("Orden de visita:\n")
        for index in result.path:
            x, y, z = points[index]
            file_obj.write(f"{index}: {x} {y} {z}\n")
    return path


def write_location_report(
    path: str | Path,
    points: list[Point3D],
    result: WarehouseLocationResult,
    title: str,
) -> Path:
    """Escribe una ubicación óptima y las distancias individuales asociadas."""

    path = ensure_parent_dir(Path(path))
    with path.open("w", encoding="utf-8") as file_obj:
        file_obj.write(f"{title}\n")
        file_obj.write(f"Ubicación: {result.location}\n")
        file_obj.write(f"Suma total mínima: {result.total_distance}\n")
        file_obj.write("\nDistancias individuales:\n")
        for i, (point, distance) in enumerate(zip(points, result.distances)):
            file_obj.write(f"{i}: punto={point}, distancia={distance}\n")
    return path


def _format_node_name(index: int, num_original_points: int) -> str:
    """Etiqueta un nodo como punto original o como bodega."""

    if index < num_original_points:
        return f"P{index}"
    return "BODEGA"


def write_mst_report(
    path: str | Path,
    points: list[Point3D],
    result: WarehouseMSTResult,
) -> Path:
    """Escribe la solución de bodega conectada por MST en un archivo de texto."""

    path = ensure_parent_dir(Path(path))
    all_nodes = points + [result.location]
    num_original_points = len(points)

    with path.open("w", encoding="utf-8") as file_obj:
        file_obj.write("SOLUCIÓN\n")
        file_obj.write(f"Bodega óptima: {result.location}\n")
        file_obj.write(f"Costo total de red compartida: {result.mst.total_cost}\n")
        file_obj.write("\nNodos:\n")

        for i, point in enumerate(points):
            file_obj.write(f"P{i}: {point}\n")
        file_obj.write(f"BODEGA: {result.location}\n")

        file_obj.write("\nAristas del MST:\n")
        for u, v, cost in result.mst.edges:
            name_u = _format_node_name(u, num_original_points)
            name_v = _format_node_name(v, num_original_points)
            file_obj.write(
                f"{name_u} {all_nodes[u]} <-> {name_v} {all_nodes[v]} | costo={cost}\n"
            )

    return path


def write_arborescence_report(
    path: str | Path,
    points: list[Point3D],
    result: WarehouseArborescenceResult,
) -> Path:
    """Escribe la solución de red dirigida monotónica en un archivo de texto."""

    path = ensure_parent_dir(Path(path))
    all_nodes = points + [result.location]
    num_original_points = len(points)

    with path.open("w", encoding="utf-8") as file_obj:
        file_obj.write("SOLUCIÓN\n")
        file_obj.write(f"Bodega óptima: {result.location}\n")
        file_obj.write(
            f"Costo total de la red compartida: {result.arborescence.total_cost}\n"
        )
        file_obj.write("\nNodos:\n")

        for i, point in enumerate(points):
            file_obj.write(f"P{i}: {point}\n")
        file_obj.write(f"BODEGA: {result.location}\n")

        file_obj.write("\nAristas dirigidas hacia la bodega:\n")
        for child, parent, cost in result.arborescence.edges_to_parent:
            child_name = _format_node_name(child, num_original_points)
            parent_name = _format_node_name(parent, num_original_points)
            file_obj.write(
                f"{child_name} {all_nodes[child]} -> "
                f"{parent_name} {all_nodes[parent]} | costo={cost}\n"
            )

    return path
