"""Entry #24 — Inverted-potential packet: drift and spread in lockstep (ITFNS Ex 4.5)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, COOL2, GRAYM

ALPHA = 0.45
X0 = 0.6
PROBE_X = 3.2


class InvertedPotentialPacketDriftSpread(Scene):
    def construct(self):
        t_tr = ValueTracker(0.0)

        ax = Axes(x_range=[-1, 6, 1], y_range=[0, 1.15, 0.5], x_length=8.2, y_length=3.2,
                  axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                               "font_size": 18}).move_to([-1.2, 1.2, 0])
        # faint inverted parabola background
        pot = ax.plot(lambda x: 1.05 - 0.06 * (x - X0) ** 2, x_range=[-1, 4.6],
                      color=GRAYM, stroke_width=1.5, stroke_opacity=0.35)
        pot_lab = MathTex(r"V=-\tfrac12\alpha x^2", font_size=22, color=GRAYM).move_to(ax.c2p(4.6, 0.95))

        def mean_t():
            return X0 * np.exp(ALPHA * t_tr.get_value())

        def sig_t():
            return np.sqrt((np.exp(2 * ALPHA * t_tr.get_value()) - 1) / (2 * ALPHA) + 0.04)

        def packet():
            m, s = mean_t(), sig_t()
            return ax.plot(lambda x: np.exp(-(x - m) ** 2 / (2 * s ** 2)),
                           x_range=[-1, 6], color=WARM, stroke_width=3)
        pkt = always_redraw(packet)
        pkt_fill = always_redraw(lambda: ax.get_area(packet(), x_range=[-1, 6], color=WARM, opacity=0.2))
        peak_dot = always_redraw(lambda: Dot(ax.c2p(mean_t(), 1.0), color=WARM2, radius=0.06))
        peak_trace = MathTex(r"\bar x = x_0 e^{\alpha t}", font_size=22, color=WARM2).move_to(ax.c2p(2.0, 1.25) + UP * 0.15)

        probe = DashedLine(ax.c2p(PROBE_X, 0), ax.c2p(PROBE_X, 1.1), color=COOL2, stroke_width=2)
        probe_lab = MathTex(r"\text{probe at fixed } x", font_size=18, color=COOL2).next_to(
            ax.c2p(PROBE_X, 1.1), UP, buff=0.05)

        # ---------- log-rho plot at the probe ----------
        axL = Axes(x_range=[0, 6, 2], y_range=[-6, 0, 2], x_length=6.5, y_length=2.6,
                   axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                                "font_size": 18}).move_to([-1.2, -2.4, 0])
        axL_x = Text("t", font_size=18, color=GRAYM).next_to(axL.x_axis, RIGHT, buff=0.1)
        axL_y = MathTex(r"\ln\rho(x_{\rm probe},t)", font_size=20, color=COOL).next_to(axL.y_axis, UP, buff=0.05)

        def logrho(t):
            m = X0 * np.exp(ALPHA * t)
            s = np.sqrt((np.exp(2 * ALPHA * t) - 1) / (2 * ALPHA) + 0.04)
            val = -(PROBE_X - m) ** 2 / (2 * s ** 2) - np.log(s)
            return val
        # reference slope -alpha line
        ref = axL.plot(lambda t: max(-0.9 - ALPHA * t, -6), x_range=[0, 6], color=GRAYM, stroke_width=1.5)
        ref_dash = DashedVMobject(ref, num_dashes=30)
        slope_lab = MathTex(r"\text{slope} = -\alpha", font_size=20, color=HOT).move_to(axL.c2p(4.5, -3.5))

        traj = VMobject().set_stroke(COOL, 3)

        def upd_traj(m):
            tv = t_tr.get_value()
            if tv < 0.05:
                m.set_points_as_corners([axL.c2p(0, np.clip(logrho(0), -6, 0))] * 2)
                return
            ts = np.linspace(0, tv, 50)
            m.set_points_as_corners([axL.c2p(t, np.clip(logrho(t), -6, 0)) for t in ts])
        traj.add_updater(upd_traj)

        note = MathTex(r"\rho\propto e^{-\alpha t},\ \text{not } e^{-2\alpha t}\ (\text{drift and spread cancel})",
                       font_size=22, color=WARM).to_edge(DOWN, buff=0.25)

        self.play(Create(ax), FadeIn(VGroup(pot, pot_lab, probe, probe_lab, peak_trace)),
                  Create(axL), FadeIn(VGroup(axL_x, axL_y, ref_dash, slope_lab)), run_time=1.2)
        self.add(pkt_fill, pkt, peak_dot, traj)
        cap = Text("a packet starts at x₀ in an inverted potential — the peak races off and the width grows in lockstep",
                   font_size=20).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(cap), run_time=0.5)
        self.play(t_tr.animate.set_value(4.5), run_time=8.0, rate_func=linear)
        self.play(FadeOut(cap), FadeIn(note), run_time=0.5)
        self.wait(2.0)
        traj.clear_updaters()
