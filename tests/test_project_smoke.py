import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestProjectSmoke(unittest.TestCase):
    def test_all_python_files_parse(self):
        files = list(ROOT.rglob("*.py"))
        self.assertTrue(files, "No Python files found")
        for path in files:
            with self.subTest(path=path.relative_to(ROOT)):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_solver_modules_import(self):
        from solvers import graphical_solver, simplex_solver, big_m_solver, transportation_solver
        from services import settings
        self.assertTrue(callable(graphical_solver.solve_lpp))
        self.assertTrue(callable(simplex_solver.max_simplex))
        self.assertTrue(hasattr(settings, "save_method_state"))
        self.assertTrue(hasattr(big_m_solver, "__file__"))
        self.assertTrue(hasattr(transportation_solver, "__file__"))


if __name__ == "__main__":
    unittest.main()
