"""Entry #25 — Quantum scrambling: the OTOC light cone (ITFNS A.13)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, COOL2, GRAYM

NSITE = 17
CENTER = NSITE // 2
NT = 22
V_BUTTERFLY = 0.7     # cone speed (sites per step)
LAMBDA = 0.28


class OtocScramblingLightCone(Scene):
    def construct(self):
        step = ValueTracker(0)

        # ---------- 1D chain grid (space vs time heatmap) ----------
        cellw = 0.40
        cellh = 0.24
        x0 = -NSITE / 2 * cellw
        y0 = -3.0
        grid_c = np.array([-2.3, 0, 0])

        def commutator(i, t):
            # C_ij(t): butterfly cone, saturating inside
            d = abs(i - CENTER)
            front = V_BUTTERFLY * t
            if d > front:
                return 0.0
            # inside cone: exponential rise then saturate
            return min(1.0, np.exp(2 * LAMBDA * (front - d)) - 1) / (np.exp(2 * LAMBDA * front) + 1e-6) * 1.0 \
                if front > 0 else 0.0

        def commutator2(i, t):
            d = abs(i - CENTER)
            front = V_BUTTERFLY * t
            if d > front + 0.5:
                return 0.0
            edge = np.clip(front - d, 0, None)
            return float(np.clip(1 - np.exp(-1.1 * edge), 0, 1))

        def heat():
            s = step.get_value()
            g = VGroup()
            for ti in range(int(min(s, NT)) + 1):
                for i in range(NSITE):
                    val = commutator2(i, ti)
                    if val < 0.02:
                        continue
                    col = interpolate_color(ManimColor(COOL), ManimColor(WARM), val)
                    g.add(Rectangle(width=cellw * 0.92, height=cellh * 0.92,
                                    fill_color=col, fill_opacity=0.85, stroke_width=0).move_to(
                        grid_c + np.array([x0 + i * cellw, y0 + ti * cellh, 0])))
            return g
        heat_m = always_redraw(heat)

        # poke marker at center bottom
        poke = Dot(grid_c + np.array([x0 + CENTER * cellw, y0, 0]), radius=0.08, color=HOT)
        poke_lab = MathTex(r"\hat x_i", font_size=22, color=HOT).next_to(poke, DOWN, buff=0.1)
        space_lab = Text("site  →", font_size=18, color=GRAYM).move_to(grid_c + np.array([0, y0 - 0.55, 0]))
        time_lab = Text("time ↑", font_size=18, color=GRAYM).rotate(PI / 2).move_to(
            grid_c + np.array([x0 - 0.5, y0 + NT * cellh / 2, 0]))
        cone_title = Text("butterfly light cone: C_ij(t) spreading outward", font_size=20, color=WARM).move_to(
            grid_c + np.array([0, y0 + NT * cellh + 0.5, 0]))

        # ---------- side: log C(t) plot ----------
        axL = Axes(x_range=[0, NT, 5], y_range=[-6, 0.5, 2], x_length=4.6, y_length=3.6,
                   axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                                "font_size": 16}).move_to([4.7, 0.9, 0])
        axL_y = MathTex(r"\ln C(t)", font_size=20, color=WARM).next_to(axL.y_axis, UP, buff=0.05)
        axL_x = Text("t", font_size=16, color=GRAYM).next_to(axL.x_axis, RIGHT, buff=0.05)
        growth = axL.plot(lambda t: max(-5.5 + 2 * LAMBDA * t, -6), x_range=[0, 11], color=WARM, stroke_width=3)
        growth_lab = MathTex(r"C=\hbar^2 e^{2\lambda t}", font_size=20, color=WARM).move_to(axL.c2p(7, -1.2))
        ceil = DashedLine(axL.c2p(0, 0), axL.c2p(NT, 0), color=GRAYM, stroke_width=2)
        ceil_lab = MathTex(r"\lambda\le 2\pi T/\hbar", font_size=18, color=GRAYM).next_to(axL.c2p(NT, 0), UP, buff=0.05).shift(LEFT*0.8)

        clock = always_redraw(lambda: Text(
            f"step {int(min(step.get_value(), NT))}", font_size=18, color=GRAYM).move_to([4.7, -2.4, 0]))

        self.play(FadeIn(VGroup(poke, poke_lab, space_lab, time_lab, cone_title)),
                  Create(axL), FadeIn(VGroup(axL_y, axL_x, ceil, ceil_lab, clock)), run_time=1.0)
        self.add(heat_m)
        self.play(Create(growth), FadeIn(growth_lab), run_time=0.5)
        cap = Text("poke one site with an operator; watch the commutator weight fill an outward-opening cone",
                   font_size=20).to_edge(DOWN, buff=0.15)
        self.play(FadeIn(cap), run_time=0.5)
        self.play(step.animate.set_value(NT), run_time=8.0, rate_func=linear)
        cap2 = Text("the cone edge advances ballistically; C(t) = ħ²e^{2λt} grows until the interior saturates — black holes hug the bound",
                    font_size=18, color=WARM).to_edge(DOWN, buff=0.15)
        self.play(FadeOut(cap), FadeIn(cap2), run_time=0.5)
        self.wait(1.8)
