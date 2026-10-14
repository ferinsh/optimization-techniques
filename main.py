"""Application entry point."""
import sys
from pathlib import Path
import tkinter as tk

PROJECT_DIR = Path(__file__).resolve().parent
GRAPHICAL_SOLVER_DIR = PROJECT_DIR / "OR_GRAPHICAL_SOLVER"
if str(GRAPHICAL_SOLVER_DIR) not in sys.path:
    sys.path.insert(0, str(GRAPHICAL_SOLVER_DIR))

from ui.app import LPPApp


if __name__ == "__main__":
    root = tk.Tk()
    app = LPPApp(root)
    root.mainloop()
