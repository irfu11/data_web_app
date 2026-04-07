"""
utils/theme.py — All color constants, font tuples, and matplotlib/seaborn global config.
Import from here everywhere — never hardcode colors in tab files.
"""

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import seaborn as sns

# ── Color Palette ──────────────────────────────────────────────────────────────
BG       = "#0F1117"
PANEL    = "#1A1D27"
CARD     = "#22263A"
ACCENT   = "#6C63FF"
ACCENT2  = "#FF6584"
ACCENT3  = "#43E97B"
TEXT     = "#E8EAF6"
SUBTEXT  = "#8892B0"
BORDER   = "#2D3250"
SUCCESS  = "#43E97B"
WARNING  = "#FFB347"
ERROR    = "#FF6B6B"

PALETTE = [
    ACCENT, ACCENT2, ACCENT3, "#FFB347", "#56CCF2",
    "#BB6BD9", "#F2994A", "#27AE60", "#EB5757", "#2D9CDB",
]

# ── Fonts ──────────────────────────────────────────────────────────────────────
FONT_TITLE  = ("Courier New", 14, "bold")
FONT_HEAD   = ("Courier New", 11, "bold")
FONT_BODY   = ("Courier New", 10)
FONT_SMALL  = ("Courier New", 9)
FONT_BIG    = ("Courier New", 28, "bold")
FONT_MONO   = ("Courier New", 9)

# ── Matplotlib / Seaborn Global Config ────────────────────────────────────────
sns.set_theme(style="darkgrid", palette="deep")

plt.rcParams.update({
    "figure.facecolor": CARD,
    "axes.facecolor":   CARD,
    "axes.edgecolor":   BORDER,
    "axes.labelcolor":  TEXT,
    "xtick.color":      SUBTEXT,
    "ytick.color":      SUBTEXT,
    "text.color":       TEXT,
    "grid.color":       BORDER,
    "grid.alpha":       0.4,
})