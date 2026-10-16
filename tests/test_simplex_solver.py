import unittest

from solvers.simplex_solver import (
    build_dual, check_negativity, convert_to_equations, max_simplex,
    min_simplex, pivot, read_lpp, recover_primal_by_complementary_slackness,
    save_tableau_snapshot, _solve_square_system,
)


class TestSimplexPreparation(unittest.TestCase):
    def test_negative_rhs_reverses_inequality_and_coefficients(self):
        normalized = check_negativity([{"var1": 2, "var2": -1, "op": "<=", "rhs": -4}])
        self.assertEqual(normalized, [{"var1": -2, "var2": 1, "op": ">=", "rhs": 4}])

    def test_invalid_operator_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid constraint operator"):
            check_negativity([{"var1": 1, "op": "!", "rhs": 2}])

    def test_equations_add_identity_slack_variables(self):
        equations = convert_to_equations([
            {"var1": 2, "var2": 3, "op": "<=", "rhs": 8},
            {"var1": 1, "var2": 0, "op": "<=", "rhs": 2},
        ], 2)
        self.assertEqual(equations, [[2.0, 3.0, 1.0, 0.0, 8.0], [1.0, 0.0, 0.0, 1.0, 2.0]])

    def test_non_le_constraint_rejected_by_current_backend(self):
        with self.assertRaisesRegex(ValueError, "Big M or Two-Phase"):
            convert_to_equations([{"var1": 1, "op": ">=", "rhs": 2}], 1)

    def test_read_lpp_rejects_empty_inputs_and_bad_values(self):
        with self.assertRaisesRegex(ValueError, "at least one variable"):
            read_lpp([], [{"var1": 1, "op": "<=", "rhs": 1}])
        with self.assertRaisesRegex(ValueError, "Add at least one constraint"):
            read_lpp([1], [])
        with self.assertRaisesRegex(ValueError, "must be numeric"):
            read_lpp([1], [{"var1": "bad", "op": "<=", "rhs": 1}])

    def test_pivot_performs_gauss_jordan_elimination(self):
        tableau = [[2.0, 1.0, 5.0], [4.0, 3.0, 11.0]]
        pivot(tableau, 0, 0)
        self.assertEqual(tableau[0], [1.0, 0.5, 2.5])
        self.assertEqual(tableau[1], [0.0, 1.0, 1.0])

    def test_pivot_rejects_zero_pivot(self):
        with self.assertRaises(ArithmeticError):
            pivot([[0.0, 1.0]], 0, 0)

    def test_tableau_snapshot_contains_labels_and_copy(self):
        tableau = [[1.0, 0.0, 4.0], [-3.0, 0.0, 0.0]]
        snapshot = save_tableau_snapshot(tableau, [1], 1, "test")
        self.assertEqual(snapshot["columns"], ["Basis", "x1", "s1", "RHS"])
        self.assertEqual(snapshot["rows"][0][0], "s1")
        snapshot["rows"][0][1] = 999
        self.assertEqual(tableau[0][0], 1.0)

    def test_square_system_solved_and_singular_detected(self):
        self.assertEqual(_solve_square_system([[2, 1], [1, -1]], [5, 1]), [2.0, 1.0])
        self.assertIsNone(_solve_square_system([[1, 2], [2, 4]], [3, 6]))
        self.assertIsNone(_solve_square_system([[1, 2]], [3]))


class TestSimplexSolving(unittest.TestCase):
    def test_known_maximization_example(self):
        result = max_simplex([3, 5], [
            {"var1": 1, "var2": 0, "op": "<=", "rhs": 4},
            {"var1": 0, "var2": 2, "op": "<=", "rhs": 12},
            {"var1": 3, "var2": 2, "op": "<=", "rhs": 18},
        ])
        self.assertEqual(result["status"], "optimal")
        self.assertAlmostEqual(result["optimum"], 36.0)
        self.assertAlmostEqual(result["solution"][0], 2.0)
        self.assertAlmostEqual(result["solution"][1], 6.0)
        self.assertEqual(result["tableau_history"][0]["title"], "Initial tableau")
        self.assertEqual(result["iterations"], len(result["tableau_history"]) - 1)

    def test_unbounded_maximization(self):
        result = max_simplex([1, 1], [{"var1": -1, "var2": 1, "op": "<=", "rhs": 1}])
        self.assertEqual(result["status"], "unbounded")
        self.assertIsNone(result["solution"])

    def test_negative_rhs_with_le_constraint_is_reported_unsupported(self):
        with self.assertRaisesRegex(ValueError, "Big M or Two-Phase"):
            max_simplex([1], [{"var1": 1, "op": "<=", "rhs": -2}])

    def test_build_dual_for_minimization(self):
        dual = build_dual([5, 4], [
            {"var1": 1, "var2": 2, "op": ">=", "rhs": 6},
            {"var1": 3, "var2": 1, "op": ">=", "rhs": 8},
        ], sense="Minimize")
        self.assertEqual(dual["sense"], "Maximize")
        self.assertEqual(dual["objective"], [6.0, 8.0])
        self.assertEqual(dual["constraints"], [
            {"var1": 1.0, "var2": 3.0, "op": "<=", "rhs": 5.0},
            {"var1": 2.0, "var2": 1.0, "op": "<=", "rhs": 4.0},
        ])
        self.assertEqual(dual["variable_signs"], ["nonnegative", "nonnegative"])

    def test_build_dual_validates_sense_and_signs(self):
        constraints = [{"var1": 1, "op": ">=", "rhs": 1}]
        with self.assertRaisesRegex(ValueError, "sense"):
            build_dual([1], constraints, sense="sideways")
        with self.assertRaisesRegex(ValueError, "one variable sign"):
            build_dual([1, 2], constraints, variable_signs=["free"])
        with self.assertRaisesRegex(ValueError, "Variable signs"):
            build_dual([1], constraints, variable_signs=["negative"])

    def test_minimization_dual_recovery_example(self):
        result = min_simplex([5, 5], [
            {"var1": 4, "var2": 4, "op": ">=", "rhs": 25},
            {"var1": 4, "var2": 2, "op": ">=", "rhs": 10},
        ])
        self.assertEqual(result["status"], "optimal")
        self.assertAlmostEqual(result["optimum"], 31.25)
        self.assertAlmostEqual(result["solution"][0], 0.0)
        self.assertAlmostEqual(result["solution"][1], 6.25)
        self.assertAlmostEqual(sum(result["dual_solution"]), 1.25)
        self.assertTrue(any("Strong duality verified" in step for step in result["steps"]))

    def test_minimization_rejects_unsupported_dual_form(self):
        with self.assertRaisesRegex(ValueError, "current Simplex backend cannot solve"):
            min_simplex([1], [{"var1": 1, "op": "<=", "rhs": 2}])

    def test_recovery_returns_none_when_no_matching_primal_basis(self):
        recovered, steps = recover_primal_by_complementary_slackness(
            [1], [{"var1": 1, "op": ">=", "rhs": 5}], [0],
            {"optimum": 0, "constraints": [{"var1": 1, "op": "<=", "rhs": 1}]},
        )
        self.assertIsNone(recovered)
        self.assertTrue(steps)


if __name__ == "__main__":
    unittest.main()
