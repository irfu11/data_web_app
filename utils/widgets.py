"""
utils/widgets.py — Reusable tkinter widget factory functions.
"""

import tkinter as tk
from tkinter import ttk
from utils.theme import (
    BG, CARD, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, BORDER
)


def make_button(parent, text, command, color=CARD, fg=TEXT, padx=10, pady=6):
    """Standard flat button used throughout the app."""
    return tk.Button(
        parent, text=text, command=command,
        font=("Courier New", 9, "bold"),
        bg=color, fg=fg, relief="flat",
        cursor="hand2", padx=padx, pady=pady,
        activebackground=ACCENT, activeforeground=TEXT,
    )


def make_label(parent, text, font=None, fg=None, bg=None, **kw):
    font = font or ("Courier New", 10)
    fg   = fg   or TEXT
    bg   = bg   or BG
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kw)


def make_section_card(parent, title):
    """A CARD-coloured frame with a title label inside."""
    frame = tk.Frame(parent, bg=CARD, padx=14, pady=12)
    frame.pack(fill="x", pady=4)
    tk.Label(frame, text=title,
             font=("Courier New", 10, "bold"),
             bg=CARD, fg=ACCENT2).pack(anchor="w", pady=(0, 8))
    return frame


def make_combobox(parent, values, default="", width=None):
    cb = ttk.Combobox(parent, state="readonly",
                      font=("Courier New", 9), values=values)
    if width:
        cb.configure(width=width)
    if default:
        cb.set(default)
    elif values:
        cb.set(values[0])
    return cb


def style_treeview(style: ttk.Style):
    """Apply dark theme to all Treeview widgets."""
    style.configure(
        "Treeview",
        background=CARD, foreground=TEXT,
        fieldbackground=CARD, rowheight=24,
        font=("Courier New", 9), borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=PANEL, foreground=ACCENT,
        font=("Courier New", 9, "bold"), relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", TEXT)],
    )