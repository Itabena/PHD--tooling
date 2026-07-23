"""Entry #12 — Convexity overshoot: <e^A> = cosh a > 1 (ITFNS §5.3).

Geometry animates continuously; numeric readouts update only at discrete
checkpoints (avoids per-frame LaTeX recompilation).
"""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, GRAYM


class ConvexityOvershootCosh(Scene):
    def construct(self):
        a_tr = ValueTracker(0.3)

        ax = Axes(x_range=[-2.6, 2.6, 1], y_range=[0, 6, 2], x_length=7.0, y_length=5.0,
                  axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                               "font_size": 20}).move_to([-2.7, -0.1, 0])
        ax_lab = MathTex(r"y=e^x", font_size=30, color=WARM).move_to(ax.c2p(1.7, 5.2))
        curve = ax.plot(np.exp, x_range=[-2.6, 1.9], color=WARM, stroke_width=3)

        def a():
            return a_tr.get_value()

        p_plus = always_redraw(lambda: Dot(ax.c2p(a(), np.exp(a())), color=WARM2, radius=0.06))
        p_minus = always_redraw(lambda: Dot(ax.c2p(-a(), np.exp(-a())), color=COOL, radius=0.06))
        chord = always_redraw(lambda: Line(
            ax.c2p(-a(), np.exp(-a())), ax.c2p(a(), np.exp(a())), color=GRAYM, stroke_width=2.5))
        mid = always_redraw(lambda: Dot(ax.c2p(0, np.cosh(a())), color=HOT, radius=0.07))
        curve_pt = Dot(ax.c2p(0, 1), color=WHITE, radius=0.06)
        gap = always_redraw(lambda: Line(ax.c2p(0, 1), ax.c2p(0, np.cosh(a())), color=HOT, stroke_width=6))
        drop_p = always_redraw(lambda: DashedLine(
            ax.c2p(a(), np.exp(a())), ax.c2p(0, np.exp(a())), color=WARM2, stroke_width=1.5, dash_length=0.06))
        drop_m = always_redraw(lambda: DashedLine(
            ax.c2p(-a(), np.exp(-a())), ax.c2p(0, np.exp(-a())), color=COOL, stroke_width=1.5, dash_length=0.06))

        rx = 3.6
        one_read = MathTex(r"e^{\langle x\rangle}=e^0=1", font_size=28, color=WHITE).move_to([rx, 0.9, 0])
        n_comp = 5
        BX, BY0, BH = 3.2, -2.9, 2.1
        comp_bar = always_redraw(lambda: Rectangle(
            width=0.7, height=max(BH * min(np.log(np.cosh(a()) ** n_comp + 1) / np.log(np.cosh(1.9) ** n_comp + 1), 1.0), 1e-3),
            fill_color=WARM, fill_opacity=0.85, stroke_width=0).move_to(
            [BX, BY0 + BH * min(np.log(np.cosh(a()) ** n_comp + 1) / np.log(np.cosh(1.9) ** n_comp + 1), 1.0) / 2, 0]))
        comp_title = MathTex(r"(\cosh a)^{5}\ \text{grows; mean exponent still } 0",
                             font_size=22, color=GRAYM).move_to([BX + 0.3, BY0 + BH + 0.4, 0])

        def readout(av):
            g = VGroup(
                MathTex(r"a=" + f"{av:.2f}", font_size=28, color=WARM2),
                MathTex(r"\cosh a=" + f"{np.cosh(av):.2f}", font_size=28, color=HOT),
                MathTex(r"\text{Jensen gap}=" + f"{np.cosh(av)-1:.2f}", font_size=26, color=HOT),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([rx, 2.4, 0])
            return g

        ro = readout(0.3)
        cosh_box = always_redraw(lambda: SurroundingRectangle(ro[1], color=HOT, buff=0.1, corner_radius=0.05))

        self.play(Create(ax), Create(curve), FadeIn(VGroup(ax_lab, one_read, curve_pt)), run_time=1.0)
        self.add(p_plus, p_minus, chord, mid, gap, drop_p, drop_m)
        self.play(FadeIn(ro), FadeIn(cosh_box), run_time=0.5)
        cap = Text("e^{+a} overshoots 1 by more than e^{−a} undershoots it — that asymmetry is convexity",
                   font_size=21).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(cap), run_time=0.5)

        # sweep a up in checkpoints; update the numeric readout at each
        cap2 = Text("sweep a up: the shaded Jensen gap cosh a − 1 grows, so the average of e^A exceeds 1",
                    font_size=21, color=HOT).to_edge(DOWN, buff=0.2)
        checkpoints = [0.7, 1.1, 1.5, 1.9]
        for i, av in enumerate(checkpoints):
            new_ro = readout(av)
            self.play(a_tr.animate.set_value(av),
                      Transform(ro, new_ro), run_time=1.1, rate_func=linear)
            if i == 0:
                self.play(FadeOut(cap), FadeIn(cap2), run_time=0.3)
        self.play(FadeIn(VGroup(comp_bar, comp_title)), run_time=0.6)
        self.wait(1.2)

        # come back down
        self.play(a_tr.animate.set_value(0.9), Transform(ro, readout(0.9)),
                  run_time=2.0, rate_func=smooth)
        cap3 = Text("the exponent averages to zero, yet its exponential grows on average — Jensen's inequality",
                    font_size=21, color=WARM).to_edge(DOWN, buff=0.2)
        self.play(FadeOut(cap2), FadeIn(cap3), run_time=0.5)
        self.wait(1.6)
