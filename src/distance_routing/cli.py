"""CLI principal del proyecto."""

from __future__ import annotations

import argparse
from pathlib import Path

from .geometry import deduplicate_points
from .io_utils import (
    default_input_path,
    default_output_path,
    read_points_txt,
    write_arborescence_report,
    write_location_report,
    write_mst_report,
    write_route_report,
)
from .routing import exact_closed_route, exact_open_route
from .warehouse import (
    best_warehouse_monotone,
    best_warehouse_mst,
    taxicab_median,
    taxicab_median_fixed_y,
)


def build_parser() -> argparse.ArgumentParser:
    """Construye el parser de la CLI con todos los subcomandos disponibles."""

    parser = argparse.ArgumentParser(prog="distance_routing")
    subparsers = parser.add_subparsers(dest="command", required=True)

    default_input = default_input_path()

    open_parser = subparsers.add_parser("open-route", help="Calcula la ruta abierta mínima")
    open_parser.add_argument("--input", type=Path, default=default_input)
    open_parser.add_argument(
        "--output",
        type=Path,
        default=default_output_path("ruta_abierta.txt"),
    )

    closed_parser = subparsers.add_parser(
        "closed-route",
        help="Calcula la ruta cerrada mínima",
    )
    closed_parser.add_argument("--input", type=Path, default=default_input)
    closed_parser.add_argument(
        "--output",
        type=Path,
        default=default_output_path("ruta_cerrada.txt"),
    )
    closed_parser.add_argument("--start", type=int, default=0)

    median_parser = subparsers.add_parser(
        "warehouse-median",
        help="Calcula la bodega óptima libre en 3D",
    )
    median_parser.add_argument("--input", type=Path, default=default_input)
    median_parser.add_argument("--output", type=Path)

    fixed_parser = subparsers.add_parser(
        "warehouse-fixed",
        help="Calcula la bodega óptima en un plano y fijo",
    )
    fixed_parser.add_argument("--input", type=Path, default=default_input)
    fixed_parser.add_argument("--output", type=Path)
    fixed_parser.add_argument("--fixed-y", type=float, default=-40.0)

    mst_parser = subparsers.add_parser(
        "warehouse-mst",
        help="Calcula la bodega óptima minimizando una red MST",
    )
    mst_parser.add_argument("--input", type=Path, default=default_input)
    mst_parser.add_argument(
        "--output",
        type=Path,
        default=default_output_path("solucion_bodega_mst.txt"),
    )
    mst_parser.add_argument("--fixed-y", type=float, default=-40.0)

    monotone_parser = subparsers.add_parser(
        "warehouse-monotone",
        help="Calcula la bodega óptima con red monotónica en y",
    )
    monotone_parser.add_argument("--input", type=Path, default=default_input)
    monotone_parser.add_argument(
        "--output",
        type=Path,
        default=default_output_path("solucion_bodega_monotona_y.txt"),
    )
    monotone_parser.add_argument("--fixed-y", type=float, default=-40.0)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Ejecuta la CLI principal."""

    args = build_parser().parse_args(argv)
    points = read_points_txt(args.input)

    if args.command == "open-route":
        result = exact_open_route(points)
        output_path = write_route_report(args.output, points, result)
        print("Ruta abierta mínima")
        print("Distancia total:", result.total_cost)
        print("Orden índices:", result.path)
        print(f"Resultado guardado en: {output_path}")
        return 0

    if args.command == "closed-route":
        result = exact_closed_route(points, start=args.start)
        output_path = write_route_report(args.output, points, result)
        print("Ruta cerrada mínima")
        print("Distancia total:", result.total_cost)
        print("Orden índices:", result.path)
        print(f"Resultado guardado en: {output_path}")
        return 0

    if args.command == "warehouse-median":
        result = taxicab_median(points)
        print("Bodega óptima:", result.location)
        print("Suma total mínima:", result.total_distance)
        if args.output is not None:
            output_path = write_location_report(args.output, points, result, "BODEGA ÓPTIMA")
            print(f"Resultado guardado en: {output_path}")
        return 0

    if args.command == "warehouse-fixed":
        result = taxicab_median_fixed_y(points, fixed_y=args.fixed_y)
        print("Bodega óptima con y fijo:", result.location)
        print("Suma total mínima:", result.total_distance)
        if args.output is not None:
            output_path = write_location_report(
                args.output,
                points,
                result,
                "BODEGA ÓPTIMA CON Y FIJO",
            )
            print(f"Resultado guardado en: {output_path}")
        return 0

    if args.command == "warehouse-mst":
        unique_points = deduplicate_points(points)
        result = best_warehouse_mst(unique_points, fixed_y=args.fixed_y)
        output_path = write_mst_report(args.output, unique_points, result)
        print("Bodega óptima:", result.location)
        print("Costo total de la red compartida:", result.mst.total_cost)
        print(f"Resultado guardado en: {output_path}")
        return 0

    if args.command == "warehouse-monotone":
        unique_points = deduplicate_points(points)
        result = best_warehouse_monotone(unique_points, fixed_y=args.fixed_y)
        output_path = write_arborescence_report(args.output, unique_points, result)
        print("Bodega óptima:", result.location)
        print("Costo total de la red compartida:", result.arborescence.total_cost)
        print(f"Resultado guardado en: {output_path}")
        return 0

    raise RuntimeError(f"Subcomando no soportado: {args.command}")
