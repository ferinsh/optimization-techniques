"""Main application controller and sidebar/page navigation."""
import json
import os
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from ui.graphical_page import GraphicalPageMixin
from ui.simplex_page import SimplexPageMixin
from ui.placeholder_page import PlaceholderPageMixin

APP_NAME = "Optimization Techniques"
APP_VERSION = "0.1.0"


class LPPApp(GraphicalPageMixin, SimplexPageMixin, PlaceholderPageMixin):
    def __init__(self, root):
        self.root = root
        self.root.title(f'{APP_NAME} v{APP_VERSION}')
        self.root.geometry('1250x800')
        self.root.minsize(1000, 650)
        self.constraint_rows = []
        self.current_page = 'graph'
        app_data = os.getenv('LOCALAPPDATA') or os.path.expanduser('~')
        self.save_path = os.path.join(app_data, 'OR Graphical Method Solver', 'lpp_settings.json')
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        self.build_ui()
        if not self.load_state():
            self.load_example()
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)
        self.schedule_autosave()

    def save_state(self):
        state = {'sense': self.sense.get(), 'c1': self.c1.get(), 'c2': self.c2.get(), 'constraints': [{'a': row['a'].get(), 'b': row['b'].get(), 'op': row['op'].get(), 'rhs': row['rhs'].get()} for row in self.constraint_rows]}
        temp_path = self.save_path + '.tmp'
        try:
            with open(temp_path, 'w', encoding='utf-8') as file:
                json.dump(state, file, indent=4)
            os.replace(temp_path, self.save_path)
        except (OSError, TypeError, ValueError) as error:
            print(f'Could not save LPP inputs: {error}')

    def load_state(self):
        try:
            with open(self.save_path, 'r', encoding='utf-8') as file:
                state = json.load(file)
            if not isinstance(state, dict):
                return False
            constraints = state.get('constraints')
            if not isinstance(constraints, list):
                return False
            if not all((isinstance(c, dict) and all((k in c for k in ('a', 'b', 'op', 'rhs'))) and (c['op'] in ('<=', '>=', '=')) for c in constraints)):
                return False
            if state.get('sense') not in ('Maximize', 'Minimize'):
                return False
            self.c1.delete(0, 'end')
            self.c1.insert(0, str(state.get('c1', '')))
            self.c2.delete(0, 'end')
            self.c2.insert(0, str(state.get('c2', '')))
            self.sense.set(state['sense'])
            for row in self.constraint_rows:
                for key in ('a', 'b', 'op', 'rhs', 'remove_button'):
                    row[key].destroy()
            self.constraint_rows.clear()
            for constraint in constraints:
                self.add_constraint(a=str(constraint['a']), b=str(constraint['b']), op=constraint['op'], rhs=str(constraint['rhs']))
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
        from ui.sidebar import Sidebar

        app_container = ttk.Frame(self.root)
        app_container.pack(fill="both", expand=True)
        app_container.rowconfigure(0, weight=1)
        app_container.columnconfigure(1, weight=1)

        self.sidebar = Sidebar(
            app_container,
            on_navigate=self.show_page,
            version=APP_VERSION,
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")

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
        pages = {'graph': self.graph_page, 'simplex': self.simplex_page, 'big_m': self.big_m_page, 'transportation': self.transportation_page}
        page = pages.get(page_name)
        if page is None:
            return
        for current_page in pages.values():
            current_page.grid_remove()
        page.grid()
        self.current_page = page_name
        titles = {'graph': 'Optimization Techniques - Graphical Method', 'simplex': 'Optimization Techniques - Simplex Method', 'big_m': 'Optimization Techniques - Big M Method', 'transportation': 'Optimization Techniques - Transportation'}
        self.root.title(titles[page_name])
