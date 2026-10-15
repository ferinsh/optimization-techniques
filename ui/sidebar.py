"""Sidebar navigation widget."""
from tkinter import ttk


class Sidebar(ttk.Frame):
    def __init__(self, parent, on_navigate, version, **kwargs):
        super().__init__(parent, padding=12, **kwargs)
        self.configure(width=195)
        self.grid_propagate(False)

        ttk.Label(
            self,
            text="OPTIMIZATION\nTECHNIQUES",
            font=("Arial", 12, "bold"),
            justify="left",
        ).pack(anchor="w", pady=(5, 20))

        ttk.Label(self, text="METHODS", font=("Arial", 9, "bold")).pack(
            anchor="w", pady=(0, 8)
        )

        ttk.Button(
            self, text="Graphical Method", command=lambda: on_navigate("graph")
        ).pack(fill="x", pady=3)

        ttk.Separator(self).pack(fill="x", pady=12)

        ttk.Button(
            self, text="Simplex Method", command=lambda: on_navigate("simplex")
        ).pack(fill="x", pady=3)

        ttk.Button(
            self, text="Big M Method", command=lambda: on_navigate("big_m")
        ).pack(fill="x", pady=3)

        ttk.Separator(self).pack(fill="x", pady=12)

        ttk.Button(
            self,
            text="Transportation",
            command=lambda: on_navigate("transportation"),
        ).pack(fill="x", pady=3)

        ttk.Label(self, text=f"Version {version}", foreground="gray").pack(
            side="bottom", anchor="w", pady=8
        )
