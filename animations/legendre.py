"""Entry #9 — Legendre transform as the envelope of tangent lines (ITFNS §1.2)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, GRAYM


def Yf(x):
    return 0.35 * x ** 2 + 0.5      # convex Y(X)


def Ypf(x):
    return 0.7 * x                  # slope P = Y'(X)


class LegendreTransformEnvelope(Scene):
    def construct(self):
        xt = ValueTracker(-2.6)

        axL = Axes(x_range=[-3, 3, 1], y_range=[-2.2, 4, 1], x_length=6.2, y_length=5.2,
                   axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                                "font_size": 20}).move_to([-3.5, -0.2, 0])
        axL_lab = MathTex(r"Y(X)", font_size=28, color=WARM).next_to(axL, UP, buff=0.15)
        curve = axL.plot(Yf, x_range=[-2.9, 2.9], color=WARM, stroke_width=3)

        axR = Axes(x_range=[-2.2, 2.2, 1], y_range=[-3, 1, 1], x_length=4.6, y_length=5.2,
                   axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                                "font_size": 20}).move_to([3.6, -0.2, 0])
        axR_xlab = MathTex(r"P", font_size=26, color=GRAYM).next_to(axR.x_axis, RIGHT, buff=0.1)
        axR_lab = MathTex(r"\psi(P)=Y-PX", font_size=26, color=COOL).next_to(axR, UP, buff=0.15)

        # psi(P) analytic: for Y=aX^2+b, P=2aX -> X=P/2a, psi = b - P^2/4a
        a, b = 0.35, 0.5
        psi = lambda P: b - P ** 2 / (4 * a)
        psi_curve = axR.plot(psi, x_range=[-2.0, 2.0], color=COOL, stroke_width=3)

        # faint traces of tangent lines (envelope)
        trace_group = VGroup()

        def tangent_line():
            x0 = xt.get_value()
            P = Ypf(x0)
            y0 = Yf(x0)
            # line y = y0 + P(x-x0); intercept psi = y0 - P x0
            xa, xb = -2.9, 2.9
            return Line(axL.c2p(xa, y0 + P * (xa - x0)),
                        axL.c2p(xb, y0 + P * (xb - x0)),
                        color=WARM2, stroke_width=2)
        tang = always_redraw(tangent_line)
        touch = always_redraw(lambda: Dot(axL.c2p(xt.get_value(), Yf(xt.get_value())),
                                          color=WHITE, radius=0.07))
        intercept = always_redraw(lambda: Dot(
            axL.c2p(0, Yf(xt.get_value()) - Ypf(xt.get_value()) * xt.get_value()),
            color=COOL, radius=0.07))
        slope_lab = always_redraw(lambda: MathTex(
            r"P=" + f"{Ypf(xt.get_value()):.2f}", font_size=24, color=WARM2).move_to(
            [-5.7, 2.7, 0]))
        psi_lab = always_redraw(lambda: MathTex(
            r"\psi=" + f"{Yf(xt.get_value()) - Ypf(xt.get_value())*xt.get_value():.2f}",
            font_size=24, color=COOL).move_to([-5.7, 2.2, 0]))
        # marker building psi(P) on the right
        psi_dot = always_redraw(lambda: Dot(
            axR.c2p(Ypf(xt.get_value()),
                    Yf(xt.get_value()) - Ypf(xt.get_value()) * xt.get_value()),
            color=COOL, radius=0.08))
        psi_built = VMobject().set_stroke(COOL, 3)
        psi_built.add_updater(lambda m: m.set_points_as_corners([
            axR.c2p(Ypf(x), psi(Ypf(x)))
            for x in np.linspace(-2.6, xt.get_value(), 60)
        ]) if xt.get_value() > -2.55 else m.set_points_as_corners([axR.c2p(-1.82, psi(-1.82))] * 2))

        self.play(Create(axL), Create(axR),
                  FadeIn(VGroup(axL_lab, axR_xlab, axR_lab)), run_time=1.0)
        self.play(Create(curve), run_time=1.0)
        self.add(tang, touch, intercept, slope_lab, psi_lab, psi_dot, psi_built)

        cap1 = Text("a tangent line sweeps the convex curve; each touch has slope P and intercept ψ = Y − PX",
                    font_size=21).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(cap1), run_time=0.5)

        # leave faint tangent traces as we sweep
        def leave_trace():
            x0 = xt.get_value()
            P, y0 = Ypf(x0), Yf(x0)
            ln = Line(axL.c2p(-2.9, y0 + P * (-2.9 - x0)),
                      axL.c2p(2.9, y0 + P * (2.9 - x0)),
                      color=WARM2, stroke_width=1, stroke_opacity=0.18)
            trace_group.add(ln)
            self.add(trace_group)

        for xv in np.linspace(-2.6, 2.6, 9):
            self.play(xt.animate.set_value(xv), run_time=0.7, rate_func=linear)
            leave_trace()
        cap2 = Text("the family of tangents renders the curve as its envelope — same information, re-encoded as ψ(P)",
                    font_size=21, color=COOL).to_edge(DOWN, buff=0.2)
        self.play(FadeOut(cap1), FadeIn(cap2), run_time=0.5)
        self.wait(1.6)

        # coda: flat/inflection region — slope stops being one-to-one
        cap3 = Text("where curvature vanishes, slope→point stops being one-to-one — hence d²Y/dX² ≠ 0",
                    font_size=21, color=HOT).to_edge(DOWN, buff=0.2)
        flat = axL.plot(lambda x: 0.5 + 0.05 * x, x_range=[-2.9, 2.9], color=HOT, stroke_width=2.5)
        flat_lab = MathTex(r"d^2Y/dX^2 \to 0", font_size=24, color=HOT).next_to(
            axL.c2p(1.6, 0.58), UP, buff=0.1)
        self.play(FadeOut(cap2), FadeIn(cap3), Create(flat), FadeIn(flat_lab), run_time=1.0)
        self.wait(1.8)
        psi_built.clear_updaters()
