"""Entry #6 — Phase-space mixing toward equilibrium via the baker's map (ITFNS §5.3).

Rendered as an evolving density image (efficient) rather than thousands of dots.
"""

from manim import *
import numpy as np
from itfns import WARM, HOT, COOL, GRAYM, WARM2

SIDE = 4.7
CXY = np.array([-3.0, 0.15])   # box center
RES = 300                      # image pixels per side
N_ITER = 7
NPTS = 120_000


def discrete_baker(p):
    x, y = p[:, 0], p[:, 1]
    left = x < 0.5
    nx = np.where(left, 2 * x, 2 * x - 1)
    ny = np.where(left, y / 2, y / 2 + 0.5)
    return np.column_stack([nx, ny])


def continuous_step(p, s):
    """One baker step, fraction s in [0,1]: stretch (s<.5) then fold (s>.5)."""
    x, y = p[:, 0].copy(), p[:, 1].copy()
    if s <= 0.5:
        u = s / 0.5
        x = x * (1 + u)
        y = y * (1 - 0.5 * u)
    else:
        x = x * 2.0
        y = y * 0.5
        v = (s - 0.5) / 0.5
        right = x > 1.0
        x[right] = x[right] - v * 1.0
        y[right] = y[right] + v * 0.5
    return np.column_stack([x, y])


# warm colormap on dark: (r,g,b) ramps from black -> deep orange -> bright
def colorize(dens):
    d = np.clip(dens, 0, 1) ** 0.55
    r = np.clip(1.0 * d * 1.6, 0, 1)
    g = np.clip(0.62 * d * 1.5, 0, 1)
    b = np.clip(0.29 * d * 1.2, 0, 1)
    rgb = (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)
    return rgb


class PhaseSpaceMixing(Scene):
    def construct(self):
        rng = np.random.default_rng(2)
        base = rng.uniform([0.02, 0.02], [0.30, 0.30], (NPTS, 2))
        # positions at each integer iteration
        iter_pts = [base]
        for _ in range(N_ITER):
            iter_pts.append(discrete_baker(iter_pts[-1]))

        prog = ValueTracker(0.0)

        GN = 20
        Smax = np.log(GN * GN)

        def density_and_entropy(pr):
            it = min(int(np.floor(pr)), N_ITER - 1)
            s = pr - it
            if pr >= N_ITER:
                it, s = N_ITER - 1, 1.0
            p = continuous_step(iter_pts[it], s) if s > 0 else iter_pts[it]
            # image histogram (note: image rows = y flipped)
            H, _, _ = np.histogram2d(p[:, 1], p[:, 0], bins=RES,
                                     range=[[0, 1], [0, 1]])
            H = H[::-1]  # flip y so up = +y
            dens = H / (NPTS / (RES * RES)) / 6.0
            # coarse entropy
            Hc, _, _ = np.histogram2d(p[:, 0], p[:, 1], bins=GN, range=[[0, 1], [0, 1]])
            occ = Hc[Hc > 0] / Hc.sum()
            S = -(occ * np.log(occ)).sum() / Smax
            return dens, S

        ent_tr = ValueTracker(0.0)

        d0, s0 = density_and_entropy(0.0)
        ent_tr.set_value(s0)
        img = ImageMobject(colorize(d0))
        img.height = SIDE
        img.move_to([*CXY, 0])

        def upd(m):
            dens, S = density_and_entropy(prog.get_value())
            newimg = ImageMobject(colorize(dens))
            newimg.height = SIDE
            newimg.move_to([*CXY, 0])
            m.pixel_array = newimg.pixel_array
            ent_tr.set_value(S)
        img.add_updater(upd)

        box = Square(SIDE, color=GRAYM, stroke_width=2.5).move_to([*CXY, 0])
        box_lab = Text("constant-energy surface (accessible region)",
                       font_size=19, color=GRAYM).next_to(box, UP, buff=0.2)

        # ---------- conserved-area readout ----------
        area_read = MathTex(r"\text{measure}=\text{const}\ (\det\hat W=1)",
                            font_size=27, color=COOL).move_to([3.5, 2.4, 0])
        area_box = SurroundingRectangle(area_read, color=COOL, buff=0.14, corner_radius=0.06)
        area_cap = Text("area never changes — only stirred finer",
                        font_size=17, color=COOL).next_to(area_box, DOWN, buff=0.1)

        # ---------- coarse entropy bar ----------
        BX, BY0, BH = 3.5, -2.7, 3.1
        bar = always_redraw(lambda: Rectangle(
            width=0.55, height=max(BH * ent_tr.get_value(), 1e-3),
            fill_color=WARM2, fill_opacity=0.9, stroke_width=0,
        ).move_to([BX - 1.0, BY0 + BH * ent_tr.get_value() / 2, 0]))
        bar_axis = Line([BX - 1.35, BY0, 0], [BX - 1.35, BY0 + BH, 0], color=GRAYM, stroke_width=2)
        ceil_line = DashedLine([BX - 1.4, BY0 + BH, 0], [BX - 0.55, BY0 + BH, 0],
                               color=GRAYM, dash_length=0.07)
        ceil_lab = Text("microcanonical ceiling", font_size=17, color=GRAYM).next_to(
            ceil_line, RIGHT, buff=0.12)
        ent_lab = Text("coarse-grained entropy", font_size=17, color=WARM2).move_to(
            [BX - 0.4, BY0 - 0.35, 0])

        self.add(img, bar)
        cap = Text("a compact dye patch under the baker's map: stretch, cut, stack",
                   font_size=22).to_edge(DOWN, buff=0.18)
        self.play(FadeIn(VGroup(box, box_lab, area_read, area_box, area_cap,
                                bar_axis, ceil_line, ceil_lab, ent_lab)),
                  FadeIn(cap), run_time=1.0)
        self.wait(0.7)
        self.play(FadeOut(cap), run_time=0.3)
        self.play(prog.animate.set_value(N_ITER), run_time=11.0, rate_func=linear)
        cap2 = Text("below any fixed resolution the region looks uniformly gray — the microcanonical state",
                    font_size=20, color=WARM).to_edge(DOWN, buff=0.18)
        self.play(FadeIn(cap2), run_time=0.5)
        self.wait(1.6)
        cap3 = Text("the fine-grained measure was never destroyed — only stirred below what we can see",
                    font_size=20, color=COOL).to_edge(DOWN, buff=0.18)
        self.play(FadeOut(cap2), FadeIn(cap3), run_time=0.5)
        self.wait(1.4)
        img.clear_updaters()
