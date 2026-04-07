"""
tabs/base.py — Abstract base class for every tab.

Each tab receives:
  - parent  : the tk.Frame that belongs to this tab in the notebook
  - app     : the root DataLensApp instance (access df, df_raw, set_status …)

Subclasses must implement:
  - build()   → create all widgets inside self.parent
  - refresh() → called whenever a new dataset is loaded
"""

import tkinter as tk


class BaseTab:
    def __init__(self, parent: tk.Frame, app):
        self.parent = parent
        self.app    = app

    # ── shortcuts ──────────────────────────────────────────────────
    @property
    def df(self):
        return self.app.df

    @df.setter
    def df(self, value):
        self.app.df = value

    @property
    def df_raw(self):
        return self.app.df_raw

    def set_status(self, msg: str):
        self.app.set_status(msg)

    # ── to be overridden ──────────────────────────────────────────
    def build(self):
        raise NotImplementedError

    def refresh(self):
        raise NotImplementedError