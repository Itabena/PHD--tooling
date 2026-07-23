"""Entry #10 — Diffusion as the continuum limit of a lattice walk (ITFNS §4.2)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, GRAYM

NW = 4000       # walkers
STEPS = 60
KAPPA = 0.5     # so that a^2/(2 tau)=kappa; here var grows as 2*kappa*t


def simulate():
    rng = np.random.default_rng(7)
    steps = rng.choice([-1, 1], size=(NW, STEPS))
    pos = np.cumsum(steps, axis=1)
    pos = np.concatenate([np.zeros((NW, 1), int), pos], axis=1)
    return pos


POS = simulate()
XMAX = 22


class DiffusionLatticeWalkContinuumLimit(Scene):
    def construct(self):
        t_tr = ValueTracker(0.0)

        axT = Axes(x_range=[-XMAX, XMAX, 5], y_range=[0, 0.32, 0.1], x_length=11.5, y_length=2.5,
                   axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                                "font_size": 18}).move_to([0, 1.7, 0])
        axT_lab = Text("ensemble of ± a walkers — histogram of positions", font_size=20,
                       color=WARM).move_to([0, 3.55, 0])
        axB = Axes(x_range=[-XMAX, XMAX, 5], y_range=[0, 0.32, 0.1], x_length=11.5, y_length=2.5,
                   axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                                "font_size": 18}).move_to([0, -1.7, 0])
        axB_lab = MathTex(r"\rho(x,t)=(4\pi\kappa t)^{-1/2}e^{-x^2/4\kappa t}", font_size=24,
                          color=COOL).next_to(axB, UP, buff=0.1)

        bins = np.arange(-XMAX - 0.5, XMAX + 1.5, 2)  # even lattice sites

        def hist_bars():
            step = int(min(t_tr.get_value(), STEPS))
            p = POS[:, step]
            counts, edges = np.histogram(p, bins=bins, density=True)
            g = VGroup()
            for c, e0, e1 in zip(counts, edges[:-1], edges[1:]):
                if c <= 0:
                    continue
                xc = (e0 + e1) / 2
                h = axT.c2p(0, c)[1] - axT.c2p(0, 0)[1]
                g.add(Rectangle(width=axT.c2p(1.6, 0)[0] - axT.c2p(0, 0)[0], height=max(h, 1e-3),
                                fill_color=WARM, fill_opacity=0.8, stroke_width=0).move_to(
                    [axT.c2p(xc, 0)[0], axT.c2p(0, 0)[1] + h / 2, 0]))
            return g
        bars = always_redraw(hist_bars)

        def gaussian():
            t = max(t_tr.get_value(), 0.4)
            var = 2 * KAPPA * t * 2  # match lattice var = t (a=1); tune visual spread
            var = max(t_tr.get_value(), 0.4)  # lattice variance = number of steps
            return axB.plot(lambda x: np.exp(-x ** 2 / (2 * var)) / np.sqrt(2 * np.pi * var),
                            x_range=[-XMAX, XMAX], color=COOL, stroke_width=3)
        gauss = always_redraw(gaussian)
        gfill = always_redraw(lambda: axB.get_area(gaussian(), x_range=[-XMAX, XMAX],
                                                   color=COOL, opacity=0.2))

        # fixed mean line + widening bracket
        mean_line_T = DashedLine(axT.c2p(0, 0), axT.c2p(0, 0.30), color=WARM2, stroke_width=2)
        mean_lab = MathTex(r"\langle x\rangle = 0\ \text{(peak never drifts)}", font_size=22,
                           color=WARM2).move_to([-3.5, 3.05, 0])

        def width_bracket():
            t = max(t_tr.get_value(), 0.4)
            sd = np.sqrt(t)
            y = axB.c2p(0, 0)[1] - 0.35
            return VGroup(
                Line([axB.c2p(-sd, 0)[0], y, 0], [axB.c2p(sd, 0)[0], y, 0], color=HOT, stroke_width=3),
                Line([axB.c2p(-sd, 0)[0], y - 0.08, 0], [axB.c2p(-sd, 0)[0], y + 0.08, 0], color=HOT),
                Line([axB.c2p(sd, 0)[0], y - 0.08, 0], [axB.c2p(sd, 0)[0], y + 0.08, 0], color=HOT),
            )
        wbr = always_redraw(width_bracket)
        wbr_lab = always_redraw(lambda: MathTex(
            r"\sqrt{\langle x^2\rangle}=\sqrt{2\kappa t}\propto\sqrt t\ =\ " +
            f"{np.sqrt(max(t_tr.get_value(),0.4)):.1f}",
            font_size=22, color=HOT).move_to([0, -3.4, 0]))

        clock = always_redraw(lambda: MathTex(
            r"t=" + f"{int(min(t_tr.get_value(),STEPS))}\\,\\tau", font_size=24, color=GRAYM).move_to([4.2, 3.05, 0]))

        self.play(Create(axT), Create(axB),
                  FadeIn(VGroup(axT_lab, axB_lab, mean_line_T, mean_lab, clock)), run_time=1.0)
        self.add(bars, gfill, gauss, wbr, wbr_lab)
        cap = Text("start all walkers at the origin; each hops ± a per step τ", font_size=22).to_edge(DOWN, buff=0.12)
        self.play(FadeIn(cap), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(cap), run_time=0.3)
        self.play(t_tr.animate.set_value(STEPS), run_time=9.0, rate_func=linear)
        cap2 = Text("peak stationary, spread ∝ √t — the corrected diffusive scaling (not ⟨x⟩ ∝ √t)",
                    font_size=22, color=HOT).to_edge(DOWN, buff=0.12)
        self.play(FadeIn(cap2), run_time=0.5)
        self.wait(1.8)
