import unittest

from solvers.graphical_solver import (
    intersect, is_feasible, corner_points, is_unbounded, solve_lpp,
)


class TestGraphicalSolver(unittest.TestCase):
    def setUp(self):
        self.constraints = [
            {"a": 1, "b": 0, "op": "<=", "rhs": 4},
            {"a": 0, "b": 1, "op": "<=", "rhs": 3},
            {"a": 1, "b": 1, "op": "<=", "rhs": 5},
        ]

    def test_intersection(self):
        self.assertEqual(intersect((1, 0, 2), (0, 1, 3)), (2.0, 3.0))

    def test_parallel_lines_have_no_unique_intersection(self):
        self.assertIsNone(intersect((1, 1, 2), (2, 2, 4)))

    def test_feasibility_checks_nonnegativity_and_all_relations(self):
        self.assertTrue(is_feasible(2, 2, self.constraints))
        self.assertFalse(is_feasible(-1, 2, self.constraints))
        self.assertFalse(is_feasible(4, 2, self.constraints))
        self.assertTrue(is_feasible(2, 3, [{"a": 1, "b": 1, "op": "=", "rhs": 5}]))
        self.assertFalse(is_feasible(2, 2, [{"a": 1, "b": 1, "op": "=", "rhs": 5}]))
        self.assertTrue(is_feasible(3, 2, [{"a": 1, "b": 1, "op": ">=", "rhs": 5}]))

    def test_corner_points_are_feasible_and_deduplicated(self):
        points = corner_points(self.constraints)
        self.assertTrue(points)
        self.assertEqual(len(points), len(set(points)))
        for x, y in points:
            self.assertTrue(is_feasible(x, y, self.constraints))
        self.assertIn((2.0, 3.0), points)

    def test_maximization_optimum(self):
        result = solve_lpp(3, 2, "Maximize", self.constraints)
        self.assertEqual(result["status"], "optimal")
        self.assertAlmostEqual(result["optimum"], 14.0)
        self.assertIn((4.0, 1.0), result["optimal_points"])

    def test_minimization_at_origin(self):
        result = solve_lpp(3, 2, "Minimize", self.constraints)
        self.assertEqual(result["status"], "optimal")
        self.assertAlmostEqual(result["optimum"], 0.0)
        self.assertIn((0.0, 0.0), result["optimal_points"])

    def test_infeasible_problem(self):
        constraints = [
            {"a": 1, "b": 0, "op": "<=", "rhs": 1},
            {"a": 1, "b": 0, "op": ">=", "rhs": 2},
        ]
        result = solve_lpp(1, 1, "Maximize", constraints)
        self.assertEqual(result["status"], "infeasible")
        self.assertIsNone(result["optimum"])

    def test_unbounded_maximization(self):
        result = solve_lpp(1, 1, "Maximize", [{"a": 1, "b": 1, "op": ">=", "rhs": 1}])
        self.assertEqual(result["status"], "unbounded")

    def test_multiple_optimal_corner_points(self):
        result = solve_lpp(1, 1, "Maximize", [
            {"a": 1, "b": 1, "op": "<=", "rhs": 4},
            {"a": 1, "b": 0, "op": "<=", "rhs": 3},
        ])
        self.assertEqual(result["status"], "multiple")
        self.assertAlmostEqual(result["optimum"], 4.0)
        self.assertGreaterEqual(len(result["optimal_points"]), 2)

    def test_is_unbounded_respects_objective_direction(self):
        constraints = [{"a": 1, "b": 1, "op": ">=", "rhs": 1}]
        self.assertTrue(is_unbounded(1, 1, "Maximize", constraints))
        self.assertFalse(is_unbounded(1, 1, "Minimize", constraints))


if __name__ == "__main__":
    unittest.main()
