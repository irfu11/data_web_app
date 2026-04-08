"""
utils/theme.py — All color constants, font tuples, and matplotlib/seaborn global config.
Import from here everywhere — never hardcode colors in tab files.
"""

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image, ImageDraw
import io

# ── Modern Glassmorphic Color Palette ──────────────────────────────────────────
BG       = "#E8F0F7"        # Light background
PANEL    = "#FFFFFF"         # White panels/sidebar
CARD     = "#F5F9FC"        # Light card background
ACCENT   = "#6366F1"        # Indigo
ACCENT2  = "#EC4899"        # Pink
ACCENT3  = "#10B981"        # Emerald Green
TEXT     = "#1E293B"        # Dark text
SUBTEXT  = "#64748B"        # Gray text
BORDER   = "#E2E8F0"        # Light border
SUCCESS  = "#10B981"
WARNING  = "#F59E0B"
ERROR    = "#EF4444"
BG_ACCENT = "#8B5CF6"       # Purple
BG_ACCENT2 = "#06B6D4"      # Cyan
BG_ACCENT3 = "#F97316"      # Orange

PALETTE = [
    ACCENT, ACCENT2, ACCENT3, "#F59E0B", "#06B6D4",
    "#8B5CF6", "#F97316", "#10B981", "#EF4444", "#3B82F6",
]

# ── Fonts ──────────────────────────────────────────────────────────────────────
FONT_TITLE  = ("Courier New", 14, "bold")
FONT_HEAD   = ("Courier New", 11, "bold")
FONT_BODY   = ("Courier New", 10)
FONT_SMALL  = ("Courier New", 9)
FONT_BIG    = ("Courier New", 28, "bold")
FONT_MONO   = ("Courier New", 9)

# ── Matplotlib / Seaborn Global Config ────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="husl")

plt.rcParams.update({
    "figure.facecolor": CARD,
    "axes.facecolor":   CARD,
    "axes.edgecolor":   BORDER,
    "axes.labelcolor":  TEXT,
    "xtick.color":      SUBTEXT,
    "ytick.color":      SUBTEXT,
    "text.color":       TEXT,
    "grid.color":       BORDER,
    "grid.alpha":       0.2,
})

# ── Rounded Corner Utilities ──────────────────────────────────────────────────
def create_rounded_rectangle(width, height, radius, color=(255, 255, 255, 200)):
    """Create a PIL image with rounded rectangle (for glassmorphic cards)."""
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    x, y = 0, 0
    # Draw rounded rectangle with transparency
    draw.rounded_rectangle(
        [(x, y), (x + width, y + height)],
        radius=radius,
        fill=color,
        outline=(*color[:3], 100) if len(color) == 4 else color
    )
    return img