"""Main application controller and sidebar/page navigation."""
import os
import tkinter as tk
from tkinter import ttk

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

    def schedule_autosave(self):
        self.root.after(30000, self.autosave)

    def autosave(self):
        self.save_state()
        if hasattr(self, "save_simplex_state"):
            self.save_simplex_state()
        self.schedule_autosave()

    def on_close(self):
        self.save_state()
        if hasattr(self, "save_simplex_state"):
            self.save_simplex_state()
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
