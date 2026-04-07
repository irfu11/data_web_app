"""
tabs/correlation.py — Tab 4: Correlation Analysis.

Shows:
  • Lower-triangle heatmap (Pearson / Spearman / Kendall)
  • Ranked list of top correlated pairs
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

from tabs.base import BaseTab
from utils.theme import (
    BG, CARD, PANEL, ACCENT, ACCENT2,
    TEXT, SUBTEXT, BORDER, ERROR, SUCCESS, WARNING,
    FONT_HEAD, FONT_SMALL
)
from utils.widgets import make_button


class CorrelationTab(BaseTab):

    def build(self):
        # ── toolbar ───────────────────────────────────────────────
        toolbar = tk.Frame(self.parent, bg=BG)
        toolbar.pack(fill="x", padx=20, pady=(16, 6))

        tk.Label(toolbar, text="Correlation Analysis",
                 font=FONT_HEAD, bg=BG, fg=ACCENT).pack(side="left")

        tk.Label(toolbar, text="Method:",
                 font=FONT_SMALL, bg=BG, fg=SUBTEXT).pack(side="left", padx=(20, 6))

        self.cb_method = ttk.Combobox(
            toolbar, state="readonly",
            font=FONT_SMALL, width=12,
            values=["pearson", "spearman", "kendall"]
        )
        self.cb_method.set("pearson")
        self.cb_method.pack(side="left", padx=(0, 10))

        make_button(toolbar, "Compute",
                    self.refresh, color=ACCENT).pack(side="left")

        # ── heatmap area ──────────────────────────────────────────
        self.heatmap_frame = tk.Frame(self.parent, bg=BG)
        self.heatmap_frame.pack(fill="both", expand=True, padx=20, pady=(0, 6))

        # ── top-pairs list ────────────────────────────────────────
        self.pairs_frame = tk.Frame(self.parent, bg=BG)
        self.pairs_frame.pack(fill="x", padx=20, pady=(0, 14))

    # ── refresh ───────────────────────────────────────────────────
    def refresh(self):
        for w in self.heatmap_frame.winfo_children():
            w.destroy()
        for w in self.pairs_frame.winfo_children():
            w.destroy()

        if self.df is None:
            return

        num_df = self.df.select_dtypes(include=np.number)
        if num_df.shape[1] < 2:
            tk.Label(self.heatmap_frame,
                     text="Need at least 2 numeric columns to compute correlation.",
                     font=FONT_SMALL, bg=BG, fg=WARNING).pack(pady=20)
            return

        method = self.cb_method.get()
        corr   = num_df.corr(method=method)

        self._draw_heatmap(corr, method)
        self._draw_top_pairs(corr)

    # ── heatmap ───────────────────────────────────────────────────
    def _draw_heatmap(self, corr, method):
        fig = Figure(figsize=(9, 5.5), facecolor=BG)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(CARD)

        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(
            corr, ax=ax, mask=mask,
            cmap="coolwarm", annot=True, fmt=".2f",
            linewidths=0.4, linecolor=BG,
            vmin=-1, vmax=1,
            annot_kws={"size": 8, "color": TEXT},
            cbar_kws={"shrink": 0.8}
        )
        ax.set_title(
            f"{method.capitalize()} Correlation Matrix",
            color=TEXT, pad=10, fontsize=12
        )
        ax.tick_params(colors=SUBTEXT, labelsize=8)

        fig.tight_layout(pad=0.6)
        canvas = FigureCanvasTkAgg(fig, self.heatmap_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ── top pairs ─────────────────────────────────────────────────
    def _draw_top_pairs(self, corr):
        tk.Label(self.pairs_frame,
                 text="Top Correlated Pairs",
                 font=FONT_HEAD, bg=BG, fg=ACCENT).pack(anchor="w", pady=(4, 6))

        abs_corr = corr.abs()
        upper    = abs_corr.where(
            np.triu(np.ones(abs_corr.shape), k=1).astype(bool)
        )
        pairs = (upper.stack()
                      .sort_values(ascending=False)
                      .head(10))

        if pairs.empty:
            tk.Label(self.pairs_frame,
                     text="No pairs found.", font=FONT_SMALL,
                     bg=BG, fg=SUBTEXT).pack(anchor="w")
            return

        # signed values for display
        signed = corr.where(
            np.triu(np.ones(corr.shape), k=1).astype(bool)
        ).stack()

        for (c1, c2), abs_v in pairs.items():
            v      = signed.get((c1, c2), abs_v)
            color  = SUCCESS if v > 0.5 else (ERROR if v < -0.5 else SUBTEXT)
            label  = (f"  {'🔴' if abs_v > 0.7 else ('🟡' if abs_v > 0.4 else '🟢')}"
                      f"  {c1}  ↔  {c2}   r = {v:+.3f}")
            tk.Label(self.pairs_frame, text=label,
                     font=FONT_SMALL, bg=BG, fg=color).pack(anchor="w")