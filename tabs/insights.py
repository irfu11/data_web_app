"""
tabs/insights.py — Tab 5: Insights + Groq AI Chat.

Layout:
  Top toolbar  : Generate Stats | Ask AI | Export | Clear Chat
  Left panel   : Statistical report (pandas/numpy, 320 px)
  Middle panel : Groq AI streamed chat + custom question input
  Right panel  : Distribution histograms (260 px)
  Bottom bar   : API key entry | Model selector | Status indicator
"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import numpy as np
import threading
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tabs.base import BaseTab
from utils.theme import (
    BG, CARD, PANEL, ACCENT, ACCENT2, ACCENT3,
    TEXT, SUBTEXT, BORDER, ERROR, SUCCESS, WARNING,
    FONT_HEAD, FONT_SMALL, FONT_MONO,
)
from utils.widgets import make_button
from utils.insights import generate_insights
from utils.GROQ_client import (
    GroqClient, GroqAPIError, GroqAuthError, GroqRateLimitError,
    build_analysis_prompt, SYSTEM_PROMPT, GROQ_MODELS,
)

AI_FG   = "#C3E6CB"   # soft green  — AI responses
USER_FG = "#FFE0A3"   # warm amber  — user prompts / labels


class InsightsTab(BaseTab):

    def build(self):
        self._client             = None   # GroqClient instance
        self._running            = False  # True while streaming
        self._placeholder_active = True   # question box placeholder state
        self._api_key_validated  = False  # True once key has been tested

        self._build_top_bar()
        self._build_body()
        self._build_bottom_bar()

    # ══════════════════════════════════════════════════════════════
    #  TOP TOOLBAR
    # ══════════════════════════════════════════════════════════════
    def _build_top_bar(self):
        bar = tk.Frame(self.parent, bg=BG)
        bar.pack(fill="x", padx=20, pady=(14, 6))

        tk.Label(bar, text="💡 Insights & Groq AI",
                 font=FONT_HEAD, bg=BG, fg=ACCENT).pack(side="left")

        make_button(bar, "  📊  Generate Stats  ",
                    self._on_generate_stats,
                    color=ACCENT).pack(side="left", padx=(18, 6))

        make_button(bar, "  🤖  Ask AI (full report)  ",
                    self._on_ask_ai_full,
                    color=ACCENT2).pack(side="left", padx=(0, 6))

        make_button(bar, "  💾  Export Report  ",
                    self._on_export,
                    color=CARD).pack(side="left", padx=(0, 6))

        make_button(bar, "  🗑  Clear Chat  ",
                    self._clear_chat,
                    color=CARD).pack(side="left")

    # ══════════════════════════════════════════════════════════════
    #  THREE-COLUMN BODY
    # ══════════════════════════════════════════════════════════════
    def _build_body(self):
        body = tk.Frame(self.parent, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 6))

        # ── LEFT: statistical report ──────────────────────────────
        left = tk.Frame(body, bg=BG, width=320)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="Statistical Report",
                 font=("Courier New", 9, "bold"),
                 bg=BG, fg=SUBTEXT).pack(anchor="w", pady=(0, 4))

        self.stats_box = scrolledtext.ScrolledText(
            left, font=("Courier New", 8),
            bg=CARD, fg=ACCENT3,
            insertbackground=TEXT, relief="flat",
            borderwidth=0, wrap="none"
        )
        self.stats_box.pack(fill="both", expand=True)
        self.stats_box.insert(
            "end", "Click  📊 Generate Stats  to compute the report.\n")
        self.stats_box.configure(state="disabled")

        # ── MIDDLE: Groq AI chat ──────────────────────────────────
        mid = tk.Frame(body, bg=BG)
        mid.pack(side="left", fill="both", expand=True, padx=(12, 12))

        mid_hdr = tk.Frame(mid, bg=BG)
        mid_hdr.pack(fill="x", pady=(0, 4))

        tk.Label(mid_hdr, text="🤖 Groq AI  (free · cloud · fast)",
                 font=("Courier New", 9, "bold"),
                 bg=BG, fg=SUBTEXT).pack(side="left")

        self.stream_lbl = tk.Label(
            mid_hdr, text="", font=FONT_SMALL, bg=BG, fg=ACCENT3)
        self.stream_lbl.pack(side="left", padx=8)

        # chat display
        self.ai_box = scrolledtext.ScrolledText(
            mid, font=("Courier New", 9),
            bg=CARD, fg=AI_FG,
            insertbackground=TEXT, relief="flat",
            borderwidth=0, wrap="word", spacing1=2, spacing3=2
        )
        self.ai_box.pack(fill="both", expand=True)

        # text colour tags
        self.ai_box.tag_configure("user",
            foreground=USER_FG, font=("Courier New", 9, "bold"))
        self.ai_box.tag_configure("ai",    foreground=AI_FG)
        self.ai_box.tag_configure("system",
            foreground=SUBTEXT, font=("Courier New", 8, "italic"))
        self.ai_box.tag_configure("error", foreground=ERROR)

        self._append("system",
            "Enter your free Groq API key in the bar below, then click\n"
            "🤖 Ask AI  or type a question and press Send.\n\n"
            "Get a free key (2 min): console.groq.com → API Keys\n")

        # question input row
        q_row = tk.Frame(mid, bg=BG)
        q_row.pack(fill="x", pady=(6, 0))

        self.question_var = tk.StringVar()
        self.q_entry = tk.Entry(
            q_row, textvariable=self.question_var,
            font=FONT_MONO, bg=CARD, fg=SUBTEXT,
            insertbackground=TEXT, relief="flat",
            bd=0, highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=ACCENT
        )
        self.q_entry.pack(side="left", fill="x", expand=True,
                          ipady=7, padx=(0, 6))
        self.q_entry.insert(0, "Ask anything about your data…")
        self.q_entry.bind("<Return>",   lambda e: self._on_ask_custom())
        self.q_entry.bind("<FocusIn>",  self._clear_ph)
        self.q_entry.bind("<FocusOut>", self._restore_ph)

        self.ask_btn = make_button(
            q_row, "  Send  ", self._on_ask_custom, color=ACCENT2)
        self.ask_btn.pack(side="left")

        # ── RIGHT: histograms ─────────────────────────────────────
        right = tk.Frame(body, bg=BG, width=260)
        right.pack(side="left", fill="y")
        right.pack_propagate(False)

        tk.Label(right, text="Distributions",
                 font=("Courier New", 9, "bold"),
                 bg=BG, fg=SUBTEXT).pack(anchor="w", pady=(0, 4))

        self.hist_frame = tk.Frame(right, bg=BG)
        self.hist_frame.pack(fill="both", expand=True)

    # ══════════════════════════════════════════════════════════════
    #  BOTTOM BAR  — API key + model picker + status
    # ══════════════════════════════════════════════════════════════
    def _build_bottom_bar(self):
        bar = tk.Frame(self.parent, bg=PANEL, height=46)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        # API key label
        tk.Label(bar, text="🔑 Groq API Key:",
                 font=FONT_SMALL, bg=PANEL, fg=SUBTEXT).pack(
                     side="left", padx=(14, 4), pady=10)

        self.key_var  = tk.StringVar()
        self.key_show = tk.BooleanVar(value=False)

        # key entry field
        self.key_entry = tk.Entry(
            bar, textvariable=self.key_var,
            font=("Courier New", 9), bg=CARD, fg=TEXT,
            insertbackground=TEXT, relief="flat", show="•",
            bd=0, highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=ACCENT,
            width=42
        )
        self.key_entry.pack(side="left", ipady=5, pady=10)
        self.key_entry.bind("<Return>", lambda e: self._on_validate_key())

        # show/hide toggle
        tk.Checkbutton(
            bar, text="Show", variable=self.key_show,
            command=lambda: self.key_entry.configure(
                show="" if self.key_show.get() else "•"),
            font=FONT_SMALL, bg=PANEL, fg=SUBTEXT,
            selectcolor=CARD, activebackground=PANEL
        ).pack(side="left", padx=(4, 0))

        # save key button
        make_button(bar, " ✓ Save Key ",
                    self._on_validate_key,
                    color=ACCENT).pack(side="left", padx=8, pady=10)

        # model selector
        tk.Label(bar, text="Model:",
                 font=FONT_SMALL, bg=PANEL, fg=SUBTEXT).pack(
                     side="left", padx=(10, 4))

        self.model_var = tk.StringVar(value="llama-3.3-70b-versatile")
        model_menu = tk.OptionMenu(
            bar, self.model_var,
            *[m[0] for m in GROQ_MODELS],
            command=lambda _: self._reset_client()
        )
        model_menu.configure(
            font=FONT_SMALL, bg=CARD, fg=TEXT,
            activebackground=ACCENT, activeforeground=TEXT,
            relief="flat", borderwidth=0, highlightthickness=0,
            width=22
        )
        model_menu.pack(side="left", pady=10)

        # status dot + label
        self.status_dot = tk.Label(
            bar, text="●", font=("Courier New", 13),
            bg=PANEL, fg=SUBTEXT)
        self.status_dot.pack(side="left", padx=(14, 4))

        self.status_lbl = tk.Label(
            bar, text="No API key entered",
            font=FONT_SMALL, bg=PANEL, fg=SUBTEXT)
        self.status_lbl.pack(side="left")

        # right-side hint
        tk.Label(
            bar,
            text="Free key → console.groq.com  |  No credit card needed",
            font=("Courier New", 8), bg=PANEL, fg=SUBTEXT
        ).pack(side="right", padx=14)

    # ══════════════════════════════════════════════════════════════
    #  REFRESH  (called when dataset is loaded)
    # ══════════════════════════════════════════════════════════════
    def refresh(self):
        if self.df is None:
            return
        self._fill_stats()
        self._draw_histograms()

    # ══════════════════════════════════════════════════════════════
    #  API KEY VALIDATION
    # ══════════════════════════════════════════════════════════════
    def _on_validate_key(self):
        key = self.key_var.get().strip()
        if not key:
            self._set_status(False, "Enter your Groq API key first.")
            return
        if not key.startswith("gsk_"):
            self._set_status(False,
                "Groq keys start with  gsk_  — check your key.")
            return

        self._set_status(None, "Validating key…")
        self.key_entry.configure(state="disabled")

        def worker():
            try:
                client = GroqClient(api_key=key, model=self.model_var.get())
                client.validate_key()
                self._client            = client
                self._api_key_validated = True
                self.parent.after(0, self._set_status, True,
                    "API key valid ✓  —  Ready to chat!")
                self.parent.after(0, self._append, "system",
                    "\n✓  Groq API key accepted. You're ready!\n"
                    "Click  🤖 Ask AI  or type a question below.\n")
            except GroqAuthError as e:
                self.parent.after(0, self._set_status, False, str(e))
                self.parent.after(0, self._append, "error",
                    f"\n✗  Invalid API key:\n{e}\n")
            except Exception as e:
                self.parent.after(0, self._set_status, False,
                    f"Validation error: {e}")
            finally:
                self.parent.after(
                    0, self.key_entry.configure, {"state": "normal"})

        threading.Thread(target=worker, daemon=True).start()

    def _set_status(self, ok, msg: str):
        """ok=True → green, ok=False → red, ok=None → yellow (busy)."""
        colour = {True: SUCCESS, False: ERROR, None: WARNING}.get(ok, SUBTEXT)
        self.status_dot.configure(fg=colour)
        self.status_lbl.configure(fg=colour, text=msg)

    # ══════════════════════════════════════════════════════════════
    #  STATS REPORT
    # ══════════════════════════════════════════════════════════════
    def _on_generate_stats(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Load a dataset first.")
            return
        self._fill_stats()
        self._draw_histograms()

    def _fill_stats(self):
        lines = generate_insights(self.df)
        self.stats_box.configure(state="normal")
        self.stats_box.delete("1.0", "end")
        self.stats_box.insert("end", "\n".join(lines))
        self.stats_box.configure(state="disabled")

    # ══════════════════════════════════════════════════════════════
    #  AI: FULL AUTO REPORT
    # ══════════════════════════════════════════════════════════════
    def _on_ask_ai_full(self):
        if not self._check_ready():
            return
        prompt = build_analysis_prompt(self.df)
        self._stream(prompt, label="📊 Full Dataset Analysis")

    # ══════════════════════════════════════════════════════════════
    #  AI: CUSTOM QUESTION
    # ══════════════════════════════════════════════════════════════
    def _on_ask_custom(self):
        if not self._check_ready():
            return
        q = self.question_var.get().strip()
        if not q or self._placeholder_active:
            messagebox.showinfo("Empty", "Type a question first.")
            return
        prompt = build_analysis_prompt(self.df, question=q)
        self._stream(prompt, label=f"❓ {q}")
        self.question_var.set("")
        self._placeholder_active = False

    def _check_ready(self) -> bool:
        if self.df is None:
            messagebox.showwarning("No Data", "Load a dataset first.")
            return False
        if not self._api_key_validated or self._client is None:
            messagebox.showwarning(
                "No API Key",
                "Enter and save your free Groq API key in the bar below.\n\n"
                "Get one free at: console.groq.com → API Keys"
            )
            return False
        return True

    # ══════════════════════════════════════════════════════════════
    #  STREAMING ENGINE
    # ══════════════════════════════════════════════════════════════
    def _stream(self, prompt: str, label: str = "AI"):
        if self._running:
            messagebox.showinfo("Busy",
                "AI is already generating. Please wait.")
            return

        # rebuild client with latest model choice
        self._client = GroqClient(
            api_key=self.key_var.get().strip(),
            model=self.model_var.get()
        )

        self._running = True
        self._set_busy(True)
        self._append("user",   f"\n▶  {label}\n")
        self._append("system", "Generating…\n")

        def worker():
            try:
                first = True
                for chunk in self._client.chat_stream(
                        prompt, system=SYSTEM_PROMPT):
                    if first:
                        self.parent.after(0, self._remove_generating)
                        first = False
                    self.parent.after(0, self._append, "ai", chunk)

                self.parent.after(0, self._append, "ai", "\n\n")
                self.parent.after(0, self._set_busy, False)

            except GroqAuthError as e:
                self.parent.after(0, self._append, "error",
                    f"\n✗  Auth error:\n{e}\n\n")
                self.parent.after(0, self._set_status, False, str(e))
                self.parent.after(0, self._set_busy, False)
                self._api_key_validated = False

            except GroqRateLimitError as e:
                self.parent.after(0, self._append, "error",
                    f"\n✗  Rate limit:\n{e}\n\n")
                self.parent.after(0, self._set_status, False,
                    "Rate limit hit — wait a moment and retry.")
                self.parent.after(0, self._set_busy, False)

            except GroqAPIError as e:
                self.parent.after(0, self._append, "error",
                    f"\n✗  Groq error:\n{e}\n\n")
                self.parent.after(0, self._set_busy, False)

            except Exception as e:
                self.parent.after(0, self._append, "error",
                    f"\n✗  Unexpected error: {e}\n\n")
                self.parent.after(0, self._set_busy, False)

        threading.Thread(target=worker, daemon=True).start()

    def _set_busy(self, busy: bool):
        self._running = busy
        self.ask_btn.configure(state="disabled" if busy else "normal")
        self.stream_lbl.configure(
            text="⏳ generating…" if busy else "")

    def _append(self, tag: str, text: str):
        self.ai_box.configure(state="normal")
        self.ai_box.insert("end", text, tag)
        self.ai_box.see("end")
        self.ai_box.configure(state="disabled")

    def _remove_generating(self):
        self.ai_box.configure(state="normal")
        idx = self.ai_box.search("Generating…\n", "1.0", tk.END)
        if idx:
            self.ai_box.delete(idx, f"{idx}+{len('Generating…') + 1}c")
        self.ai_box.configure(state="disabled")

    def _clear_chat(self):
        self.ai_box.configure(state="normal")
        self.ai_box.delete("1.0", "end")
        self.ai_box.configure(state="disabled")
        self._append("system",
            "Chat cleared. Click  🤖 Ask AI  or type a question.\n")

    # ══════════════════════════════════════════════════════════════
    #  HISTOGRAMS
    # ══════════════════════════════════════════════════════════════
    def _draw_histograms(self):
        from utils.theme import PALETTE
        for w in self.hist_frame.winfo_children():
            w.destroy()

        num = self.df.select_dtypes(include=np.number)
        if num.empty:
            tk.Label(self.hist_frame, text="No numeric cols.",
                     font=FONT_SMALL, bg=BG, fg=SUBTEXT).pack(pady=20)
            return

        cols = list(num.columns[:8])
        rows = (len(cols) + 1) // 2
        fig  = Figure(figsize=(3.2, max(4, rows * 2.0)), facecolor=BG)

        for i, col in enumerate(cols, 1):
            ax = fig.add_subplot(rows, 2, i)
            ax.set_facecolor(CARD)
            ax.hist(num[col].dropna(), bins=20,
                    color=PALETTE[i % len(PALETTE)],
                    edgecolor=BG, alpha=0.88)
            ax.set_title(col, color=TEXT, fontsize=7, pad=3)
            ax.tick_params(labelsize=6, colors=SUBTEXT)

        fig.tight_layout(pad=0.8)
        canvas = FigureCanvasTkAgg(fig, self.hist_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ══════════════════════════════════════════════════════════════
    #  EXPORT
    # ══════════════════════════════════════════════════════════════
    def _on_export(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Load a dataset first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("Markdown", "*.md")]
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write("DataLens Analytics Report\n" + "=" * 54 + "\n\n")
            f.write("=== STATISTICAL REPORT ===\n\n")
            f.write(self.stats_box.get("1.0", "end"))
            f.write("\n\n=== AI ANALYSIS (Groq) ===\n\n")
            f.write(self.ai_box.get("1.0", "end"))
        messagebox.showinfo("Saved", f"Report saved:\n{path}")
        self.set_status(f"Exported → {path}")

    # ══════════════════════════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════════════════════════
    def _reset_client(self):
        self._client = None

    def _clear_ph(self, event):
        if self._placeholder_active:
            self.q_entry.delete(0, "end")
            self.q_entry.configure(fg=TEXT)
            self._placeholder_active = False

    def _restore_ph(self, event):
        if not self.question_var.get().strip():
            self.q_entry.insert(0, "Ask anything about your data…")
            self.q_entry.configure(fg=SUBTEXT)
            self._placeholder_active = True