import json
import os
import importlib.util
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import matplotlib

matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Polygon

import sys
from pathlib import Path

GRAPHICAL_SOLVER_DIR = (
    Path(__file__).resolve().parent / "OR_GRAPHICAL_SOLVER"
)

sys.path.insert(0, str(GRAPHICAL_SOLVER_DIR))

from solver import solve_lpp, is_feasible, intersect


# Load the Simplex solver from its own folder using an explicit file path.
# This avoids confusing SIMPLEX_METHOD/solver.py with OR_GRAPHICAL_SOLVER/solver.py.
PROJECT_DIR = Path(__file__).resolve().parent
SIMPLEX_SOLVER_PATH = PROJECT_DIR / "SIMPLEX_METHOD" / "solver.py"

if SIMPLEX_SOLVER_PATH.exists():
    simplex_spec = importlib.util.spec_from_file_location(
        "simplex_method_solver", SIMPLEX_SOLVER_PATH
    )
    simplex_module = importlib.util.module_from_spec(simplex_spec)
    simplex_spec.loader.exec_module(simplex_module)
    max_simplex = simplex_module.max_simplex
else:
    max_simplex = None


class GraphicalLPPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimization Techniques")
        self.root.geometry("1250x800")
        self.root.minsize(1000, 650)

        self.constraint_rows = []
        self.current_page = "graph"

        app_data = os.getenv("LOCALAPPDATA") or os.path.expanduser("~")
        self.save_path = os.path.join(
            app_data,
            "OR Graphical Method Solver",
            "lpp_settings.json",
        )
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

        self.build_ui()

        # Restore saved graphical-method inputs, or load the example.
        if not self.load_state():
            self.load_example()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.schedule_autosave()

    # ------------------------------------------------------------------
    # Persistence for the graphical-method inputs
    # ------------------------------------------------------------------

    def save_state(self):
        state = {
            "sense": self.sense.get(),
            "c1": self.c1.get(),
            "c2": self.c2.get(),
            "constraints": [
                {
                    "a": row["a"].get(),
                    "b": row["b"].get(),
                    "op": row["op"].get(),
                    "rhs": row["rhs"].get(),
                }
                for row in self.constraint_rows
            ],
        }

        temp_path = self.save_path + ".tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(state, file, indent=4)
            os.replace(temp_path, self.save_path)
        except (OSError, TypeError, ValueError) as error:
            print(f"Could not save LPP inputs: {error}")

    def load_state(self):
        try:
            with open(self.save_path, "r", encoding="utf-8") as file:
                state = json.load(file)

            if not isinstance(state, dict):
                return False

            constraints = state.get("constraints")
            if not isinstance(constraints, list):
                return False

            if not all(
                isinstance(c, dict)
                and all(k in c for k in ("a", "b", "op", "rhs"))
                and c["op"] in ("<=", ">=", "=")
                for c in constraints
            ):
                return False

            if state.get("sense") not in ("Maximize", "Minimize"):
                return False

            self.c1.delete(0, "end")
            self.c1.insert(0, str(state.get("c1", "")))
            self.c2.delete(0, "end")
            self.c2.insert(0, str(state.get("c2", "")))
            self.sense.set(state["sense"])

            for row in self.constraint_rows:
                for key in ("a", "b", "op", "rhs", "remove_button"):
                    row[key].destroy()
            self.constraint_rows.clear()

            for constraint in constraints:
                self.add_constraint(
                    a=str(constraint["a"]),
                    b=str(constraint["b"]),
                    op=constraint["op"],
                    rhs=str(constraint["rhs"]),
                )

            return True
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return False

    def schedule_autosave(self):
        self.root.after(30000, self.autosave)

    def autosave(self):
        self.save_state()
        self.schedule_autosave()

    def on_close(self):
        self.save_state()
        self.root.destroy()

    # ------------------------------------------------------------------
    # Application layout and sidebar navigation
    # ------------------------------------------------------------------

    def build_ui(self):
        app_container = ttk.Frame(self.root)
        app_container.pack(fill="both", expand=True)
        app_container.rowconfigure(0, weight=1)
        app_container.columnconfigure(1, weight=1)

        # Sidebar
        sidebar = ttk.Frame(app_container, padding=12)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.configure(width=195)
        sidebar.grid_propagate(False)

        ttk.Label(
            sidebar,
            text="OPTIMIZATION\nTECHNIQUES",
            font=("Arial", 12, "bold"),
            justify="left",
        ).pack(anchor="w", pady=(5, 20))

        ttk.Label(
            sidebar, text="METHODS", font=("Arial", 9, "bold")
        ).pack(anchor="w", pady=(0, 8))

        self.graph_button = ttk.Button(
            sidebar,
            text="Graphical Method",
            command=lambda: self.show_page("graph"),
        )
        self.graph_button.pack(fill="x", pady=3)

        self.simplex_button = ttk.Button(
            sidebar,
            text="Simplex Method",
            command=lambda: self.show_page("simplex"),
        )
        self.simplex_button.pack(fill="x", pady=3)

        ttk.Separator(sidebar).pack(fill="x", pady=12)

        ttk.Button(
            sidebar,
            text="Big M Method",
            command=lambda: self.show_page("big_m"),
        ).pack(fill="x", pady=3)

        ttk.Button(
            sidebar,
            text="Transportation",
            command=lambda: self.show_page("transportation"),
        ).pack(fill="x", pady=3)

        ttk.Label(
            sidebar,
            text="More methods can be\nadded later.",
            justify="left",
            foreground="gray",
        ).pack(side="bottom", anchor="w", pady=8)

        # Main content area: each method has its own page.
        self.page_container = ttk.Frame(app_container, padding=0)
        self.page_container.grid(row=0, column=1, sticky="nsew")
        self.page_container.rowconfigure(0, weight=1)
        self.page_container.columnconfigure(0, weight=1)

        self.graph_page = ttk.Frame(self.page_container)
        self.simplex_page = ttk.Frame(self.page_container)
        self.big_m_page = ttk.Frame(self.page_container)
        self.transportation_page = ttk.Frame(self.page_container)

        for page in (
            self.graph_page,
            self.simplex_page,
            self.big_m_page,
            self.transportation_page,
        ):
            page.grid(row=0, column=0, sticky="nsew")

        self.build_graph_page()
        self.build_simplex_page()
        self.build_placeholder_page(
            self.big_m_page,
            "Big M Method",
            "This page will support linear programming problems "
            "that require artificial variables.",
        )
        self.build_placeholder_page(
            self.transportation_page,
            "Transportation Problem",
            "This page will support transportation models, "
            "initial feasible solutions, and optimization tests.",
        )

        self.show_page("graph")

    def show_page(self, page_name):
        pages = {
            "graph": self.graph_page,
            "simplex": self.simplex_page,
            "big_m": self.big_m_page,
            "transportation": self.transportation_page,
        }

        page = pages.get(page_name)
        if page is None:
            return

        for current_page in pages.values():
            current_page.grid_remove()

        page.grid()
        self.current_page = page_name

        titles = {
            "graph": "Optimization Techniques - Graphical Method",
            "simplex": "Optimization Techniques - Simplex Method",
            "big_m": "Optimization Techniques - Big M Method",
            "transportation": "Optimization Techniques - Transportation",
        }
        self.root.title(titles[page_name])

    # ------------------------------------------------------------------
    # Graphical-method page
    # ------------------------------------------------------------------

    def build_graph_page(self):
        main = ttk.Frame(self.graph_page, padding=10)
        main.pack(fill="both", expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        # Left side: problem input and report
        left = ttk.Frame(main, padding=5)
        left.grid(row=0, column=0, sticky="nsew")
        left.columnconfigure(0, weight=1)

        ttk.Label(
            left,
            text="Linear Programming Problem",
            font=("Arial", 14, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        objective = ttk.LabelFrame(
            left, text="Objective function", padding=8
        )
        objective.grid(row=1, column=0, sticky="ew", pady=5)

        ttk.Label(objective, text="Goal").grid(
            row=0, column=0, sticky="w"
        )
        self.sense = ttk.Combobox(
            objective,
            values=["Maximize", "Minimize"],
            state="readonly",
            width=10,
        )
        self.sense.set("Maximize")
        self.sense.grid(row=0, column=1, columnspan=2, sticky="w")

        ttk.Label(objective, text="Z =").grid(
            row=1, column=0, sticky="w", pady=(8, 0)
        )

        self.c1 = ttk.Entry(objective, width=8)
        self.c1.grid(row=1, column=1, pady=(8, 0))
        ttk.Label(objective, text="x +").grid(
            row=1, column=2, pady=(8, 0)
        )
        self.c2 = ttk.Entry(objective, width=8)
        self.c2.grid(row=1, column=3, pady=(8, 0))
        ttk.Label(objective, text="y").grid(
            row=1, column=4, pady=(8, 0)
        )

        constraints_box = ttk.LabelFrame(
            left, text="Constraints", padding=8
        )
        constraints_box.grid(row=2, column=0, sticky="ew", pady=5)

        headers = ["x", "y", "Relation", "RHS", ""]
        for col, heading in enumerate(headers):
            ttk.Label(
                constraints_box, text=heading
            ).grid(row=0, column=col, padx=3, pady=3)

        self.rows_frame = ttk.Frame(constraints_box)
        self.rows_frame.grid(
            row=1, column=0, columnspan=5, sticky="ew"
        )

        ttk.Button(
            constraints_box,
            text="+ Add constraint",
            command=self.add_constraint,
        ).grid(row=2, column=0, columnspan=5, sticky="w", pady=6)

        ttk.Label(
            left, text="Non-negativity: x ≥ 0, y ≥ 0"
        ).grid(row=3, column=0, sticky="w", pady=4)

        actions = ttk.Frame(left)
        actions.grid(row=4, column=0, sticky="ew", pady=8)

        ttk.Button(
            actions, text="Solve", command=self.solve
        ).grid(row=0, column=0, padx=(0, 5))

        ttk.Button(
            actions, text="Load example", command=self.load_example
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            actions, text="Clear", command=self.clear
        ).grid(row=0, column=2, padx=5)

        report_box = ttk.LabelFrame(
            left, text="Solution report", padding=6
        )
        report_box.grid(row=5, column=0, sticky="nsew", pady=5)
        left.rowconfigure(5, weight=1)

        self.report = tk.Text(
            report_box,
            width=43,
            height=14,
            wrap="word",
            font=("Consolas", 10),
        )
        self.report.pack(side="left", fill="both", expand=True)

        report_scroll = ttk.Scrollbar(
            report_box, command=self.report.yview
        )
        report_scroll.pack(side="right", fill="y")
        self.report.configure(yscrollcommand=report_scroll.set)

        # Right side: Matplotlib graph
        graph_box = ttk.LabelFrame(
            main, text="Graphical solution", padding=5
        )
        graph_box.grid(
            row=0, column=1, sticky="nsew", padx=(10, 0)
        )
        graph_box.rowconfigure(0, weight=1)
        graph_box.columnconfigure(0, weight=1)

        self.figure = Figure(figsize=(7, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(
            self.figure, master=graph_box
        )
        self.canvas.get_tk_widget().grid(
            row=0, column=0, sticky="nsew"
        )
        self.draw_empty_graph()

    def add_constraint(self, a="1", b="1", op="<=", rhs="10"):
        row = len(self.constraint_rows)
        frame = self.rows_frame

        ea = ttk.Entry(frame, width=7)
        ea.grid(row=row, column=0, padx=3, pady=2)
        ea.insert(0, a)

        eb = ttk.Entry(frame, width=7)
        eb.grid(row=row, column=1, padx=3, pady=2)
        eb.insert(0, b)

        relation = ttk.Combobox(
            frame, values=["<=", ">=", "="],
            state="readonly", width=5
        )
        relation.grid(row=row, column=2, padx=3, pady=2)
        relation.set(op)

        erhs = ttk.Entry(frame, width=7)
        erhs.grid(row=row, column=3, padx=3, pady=2)
        erhs.insert(0, rhs)

        row_data = {
            "frame": frame,
            "a": ea,
            "b": eb,
            "op": relation,
            "rhs": erhs,
        }

        remove_button = ttk.Button(
            frame,
            text="X",
            width=3,
            command=lambda item=row_data: self.remove_constraint(item),
        )
        remove_button.grid(row=row, column=4, padx=3, pady=2)
        row_data["remove_button"] = remove_button

        self.constraint_rows.append(row_data)

    def remove_constraint(self, item):
        if item not in self.constraint_rows:
            return

        for key in ("a", "b", "op", "rhs", "remove_button"):
            item[key].destroy()

        self.constraint_rows.remove(item)
        self.refresh_constraint_rows()
        self.report.delete("1.0", "end")
        self.draw_empty_graph()
        self.save_state()

    def refresh_constraint_rows(self):
        for row, item in enumerate(self.constraint_rows):
            for col, key in enumerate(("a", "b", "op", "rhs")):
                item[key].grid(
                    row=row, column=col, padx=3, pady=2
                )
            item["remove_button"].grid(
                row=row, column=4, padx=3, pady=2
            )

    def clear(self):
        self.c1.delete(0, "end")
        self.c2.delete(0, "end")

        for item in self.constraint_rows:
            for key in ("a", "b", "op", "rhs", "remove_button"):
                item[key].destroy()

        self.constraint_rows.clear()
        self.report.delete("1.0", "end")
        self.draw_empty_graph()
        self.save_state()

    def load_example(self):
        self.clear()
        self.c1.insert(0, "40")
        self.c2.insert(0, "30")
        self.sense.set("Maximize")
        self.add_constraint("2", "1", "<=", "40")
        self.add_constraint("1", "2", "<=", "50")
        self.save_state()

    def read_problem(self):
        try:
            c1 = float(self.c1.get())
            c2 = float(self.c2.get())
        except ValueError as error:
            raise ValueError(
                "Enter valid numeric objective coefficients."
            ) from error

        if not np.isfinite(c1) or not np.isfinite(c2):
            raise ValueError("Objective coefficients must be finite.")

        if not self.constraint_rows:
            raise ValueError("Add at least one constraint.")

        constraints = []
        for index, row in enumerate(self.constraint_rows, 1):
            try:
                a = float(row["a"].get())
                b = float(row["b"].get())
                rhs = float(row["rhs"].get())
            except ValueError as error:
                raise ValueError(
                    f"Constraint {index}: enter valid numeric values."
                ) from error

            op = row["op"].get()

            if not all(np.isfinite(v) for v in (a, b, rhs)):
                raise ValueError(
                    f"Constraint {index}: values must be finite."
                )

            if abs(a) < 1e-12 and abs(b) < 1e-12:
                raise ValueError(
                    f"Constraint {index}: x and y coefficients "
                    "cannot both be zero."
                )

            if op not in ("<=", ">=", "="):
                raise ValueError(
                    f"Choose a relation for constraint {index}."
                )

            constraints.append(
                {"a": a, "b": b, "op": op, "rhs": rhs}
            )

        return c1, c2, self.sense.get(), constraints

    def solve(self):
        try:
            c1, c2, sense, constraints = self.read_problem()
            result = solve_lpp(c1, c2, sense, constraints)
            self.display_report(c1, c2, result)
            self.plot_graph(c1, c2, sense, constraints, result)
        except (ValueError, OverflowError) as error:
            messagebox.showerror("Invalid input", str(error))
        except np.linalg.LinAlgError:
            messagebox.showerror(
                "Calculation error",
                "The numerical calculation failed. "
                "Check the constraint coefficients.",
            )

    def display_report(self, c1, c2, result):
        self.report.delete("1.0", "end")
        self.report.insert(
            "end", f"Status: {result['status'].upper()}\n\n"
        )

        if result["status"] == "infeasible":
            self.report.insert(
                "end",
                "No point satisfies all constraints and "
                "non-negativity restrictions.\n",
            )
            return

        self.report.insert("end", "Feasible corner points:\n")
        for x, y in result["points"]:
            z = c1 * x + c2 * y
            self.report.insert(
                "end", f"  ({x:.4g}, {y:.4g})  Z = {z:.4g}\n"
            )

        if result["status"] == "unbounded":
            self.report.insert(
                "end", "\nThe objective can improve indefinitely.\n"
            )
            return

        self.report.insert(
            "end", f"\nOptimal Z = {result['optimum']:.8g}\n"
        )

        if result["status"] == "multiple":
            self.report.insert(
                "end", "Multiple optimal solutions exist.\n"
            )

        self.report.insert("end", "\nOptimal point(s):\n")
        for x, y in result["optimal_points"]:
            self.report.insert(
                "end", f"  x = {x:.8g}, y = {y:.8g}\n"
            )

    def draw_empty_graph(self):
        self.ax.clear()
        self.ax.set_title("Enter a problem and click Solve")
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 20)
        self.ax.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_graph(self, c1, c2, sense, constraints, result):
        ax = self.ax
        ax.clear()

        xs = [point[0] for point in result["points"]]
        ys = [point[1] for point in result["points"]]
        intercept_x, intercept_y = [], []

        for constraint in constraints:
            if abs(constraint["a"]) > 1e-12:
                intercept_x.append(
                    constraint["rhs"] / constraint["a"]
                )
            if abs(constraint["b"]) > 1e-12:
                intercept_y.append(
                    constraint["rhs"] / constraint["b"]
                )

        positive_x = [value for value in intercept_x if value > 0]
        positive_y = [value for value in intercept_y if value > 0]

        xmax = max(
            [10.0]
            + [1.25 * value for value in xs if value > 0]
            + [1.15 * value for value in positive_x]
        )
        ymax = max(
            [10.0]
            + [1.25 * value for value in ys if value > 0]
            + [1.15 * value for value in positive_y]
        )

        xmax = min(xmax, 1e6)
        ymax = min(ymax, 1e6)

        boundaries = [
            (c["a"], c["b"], c["rhs"]) for c in constraints
        ]
        boundaries.extend([
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (1.0, 0.0, xmax),
            (0.0, 1.0, ymax),
        ])

        clipped = []
        for line1, line2 in combinations_for_plot(boundaries):
            point = intersect(line1, line2)
            if point is None:
                continue

            x, y = point
            if (
                -1e-7 <= x <= xmax + 1e-7
                and -1e-7 <= y <= ymax + 1e-7
                and is_feasible(x, y, constraints)
            ):
                if not any(
                    np.hypot(x - px, y - py) < 1e-7
                    for px, py in clipped
                ):
                    clipped.append((max(0, x), max(0, y)))

        if len(clipped) >= 3:
            center = np.mean(clipped, axis=0)
            clipped.sort(
                key=lambda point: np.arctan2(
                    point[1] - center[1],
                    point[0] - center[0],
                )
            )
            ax.add_patch(Polygon(
                clipped,
                closed=True,
                facecolor="green",
                edgecolor="green",
                alpha=0.22,
                label="Feasible region",
            ))

        xline = np.linspace(0, xmax, 500)
        for i, constraint in enumerate(constraints, 1):
            a, b, rhs = (
                constraint["a"],
                constraint["b"],
                constraint["rhs"],
            )

            if abs(b) > 1e-12:
                yline = (rhs - a * xline) / b
                valid = (yline >= 0) & (yline <= ymax)
                ax.plot(
                    xline[valid],
                    yline[valid],
                    label=(
                        f"C{i}: {a:g}x + {b:g}y "
                        f"{constraint['op']} {rhs:g}"
                    ),
                )
            elif abs(a) > 1e-12:
                xvalue = rhs / a
                if 0 <= xvalue <= xmax:
                    ax.axvline(
                        xvalue,
                        label=f"C{i}: {a:g}x {constraint['op']} {rhs:g}",
                    )

        if result["points"]:
            px, py = zip(*result["points"])
            ax.scatter(
                px, py, color="black", s=28, zorder=4,
                label="Feasible corner points",
            )

            for i, (x, y) in enumerate(result["points"]):
                label = chr(ord("A") + i)
                ax.annotate(
                    f"{label} ({x:g}, {y:g})",
                    xy=(x, y),
                    xytext=(8, 8),
                    textcoords="offset points",
                    fontsize=9,
                    color="black",
                    bbox=dict(
                        boxstyle="round,pad=0.25",
                        fc="white",
                        alpha=0.85,
                        ec="none",
                    ),
                    zorder=6,
                )

        if result.get("optimal_points"):
            ox, oy = zip(*result["optimal_points"])
            ax.scatter(
                ox, oy, color="red", marker="*", s=180, zorder=5,
                label="Optimal point",
            )

        ax.set_xlim(0, xmax)
        ax.set_ylim(0, ymax)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title(f"{sense} Z = {c1:g}x + {c2:g}y")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, loc="best")
        self.figure.tight_layout()
        self.canvas.draw()

    # ------------------------------------------------------------------
    # Other method pages
    # ------------------------------------------------------------------

    def build_simplex_page(self):
        """Build a working Simplex UI connected to SIMPLEX_METHOD/solver.py."""
        page = self.simplex_page
        page.columnconfigure(0, weight=1)
        page.rowconfigure(1, weight=1)

        header = ttk.Frame(page, padding=(20, 16, 20, 8))
        header.grid(row=0, column=0, sticky="ew")

        ttk.Label(
            header, text="Simplex Method", font=("Arial", 18, "bold")
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="Maximize a linear objective using the tableau-based Simplex method.",
        ).pack(anchor="w", pady=(4, 0))

        content = ttk.Frame(page, padding=(20, 8, 20, 20))
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(3, weight=1)

        settings = ttk.LabelFrame(content, text="Problem setup", padding=10)
        settings.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(settings, text="Number of variables").grid(
            row=0, column=0, sticky="w"
        )
        self.simplex_var_count = tk.IntVar(value=2)
        self.simplex_var_spin = ttk.Spinbox(
            settings, from_=1, to=10, width=5,
            textvariable=self.simplex_var_count,
            command=self.rebuild_simplex_inputs,
        )
        self.simplex_var_spin.grid(row=0, column=1, padx=(8, 16), sticky="w")
        self.simplex_var_spin.bind(
            "<Return>", lambda _event: self.rebuild_simplex_inputs()
        )
        self.simplex_var_spin.bind(
            "<FocusOut>", lambda _event: self.rebuild_simplex_inputs()
        )

        ttk.Label(settings, text="Goal").grid(row=0, column=2, sticky="w")
        ttk.Label(
            settings, text="Maximize", font=("Arial", 9, "bold")
        ).grid(row=0, column=3, padx=(8, 0), sticky="w")

        objective_box = ttk.LabelFrame(
            content, text="Objective function: Maximize Z", padding=10
        )
        objective_box.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.simplex_objective_box = objective_box
        self.simplex_objective_entries = []
        self.simplex_objective_labels = []

        constraints_box = ttk.LabelFrame(
            content, text="Constraints (decision variables are non-negative)", padding=10
        )
        constraints_box.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.simplex_constraints_box = constraints_box

        self.simplex_constraint_header = ttk.Frame(constraints_box)
        self.simplex_constraint_header.grid(row=0, column=0, sticky="w")

        self.simplex_rows_frame = ttk.Frame(constraints_box)
        self.simplex_rows_frame.grid(row=1, column=0, sticky="w")

        controls = ttk.Frame(constraints_box)
        controls.grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Button(
            controls, text="+ Add constraint",
            command=self.add_simplex_constraint,
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            controls, text="Load example",
            command=self.load_simplex_example,
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            controls, text="Solve",
            command=self.solve_simplex,
        ).pack(side="left")

        results_box = ttk.LabelFrame(content, text="Simplex result", padding=8)
        results_box.grid(row=3, column=0, sticky="nsew")
        results_box.rowconfigure(0, weight=1)
        results_box.columnconfigure(0, weight=1)

        self.simplex_report = tk.Text(
            results_box, height=10, wrap="word", font=("Consolas", 10)
        )
        self.simplex_report.grid(row=0, column=0, sticky="nsew")
        simplex_scroll = ttk.Scrollbar(
            results_box, orient="vertical",
            command=self.simplex_report.yview,
        )
        simplex_scroll.grid(row=0, column=1, sticky="ns")
        self.simplex_report.configure(yscrollcommand=simplex_scroll.set)

        self.simplex_constraint_rows = []
        self.rebuild_simplex_inputs()
        self.load_simplex_example()

    def rebuild_simplex_inputs(self):
        """Rebuild objective and constraint coefficient widgets for n variables."""
        if not hasattr(self, "simplex_objective_box"):
            return

        try:
            num_variables = int(self.simplex_var_count.get())
        except (ValueError, tk.TclError):
            return

        if not 1 <= num_variables <= 10:
            return

        old_objective = [
            entry.get() for entry in getattr(self, "simplex_objective_entries", [])
        ]
        old_constraints = []
        for row in getattr(self, "simplex_constraint_rows", []):
            old_constraints.append({
                "coefficients": [entry.get() for entry in row["coefficients"]],
                "op": row["op"].get(),
                "rhs": row["rhs"].get(),
            })

        for widget in self.simplex_objective_box.winfo_children():
            widget.destroy()
        self.simplex_objective_entries = []
        self.simplex_objective_labels = []

        for j in range(num_variables):
            ttk.Label(
                self.simplex_objective_box, text=f"x{j + 1}"
            ).grid(row=0, column=2 * j, padx=(2, 4), pady=2)
            entry = ttk.Entry(self.simplex_objective_box, width=8)
            entry.grid(row=0, column=2 * j + 1, padx=(0, 8), pady=2)
            value = old_objective[j] if j < len(old_objective) else ("3" if j == 0 else "5" if j == 1 else "0")
            entry.insert(0, value)
            self.simplex_objective_entries.append(entry)

        for widget in self.simplex_constraint_header.winfo_children():
            widget.destroy()
        for col in range(num_variables):
            ttk.Label(
                self.simplex_constraint_header,
                text=f"x{col + 1}",
            ).grid(row=0, column=col, padx=3, pady=2)
        ttk.Label(self.simplex_constraint_header, text="Relation").grid(
            row=0, column=num_variables, padx=3, pady=2
        )
        ttk.Label(self.simplex_constraint_header, text="RHS").grid(
            row=0, column=num_variables + 1, padx=3, pady=2
        )
        ttk.Label(self.simplex_constraint_header, text="").grid(
            row=0, column=num_variables + 2, padx=3, pady=2
        )

        # Destroy old constraint widgets and recreate them while preserving values.
        for row in getattr(self, "simplex_constraint_rows", []):
            for widget in row["widgets"]:
                widget.destroy()
        self.simplex_constraint_rows = []

        if old_constraints:
            for constraint in old_constraints:
                coefficients = constraint["coefficients"][:num_variables]
                coefficients += ["0"] * (num_variables - len(coefficients))
                self.add_simplex_constraint(
                    coefficients=coefficients,
                    op=constraint["op"],
                    rhs=constraint["rhs"],
                )
        else:
            self.add_simplex_constraint(
                coefficients=["1"] + ["0"] * (num_variables - 1),
                op="<=", rhs="4",
            )
            self.add_simplex_constraint(
                coefficients=["0", "2"][:num_variables] + (
                    ["0"] * max(0, num_variables - 2)
                ),
                op="<=", rhs="12",
            )
            self.add_simplex_constraint(
                coefficients=(["3", "2"][:num_variables] + (
                    ["0"] * max(0, num_variables - 2)
                )),
                op="<=", rhs="18",
            )

    def add_simplex_constraint(self, coefficients=None, op="<=", rhs="10"):
        num_variables = len(self.simplex_objective_entries)
        if coefficients is None:
            coefficients = ["0"] * num_variables
            if coefficients:
                coefficients[0] = "1"
        else:
            coefficients = list(coefficients)
            coefficients = coefficients[:num_variables]
            coefficients += ["0"] * (num_variables - len(coefficients))

        row_index = len(self.simplex_constraint_rows)
        widgets = []
        coefficient_entries = []

        for j in range(num_variables):
            entry = ttk.Entry(self.simplex_rows_frame, width=8)
            entry.grid(row=row_index, column=j, padx=3, pady=2)
            entry.insert(0, str(coefficients[j]))
            coefficient_entries.append(entry)
            widgets.append(entry)

        relation = ttk.Combobox(
            self.simplex_rows_frame,
            values=["<=", ">=", "="],
            state="readonly",
            width=5,
        )
        relation.grid(row=row_index, column=num_variables, padx=3, pady=2)
        relation.set(op)
        widgets.append(relation)

        rhs_entry = ttk.Entry(self.simplex_rows_frame, width=8)
        rhs_entry.grid(row=row_index, column=num_variables + 1, padx=3, pady=2)
        rhs_entry.insert(0, str(rhs))
        widgets.append(rhs_entry)

        row_data = {
            "coefficients": coefficient_entries,
            "op": relation,
            "rhs": rhs_entry,
            "widgets": widgets,
        }

        remove_button = ttk.Button(
            self.simplex_rows_frame,
            text="X",
            width=3,
            command=lambda item=row_data: self.remove_simplex_constraint(item),
        )
        remove_button.grid(
            row=row_index, column=num_variables + 2, padx=3, pady=2
        )
        widgets.append(remove_button)
        row_data["remove_button"] = remove_button

        self.simplex_constraint_rows.append(row_data)

    def remove_simplex_constraint(self, item):
        if item not in self.simplex_constraint_rows:
            return
        for widget in item["widgets"]:
            widget.destroy()
        self.simplex_constraint_rows.remove(item)
        for row_index, row in enumerate(self.simplex_constraint_rows):
            for col, widget in enumerate(row["widgets"]):
                widget.grid(row=row_index, column=col, padx=3, pady=2)

    def load_simplex_example(self):
        self.simplex_var_count.set(2)
        self.rebuild_simplex_inputs()

        for entry, value in zip(self.simplex_objective_entries, ("3", "5")):
            entry.delete(0, "end")
            entry.insert(0, value)

        # Replace example constraints with the standard 3-constraint example.
        for row in list(self.simplex_constraint_rows):
            for widget in row["widgets"]:
                widget.destroy()
        self.simplex_constraint_rows.clear()

        self.add_simplex_constraint(["1", "0"], "<=", "4")
        self.add_simplex_constraint(["0", "2"], "<=", "12")
        self.add_simplex_constraint(["3", "2"], "<=", "18")

        self.simplex_report.delete("1.0", "end")
        self.simplex_report.insert(
            "end",
            "Example loaded:\nMaximize Z = 3x1 + 5x2\n"
            "x1 <= 4\n2x2 <= 12\n3x1 + 2x2 <= 18\n",
        )

    def solve_simplex(self):
        if max_simplex is None:
            messagebox.showerror(
                "Simplex solver not found",
                "Could not load SIMPLEX_METHOD/solver.py.\n"
                "Check that the file exists in that folder.",
            )
            return

        try:
            objective = [float(entry.get()) for entry in self.simplex_objective_entries]
            if not objective or not all(np.isfinite(value) for value in objective):
                raise ValueError("Objective coefficients must be finite numbers.")

            if not self.simplex_constraint_rows:
                raise ValueError("Add at least one constraint.")

            constraints = []
            for index, row in enumerate(self.simplex_constraint_rows, start=1):
                try:
                    coefficients = [float(entry.get()) for entry in row["coefficients"]]
                    rhs = float(row["rhs"].get())
                except ValueError as error:
                    raise ValueError(
                        f"Constraint {index}: enter numeric coefficients and RHS."
                    ) from error

                if not all(np.isfinite(value) for value in coefficients + [rhs]):
                    raise ValueError(f"Constraint {index}: values must be finite.")

                constraint = {
                    f"var{j + 1}": value
                    for j, value in enumerate(coefficients)
                }
                constraint["op"] = row["op"].get()
                constraint["rhs"] = rhs
                constraints.append(constraint)

            self.simplex_report.delete("1.0", "end")
            self.simplex_report.insert("end", "Solving...\n")
            self.root.update_idletasks()

            result = max_simplex(objective, constraints)

            self.simplex_report.delete("1.0", "end")
            self.simplex_report.insert(
                "end", f"Status: {result['status'].upper()}\n"
            )
            self.simplex_report.insert(
                "end", f"Iterations: {result.get('iterations', '-')}\n"
            )

            if result["status"] == "optimal":
                self.simplex_report.insert("end", "\nOptimal solution:\n")
                for index, value in enumerate(result["solution"], start=1):
                    self.simplex_report.insert(
                        "end", f"x{index} = {value:.8g}\n"
                    )
                self.simplex_report.insert(
                    "end", f"\nMaximum Z = {result['optimum']:.8g}\n"
                )
            elif result["status"] == "unbounded":
                self.simplex_report.insert(
                    "end",
                    "\nThe objective is unbounded. No finite maximum exists.\n",
                )
            elif result["status"] == "iteration_limit":
                self.simplex_report.insert(
                    "end", "\nStopped after reaching the iteration limit.\n"
                )
            else:
                self.simplex_report.insert(
                    "end",
                    "\nThe problem could not be solved by the current "
                    "basic Simplex implementation.\n",
                )

        except (ValueError, TypeError, OverflowError, ArithmeticError) as error:
            messagebox.showerror("Simplex input/calculation error", str(error))

    def build_placeholder_page(self, page, title, description):
        container = ttk.Frame(page, padding=25)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container, text=title, font=("Arial", 18, "bold")
        ).pack(anchor="w", pady=(0, 10))

        ttk.Label(
            container, text=description, wraplength=700
        ).pack(anchor="w", pady=(0, 20))

        ttk.Label(
            container,
            text="Status: Planned",
            foreground="gray",
        ).pack(anchor="w")


def combinations_for_plot(lines):
    from itertools import combinations
    return combinations(lines, 2)


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphicalLPPApp(root)
    root.mainloop()
