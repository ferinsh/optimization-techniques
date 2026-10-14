# Optimization Techniques

A Python-based desktop application for solving Operations Research problems, starting with the **Graphical Method for Linear Programming (LPP)**.

The application provides an interactive interface for entering an objective function and constraints, visualizing the feasible region, identifying corner points, and determining the optimal solution.

The long-term goal is to bring multiple Operations Research and optimization techniques together in one desktop application.

## Features

### Graphical Method for Linear Programming

- Enter objective function coefficients.
- Choose between maximization and minimization.
- Add linear constraints with different inequality operators.
- Visualize constraint lines and the feasible region.
- Identify and label corner points of the feasible region.
- Calculate the objective function value at candidate solutions.
- Identify optimal solutions for supported problems.
- Detect unbounded problems.
- Save input settings automatically and restore them when reopening the application.

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
│   ├── __pycache__/
│   ├── lpp_settings.json
│   ├── main.py
│   └── solver.py
│
├── app.py
├── requirements.txt
├── .gitignore
├── OR Graphical Method Solver.spec
│
├── .venv/       # Local Python virtual environment
├── build/       # PyInstaller build files
└── dist/        # Generated application build
```

### Important Files

| File | Purpose |
|---|---|
| `app.py` | Application entry point or main application launcher, depending on the current setup. |
| `OR_GRAPHICAL_SOLVER/main.py` | Graphical solver interface and application logic. |
| `OR_GRAPHICAL_SOLVER/solver.py` | Linear programming calculations and optimization logic. |
| `OR_GRAPHICAL_SOLVER/lpp_settings.json` | Stores saved application inputs and settings. |
| `requirements.txt` | Python dependencies required to run the application. |
| `OR Graphical Method Solver.spec` | PyInstaller configuration for packaging the desktop application. |
| `.gitignore` | Specifies files and folders that Git should ignore. |

*The descriptions above reflect the visible folder and filenames; update them if responsibilities change as the codebase develops.*

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

If `app.py` is the configured entry point:

```powershell
python app.py
```

Alternatively, if `OR_GRAPHICAL_SOLVER/main.py` is the intended entry point, run:

```powershell
python OR_GRAPHICAL_SOLVER/main.py
```

Use the entry point that matches the current application setup.

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

The following methods are planned for future development:

- [x] Graphical Method for two-variable LPP
- [ ] Simplex Method
- [ ] Big M Method
- [ ] Two-Phase Method
- [ ] Transportation Problems
- [ ] Assignment Problems
- [ ] Additional Operations Research techniques

## Project Goals

- Make Operations Research methods easier to explore and understand.
- Combine numerical calculations with graphical explanations.
- Keep each optimization algorithm modular and maintainable.
- Expand the application gradually without compromising the existing solvers.
- Provide a convenient desktop tool for students and anyone learning optimization.

## Development Status

**Early development.** The Graphical Method is the initial focus, with additional algorithms planned.

## License

No license has been selected yet. A license will be added when the project's distribution and reuse terms are decided.