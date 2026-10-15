# Optimization Techniques

A Python-based desktop application for exploring Operations Research (OR) methods, starting with Linear Programming Problems (LPPs). The application combines optimization calculations with an interactive graphical interface and is being expanded to include additional techniques.

## Features

### Graphical Method for Linear Programming

- Enter objective-function coefficients for a two-variable LPP.
- Choose maximization or minimization.
- Add and remove constraints using `<=`, `>=`, or `=`.
- Visualize constraint lines and the feasible region.
- Identify and label feasible corner points.
- Evaluate the objective function at candidate solutions.
- Display optimal point(s) and the optimal objective value for supported problems.
- Report infeasible and unbounded problem statuses.
- Save graphical-method inputs locally and restore them on restart.
- Autosave inputs every 30 seconds and when the application closes.

### Simplex Method

- Enter objective-function coefficients for multiple decision variables.
- Add and remove constraints in the interface.
- Select constraint relations (`<=`, `>=`, or `=`).
- Run the tableau-based Simplex solver for supported maximization problems.
- Display the solution status, iteration count, decision-variable values, and maximum objective value.
- Load a built-in example problem.
- Capture the initial tableau and subsequent tableaux after each pivot.
- Browse saved tableau snapshots using Previous and Next navigation.
- View entering-variable, leaving-variable, and pivot-element details when supplied by the solver.

**Current Simplex limitations:** The solver currently supports problems that can start with a feasible slack-variable basis after right-hand-side normalization. Although the interface offers `>=` and `=` relations, constraints requiring surplus or artificial variables are not yet supported by this implementation. The Simplex interface currently supports maximization only. Tableau history is available when the solver returns `tableau_history` in the format expected by the tableau viewer.

### Additional Method Pages

The sidebar provides pages for additional methods, currently planned or represented by placeholders:

- **Big M Method** — planned.
- **Transportation Problems** — planned.

These pages provide a navigation structure for future OR methods.

## Technology Stack

- **Python** — application and optimization logic.
- **Tkinter / ttk** — desktop user interface.
- **Matplotlib** — graphical plotting and feasible-region visualization.
- **NumPy** — numerical computations.
- **JSON** — persistence of graphical-method inputs.

## Project Structure

The project is modularized into UI pages and solver modules. The exact file layout may differ as development continues. The following is a representative structure:

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

Your actual project may still contain legacy folders such as `OR_GRAPHICAL_SOLVER/` and `SIMPLEX_METHOD/`. If those files are still the active solver locations, keep them and use the entry point and imports configured in your current checkout. Do not move or delete solver files without updating imports.

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

If PowerShell blocks activation, you can run Python directly from the environment instead.

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Run the application

Run the entry point used by your current project layout. For the modular application, this may be:

```powershell
python main.py
```

If your checkout still uses the earlier sidebar launcher, run:

```powershell
python main_with_simplex_ui.py
```

Use the entry point that exists in your checkout and matches the imports in your UI modules.

## Simplex Tableau History

The tableau viewer is a UI component; it displays snapshots supplied by the solver and does not calculate pivots itself.

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

The solver should return the snapshots in a `tableau_history` list. The UI can then pass that list to `SimplexTableauPage.display_iterations(...)`. The exact integration depends on the solver and UI version in use.

## Building a Windows Application

The project can be packaged as a Windows executable using PyInstaller.

Install PyInstaller if required:

```powershell
python -m pip install pyinstaller
```

If the repository contains a `.spec` file, review its entry point, imported modules, assets, and data-file paths before building:

```powershell
python -m PyInstaller "OR Graphical Method Solver.spec"
```

The output is normally placed in `dist/`. The exact output structure depends on the PyInstaller configuration.

## Roadmap

- [x] Graphical Method for two-variable LPPs
- [x] Sidebar navigation between method pages
- [x] Simplex UI connected to a basic tableau solver
- [x] Add a tableau viewer component for displaying saved iterations
- [ ] Finish and verify end-to-end capture and display of actual Simplex tableau history
- [ ] Add minimization support to the Simplex solver
- [ ] Support artificial variables through the Big M Method
- [ ] Implement the Two-Phase Method
- [ ] Implement Transportation Problems
- [ ] Implement Assignment Problems
- [ ] Add automated tests for solver edge cases and UI integration
- [ ] Add further Operations Research techniques

## Project Goals

- Make Operations Research methods easier to explore and understand.
- Combine numerical calculations with graphical explanations.
- Keep optimization algorithms modular and maintainable.
- Expand the application gradually while preserving existing solver behavior.
- Provide a convenient desktop tool for students and anyone learning optimization.

## Development Status

**Early development.** The application includes a Graphical Method page and a basic Simplex page. A reusable tableau viewer has been added for displaying iteration snapshots; full integration depends on the solver returning the expected history data. Big M and Transportation pages are planned or placeholders. Constraint support, minimization, validation, and automated testing remain areas for future development.

## License

No license has been selected yet. A license will be added when the project's distribution and reuse terms are decided.
