
import unittest

from solvers.simplex_solver import max_simplex, min_simplex


class TestSimplexMultipleOptima(unittest.TestCase):

    def test_maximization_with_multiple_optima(self):
        # Maximize Z = 5x1 + 5x2
        constraints = [
            {"var1": 4, "var2": 4, "op": "<=", "rhs": 25},
            {"var1": 4, "var2": 2, "op": "<=", "rhs": 20},
        ]

        result = max_simplex([5, 5], constraints)

        self.assertEqual(result["status"], "optimal")
        self.assertAlmostEqual(result["optimum"], 31.25)

        # This assertion will fail until detection is implemented.
        self.assertIs(result.get("multiple_optima"), True)

    def test_minimization_with_multiple_optima(self):
        # Minimize Z = 5x1 + 5x2
        constraints = [
            {"var1": 4, "var2": 4, "op": ">=", "rhs": 25},
            {"var1": 4, "var2": 2, "op": ">=", "rhs": 10},
        ]

        result = min_simplex([5, 5], constraints)

        self.assertEqual(result["status"], "optimal")
        self.assertAlmostEqual(result["optimum"], 31.25)

        # This assertion will fail until detection is implemented.
        self.assertIs(result.get("multiple_optima"), True)

    def test_minimization_with_unique_optimum(self):
        # Minimize Z = 5x1 + 5x2
        constraints = [
            {"var1": 4, "var2": 4, "op": ">=", "rhs": 25},
            {"var1": 4, "var2": 2, "op": ">=", "rhs": 30},
        ]

        result = min_simplex([5, 5], constraints)

        self.assertEqual(result["status"], "optimal")
        self.assertAlmostEqual(result["optimum"], 37.5)
        self.assertAlmostEqual(result["solution"][0], 7.5)
        self.assertAlmostEqual(result["solution"][1], 0.0)

        # A unique optimum should not be flagged as multiple.
        self.assertIs(result.get("multiple_optima"), False)


if __name__ == "__main__":
    unittest.main()
