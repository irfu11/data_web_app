"""
app.py — Root application window.
Builds the header, notebook tabs, and status bar.
Wires together all tab modules.

Tabs:
    1. Overview      — stat cards, data preview, dtype info
    2. Data Cleaning — missing values, duplicates, outliers
    3. Visualize     — 9 chart types
    4. Correlation   — heatmap + top pairs
    5. Insights + AI — stats report + Ollama AI chat (free, local, private)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import os

from utils.theme import (
    BG, PANEL, CARD, ACCENT, ACCENT2, ACCENT3,
    SUBTEXT, BORDER, ERROR, SUCCESS, TEXT
)
from utils.widgets import make_button, style_treeview
from tabs.overview     import OverviewTab
from tabs.cleaning     import CleaningTab
from tabs.visualize    import VisualizeTab
from tabs.coorelation  import CorrelationTab
from tabs.insights     import InsightsTab
from tabs.gamma_export import GammaExportTab


class DataLensApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DataLens — Analytics Dashboard with GROQ AI")
        self.geometry("1400x860")
        self.configure(bg=BG)
        self.resizable(True, True)

        # ── shared data state ──────────────────────────────────────
        self.df_raw           = None   # original uploaded dataframe
        self.df               = None   # working (cleaned) copy
        self.file_path        = tk.StringVar(value="No file loaded")
        self._loaded_filename = ""     # bare name without extension

        self._build_style()
        self._build_header()
        self._build_tabs()
        self._build_status_bar()

    # ══════════════════════════════════════════════════════════════
    #  TTK STYLE
    # ══════════════════════════════════════════════════════════════
    def _build_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure("TNotebook",
                    background=BG, borderwidth=0, tabmargins=[0, 0, 0, 0])
        s.configure("TNotebook.Tab",
                    background=PANEL, foreground=SUBTEXT,
                    padding=[20, 10],
                    font=("Courier New", 10, "bold"), borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", ACCENT)],
              foreground=[("selected", TEXT)])

        s.configure("TScrollbar",
                    background=PANEL, troughcolor=BG, arrowcolor=SUBTEXT)
        s.configure("Vertical.TScrollbar",
                    background=PANEL, troughcolor=BG, arrowcolor=SUBTEXT)
        s.configure("TCombobox",
                    fieldbackground=CARD, background=CARD,
                    foreground=TEXT, selectbackground=ACCENT,
                    bordercolor=BORDER)

        style_treeview(s)

    # ══════════════════════════════════════════════════════════════
    #  HEADER
    # ══════════════════════════════════════════════════════════════
    def _build_header(self):
        hdr = tk.Frame(self, bg=PANEL, height=64)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        # logo
        tk.Label(
            hdr, text="◈ DataLens",
            font=("Courier New", 18, "bold"),
            bg=PANEL, fg=ACCENT
        ).pack(side="left", padx=24, pady=14)

        # subtitle
        tk.Label(
            hdr, text="Analytics Dashboard  ·  GROQ AI ",
            font=("Courier New", 11),
            bg=PANEL, fg=SUBTEXT
        ).pack(side="left")

        # loaded file name (right side)
        tk.Label(
            hdr, textvariable=self.file_path,
            font=("Courier New", 9),
            bg=PANEL, fg=ACCENT3, anchor="e"
        ).pack(side="right", padx=20)

        # load button
        tk.Button(
            hdr, text="⬆  Load Dataset",
            font=("Courier New", 10), bg=ACCENT, fg=TEXT,
            relief="flat", cursor="hand2", padx=14, pady=6,
            activebackground=ACCENT2, activeforeground=TEXT,
            command=self._load_file
        ).pack(side="right", padx=(0, 12), pady=12)

    # ══════════════════════════════════════════════════════════════
    #  NOTEBOOK TABS
    # ══════════════════════════════════════════════════════════════
    def _build_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        tab_defs = [
            ("📂  Overview",      OverviewTab),
            ("🧹  Data Cleaning", CleaningTab),
            ("📊  Visualize",     VisualizeTab),
            ("🔗  Correlation",   CorrelationTab),
            ("💡  Insights + AI", InsightsTab),   # Ollama AI lives here
        ]

        self.tabs = {}
        for label, TabClass in tab_defs:
            frame = tk.Frame(self.notebook, bg=BG)
            self.notebook.add(frame, text=label)
            instance = TabClass(frame, self)
            instance.build()
            self.tabs[label] = instance

    # ══════════════════════════════════════════════════════════════
    #  STATUS BAR
    # ══════════════════════════════════════════════════════════════
    def _build_status_bar(self):
        self.status_var = tk.StringVar(
            value="Ready — load a CSV, Excel, JSON, or TSV file to begin.")

        bar = tk.Frame(self, bg=PANEL, height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        tk.Label(
            bar, textvariable=self.status_var,
            font=("Courier New", 9),
            bg=PANEL, fg=SUBTEXT, anchor="w"
        ).pack(side="left", padx=14)

    def set_status(self, msg: str):
        """Update the bottom status bar text from any tab."""
        self.status_var.set(msg)

    # ══════════════════════════════════════════════════════════════
    #  FILE LOADING
    # ══════════════════════════════════════════════════════════════
    def _load_file(self):
        path = filedialog.askopenfilename(
            title="Select Dataset",
            filetypes=[
                ("CSV files",   "*.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("JSON files",  "*.json"),
                ("TSV files",   "*.tsv"),
                ("All files",   "*.*"),
            ]
        )
        if not path:
            return

        try:
            ext = os.path.splitext(path)[1].lower()

            if ext == ".csv":
                self.df_raw = pd.read_csv(path)
            elif ext in (".xlsx", ".xls"):
                self.df_raw = pd.read_excel(path)
            elif ext == ".json":
                self.df_raw = pd.read_json(path)
            elif ext == ".tsv":
                self.df_raw = pd.read_csv(path, sep="\t")
            else:
                self.df_raw = pd.read_csv(path)

            self.df               = self.df_raw.copy()
            fname                 = os.path.basename(path)
            self._loaded_filename = os.path.splitext(fname)[0]

            self.file_path.set(f"📄 {fname}")
            self.set_status(
                f"Loaded: {fname}  |  "
                f"{self.df.shape[0]:,} rows × {self.df.shape[1]} cols"
            )
            self._refresh_all()

        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    # ══════════════════════════════════════════════════════════════
    #  REFRESH ALL TABS
    # ══════════════════════════════════════════════════════════════
    def _refresh_all(self):
        """Called after every file load — tells every tab to redraw."""
        for tab in self.tabs.values():
            tab.refresh()