"""
tabs/gamma_export.py — Gamma Export Tab
Export data and analysis results to Gamma format
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from tabs.base import BaseTab
from utils.theme import (
    BG, CARD, PANEL, ACCENT, ACCENT2, ACCENT3,
    TEXT, SUBTEXT, BORDER, ERROR, SUCCESS, WARNING,
    FONT_HEAD, FONT_SMALL, FONT_MONO, FONT_BODY
)
from utils.widgets import make_button


class GammaExportTab(BaseTab):
    """Tab for exporting datasets and analyses to Gamma format"""
    
    def build(self):
        """Create the export interface"""
        # Main container
        main_frame = tk.Frame(self.parent, bg=BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(
            main_frame,
            text="γ  Gamma Export",
            font=FONT_HEAD,
            bg=BG,
            fg=ACCENT
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # Info card
        info_frame = tk.Frame(main_frame, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_label = tk.Label(
            info_frame,
            text="Export your dataset and analysis results to Gamma format for sharing and collaboration.",
            font=FONT_BODY,
            bg=CARD,
            fg=SUBTEXT,
            wraplength=400,
            justify="left"
        )
        info_label.pack(padx=16, pady=16)
        
        # Export options frame
        options_frame = tk.LabelFrame(
            main_frame,
            text="Export Options",
            font=FONT_HEAD,
            bg=PANEL,
            fg=TEXT,
            padx=16,
            pady=16
        )
        options_frame.pack(fill="x", pady=(0, 20))
        
        # Checkbox options
        self.export_data = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Export Dataset",
            variable=self.export_data,
            font=FONT_BODY,
            bg=PANEL,
            fg=TEXT,
            activebackground=PANEL,
            activeforeground=ACCENT
        ).pack(anchor="w", pady=8)
        
        self.export_analysis = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Export Analysis & Insights",
            variable=self.export_analysis,
            font=FONT_BODY,
            bg=PANEL,
            fg=TEXT,
            activebackground=PANEL,
            activeforeground=ACCENT
        ).pack(anchor="w", pady=8)
        
        self.export_charts = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Export Visualizations",
            variable=self.export_charts,
            font=FONT_BODY,
            bg=PANEL,
            fg=TEXT,
            activebackground=PANEL,
            activeforeground=ACCENT
        ).pack(anchor="w", pady=8)
        
        # Export button
        export_btn = make_button(
            main_frame,
            text="⬇  Export to Gamma",
            command=self._export
        )
        export_btn.pack(fill="x", pady=20)
    
    def refresh(self):
        """Called when data is refreshed"""
        if self.df is None:
            self.set_status("Load a dataset first to enable export")
        else:
            self.set_status(f"Ready to export: {self.df.shape[0]:,} rows × {self.df.shape[1]} cols")
    
    def _export(self):
        """Handle export action"""
        if self.df is None:
            messagebox.showerror("Export Error", "Please load a dataset first")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".gamma",
            filetypes=[
                ("Gamma files", "*.gamma"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # Placeholder export logic
            self.set_status(f"Export feature coming soon: {file_path}")
            messagebox.showinfo("Export", "Gamma export feature is currently under development")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
