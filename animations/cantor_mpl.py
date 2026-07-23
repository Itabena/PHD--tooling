"""Entry #16 — Cantor box-counting, matplotlib -> crisp SVG + PNG preview (ITFNS §5.4)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

WARM, WARM2, GRAYM, WHITE, BG = "#FF9E4A", "#FFC94A", "#B9B9B9", "#ECECEC", "#12141a"
ROWS = 5


def seg_intervals(n):
    segs = [(0.0, 1.0)]
    for _ in range(n):
        nxt = []
        for a, b in segs:
            t = (b - a) / 3
            nxt += [(a, a + t), (b - t, b)]
        segs = nxt
    return segs


fig, ax = plt.subplots(figsize=(9.2, 5.7), dpi=100)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(-0.02, 1.62)
ax.set_ylim(-0.15, ROWS + 1.15)
ax.axis("off")

ax.text(0.5, ROWS + 0.85, "Cantor set: box-counting dimension",
        color=WHITE, fontsize=20, ha="center", family="serif")

bar_h = 0.34
for n in range(ROWS):
    y = ROWS - 1 - n + 0.5
    for a, b in seg_intervals(n):
        ax.add_patch(plt.Rectangle((a, y - bar_h / 2), max(b - a, 0.001), bar_h,
                                    facecolor=WARM, edgecolor="none"))
    ax.text(1.05, y, rf"$N=2^{{{n}}}={2**n},\ \ \epsilon=3^{{-{n}}}=1/{3**n}$",
            color=GRAYM, fontsize=13, va="center", family="serif")

ratio = np.log(2) / np.log(3)
ax.axhline(0.28, xmin=0.0, xmax=0.98, color=GRAYM, lw=0.8, alpha=0.4)
ax.text(0.0, 0.02, rf"$d_f=\dfrac{{\ln N}}{{\ln(1/\epsilon)}}"
        rf"=\dfrac{{n\ln 2}}{{n\ln 3}}=\dfrac{{\ln 2}}{{\ln 3}}\approx {ratio:.2f}$",
        color=WARM2, fontsize=16, va="center", family="serif")
ax.text(0.73, 0.02, "at every scale a fixed fraction stays empty\n"
        "(self-similar holeyness) — between a point and a line",
        color=GRAYM, fontsize=10.5, va="center", family="serif")

plt.tight_layout(pad=0.4)
base = ("C:/Users/itama/Documents/My Projects/Phd/Notes_phd/z-Assets/"
        "ITFNS-animations/ch5-chaos-rg/cantor-set-box-counting.svg")
import os
from components import refuse_if_exists
os.makedirs(os.path.dirname(base), exist_ok=True)
refuse_if_exists(base)
fig.savefig(base, facecolor=BG, format="svg")
fig.savefig("cantor_preview.png", facecolor=BG, dpi=110)
print("saved svg + preview")
