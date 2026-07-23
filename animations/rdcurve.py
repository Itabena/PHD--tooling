"""Entry #28 — Rate-distortion curve for the binary source, static SVG (ITFNS Ex 3.2)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

WARM, WARM2, HOT, COOL, COOL2, GRAYM, WHITE, BG = (
    "#FF9E4A", "#FFC94A", "#FF5C5C", "#5CA8FF", "#7BE0D4", "#B9B9B9", "#ECECEC", "#12141a")

P = 0.5 * 0 + 0.35     # source bias p


def Sb(x):
    x = np.clip(x, 1e-9, 1 - 1e-9)
    return -x * np.log2(x) - (1 - x) * np.log2(1 - x)


fig, ax = plt.subplots(figsize=(9.6, 6.2), dpi=100)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

D = np.linspace(0, P, 200)
R = Sb(P) - Sb(D)
ax.plot(D, R, color=WARM, lw=3, zorder=5)
ax.plot([P, 0.5], [0, 0], color=WARM, lw=3, zorder=5)   # flat R=0 for D>p

# endpoints & kink
ax.plot(0, Sb(P), "o", color=WARM2, ms=9, zorder=6)
ax.annotate(rf"$(0,\ S_b(p))={Sb(P):.2f}$ bits", (0, Sb(P)), xytext=(0.06, Sb(P) - 0.02),
            color=WARM2, fontsize=12, family="serif")
ax.plot(P, 0, "o", color=HOT, ms=9, zorder=6)
ax.annotate("kink at D = p:\nbeyond this, send nothing\n(guess the majority symbol)",
            (P, 0), xytext=(P + 0.02, 0.28), color=HOT, fontsize=11, family="serif",
            arrowprops=dict(arrowstyle="->", color=HOT, lw=1.2))

# tangent at a chosen D0 with slope -beta
D0 = 0.15
R0 = Sb(P) - Sb(D0)
beta = np.log2((1 - D0) / D0)     # slope magnitude dR/dD = -beta (bits)
tx = np.linspace(D0 - 0.11, D0 + 0.13, 2)
ax.plot(tx, R0 - beta * (tx - D0), color=COOL2, lw=1.6, ls="--", zorder=4)
ax.plot(D0, R0, "o", color=COOL, ms=7, zorder=6)
ax.annotate(rf"slope $=-\beta=\dfrac{{dR}}{{dD}}$,  $\beta=\ln\frac{{1-D}}{{D}}$",
            (D0, R0), xytext=(D0 + 0.11, R0 + 0.35), color=COOL2, fontsize=12, family="serif",
            arrowprops=dict(arrowstyle="->", color=COOL2, lw=1.1))

ax.set_xlim(-0.02, 0.52); ax.set_ylim(-0.06, Sb(P) + 0.35)
ax.set_xlabel("distortion  D", color=WHITE, fontsize=13, family="serif")
ax.set_ylabel("rate  R(D)  [bits]", color=WHITE, fontsize=13, family="serif")
ax.set_title(rf"Rate-distortion of a binary source (p = {P}):  "
             rf"$R(D)=S_b(p)-S_b(D)$", color=WHITE, fontsize=15, family="serif", pad=14)
ax.tick_params(colors=GRAYM)
for sp in ax.spines.values():
    sp.set_color(GRAYM)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.grid(True, color=GRAYM, alpha=0.15)

base = ("C:/Users/itama/Documents/My Projects/Phd/Notes_phd/z-Assets/"
        "ITFNS-animations/exercises/rate-distortion-binary-source-curve.svg")
import os
from components import refuse_if_exists
os.makedirs(os.path.dirname(base), exist_ok=True)
refuse_if_exists(base)
fig.savefig(base, facecolor=BG, format="svg", bbox_inches="tight")
fig.savefig("rd_preview.png", facecolor=BG, dpi=105, bbox_inches="tight")
print("saved; Sb(p)=", round(Sb(P), 3), "beta=", round(beta, 3))
