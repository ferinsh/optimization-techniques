# Optimization Techniques

A Python-based desktop application for solving Operations Research problems, starting with the **Graphical Method for Linear Programming (LPP)**.

The application provides an interactive interface for entering an objective function and constraints, visualizing the feasible region, identifying corner points, and determining the optimal solution.

The long-term goal is to bring multiple Operations Research and optimization techniques together in one desktop application.

## Features

### Graphical Method for Linear Programming

- Enter objective function coefficients for a two-variable LPP.
- Choose maximization or minimization.
- Add and remove constraints using `<=`, `>=`, or `=`.
- Visualize constraint lines and the feasible region.
- Identify and label feasible corner points.
- Evaluate the objective function at candidate solutions.
- Display optimal point(s) and the optimal objective value for supported problems.
- Report infeasible and unbounded problem statuses.
- Automatically save graphical-method inputs and restore them when the application restarts.
- Autosave inputs every 30 seconds and when the application closes.

### Simplex Method

- Enter objective-function coefficients for multiple decision variables.
- Add and remove constraints.
- Choose constraint relations (`<=`, `>=`, or `=`) in the interface.
- Run the tableau-based Simplex implementation for supported maximization problems.
- Display the solution status, iteration count, decision-variable values, and maximum objective value.
- Load a built-in example problem.

**Current Simplex limitation:** The connected solver currently supports problems that can start with a feasible slack-variable basis after RHS normalization. Problems requiring artificial variables, including some `>=` and equality constraints, need a future Big M or Two-Phase implementation. The interface currently handles maximization.

### Additional Method Pages

The sidebar also provides separate pages for:

- **Big M Method** — planned; page is currently a placeholder.
- **Transportation Problems** — planned; page is currently a placeholder.

These pages establish the navigation structure for adding more Operations Research techniques in future updates.

## Technology Stack

- **Python** — Core application and optimization logic.
- **Tkinter** — Desktop graphical user interface.
- **Matplotlib** — Graph plotting and feasible-region visualization.
- **NumPy** — Numerical computations.
- **JSON** — Persistence of user input settings.

## Project Structure

```text
OR_PYTHON_APP/
│
├── OR_GRAPHICAL_SOLVER/
│   ├── __pycache__/             # Python cache (generated)
│   ├── lpp_settings.json        # Local saved graphical-method inputs, if present
│   └── solver.py                # Graphical-method solver
│
├── SIMPLEX_METHOD/
│   ├── __pycache__/             # Python cache (generated)
│   ├── algorithm.md             # Simplex algorithm notes
│   └── solver.py                # Simplex tableau implementation
│
├── main.py                      # Existing application entry point (if used)
├── main_with_simplex_ui.py      # Sidebar application with Graphical and Simplex pages
├── app.py                       # Existing launcher or application entry point (if used)
├── requirements.txt             # Python dependencies
├── .gitignore
├── OR Graphical Method Solver.spec  # PyInstaller configuration
├── .venv/                       # Local virtual environment (not committed)
├── build/                       # PyInstaller build output (not committed)
└── dist/                        # Packaged application output (not committed)
```

### Important Files

| File | Purpose |
|---|---|
| `main_with_simplex_ui.py` | Current sidebar-based interface connecting the Graphical Method and Simplex pages. |
| `OR_GRAPHICAL_SOLVER/solver.py` | Feasible-region, corner-point, and graphical LPP solving logic. |
| `SIMPLEX_METHOD/solver.py` | Tableau-based Simplex solver for supported maximization problems. |
| `SIMPLEX_METHOD/algorithm.md` | Notes describing the Simplex algorithm. |
| `OR_GRAPHICAL_SOLVER/lpp_settings.json` | Local persisted graphical-method inputs, when present. |
| `requirements.txt` | Python packages required by the application. |
| `OR Graphical Method Solver.spec` | PyInstaller configuration; review its paths before using it to package the sidebar application. |
| `.gitignore` | Specifies generated and local files that Git should ignore. |

The sidebar application loads the two `solver.py` files from their separate folders. Keep those files in their current locations unless you also update the imports.

## Installation and Setup

### Requirements

- Windows
- Python 3.12 or a compatible Python version
- Git (optional, for cloning and version control)

### 1. Clone the repository

```bash
git clone https://github.com/ferinsh/optimization-techniques.git
cd optimization-techniques
```

### 2. Create a virtual environment

```powershell
py -3.12 -m venv .venv
```

### 3. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run Python directly through the virtual environment instead.

### 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 5. Run the application

From the project root, run the sidebar application:

```powershell
python main_with_simplex_ui.py
```

The app imports the graphical solver from `OR_GRAPHICAL_SOLVER/solver.py` and the Simplex solver from `SIMPLEX_METHOD/solver.py`.

If you are running an older entry point instead, use the command appropriate to that version.

## Building the Windows Application

The project can be packaged as a standalone Windows executable using PyInstaller.

Install PyInstaller if it is not already listed in your dependencies:

```powershell
python -m pip install pyinstaller
```

Build using the existing specification file:

```powershell
python -m PyInstaller "OR Graphical Method Solver.spec"
```

The generated application will normally be placed in the `dist/` directory. The exact output structure depends on the PyInstaller configuration.

## Roadmap

- [x] Graphical Method for two-variable LPP
- [x] Sidebar navigation between method pages
- [x] Simplex Method UI connected to a basic tableau solver
- [ ] Show each intermediate simplex tableau and pivot operation
- [ ] Add support for artificial variables with the Big M Method
- [ ] Implement the Two-Phase Method
- [ ] Implement Transportation Problems
- [ ] Implement Assignment Problems
- [ ] Add further Operations Research techniques
- [ ] Add more validation and automated tests for solver edge cases

## Project Goals

- Make Operations Research methods easier to explore and understand.
- Combine numerical calculations with graphical explanations.
- Keep each optimization algorithm modular and maintainable.
- Expand the application gradually without compromising the existing solvers.
- Provide a convenient desktop tool for students and anyone learning optimization.

## Development Status

**Early development.** The sidebar-based application currently includes the Graphical Method and a Simplex page connected to a basic solver. Big M and Transportation pages are placeholders; additional methods and solver capabilities are planned.

## License

No license has been selected yet. A license will be added when the project's distribution and reuse terms are decided.