"""Entry #27 — Counterfeit-coin ternary decision tree, static SVG (ITFNS Ex 2.4)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

WARM, WARM2, HOT, COOL, COOL2, GRAYM, WHITE, BG = (
    "#FF9E4A", "#FFC94A", "#FF5C5C", "#5CA8FF", "#7BE0D4", "#B9B9B9", "#ECECEC", "#12141a")

fig, ax = plt.subplots(figsize=(12.4, 6.6), dpi=100)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(-2.5, 29.5); ax.set_ylim(-0.5, 6.6); ax.axis("off")

# three levels: root 27 -> 9 -> 3 -> 1
levels = [
    (5.6, [(13.5, "27 coins", WARM)]),
    (3.9, [(4.5, "9", WARM2), (13.5, "9", WARM2), (22.5, "9", WARM2)]),
    (2.2, None),   # 9 nodes
    (0.6, None),   # 27 leaves (just ticks)
]

def node(x, y, label, color, w=1.6, h=0.6):
    box = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.05",
                         facecolor=color, edgecolor="none", alpha=0.85)
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", color="#101010", fontsize=12,
            family="serif", weight="bold")

# root
node(13.5, 5.6, "27 coins", WARM, w=2.4)
# level 1: three 9-nodes
l1x = [4.5, 13.5, 22.5]
branch_labels = ["A lighter\n→ fake in A", "balanced\n→ fake in C", "B lighter\n→ fake in B"]
for i, x in enumerate(l1x):
    ax.plot([13.5, x], [5.3, 4.2], color=GRAYM, lw=1.2)
    ax.text((13.5 + x) / 2 + (0.2 if i != 1 else 0), 4.95, branch_labels[i], ha="center",
            va="center", color=COOL2, fontsize=9, family="serif")
    node(x, 3.9, "9", WARM2)

# level 2: each 9-node -> three 3-nodes
l2x = []
for x in l1x:
    for dx in (-2.2, 0, 2.2):
        cx = x + dx
        l2x.append(cx)
        ax.plot([x, cx], [3.6, 2.5], color=GRAYM, lw=1.0)
        node(cx, 2.2, "3", COOL2, w=1.1, h=0.5)

# level 3: each 3-node -> three single coins (leaf ticks)
for x in l2x:
    for dx in (-0.7, 0, 0.7):
        cx = x + dx
        ax.plot([x, cx], [1.95, 1.05], color=GRAYM, lw=0.7)
        ax.plot(cx, 0.75, "o", color=WARM, ms=4)

# side annotations
for y, txt in [(3.9, "weigh 9 vs 9"), (2.2, "weigh 3 vs 3"), (0.75, "weigh 1 vs 1")]:
    ax.text(29.2, y, txt, ha="right", va="center", color=GRAYM, fontsize=10, family="serif")

ax.text(-2.3, 3.9, "each weighing:\n×3 eliminated,\n$\\log_2 3$ bits", ha="left", va="center",
        color=WARM, fontsize=10, family="serif")
ax.text(13.5, 6.35, "Counterfeit coin: a balance has THREE outcomes (L / R / balanced)",
        ha="center", color=WHITE, fontsize=15, family="serif")
ax.text(13.5, -0.25,
        r"$\log_2 27 = 3\log_2 3$  —  three weighings, no rounding "
        r"(equal-outcome = maximum entropy per weighing)",
        ha="center", color=WARM2, fontsize=12, family="serif")

base = ("C:/Users/itama/Documents/My Projects/Phd/Notes_phd/z-Assets/"
        "ITFNS-animations/exercises/counterfeit-coin-ternary-tree.svg")
import os
os.makedirs(os.path.dirname(base), exist_ok=True)
fig.savefig(base, facecolor=BG, format="svg")
fig.savefig("cointree_preview.png", facecolor=BG, dpi=105)
print("saved")
