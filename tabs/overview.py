"""
tabs/overview.py — Tab 1: Dataset Overview.

Shows:
  • Stat cards  (rows, cols, numeric, categorical, missing, duplicates)
  • Scrollable data preview table (first 500 rows)
  • Column dtype / null / unique summary
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import numpy as np

from tabs.base import BaseTab
from utils.theme import (
    BG, PANEL, CARD, ACCENT, ACCENT2, ACCENT3,
    TEXT, SUBTEXT, ERROR, SUCCESS, WARNING, FONT_BIG, FONT_SMALL, FONT_MONO
)


class OverviewTab(BaseTab):

    def build(self):
        # ── stat cards row ─────────────────────────────────────────
        self.cards_frame = tk.Frame(self.parent, bg=BG)
        self.cards_frame.pack(fill="x", padx=20, pady=(20, 8))

        # ── section label ─────────────────────────────────────────
        lbl_row = tk.Frame(self.parent, bg=BG)
        lbl_row.pack(fill="x", padx=20, pady=(8, 4))
        tk.Label(lbl_row, text="Data Preview  (first 500 rows)",
                 font=("Courier New", 11, "bold"),
                 bg=BG, fg=ACCENT).pack(side="left")

        # ── data table ────────────────────────────────────────────
        tbl_outer = tk.Frame(self.parent, bg=BG)
        tbl_outer.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        vsb = ttk.Scrollbar(tbl_outer, orient="vertical")
        hsb = ttk.Scrollbar(tbl_outer, orient="horizontal")
        self.tree = ttk.Treeview(
            tbl_outer, show="headings",
            yscrollcommand=vsb.set, xscrollcommand=hsb.set
        )
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tbl_outer.grid_rowconfigure(0, weight=1)
        tbl_outer.grid_columnconfigure(0, weight=1)

        # ── dtype / null / unique info ───────────────────────────
        info_frame = tk.Frame(self.parent, bg=BG)
        info_frame.pack(fill="x", padx=20, pady=(0, 16))
        tk.Label(info_frame, text="Column Information",
                 font=("Courier New", 11, "bold"),
                 bg=BG, fg=ACCENT).pack(anchor="w")
        self.dtype_box = scrolledtext.ScrolledText(
            info_frame, height=6, font=FONT_MONO,
            bg=CARD, fg=TEXT, insertbackground=TEXT,
            relief="flat", borderwidth=0, wrap="none"
        )
        self.dtype_box.pack(fill="x", pady=(4, 0))

        # placeholder
        self._show_placeholder()

    # ─────────────────────────────────────────────────────────────
    def refresh(self):
        if self.df is None:
            return
        self._draw_cards()
        self._fill_table()
        self._fill_dtype_info()

    # ── internal ─────────────────────────────────────────────────
    def _show_placeholder(self):
        tk.Label(
            self.cards_frame,
            text="Load a dataset to see statistics here.",
            font=("Courier New", 10), bg=BG, fg=SUBTEXT
        ).pack(side="left", pady=10)

    def _draw_cards(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()

        df = self.df
        num_cols = df.select_dtypes(include=np.number).shape[1]
        cat_cols = df.select_dtypes(include="object").shape[1]
        missing  = int(df.isnull().sum().sum())
        dup      = int(df.duplicated().sum())

        cards = [
            ("Rows",         f"{df.shape[0]:,}",  ACCENT),
            ("Columns",      f"{df.shape[1]}",    ACCENT2),
            ("Numeric",      f"{num_cols}",        ACCENT3),
            ("Categorical",  f"{cat_cols}",        WARNING),
            ("Missing",      f"{missing:,}",       ERROR if missing else SUCCESS),
            ("Duplicates",   f"{dup:,}",           ERROR if dup    else SUCCESS),
        ]
        for title, val, color in cards:
            card = tk.Frame(self.cards_frame, bg=CARD, padx=20, pady=14)
            card.pack(side="left", fill="x", expand=True, padx=6)
            tk.Label(card, text=val,   font=FONT_BIG,   bg=CARD, fg=color).pack()
            tk.Label(card, text=title, font=FONT_SMALL, bg=CARD, fg=SUBTEXT).pack()

    def _fill_table(self):
        tree = self.tree
        tree.delete(*tree.get_children())

        cols = list(self.df.columns)
        tree["columns"] = cols
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=max(90, len(str(c)) * 9), anchor="w", minwidth=60)

        for _, row in self.df.head(500).iterrows():
            tree.insert("", "end", values=list(row))

    def _fill_dtype_info(self):
        self.dtype_box.configure(state="normal")
        self.dtype_box.delete("1.0", "end")
        header = (
            f"  {'Column':<30} {'dtype':<14} {'unique':<10} {'null %'}\n"
            f"  {'─'*30} {'─'*14} {'─'*10} {'─'*8}\n"
        )
        rows = []
        for col, dtype in self.df.dtypes.items():
            null_pct = self.df[col].isnull().mean() * 100
            unique   = self.df[col].nunique()
            rows.append(
                f"  {col:<30} {str(dtype):<14} {unique:<10} {null_pct:.1f}%"
            )
        self.dtype_box.insert("end", header + "\n".join(rows))
        self.dtype_box.configure(state="disabled")