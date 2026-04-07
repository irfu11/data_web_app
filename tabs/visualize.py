"""
tabs/visualize.py — Tab 3: Data Visualization.

Left  : controls (chart type, columns, palette)
Right : matplotlib canvas + navigation toolbar
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import seaborn as sns

from tabs.base import BaseTab
from utils.theme import (
    BG, CARD, PANEL, ACCENT, ACCENT2, ACCENT3,
    TEXT, SUBTEXT, BORDER, ERROR, WARNING, SUCCESS, PALETTE,
    FONT_HEAD, FONT_SMALL
)
from utils.widgets import make_button


CHART_TYPES = [
    "Histogram",
    "Box Plot",
    "Violin Plot",
    "Scatter Plot",
    "Bar Chart",
    "Line Chart",
    "KDE Plot",
    "Pair Plot",
    "Count Plot",
]

COLOR_PALETTES = [
    "deep", "muted", "bright", "pastel",
    "dark", "colorblind", "viridis", "plasma", "coolwarm",
]


class VisualizeTab(BaseTab):

    def build(self):
        # ── control sidebar ───────────────────────────────────────
        ctrl = tk.Frame(self.parent, bg=PANEL, width=240)
        ctrl.pack(side="left", fill="y")
        ctrl.pack_propagate(False)

        # ── plot area ─────────────────────────────────────────────
        self.plot_frame = tk.Frame(self.parent, bg=BG)
        self.plot_frame.pack(side="left", fill="both", expand=True)

        self._build_controls(ctrl)
        self._show_placeholder()

        self._fig    = None
        self._canvas = None

    # ── controls ──────────────────────────────────────────────────
    def _build_controls(self, parent):
        tk.Label(parent, text="Plot Controls",
                 font=FONT_HEAD, bg=PANEL, fg=ACCENT,
                 padx=14, pady=14).pack(anchor="w")

        def row(label, widget_fn):
            tk.Label(parent, text=label, font=FONT_SMALL,
                     bg=PANEL, fg=SUBTEXT, padx=14).pack(anchor="w", pady=(8, 2))
            w = widget_fn(parent)
            w.pack(fill="x", padx=14, pady=2)
            return w

        self.cb_type    = row("Chart Type",          self._make_type_cb)
        self.cb_x       = row("X  Column",           self._make_col_cb)
        self.cb_y       = row("Y  Column (optional)", self._make_col_cb)
        self.cb_hue     = row("Hue Column (optional)", self._make_col_cb)
        self.cb_palette = row("Color Palette",        self._make_palette_cb)

        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=14, pady=14)

        make_button(parent, "  ▶  Generate Plot  ",
                    self._on_generate, color=ACCENT).pack(fill="x", padx=14, pady=4)
        make_button(parent, "  💾  Save Plot  ",
                    self._on_save, color=CARD).pack(fill="x", padx=14, pady=4)

    def _make_type_cb(self, p):
        cb = ttk.Combobox(p, state="readonly", font=FONT_SMALL,
                          values=CHART_TYPES)
        cb.set("Histogram")
        return cb

    def _make_col_cb(self, p):
        return ttk.Combobox(p, state="readonly", font=FONT_SMALL)

    def _make_palette_cb(self, p):
        cb = ttk.Combobox(p, state="readonly", font=FONT_SMALL,
                          values=COLOR_PALETTES)
        cb.set("deep")
        return cb

    # ── refresh ───────────────────────────────────────────────────
    def refresh(self):
        if self.df is None: return
        all_cols = [""] + list(self.df.columns)
        num_cols = [""] + list(self.df.select_dtypes(include=np.number).columns)
        cat_cols = [""] + list(self.df.select_dtypes(include="object").columns)

        self.cb_x["values"]   = all_cols
        self.cb_y["values"]   = num_cols
        self.cb_hue["values"] = cat_cols

        if len(all_cols) > 1:
            self.cb_x.set(all_cols[1])
        if len(num_cols) > 2:
            self.cb_y.set(num_cols[2])
        self.cb_hue.set("")

    # ── plot generation ───────────────────────────────────────────
    def _on_generate(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Please load a dataset first.")
            return
        for w in self.plot_frame.winfo_children():
            w.destroy()

        chart   = self.cb_type.get()
        x       = self.cb_x.get()      or None
        y       = self.cb_y.get()      or None
        hue     = self.cb_hue.get()    or None
        palette = self.cb_palette.get()

        fig = Figure(figsize=(10, 6), facecolor=BG)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(CARD)

        try:
            self._draw(ax, fig, chart, x, y, hue, palette)
        except Exception as exc:
            ax.text(0.5, 0.5, f"Error rendering plot:\n{exc}",
                    ha="center", va="center", color=ERROR,
                    fontsize=11, transform=ax.transAxes)

        fig.tight_layout(pad=1.0)
        self._fig = fig
        canvas = FigureCanvasTkAgg(fig, self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self.plot_frame)
        toolbar.update()
        self._canvas = canvas

    def _draw(self, ax, fig, chart, x, y, hue, palette):
        df = self.df

        if chart == "Histogram":
            if not x: raise ValueError("Select an X column.")
            df[x].dropna().plot.hist(
                ax=ax, bins=30, color=ACCENT, edgecolor=BG, alpha=0.85)
            ax.set_title(f"Histogram — {x}", color=TEXT, pad=10)
            ax.set_xlabel(x, color=SUBTEXT)
            ax.set_ylabel("Frequency", color=SUBTEXT)

        elif chart == "Box Plot":
            cols = [c for c in [x, y] if c]
            if not cols: raise ValueError("Select at least one column.")
            bp = df[cols].dropna().boxplot(
                ax=ax, patch_artist=True,
                boxprops=dict(facecolor=ACCENT, color=BORDER),
                medianprops=dict(color=ACCENT2, linewidth=2),
                whiskerprops=dict(color=SUBTEXT),
                capprops=dict(color=SUBTEXT),
                flierprops=dict(color=ACCENT3, markerfacecolor=ACCENT3))
            ax.set_title(f"Box Plot — {', '.join(cols)}", color=TEXT)

        elif chart == "Violin Plot":
            if not (x and y): raise ValueError("Select both X and Y columns.")
            sns.violinplot(data=df, x=x, y=y, hue=hue,
                           palette=palette, ax=ax, inner="quart")
            ax.set_title(f"Violin — {x}  vs  {y}", color=TEXT)

        elif chart == "Scatter Plot":
            if not (x and y): raise ValueError("Select both X and Y columns.")
            sns.scatterplot(data=df, x=x, y=y, hue=hue,
                            palette=palette, ax=ax, alpha=0.7, s=40)
            ax.set_title(f"Scatter — {x}  vs  {y}", color=TEXT)

        elif chart == "Bar Chart":
            if not x: raise ValueError("Select an X column.")
            if df[x].dtype == object:
                vc = df[x].value_counts().head(20)
                ax.bar(vc.index, vc.values,
                       color=PALETTE[:len(vc)])
                ax.set_xticklabels(vc.index, rotation=35, ha="right", fontsize=8)
                ax.set_title(f"Bar Chart — {x}", color=TEXT)
            elif y:
                df.groupby(x)[y].mean().plot.bar(ax=ax, color=ACCENT)
                ax.set_title(f"Mean {y}  by  {x}", color=TEXT)
            else:
                raise ValueError("For numeric X, also select a Y column.")

        elif chart == "Line Chart":
            if not (x and y): raise ValueError("Select both X and Y columns.")
            df.sort_values(x).plot(x=x, y=y, ax=ax,
                                   color=ACCENT, linewidth=1.8)
            ax.set_title(f"Line — {x}  vs  {y}", color=TEXT)

        elif chart == "KDE Plot":
            if not x: raise ValueError("Select an X column.")
            data = df[x].dropna()
            data.plot.kde(ax=ax, color=ACCENT, linewidth=2)
            ax.fill_between(ax.lines[0].get_xdata(),
                            ax.lines[0].get_ydata(),
                            alpha=0.2, color=ACCENT)
            ax.set_title(f"KDE — {x}", color=TEXT)

        elif chart == "Pair Plot":
            num = df.select_dtypes(include=np.number).iloc[:, :5]
            fig.clear()
            g = sns.pairplot(num, plot_kws={"color": ACCENT, "alpha": 0.5})
            g.fig.set_facecolor(BG)
            for w in self.plot_frame.winfo_children():
                w.destroy()
            c = FigureCanvasTkAgg(g.fig, self.plot_frame)
            c.draw()
            c.get_tk_widget().pack(fill="both", expand=True)
            NavigationToolbar2Tk(c, self.plot_frame).update()
            self._fig    = g.fig
            self._canvas = c
            return  # early exit — already rendered

        elif chart == "Count Plot":
            if not x: raise ValueError("Select an X column.")
            order = df[x].value_counts().index[:20]
            sns.countplot(data=df, x=x, hue=hue,
                          order=order, palette=palette, ax=ax)
            ax.set_xticklabels(ax.get_xticklabels(),
                               rotation=35, ha="right", fontsize=8)
            ax.set_title(f"Count Plot — {x}", color=TEXT)

        else:
            ax.text(0.5, 0.5, "Unknown chart type",
                    ha="center", va="center", color=WARNING,
                    fontsize=13, transform=ax.transAxes)

    # ── save ─────────────────────────────────────────────────────
    def _on_save(self):
        if self._fig is None:
            messagebox.showinfo("No Plot", "Generate a plot first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("SVG", "*.svg"), ("PDF", "*.pdf")]
        )
        if path:
            self._fig.savefig(path, dpi=150,
                              bbox_inches="tight", facecolor=BG)
            self.set_status(f"Plot saved → {path}")

    def _show_placeholder(self):
        tk.Label(
            self.plot_frame,
            text="← Select options and click  ▶  Generate Plot",
            font=("Courier New", 12), bg=BG, fg=SUBTEXT
        ).pack(expand=True)