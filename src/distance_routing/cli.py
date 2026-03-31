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


def _print_route_summary(title: str, total_cost: float, path: list[int]) -> None:
    """Imprime un resumen compacto de una ruta exacta."""

    print(title)
    print("Distancia total:", total_cost)
    print("Orden índices:", path)


def _print_location_summary(title: str, location: tuple[float, float, float], total: float) -> None:
    """Imprime un resumen compacto de una ubicación óptima."""

    print(title, location)
    print("Suma total mínima:", total)


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

    run_all_parser = subparsers.add_parser(
        "run-all",
        help="Ejecuta todos los algoritmos con una sola invocación",
    )
    run_all_parser.add_argument("--input", type=Path, default=default_input)
    run_all_parser.add_argument("--start", type=int, default=0)
    run_all_parser.add_argument("--fixed-y", type=float, default=-40.0)
    run_all_parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output_path("placeholder.txt").parent,
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Ejecuta la CLI principal."""

    args = build_parser().parse_args(argv)
    points = read_points_txt(args.input)

    if args.command == "open-route":
        result = exact_open_route(points)
        output_path = write_route_report(args.output, points, result)
        _print_route_summary("Ruta abierta mínima", result.total_cost, result.path)
        print(f"Resultado guardado en: {output_path}")
        return 0

    if args.command == "closed-route":
        result = exact_closed_route(points, start=args.start)
        output_path = write_route_report(args.output, points, result)
        _print_route_summary("Ruta cerrada mínima", result.total_cost, result.path)
        print(f"Resultado guardado en: {output_path}")
        return 0

    if args.command == "warehouse-median":
        result = taxicab_median(points)
        _print_location_summary("Bodega óptima:", result.location, result.total_distance)
        if args.output is not None:
            output_path = write_location_report(args.output, points, result, "BODEGA ÓPTIMA")
            print(f"Resultado guardado en: {output_path}")
        return 0

    if args.command == "warehouse-fixed":
        result = taxicab_median_fixed_y(points, fixed_y=args.fixed_y)
        _print_location_summary(
            "Bodega óptima con y fijo:",
            result.location,
            result.total_distance,
        )
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

    if args.command == "run-all":
        output_dir = args.output_dir
        unique_points = deduplicate_points(points)

        open_result = exact_open_route(points)
        open_output = write_route_report(output_dir / "ruta_abierta.txt", points, open_result)
        _print_route_summary("Ruta abierta mínima", open_result.total_cost, open_result.path)
        print(f"Resultado guardado en: {open_output}")
        print()

        closed_result = exact_closed_route(points, start=args.start)
        closed_output = write_route_report(output_dir / "ruta_cerrada.txt", points, closed_result)
        _print_route_summary("Ruta cerrada mínima", closed_result.total_cost, closed_result.path)
        print(f"Resultado guardado en: {closed_output}")
        print()

        median_result = taxicab_median(points)
        _print_location_summary("Bodega óptima:", median_result.location, median_result.total_distance)
        print()

        fixed_result = taxicab_median_fixed_y(points, fixed_y=args.fixed_y)
        _print_location_summary(
            "Bodega óptima con y fijo:",
            fixed_result.location,
            fixed_result.total_distance,
        )
        print()

        mst_result = best_warehouse_mst(unique_points, fixed_y=args.fixed_y)
        mst_output = write_mst_report(output_dir / "solucion_bodega_mst.txt", unique_points, mst_result)
        print("Bodega óptima MST:", mst_result.location)
        print("Costo total de la red compartida:", mst_result.mst.total_cost)
        print(f"Resultado guardado en: {mst_output}")
        print()

        monotone_result = best_warehouse_monotone(unique_points, fixed_y=args.fixed_y)
        monotone_output = write_arborescence_report(
            output_dir / "solucion_bodega_monotona_y.txt",
            unique_points,
            monotone_result,
        )
        print("Bodega óptima monotónica:", monotone_result.location)
        print(
            "Costo total de la red compartida:",
            monotone_result.arborescence.total_cost,
        )
        print(f"Resultado guardado en: {monotone_output}")
        return 0

    raise RuntimeError(f"Subcomando no soportado: {args.command}")
