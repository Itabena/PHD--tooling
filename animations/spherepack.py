"""Entry #15 — Sphere-packing / covering geometry of channel capacity (ITFNS §2.5-2.6).
Static SVG, dark-mode. Left: packing (capacity). Right: covering (rate-distortion)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np

WARM, WARM2, HOT, COOL, COOL2, GRAYM, WHITE, BG = (
    "#FF9E4A", "#FFC94A", "#FF5C5C", "#5CA8FF", "#7BE0D4", "#B9B9B9", "#ECECEC", "#12141a")

fig, axes = plt.subplots(1, 2, figsize=(11.4, 6.0), dpi=100)
fig.patch.set_facecolor(BG)

# ---------- LEFT: packing = capacity ----------
ax = axes[0]
ax.set_facecolor(BG)
ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.2, 1.3); ax.set_aspect("equal"); ax.axis("off")
ax.add_patch(Circle((0, 0), 1.0, fill=False, edgecolor=GRAYM, lw=2.2))
r = 0.16
centers = []
for iy, y in enumerate(np.arange(-0.82, 0.83, r * np.sqrt(3))):
    xoff = 0 if iy % 2 == 0 else r
    for x in np.arange(-0.85 + xoff, 0.86, 2 * r):
        if x * x + y * y < (1 - r) ** 2:
            centers.append((x, y))
for (x, y) in centers:
    ax.add_patch(Circle((x, y), r, facecolor=WARM, edgecolor=WARM2, lw=0.8, alpha=0.55))
    ax.plot(x, y, ".", color=WHITE, ms=2.5)
ax.text(0, 1.16, "capacity = packing (disjoint)", color=WARM, fontsize=15,
        ha="center", family="serif")
ax.text(0, -1.12, r"# disjoint noise-balls $= 2^{N\,I(A,B)}$", color=WHITE, fontsize=13,
        ha="center", family="serif")
ax.annotate("error sphere\n" + r"$2^{N\,S(A|B)}$", xy=centers[len(centers) // 2],
            xytext=(0.5, 0.8), color=WARM2, fontsize=10, family="serif",
            arrowprops=dict(arrowstyle="->", color=WARM2, lw=1))
ax.text(-1.05, 0.6, "output space\n" + r"$\sim 2^{N\,S(A)}$", color=GRAYM, fontsize=10,
        family="serif", ha="left")

# ---------- RIGHT: covering = rate-distortion ----------
ax = axes[1]
ax.set_facecolor(BG)
ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.2, 1.3); ax.set_aspect("equal"); ax.axis("off")
ax.add_patch(Circle((0, 0), 1.0, fill=False, edgecolor=GRAYM, lw=2.2))
R = 0.26
covers = []
for iy, y in enumerate(np.arange(-0.78, 0.8, R * 1.3)):
    xoff = 0 if iy % 2 == 0 else R * 0.7
    for x in np.arange(-0.85 + xoff, 0.86, R * 1.4):
        if x * x + y * y < 1.0:
            covers.append((x, y))
for (x, y) in covers:
    ax.add_patch(Circle((x, y), R, facecolor=COOL, edgecolor=COOL2, lw=0.8, alpha=0.32))
ax.text(0, 1.16, "rate-distortion = covering (overlap OK)", color=COOL, fontsize=15,
        ha="center", family="serif")
ax.text(0, -1.12, "distortion-balls cover the whole region", color=WHITE, fontsize=13,
        ha="center", family="serif")

# ---------- inset caption (plain text, no mathtext) ----------
fig.text(0.5, 0.045,
         "2.6 inset: volume ratio of nested ellipsoids (signal+noise vs noise) "
         "gives  C = (1/2) log2(1 + SNR)",
         color=GRAYM, fontsize=11, ha="center", family="serif")

fig.suptitle("Channel capacity as sphere-packing;  its rate-distortion mirror as covering",
             color=WHITE, fontsize=17, family="serif", y=0.98)
plt.tight_layout(rect=[0, 0.06, 1, 0.95])
base = ("C:/Users/itama/Documents/My Projects/Phd/Notes_phd/z-Assets/"
        "ITFNS-animations/ch2-info-coding/channel-capacity-sphere-packing.svg")
import os
from components import refuse_if_exists
os.makedirs(os.path.dirname(base), exist_ok=True)
refuse_if_exists(base)
fig.savefig(base, facecolor=BG, format="svg")
fig.savefig("sphere_preview.png", facecolor=BG, dpi=110)
print("saved", len(centers), "packed,", len(covers), "covers")
