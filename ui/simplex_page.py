"""Simplex-method UI. Existing SIMPLEX_METHOD/solver.py is loaded explicitly."""
import importlib.util
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

# PROJECT_DIR = Path(__file__).resolve().parents[1]
# SIMPLEX_SOLVER_PATH = PROJECT_DIR / "SIMPLEX_METHOD" / "solver.py"
# if SIMPLEX_SOLVER_PATH.exists():
#     _spec = importlib.util.spec_from_file_location("simplex_method_solver", SIMPLEX_SOLVER_PATH)
#     _module = importlib.util.module_from_spec(_spec)
#     _spec.loader.exec_module(_module)
#     max_simplex = _module.max_simplex
# else:
#     max_simplex = None

from solvers.simplex_solver import max_simplex

from ui.simplex_tableau import SimplexTableauPage


class SimplexPageMixin:

    def build_simplex_page(self):
        """Build a working Simplex UI connected to SIMPLEX_METHOD/solver.py."""
        app_container = ttk.Frame(self.root)
        app_container.pack(fill="both", expand=True)
        app_container.rowconfigure(0, weight=1)
        app_container.columnconfigure(1, weight=1)

        self.page_container = ttk.Frame(app_container, padding=0)
        self.page_container.grid(row=0, column=1, sticky="nsew")
        self.page_container.rowconfigure(0, weight=1)
        self.page_container.columnconfigure(0, weight=1)
    
        # Container for the tableau viewer
        self.tableau_iterations = ttk.Frame(self.page_container)
        self.tableau_iterations.grid(
            row=0, column=0, sticky="nsew"
        )
        self.tableau_iterations.grid_remove()

        # Tableau viewer
        self.tableau_page = SimplexTableauPage(
            self.tableau_iterations
        )
        self.tableau_page.pack(fill="both", expand=True)

        # Return to the Simplex input page
        ttk.Button(
            self.tableau_iterations,
            text="Back to Simplex",
            command=self.show_simplex_inputs,
        ).pack(anchor="w", padx=16, pady=(0, 12))
        
        page = self.simplex_page
        page.columnconfigure(0, weight=1)
        page.rowconfigure(1, weight=1)
        header = ttk.Frame(page, padding=(20, 16, 20, 8))
        header.grid(row=0, column=0, sticky='ew')
        ttk.Label(header, text='Simplex Method', font=('Arial', 18, 'bold')).pack(anchor='w')
        ttk.Label(header, text='Maximize a linear objective using the tableau-based Simplex method.').pack(anchor='w', pady=(4, 0))
        content = ttk.Frame(page, padding=(20, 8, 20, 20))
        content.grid(row=1, column=0, sticky='nsew')
        content.columnconfigure(0, weight=1)
        content.rowconfigure(3, weight=1)
        self.simplex_inputs_view = content

        self.tableau_view = ttk.Frame(page)
        self.tableau_view.grid(row=1, column=0, sticky="nsew")
        self.tableau_view.grid_remove()

        self.tableau_page = SimplexTableauPage(self.tableau_view)
        self.tableau_page.pack(fill="both", expand=True, padx=20, pady=10)

        ttk.Button(
            self.tableau_view,
            text="Back to Simplex",
            command=self.show_simplex_inputs,
        ).pack(anchor="w", padx=16, pady=10)
        settings = ttk.LabelFrame(content, text='Problem setup', padding=10)
        settings.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        ttk.Label(settings, text='Number of variables').grid(row=0, column=0, sticky='w')
        self.simplex_var_count = tk.IntVar(value=2)
        self.simplex_var_spin = ttk.Spinbox(settings, from_=1, to=10, width=5, textvariable=self.simplex_var_count, command=self.rebuild_simplex_inputs)
        self.simplex_var_spin.grid(row=0, column=1, padx=(8, 16), sticky='w')
        self.simplex_var_spin.bind('<Return>', lambda _event: self.rebuild_simplex_inputs())
        self.simplex_var_spin.bind('<FocusOut>', lambda _event: self.rebuild_simplex_inputs())
        ttk.Label(settings, text='Goal').grid(row=0, column=2, sticky='w')
        ttk.Label(settings, text='Maximize', font=('Arial', 9, 'bold')).grid(row=0, column=3, padx=(8, 0), sticky='w')
        objective_box = ttk.LabelFrame(content, text='Objective function: Maximize Z', padding=10)
        objective_box.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        self.simplex_objective_box = objective_box
        self.simplex_objective_entries = []
        self.simplex_objective_labels = []
        constraints_box = ttk.LabelFrame(content, text='Constraints (decision variables are non-negative)', padding=10)
        constraints_box.grid(row=2, column=0, sticky='ew', pady=(0, 10))
        self.simplex_constraints_box = constraints_box
        self.simplex_constraint_header = ttk.Frame(constraints_box)
        self.simplex_constraint_header.grid(row=0, column=0, sticky='w')
        self.simplex_rows_frame = ttk.Frame(constraints_box)
        self.simplex_rows_frame.grid(row=1, column=0, sticky='w')
        controls = ttk.Frame(constraints_box)
        controls.grid(row=2, column=0, sticky='w', pady=(8, 0))
        ttk.Button(controls, text='+ Add constraint', command=self.add_simplex_constraint).pack(side='left', padx=(0, 8))
        ttk.Button(controls, text='Load example', command=self.load_simplex_example).pack(side='left', padx=(0, 8))
        ttk.Button(controls, text='Solve', command=self.solve_simplex).pack(side='left')
        ttk.Button(
            controls,
            text="Show Iterations",
            command=self.show_tableau_iterations,
        ).pack(side="left", padx=(8, 0))
        results_box = ttk.LabelFrame(content, text='Simplex result', padding=8)
        results_box.grid(row=3, column=0, sticky='nsew')
        results_box.rowconfigure(0, weight=1)
        results_box.columnconfigure(0, weight=1)
        self.simplex_report = tk.Text(results_box, height=10, wrap='word', font=('Consolas', 10))
        self.simplex_report.grid(row=0, column=0, sticky='nsew')
        simplex_scroll = ttk.Scrollbar(results_box, orient='vertical', command=self.simplex_report.yview)
        simplex_scroll.grid(row=0, column=1, sticky='ns')
        self.simplex_report.configure(yscrollcommand=simplex_scroll.set)
        self.simplex_constraint_rows = []
        self.rebuild_simplex_inputs()
        self.load_simplex_example()

    def show_tableau_iterations(self):
        self.simplex_inputs_view.grid_remove()
        self.tableau_view.grid()

    def show_simplex_inputs(self):
        self.tableau_view.grid_remove()
        self.simplex_inputs_view.grid()

    def rebuild_simplex_inputs(self):
        """Rebuild objective and constraint coefficient widgets for n variables."""
        if not hasattr(self, 'simplex_objective_box'):
            return
        try:
            num_variables = int(self.simplex_var_count.get())
        except (ValueError, tk.TclError):
            return
        if not 1 <= num_variables <= 10:
            return
        old_objective = [entry.get() for entry in getattr(self, 'simplex_objective_entries', [])]
        old_constraints = []
        for row in getattr(self, 'simplex_constraint_rows', []):
            old_constraints.append({'coefficients': [entry.get() for entry in row['coefficients']], 'op': row['op'].get(), 'rhs': row['rhs'].get()})
        for widget in self.simplex_objective_box.winfo_children():
            widget.destroy()
        self.simplex_objective_entries = []
        self.simplex_objective_labels = []
        for j in range(num_variables):
            ttk.Label(self.simplex_objective_box, text=f'x{j + 1}').grid(row=0, column=2 * j, padx=(2, 4), pady=2)
            entry = ttk.Entry(self.simplex_objective_box, width=8)
            entry.grid(row=0, column=2 * j + 1, padx=(0, 8), pady=2)
            value = old_objective[j] if j < len(old_objective) else '3' if j == 0 else '5' if j == 1 else '0'
            entry.insert(0, value)
            self.simplex_objective_entries.append(entry)
        for widget in self.simplex_constraint_header.winfo_children():
            widget.destroy()
        for col in range(num_variables):
            ttk.Label(self.simplex_constraint_header, text=f'x{col + 1}').grid(row=0, column=col, padx=3, pady=2)
        ttk.Label(self.simplex_constraint_header, text='Relation').grid(row=0, column=num_variables, padx=3, pady=2)
        ttk.Label(self.simplex_constraint_header, text='RHS').grid(row=0, column=num_variables + 1, padx=3, pady=2)
        ttk.Label(self.simplex_constraint_header, text='').grid(row=0, column=num_variables + 2, padx=3, pady=2)
        for row in getattr(self, 'simplex_constraint_rows', []):
            for widget in row['widgets']:
                widget.destroy()
        self.simplex_constraint_rows = []
        if old_constraints:
            for constraint in old_constraints:
                coefficients = constraint['coefficients'][:num_variables]
                coefficients += ['0'] * (num_variables - len(coefficients))
                self.add_simplex_constraint(coefficients=coefficients, op=constraint['op'], rhs=constraint['rhs'])
        else:
            self.add_simplex_constraint(coefficients=['1'] + ['0'] * (num_variables - 1), op='<=', rhs='4')
            self.add_simplex_constraint(coefficients=['0', '2'][:num_variables] + ['0'] * max(0, num_variables - 2), op='<=', rhs='12')
            self.add_simplex_constraint(coefficients=['3', '2'][:num_variables] + ['0'] * max(0, num_variables - 2), op='<=', rhs='18')

    def add_simplex_constraint(self, coefficients=None, op='<=', rhs='10'):
        num_variables = len(self.simplex_objective_entries)
        if coefficients is None:
            coefficients = ['0'] * num_variables
            if coefficients:
                coefficients[0] = '1'
        else:
            coefficients = list(coefficients)
            coefficients = coefficients[:num_variables]
            coefficients += ['0'] * (num_variables - len(coefficients))
        row_index = len(self.simplex_constraint_rows)
        widgets = []
        coefficient_entries = []
        for j in range(num_variables):
            entry = ttk.Entry(self.simplex_rows_frame, width=8)
            entry.grid(row=row_index, column=j, padx=3, pady=2)
            entry.insert(0, str(coefficients[j]))
            coefficient_entries.append(entry)
            widgets.append(entry)
        relation = ttk.Combobox(self.simplex_rows_frame, values=['<=', '>=', '='], state='readonly', width=5)
        relation.grid(row=row_index, column=num_variables, padx=3, pady=2)
        relation.set(op)
        widgets.append(relation)
        rhs_entry = ttk.Entry(self.simplex_rows_frame, width=8)
        rhs_entry.grid(row=row_index, column=num_variables + 1, padx=3, pady=2)
        rhs_entry.insert(0, str(rhs))
        widgets.append(rhs_entry)
        row_data = {'coefficients': coefficient_entries, 'op': relation, 'rhs': rhs_entry, 'widgets': widgets}
        remove_button = ttk.Button(self.simplex_rows_frame, text='X', width=3, command=lambda item=row_data: self.remove_simplex_constraint(item))
        remove_button.grid(row=row_index, column=num_variables + 2, padx=3, pady=2)
        widgets.append(remove_button)
        row_data['remove_button'] = remove_button
        self.simplex_constraint_rows.append(row_data)

    def remove_simplex_constraint(self, item):
        if item not in self.simplex_constraint_rows:
            return
        for widget in item['widgets']:
            widget.destroy()
        self.simplex_constraint_rows.remove(item)
        for row_index, row in enumerate(self.simplex_constraint_rows):
            for col, widget in enumerate(row['widgets']):
                widget.grid(row=row_index, column=col, padx=3, pady=2)

    def load_simplex_example(self):
        self.simplex_var_count.set(2)
        self.rebuild_simplex_inputs()
        for entry, value in zip(self.simplex_objective_entries, ('3', '5')):
            entry.delete(0, 'end')
            entry.insert(0, value)
        for row in list(self.simplex_constraint_rows):
            for widget in row['widgets']:
                widget.destroy()
        self.simplex_constraint_rows.clear()
        self.add_simplex_constraint(['1', '0'], '<=', '4')
        self.add_simplex_constraint(['0', '2'], '<=', '12')
        self.add_simplex_constraint(['3', '2'], '<=', '18')
        self.simplex_report.delete('1.0', 'end')
        self.simplex_report.insert('end', 'Example loaded:\nMaximize Z = 3x1 + 5x2\nx1 <= 4\n2x2 <= 12\n3x1 + 2x2 <= 18\n')

    def solve_simplex(self):
        if max_simplex is None:
            messagebox.showerror('Simplex solver not found', 'Could not load SIMPLEX_METHOD/solver.py.\nCheck that the file exists in that folder.')
            return
        try:
            objective = [float(entry.get()) for entry in self.simplex_objective_entries]
            if not objective or not all((np.isfinite(value) for value in objective)):
                raise ValueError('Objective coefficients must be finite numbers.')
            if not self.simplex_constraint_rows:
                raise ValueError('Add at least one constraint.')
            constraints = []
            for index, row in enumerate(self.simplex_constraint_rows, start=1):
                try:
                    coefficients = [float(entry.get()) for entry in row['coefficients']]
                    rhs = float(row['rhs'].get())
                except ValueError as error:
                    raise ValueError(f'Constraint {index}: enter numeric coefficients and RHS.') from error
                if not all((np.isfinite(value) for value in coefficients + [rhs])):
                    raise ValueError(f'Constraint {index}: values must be finite.')
                constraint = {f'var{j + 1}': value for j, value in enumerate(coefficients)}
                constraint['op'] = row['op'].get()
                constraint['rhs'] = rhs
                constraints.append(constraint)
            self.simplex_report.delete('1.0', 'end')
            self.simplex_report.insert('end', 'Solving...\n')
            self.root.update_idletasks()
            result = max_simplex(objective, constraints)
            self.tableau_page.display_iterations(
                result.get("tableau_history", []),
                objective_value=result.get("optimum"),
                status=result.get("status"),
            )
            self.simplex_report.delete('1.0', 'end')
            self.simplex_report.insert('end', f"Status: {result['status'].upper()}\n")
            self.simplex_report.insert('end', f"Iterations: {result.get('iterations', '-')}\n")
            if result['status'] == 'optimal':
                self.simplex_report.insert('end', '\nOptimal solution:\n')
                for index, value in enumerate(result['solution'], start=1):
                    self.simplex_report.insert('end', f'x{index} = {value:.8g}\n')
                self.simplex_report.insert('end', f"\nMaximum Z = {result['optimum']:.8g}\n")
            elif result['status'] == 'unbounded':
                self.simplex_report.insert('end', '\nThe objective is unbounded. No finite maximum exists.\n')
            elif result['status'] == 'iteration_limit':
                self.simplex_report.insert('end', '\nStopped after reaching the iteration limit.\n')
            else:
                self.simplex_report.insert('end', '\nThe problem could not be solved by the current basic Simplex implementation.\n')
        except (ValueError, TypeError, OverflowError, ArithmeticError) as error:
            messagebox.showerror('Simplex input/calculation error', str(error))
