"""
tabs/cleaning.py — Tab 2: Data Cleaning.

Left panel  : cleaning operation controls
Right panel : cleaning log + missing-value heatmap
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

from tabs.base import BaseTab
from utils.theme import (
    BG, CARD, PANEL, ACCENT, ACCENT2, ACCENT3,
    TEXT, SUBTEXT, BORDER, ERROR, SUCCESS, WARNING,
    FONT_HEAD, FONT_BODY, FONT_SMALL, FONT_MONO
)
from utils.widgets import make_button, make_section_card
from utils import cleaner


class CleaningTab(BaseTab):

    def build(self):
        # ── two-column layout ─────────────────────────────────────
        left = tk.Frame(self.parent, bg=BG, width=320)
        left.pack(side="left", fill="y", padx=(20, 8), pady=20)
        left.pack_propagate(False)

        right = tk.Frame(self.parent, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(8, 20), pady=20)

        self._build_controls(left)
        self._build_log_panel(right)

    # ── left panel ────────────────────────────────────────────────
    def _build_controls(self, parent):
        tk.Label(parent, text="🧹 Cleaning Operations",
                 font=FONT_HEAD, bg=BG, fg=ACCENT).pack(anchor="w", pady=(0, 10))

        # ── Missing values ────────────────────────────────────────
        mv = make_section_card(parent, "▸ Handle Missing Values")
        self.mv_strategy = tk.StringVar(value="drop_rows")
        options = [
            ("drop_rows",   "Drop rows with any NaN"),
            ("drop_cols",   "Drop cols > 50 % NaN"),
            ("fill_mean",   "Fill numeric → mean"),
            ("fill_median", "Fill numeric → median"),
            ("fill_mode",   "Fill all → mode"),
            ("fill_zero",   "Fill numeric → 0"),
        ]
        for val, label in options:
            tk.Radiobutton(mv, text=label, variable=self.mv_strategy,
                           value=val, font=FONT_SMALL,
                           bg=CARD, fg=TEXT, selectcolor=ACCENT,
                           activebackground=CARD).pack(anchor="w")
        make_button(mv, "Apply", self._on_missing,
                    color=ACCENT).pack(fill="x", pady=(8, 0))

        # ── Duplicates ────────────────────────────────────────────
        dp = make_section_card(parent, "▸ Remove Duplicates")
        make_button(dp, "Drop Duplicate Rows",
                    self._on_duplicates).pack(fill="x")

        # ── Dtypes ───────────────────────────────────────────────
        dt = make_section_card(parent, "▸ Auto-Infer Dtypes")
        make_button(dt, "Infer Better Dtypes",
                    self._on_dtypes).pack(fill="x")

        # ── Outliers ─────────────────────────────────────────────
        ot = make_section_card(parent, "▸ Outlier Removal  (IQR)")
        tk.Label(ot, text="Column:", font=FONT_SMALL,
                 bg=CARD, fg=SUBTEXT).pack(anchor="w")
        self.outlier_col_cb = ttk.Combobox(ot, font=FONT_SMALL, state="readonly")
        self.outlier_col_cb.pack(fill="x", pady=2)
        make_button(ot, "Remove IQR Outliers",
                    self._on_outliers).pack(fill="x", pady=(6, 0))

        # ── Reset ─────────────────────────────────────────────────
        make_button(parent, "↺  Reset to Original",
                    self._on_reset, color=ERROR).pack(fill="x", pady=14)

    # ── right panel ───────────────────────────────────────────────
    def _build_log_panel(self, parent):
        tk.Label(parent, text="Cleaning Log",
                 font=FONT_HEAD, bg=BG, fg=ACCENT).pack(anchor="w")

        self.log_box = scrolledtext.ScrolledText(
            parent, height=14, font=FONT_MONO,
            bg=CARD, fg=ACCENT3, insertbackground=TEXT,
            relief="flat", borderwidth=0
        )
        self.log_box.pack(fill="x", pady=(4, 14))
        self.log_box.insert("end", "Load a dataset to begin cleaning...\n")

        tk.Label(parent, text="Missing Values Heatmap  (first 100 rows)",
                 font=FONT_HEAD, bg=BG, fg=ACCENT).pack(anchor="w")
        self.heatmap_frame = tk.Frame(parent, bg=CARD)
        self.heatmap_frame.pack(fill="both", expand=True)

    # ── refresh ───────────────────────────────────────────────────
    def refresh(self):
        if self.df is None:
            return
        num_cols = list(self.df.select_dtypes(include=np.number).columns)
        self.outlier_col_cb["values"] = num_cols
        if num_cols:
            self.outlier_col_cb.set(num_cols[0])
        self._draw_heatmap()

    # ── event handlers ────────────────────────────────────────────
    def _on_missing(self):
        if self.df is None: return
        new_df, msg = cleaner.handle_missing(self.df, self.mv_strategy.get())
        self.df = new_df
        self._log(msg)
        self.set_status(f"Cleaned. Shape: {self.df.shape}")
        self._draw_heatmap()

    def _on_duplicates(self):
        if self.df is None: return
        new_df, msg = cleaner.remove_duplicates(self.df)
        self.df = new_df
        self._log(msg)
        self.set_status(f"Cleaned. Shape: {self.df.shape}")

    def _on_dtypes(self):
        if self.df is None: return
        new_df, msg = cleaner.infer_dtypes(self.df)
        self.df = new_df
        self._log(msg)

    def _on_outliers(self):
        if self.df is None: return
        col = self.outlier_col_cb.get()
        if not col: return
        new_df, msg = cleaner.remove_outliers_iqr(self.df, col)
        self.df = new_df
        self._log(msg)
        self.set_status(f"Cleaned. Shape: {self.df.shape}")

    def _on_reset(self):
        if self.df_raw is None: return
        self.df = self.df_raw.copy()
        self._log("Dataset reset to original.")
        self.refresh()
        self.set_status("Reset to original dataset.")

    # ── helpers ───────────────────────────────────────────────────
    def _log(self, msg: str):
        self.log_box.insert("end", f"▶ {msg}\n")
        self.log_box.see("end")

    def _draw_heatmap(self):
        for w in self.heatmap_frame.winfo_children():
            w.destroy()

        from utils.theme import CARD, TEXT, ACCENT2, SUCCESS, BG, BORDER
        fig = Figure(figsize=(8, 2.6), facecolor=BG)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(CARD)

        missing = self.df.isnull()
        if missing.values.any():
            sns.heatmap(
                missing.head(100).T,
                ax=ax, cmap=[CARD, ACCENT2],
                cbar=False, yticklabels=True, xticklabels=False
            )
            ax.set_title("Missing Value Map  (first 100 rows)",
                         color=TEXT, pad=6, fontsize=9)
        else:
            ax.text(0.5, 0.5, "✓  No missing values",
                    ha="center", va="center", color=SUCCESS,
                    fontsize=13, transform=ax.transAxes)
            ax.set_axis_off()

        fig.tight_layout(pad=0.5)
        canvas = FigureCanvasTkAgg(fig, self.heatmap_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)