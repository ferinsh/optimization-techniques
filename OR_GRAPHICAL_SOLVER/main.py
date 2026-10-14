import json
import os

import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import matplotlib

matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Polygon

from solver import solve_lpp, is_feasible, intersect


class GraphicalLPPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OR Graphical Method Solver")
        self.root.geometry("1150x760")
        self.root.minsize(900, 620)

        self.constraint_rows = []

        app_data = os.getenv("LOCALAPPDATA") or os.path.expanduser("~")

        self.save_path = os.path.join(
            app_data,
            "OR Graphical Method Solver",
            "lpp_settings.json"
        )

        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

        self.build_ui()
        # Restore the last saved inputs, or load the example.
        if not self.load_state():
            self.load_example()

        # Save when the user clicks the window's X button.
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start autosaving every 30 seconds.
        self.schedule_autosave()

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
                json.dump(state, file, indent = 4)

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

            # Restore objective function and optimization direction.
            self.c1.delete(0, "end")
            self.c1.insert(0, str(state.get("c1", "")))

            self.c2.delete(0, "end")
            self.c2.insert(0, str(state.get("c2", "")))

            self.sense.set(state["sense"])

            # Remove existing constraint widgets without deleting
            # their shared parent container.
            for row in self.constraint_rows:
                for key in ("a", "b", "op", "rhs", "remove_button"):
                    row[key].destroy()

            self.constraint_rows.clear()

            # Restore all saved constraints.
            for c in constraints:
                self.add_constraint(
                    a=str(c["a"]),
                    b=str(c["b"]),
                    op=c["op"],
                    rhs=str(c["rhs"]),
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

    def build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main = ttk.Frame(self.root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        # Left side: problem input and report
        left = ttk.Frame(main, padding=5)
        left.grid(row=0, column=0, sticky="nsew")
        left.columnconfigure(0, weight=1)

        ttk.Label(
            left, text="Linear Programming Problem",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        objective = ttk.LabelFrame(
            left, text="Objective function", padding=8
        )
        objective.grid(row=1, column=0, sticky="ew", pady=5)

        ttk.Label(objective, text="Goal").grid(
            row=0, column=0, sticky="w"
        )
        self.sense = ttk.Combobox(
            objective, values=["Maximize", "Minimize"],
            state="readonly", width=10
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
        constraints_box.grid(
            row=2, column=0, sticky="ew", pady=5
        )
        self.constraints_box = constraints_box

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
            constraints_box, text="+ Add constraint",
            command=self.add_constraint
        ).grid(row=2, column=0, columnspan=5, sticky="w", pady=6)

        ttk.Label(
            left, text="Non-negativity: x ≥ 0, y ≥ 0"
        ).grid(row=3, column=0, sticky="w", pady=4)

        actions = ttk.Frame(left)
        actions.grid(row=4, column=0, sticky="ew", pady=8)

        ttk.Button(
            actions, text="Solve",
            command=self.solve
        ).grid(row=0, column=0, padx=(0, 5))

        ttk.Button(
            actions, text="Load example",
            command=self.load_example
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            actions, text="Clear",
            command=self.clear
        ).grid(row=0, column=2, padx=5)

        report_box = ttk.LabelFrame(
            left, text="Solution report", padding=6
        )
        report_box.grid(
            row=5, column=0, sticky="nsew", pady=5
        )
        left.rowconfigure(5, weight=1)

        self.report = tk.Text(
            report_box, width=43, height=14,
            wrap="word", font=("Consolas", 10)
        )
        self.report.pack(
            side="left", fill="both", expand=True
        )

        report_scroll = ttk.Scrollbar(
            report_box, command=self.report.yview
        )
        report_scroll.pack(side="right", fill="y")
        self.report.configure(
            yscrollcommand=report_scroll.set
        )

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

    def add_constraint(self, a="1", b="1",
                       op="<=", rhs="10"):
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
            "frame": frame, "a": ea, "b": eb,
            "op": relation, "rhs": erhs
        }

        remove_button = ttk.Button(
            frame, text="X", width=3,
            command=lambda item=row_data: self.remove_constraint(item)
        )
        remove_button.grid(row=row, column=4, padx=3, pady=2)
        row_data["remove_button"] = remove_button

        self.constraint_rows.append(row_data)

    def remove_constraint(self, item):
        if item not in self.constraint_rows:
            return

        # Destroy the widgets belonging to this constraint only.
        for key in ("a", "b", "op", "rhs", "remove_button"):
            item[key].destroy()

        # Remove the constraint from the application's data.
        self.constraint_rows.remove(item)

        # Reposition the remaining rows.
        self.refresh_constraint_rows()

        # Clear the outdated solution and graph.
        self.report.delete("1.0", "end")
        self.draw_empty_graph()

        # Save the updated constraints immediately.
        self.save_state()

    def refresh_constraint_rows(self):
        # Re-grid existing widgets after a row is removed.
        for row, item in enumerate(self.constraint_rows):
            for col, key in enumerate(["a", "b", "op", "rhs"]):
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

    def load_example(self):
        self.clear()

        self.c1.insert(0, "40")
        self.c2.insert(0, "30")
        self.sense.set("Maximize")

        self.add_constraint("2", "1", "<=", "40")
        self.add_constraint("1", "2", "<=", "50")

    def read_problem(self):
        c1 = float(self.c1.get())
        c2 = float(self.c2.get())

        if not self.constraint_rows:
            raise ValueError("Add at least one constraint.")

        constraints = []

        for index, row in enumerate(self.constraint_rows, 1):
            a = float(row["a"].get())
            b = float(row["b"].get())
            rhs = float(row["rhs"].get())
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

            constraints.append({
                "a": a, "b": b, "op": op, "rhs": rhs
            })

        if not np.isfinite(c1) or not np.isfinite(c2):
            raise ValueError(
                "Objective coefficients must be finite."
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
                "Check the constraint coefficients."
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
                "non-negativity restrictions.\n"
            )
            return

        self.report.insert("end", "Feasible corner points:\n")

        for x, y in result["points"]:
            z = c1 * x + c2 * y
            self.report.insert(
                "end", f"  ({x:.4g}, {y:.4g})"
                f"  Z = {z:.4g}\n"
            )

        if result["status"] == "unbounded":
            self.report.insert(
                "end",
                "\nThe objective can improve indefinitely.\n"
            )
            return

        self.report.insert(
            "end",
            f"\nOptimal Z = {result['optimum']:.8g}\n"
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

        # Choose a useful viewing window from intercepts
        # and feasible corner points.
        xs = [p[0] for p in result["points"]]
        ys = [p[1] for p in result["points"]]
        intercept_x, intercept_y = [], []

        for c in constraints:
            if abs(c["a"]) > 1e-12:
                intercept_x.append(c["rhs"] / c["a"])
            if abs(c["b"]) > 1e-12:
                intercept_y.append(c["rhs"] / c["b"])

        positive_x = [v for v in intercept_x if v > 0]
        positive_y = [v for v in intercept_y if v > 0]

        xmax = max(
            [10.0] + [1.25 * v for v in xs if v > 0]
            + [1.15 * v for v in positive_x]
        )
        ymax = max(
            [10.0] + [1.25 * v for v in ys if v > 0]
            + [1.15 * v for v in positive_y]
        )

        # Prevent enormous graph ranges from poor input values.
        xmax = min(xmax, 1e6)
        ymax = min(ymax, 1e6)

        # Clip the feasible region to the visible plotting window.
        boundaries = [
            (c["a"], c["b"], c["rhs"])
            for c in constraints
        ]
        boundaries.extend([
            (1.0, 0.0, 0.0),      # x = 0
            (0.0, 1.0, 0.0),      # y = 0
            (1.0, 0.0, xmax),     # right plot edge
            (0.0, 1.0, ymax),     # top plot edge
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
                key=lambda p: np.arctan2(
                    p[1] - center[1],
                    p[0] - center[0]
                )
            )

            ax.add_patch(Polygon(
                clipped,
                closed=True,
                facecolor="green",
                edgecolor="green",
                alpha=0.22,
                label="Feasible region"
            ))

        xline = np.linspace(0, xmax, 500)

        for i, c in enumerate(constraints, 1):
            a, b, rhs = c["a"], c["b"], c["rhs"]

            if abs(b) > 1e-12:
                yline = (rhs - a * xline) / b
                valid = (yline >= 0) & (yline <= ymax)
                ax.plot(
                    xline[valid], yline[valid],
                    label=f"C{i}: {a:g}x + {b:g}y {c['op']} {rhs:g}"
                )
            elif abs(a) > 1e-12:
                xvalue = rhs / a
                if 0 <= xvalue <= xmax:
                    ax.axvline(
                        xvalue,
                        label=f"C{i}: {a:g}x {c['op']} {rhs:g}"
                    )

        
        if result["points"]:
            px, py = zip(*result["points"])

            ax.scatter(
                px, py,
                color="black",
                s=28,
                zorder=4,
                label="Feasible corner points"
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
                        ec="none"
                    ),
                    zorder=6
                )



        if result["optimal_points"]:
            ox, oy = zip(*result["optimal_points"])
            ax.scatter(
                ox, oy, color="red", marker="*",
                s=180, zorder=5, label="Optimal point"
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


def combinations_for_plot(lines):
    # Keep this separate from solver.py's candidate enumeration.
    from itertools import combinations
    return combinations(lines, 2)


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphicalLPPApp(root)
    root.mainloop()
