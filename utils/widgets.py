"""
utils/widgets.py — Reusable tkinter widget factory functions.
"""

import tkinter as tk
from tkinter import ttk
from utils.theme import (
    BG, CARD, PANEL, ACCENT, ACCENT2, TEXT, SUBTEXT, BORDER, ACCENT3
)


def make_button(parent, text, command, color=ACCENT, fg=TEXT, padx=14, pady=8):
    """Modern flat button with rounded appearance."""
    return tk.Button(
        parent, text=text, command=command,
        font=("Segoe UI", 10, "bold"),
        bg=color, fg=fg, relief="flat",
        cursor="hand2", padx=padx, pady=pady,
        activebackground=color, activeforeground=TEXT,
        highlightthickness=0, bd=0
    )


def make_label(parent, text, font=None, fg=None, bg=None, **kw):
    font = font or ("Segoe UI", 10)
    fg   = fg   or TEXT
    bg   = bg   or BG
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, highlightthickness=0, **kw)


def make_section_card(parent, title):
    """A modern card with rounded appearance and light background."""
    frame = tk.Frame(parent, bg=CARD, padx=16, pady=14)
    frame.pack(fill="x", pady=8)
    tk.Label(frame, text=title,
             font=("Segoe UI", 11, "bold"),
             bg=CARD, fg=ACCENT, highlightthickness=0).pack(anchor="w", pady=(0, 10))
    return frame


def make_stat_card(parent, title, value, icon="📊", color=ACCENT):
    """Modern stat card with color accent and icon."""
    card = tk.Frame(parent, bg=CARD, relief="flat", highlightthickness=0)
    
    # Color bar on left
    left_bar = tk.Frame(card, bg=color, width=5)
    left_bar.pack(side="left", fill="y")
    
    # Content
    content = tk.Frame(card, bg=CARD)
    content.pack(side="left", fill="both", expand=True, padx=14, pady=12)
    
    # Icon + Title row
    header = tk.Frame(content, bg=CARD)
    header.pack(fill="x", pady=(0, 6))
    
    tk.Label(header, text=icon, font=("Segoe UI", 16), bg=CARD).pack(side="left", padx=(0, 8))
    tk.Label(header, text=title, font=("Segoe UI", 9), fg=SUBTEXT, bg=CARD).pack(side="left")
    
    tk.Label(content, text=value, font=("Segoe UI", 20, "bold"), fg=TEXT, bg=CARD).pack(anchor="w")
    
    return card


def make_combobox(parent, values, default="", width=None):
    cb = ttk.Combobox(parent, state="readonly",
                      font=("Segoe UI", 9), values=values)
    if width:
        cb.configure(width=width)
    if default:
        cb.set(default)
    elif values:
        cb.set(values[0])
    return cb


def style_treeview(style: ttk.Style):
    """Apply modern light theme to all Treeview widgets."""
    style.configure(
        "Treeview",
        background=CARD, foreground=TEXT,
        fieldbackground=CARD, rowheight=26,
        font=("Segoe UI", 9), borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=PANEL, foreground=TEXT,
        font=("Segoe UI", 9, "bold"), relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", "#FFFFFF")],
    )