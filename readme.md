# Optimization Techniques

A Python desktop application for exploring **Operations Research (OR)** methods, starting with Linear Programming Problems (LPPs). It combines optimization calculations with an interactive interface and is being expanded to include additional techniques.

## Features

### Graphical Method

- Solve two-variable linear programming problems.
- Choose maximization or minimization.
- Add and remove constraints using `<=`, `>=`, or `=`.
- Plot constraint lines and visualize the feasible region.
- Identify feasible corner points and evaluate the objective function at candidate solutions.
- Display optimal point(s) and objective values for supported problems.
- Report infeasible and unbounded statuses when detected by the solver.
- Save graphical-method inputs locally and restore them after restart.
- Autosave inputs every 30 seconds and when the application closes.

### Simplex Method

- Enter objective-function coefficients for multiple decision variables.
- Add and remove constraints in the interface.
- Select `<=`, `>=`, or `=` constraint relations.
- Solve supported maximization problems using a tableau-based Simplex solver.
- Solve supported minimization problems by converting the primal problem to its dual, solving the dual, and recovering a primal solution using complementary slackness and active-constraint checks.
- Display solution status, iteration count, decision-variable values, and objective value.
- Display the dual solution and conversion/recovery steps for supported minimization problems.
- Load a built-in example problem.
- Browse tableau snapshots with Previous and Next navigation when the solver supplies compatible `tableau_history`.
- Display entering-variable, leaving-variable, and pivot-element information when supplied by the solver.

#### Current Simplex limitations

The solver is still under development. The basic tableau Simplex implementation expects problems that can begin with a feasible slack-variable basis after RHS normalization. Constraint forms requiring surplus or artificial variables—such as many `>=` and `=` cases—may be rejected and require the planned Big M or Two-Phase implementations.

Minimization through dual conversion works only when the generated dual can be solved by the currently supported solver path. It is not yet a general-purpose LP solver for every combination of constraint directions, RHS values, and variable sign restrictions.

Multiple-optimum detection is not yet fully implemented. The solver may report one optimal solution without identifying other optimal solutions. Infeasibility detection for cases requiring artificial variables is also limited. Validate results against the original constraints, especially for unsupported problem forms.

Tableau history is available only when the solver returns `tableau_history` in the format expected by the tableau viewer. The viewer presents snapshots; it does not calculate Simplex pivots itself.

### Additional Method Pages

The sidebar provides navigation for additional methods:

- **Big M Method** — planned / in development.
- **Transportation Problems** — planned / placeholder.

These pages provide a structure for adding more OR techniques later.

## Technology Stack

- **Python** — application and optimization logic.
- **Tkinter / ttk** — desktop user interface.
- **Matplotlib** — graphical plotting and feasible-region visualization.
- **NumPy** — numerical computations.
- **JSON** — local persistence of graphical-method inputs.

## Project Structure

The project is modularized into UI pages and solver modules. The exact file layout may change as development continues.

```text
OR_PYTHON_APP/
├── main.py
├── ui/
│   ├── app.py
│   ├── sidebar.py
│   ├── graphical_page.py
│   ├── simplex_page.py
│   ├── simplex_tableau.py
│   ├── big_m_page.py
│   ├── transportation_page.py
│   └── placeholder_page.py
├── solvers/
│   ├── __init__.py
│   ├── graphical_solver.py
│   └── simplex_solver.py
├── services/
│   └── settings.py
├── requirements.txt
├── .gitignore
└── README.md
```

This is a representative structure. Use the files and entry point present in your current checkout; do not move solver modules without updating imports.

## Installation and Setup

### Requirements

- Windows
- Python 3.12 or another version compatible with the project's dependencies
- Git (optional, for cloning and version control)

### 1. Clone the repository

```powershell
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

If PowerShell blocks activation, you can run the environment's Python executable directly.

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Run the application

For the modular application, run:

```powershell
python main.py
```

Use the entry point that exists in your checkout and matches the imports in your UI modules.

## Simplex Tableau History

The tableau viewer is a UI component. It displays snapshots supplied by the solver and does not calculate pivots itself.

Each history item should follow this general structure:

```python
{
    "title": "Initial tableau",
    "columns": ["Basis", "x1", "x2", "s1", "RHS"],
    "rows": [
        ["s1", 1, 2, 1, 10],
        ["Z", -3, -5, 0, 0],
    ],
    "note": "Optional explanation",
    "entering": "x2",
    "leaving": "s1",
    "pivot": 2,
}
```

The solver should return snapshots in a `tableau_history` list. The UI can then pass that list to `SimplexTableauPage.display_iterations(...)`. The precise integration depends on the current solver and UI implementation.

## Building a Windows Application

The project can be packaged as a Windows executable using PyInstaller.

Install PyInstaller if needed:

```powershell
python -m pip install pyinstaller
```

If the repository contains a `.spec` file, review its entry point, imported modules, assets, and data-file paths before building. For example:

```powershell
python -m PyInstaller "OR Graphical Method Solver.spec"
```

The output is normally placed in `dist/`. The exact output structure depends on the PyInstaller configuration.

## Roadmap

- [x] Graphical Method for two-variable LPPs
- [x] Sidebar navigation between method pages
- [x] Basic tableau-based Simplex solver
- [x] Simplex tableau viewer component
- [x] Maximization support for currently supported Simplex problem forms
- [x] Initial minimization workflow using dual conversion and primal recovery for supported cases
- [ ] Improve and verify end-to-end tableau history for all supported solver paths
- [ ] Detect and report multiple optimal solutions
- [ ] Add robust infeasibility detection for problems requiring artificial variables
- [ ] Implement the Big M Method
- [ ] Implement the Two-Phase Method
- [ ] Implement Transportation Problems
- [ ] Implement Assignment Problems
- [ ] Add automated tests for solver edge cases and UI integration
- [ ] Add further Operations Research techniques

## Project Goals

- Make Operations Research methods easier to explore and understand.
- Combine numerical calculations with graphical explanations.
- Keep optimization algorithms modular and maintainable.
- Expand the application gradually while preserving existing behavior.
- Provide a convenient desktop tool for students and anyone learning optimization.

## Development Status

**Early development.** The application includes a Graphical Method page and a basic tableau-based Simplex page. The Simplex page supports maximization for a restricted set of LP forms and has an initial minimization workflow based on dual conversion and primal recovery. These features are not yet a substitute for a fully general LP solver.

Big M and Transportation pages are planned or placeholders. Full support for artificial variables, robust infeasibility handling, multiple-optimum detection, broader minimization cases, and automated regression testing remains future work.

## License

No license has been selected yet. A license will be added when the project's distribution and reuse terms are decided.

## About

Optimization Techniques is a Python-based Operations Research toolkit for learning and experimenting with linear programming and other optimization methods through an interactive desktop application.
