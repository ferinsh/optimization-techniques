"""Tkinter page for displaying Simplex tableau iterations.

Expected input:
    iterations = [
        {
            "title": "Initial tableau",       # optional
            "columns": ["Basis", "x1", "x2", "s1", "RHS"],
            "rows": [
                ["s1", 1, 2, 1, 10],
                ["Z", -3, -5, 0, 0],
            ],
            "note": "Initial feasible tableau",  # optional
            "entering": "x2",                    # optional
            "leaving": "s1",                     # optional
            "pivot": 2,                           # optional
        },
        ...
    ]

This module displays tableau history supplied by the solver. It does not
calculate Simplex iterations itself; the solver must save each tableau snapshot.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Iterable, Mapping, Sequence


def _format_value(value: Any) -> str:
    """Format numeric tableau values without unnecessary trailing zeros."""
    if isinstance(value, float):
        if abs(value) < 1e-10:
            value = 0.0
        return f"{value:.6g}"
    return str(value)


class SimplexTableauPage(ttk.Frame):
    """A reusable, scrollable Tkinter page for browsing tableau iterations."""

    def __init__(self, parent: tk.Misc, **kwargs: Any) -> None:
        super().__init__(parent, **kwargs)
        self.iterations: list[dict[str, Any]] = []
        self.current_index = 0

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = ttk.Frame(self, padding=(16, 14, 16, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Simplex Tableau Iterations",
            font=("Arial", 17, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.subtitle = ttk.Label(
            header,
            text="Review each tableau produced while solving the LPP.",
        )
        self.subtitle.grid(row=1, column=0, sticky="w", pady=(4, 0))

        navigation = ttk.Frame(self, padding=(16, 4, 16, 8))
        navigation.grid(row=1, column=0, sticky="ew")
        navigation.columnconfigure(1, weight=1)

        self.previous_button = ttk.Button(
            navigation, text="← Previous", command=self.show_previous
        )
        self.previous_button.grid(row=0, column=0, sticky="w")

        self.iteration_label = ttk.Label(
            navigation, text="No iterations", anchor="center"
        )
        self.iteration_label.grid(row=0, column=1, sticky="ew", padx=10)

        self.next_button = ttk.Button(
            navigation, text="Next →", command=self.show_next
        )
        self.next_button.grid(row=0, column=2, sticky="e")

        body = ttk.Frame(self, padding=(16, 0, 16, 16))
        body.grid(row=2, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        self.tableau_title = ttk.Label(
            body, text="No tableau available", font=("Arial", 12, "bold")
        )
        self.tableau_title.grid(row=0, column=0, sticky="w", pady=(0, 8))

        table_frame = ttk.Frame(body)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.table = ttk.Treeview(table_frame, show="headings", height=12)
        self.table.grid(row=0, column=0, sticky="nsew")

        vertical_scroll = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.table.yview
        )
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll = ttk.Scrollbar(
            table_frame, orient="horizontal", command=self.table.xview
        )
        horizontal_scroll.grid(row=1, column=0, sticky="ew")

        self.table.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set,
        )

        self.details = tk.Text(
            body,
            height=4,
            wrap="word",
            font=("Consolas", 10),
            state="disabled",
        )
        self.details.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        self._render_current()

    def display_iterations(
        self,
        iterations: Iterable[Mapping[str, Any]],
        *,
        objective_value: Any = None,
        status: str | None = None,
    ) -> None:
        """Load and display snapshots returned by the solver.

        Each snapshot should contain `columns` and `rows`. `title`, `note`,
        `entering`, `leaving`, and `pivot` are optional display metadata.
        """
        normalized: list[dict[str, Any]] = []
        for number, snapshot in enumerate(iterations, start=0):
            item = dict(snapshot)
            item.setdefault(
                "title",
                "Initial tableau" if number == 0 else f"Iteration {number}",
            )
            item.setdefault("columns", [])
            item.setdefault("rows", [])
            normalized.append(item)

        self.iterations = normalized
        self.current_index = 0
        self.objective_value = objective_value
        self.status = status
        self._render_current()

    def clear(self) -> None:
        """Clear the page before a new solve."""
        self.display_iterations([])

    def show_previous(self) -> None:
        if self.current_index > 0:
            self.current_index -= 1
            self._render_current()

    def show_next(self) -> None:
        if self.current_index < len(self.iterations) - 1:
            self.current_index += 1
            self._render_current()

    def _set_details(self, text: str) -> None:
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", text)
        self.details.configure(state="disabled")

    def _render_current(self) -> None:
        for item_id in self.table.get_children():
            self.table.delete(item_id)

        if not self.iterations:
            self.table["columns"] = ()
            self.tableau_title.configure(text="No tableau available")
            self.iteration_label.configure(text="No iterations")
            self.previous_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
            self._set_details(
                "Run the Simplex solver and pass its saved tableau snapshots "
                "to display_iterations()."
            )
            return

        snapshot = self.iterations[self.current_index]
        columns: Sequence[Any] = snapshot.get("columns", [])
        rows: Sequence[Sequence[Any]] = snapshot.get("rows", [])

        # If column labels were not supplied, generate generic ones.
        width = max(
            [len(columns)] + [len(row) for row in rows] + [1]
        )
        if not columns:
            columns = [f"Column {index + 1}" for index in range(width)]
        else:
            columns = list(columns)
            if len(columns) < width:
                columns.extend(
                    f"Column {index + 1}"
                    for index in range(len(columns), width)
                )

        column_ids = [f"c{index}" for index in range(len(columns))]
        self.table["columns"] = column_ids

        for index, (column_id, heading) in enumerate(zip(column_ids, columns)):
            self.table.heading(column_id, text=str(heading))
            self.table.column(
                column_id,
                width=115 if index else 135,
                minwidth=70,
                anchor="center",
                stretch=True,
            )

        for row_index, row in enumerate(rows):
            values = [_format_value(value) for value in row]
            values.extend([""] * (len(columns) - len(values)))
            self.table.insert("", "end", values=values[: len(columns)])

        title = str(snapshot.get("title", f"Iteration {self.current_index}"))
        self.tableau_title.configure(text=title)
        self.iteration_label.configure(
            text=f"Tableau {self.current_index + 1} of {len(self.iterations)}"
        )
        self.previous_button.configure(
            state="normal" if self.current_index > 0 else "disabled"
        )
        self.next_button.configure(
            state=(
                "normal"
                if self.current_index < len(self.iterations) - 1
                else "disabled"
            )
        )

        detail_lines: list[str] = []
        if snapshot.get("entering") is not None:
            detail_lines.append(f"Entering variable: {snapshot['entering']}")
        if snapshot.get("leaving") is not None:
            detail_lines.append(f"Leaving variable: {snapshot['leaving']}")
        if snapshot.get("pivot") is not None:
            detail_lines.append(f"Pivot element: {_format_value(snapshot['pivot'])}")
        if snapshot.get("note"):
            detail_lines.append(str(snapshot["note"]))
        if self.current_index == len(self.iterations) - 1:
            if self.status:
                detail_lines.append(f"Solver status: {self.status}")
            if self.objective_value is not None:
                detail_lines.append(
                    f"Objective value: {_format_value(self.objective_value)}"
                )
        self._set_details("\n".join(detail_lines) or "No iteration notes provided.")


if __name__ == "__main__":
    # Small standalone preview for testing the page without launching the app.
    root = tk.Tk()
    root.title("Simplex Tableau Viewer")
    root.geometry("900x520")

    page = SimplexTableauPage(root)
    page.pack(fill="both", expand=True)
    page.display_iterations(
        [
            {
                "title": "Initial tableau",
                "columns": ["Basis", "x1", "x2", "s1", "s2", "RHS"],
                "rows": [
                    ["s1", 1, 0, 1, 0, 4],
                    ["s2", 0, 2, 0, 1, 12],
                    ["Z", -3, -5, 0, 0, 0],
                ],
                "note": "Starting tableau (illustrative example).",
            },
            {
                "title": "Iteration 1",
                "columns": ["Basis", "x1", "x2", "s1", "s2", "RHS"],
                "rows": [
                    ["s1", 1, 0, 1, 0, 4],
                    ["x2", 0, 1, 0, 0.5, 6],
                    ["Z", -3, 0, 0, 2.5, 30],
                ],
                "entering": "x2",
                "leaving": "s2",
                "pivot": 2,
                "note": "Illustrative tableau only; use snapshots from your solver.",
            },
        ],
        objective_value=30,
        status="optimal",
    )
    root.mainloop()
