"""Placeholder pages for optimization methods that will be implemented later."""
import tkinter as tk
from tkinter import ttk


class PlaceholderPageMixin:
    def build_placeholder_page(self, page, title, description):
        container = ttk.Frame(page, padding=25)
        container.pack(fill='both', expand=True)
        ttk.Label(container, text=title, font=('Arial', 18, 'bold')).pack(anchor='w', pady=(0, 10))
        ttk.Label(container, text=description, wraplength=700).pack(anchor='w', pady=(0, 20))
        ttk.Label(container, text='Status: Planned', foreground='gray').pack(anchor='w')
