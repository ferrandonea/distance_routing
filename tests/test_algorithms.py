import unittest

from distance_routing.geometry import deduplicate_points
from distance_routing.routing import exact_closed_route, exact_open_route
from distance_routing.warehouse import (
    best_warehouse_monotone,
    best_warehouse_mst,
    taxicab_median,
    taxicab_median_fixed_y,
)


class AlgorithmTests(unittest.TestCase):
    """Cobertura mínima de los algoritmos principales del paquete."""

    def test_deduplicate_points_removes_duplicates(self) -> None:
        points = [(0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)]

        unique_points = deduplicate_points(points)

        self.assertEqual(unique_points, [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)])

    def test_exact_routes_for_two_points_have_expected_costs(self) -> None:
        points = [(0.0, 0.0, 0.0), (2.0, 0.0, 0.0)]

        open_result = exact_open_route(points)
        closed_result = exact_closed_route(points)

        self.assertEqual(open_result.total_cost, 2.0)
        self.assertEqual(sorted(open_result.path), [0, 1])
        self.assertEqual(closed_result.total_cost, 4.0)
        self.assertEqual(closed_result.path, [0, 1, 0])

    def test_taxicab_median_variants_return_expected_locations(self) -> None:
        points = [(0.0, 0.0, 0.0), (2.0, 4.0, 2.0)]

        free_result = taxicab_median(points)
        fixed_result = taxicab_median_fixed_y(points, fixed_y=-1.0)

        self.assertEqual(free_result.location, (1.0, 2.0, 1.0))
        self.assertEqual(free_result.total_distance, 8.0)
        self.assertEqual(fixed_result.location, (1.0, -1.0, 1.0))
        self.assertEqual(fixed_result.total_distance, 10.0)

    def test_best_warehouse_mst_returns_expected_small_solution(self) -> None:
        points = [(0.0, 0.0, 0.0), (2.0, 0.0, 0.0)]

        result = best_warehouse_mst(points, fixed_y=0.0)

        self.assertIn(
            result.location,
            {(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (2.0, 0.0, 0.0)},
        )
        self.assertEqual(result.mst.total_cost, 2.0)
        self.assertEqual(len(result.mst.edges), 2)

    def test_best_warehouse_monotone_returns_expected_small_solution(self) -> None:
        points = [(0.0, 1.0, 0.0), (2.0, 2.0, 0.0)]

        result = best_warehouse_monotone(points, fixed_y=0.0)

        self.assertEqual(result.location, (0.0, 0.0, 0.0))
        self.assertEqual(result.arborescence.total_cost, 4.0)
        self.assertEqual(len(result.arborescence.edges_to_parent), 2)

    def test_best_warehouse_monotone_rejects_infeasible_case(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "No existe solución factible"):
            best_warehouse_monotone([(0.0, -1.0, 0.0)], fixed_y=0.0)


if __name__ == "__main__":
    unittest.main()
