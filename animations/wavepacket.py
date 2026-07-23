"""Entry #23 — Minimum-uncertainty wave packet as a Fourier squeeze (ITFNS §6.1)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, COOL2, GRAYM

HBAR = 1.0


class MinimumUncertaintyWavepacketSqueeze(Scene):
    def construct(self):
        a_tr = ValueTracker(0.4)     # squeeze parameter

        def sx():
            return 1 / np.sqrt(4 * a_tr.get_value())

        def sp():
            return HBAR * np.sqrt(a_tr.get_value())

        axX = Axes(x_range=[-4, 4, 1], y_range=[0, 1.1, 0.5], x_length=6.0, y_length=2.4,
                   axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                                "font_size": 18}).move_to([-3.2, 1.7, 0])
        axX_lab = MathTex(r"|\psi(x)|^2", font_size=26, color=WARM).next_to(axX, UP, buff=0.1)
        psiX = always_redraw(lambda: axX.plot(
            lambda x: np.exp(-x ** 2 / (2 * sx() ** 2)) / (sx() * np.sqrt(2 * np.pi)) * (sx() * np.sqrt(2 * np.pi)),
            x_range=[-4, 4], color=WARM, stroke_width=3))
        # normalize height to 1 for display (use gaussian shape peak=1)
        psiX = always_redraw(lambda: axX.plot(
            lambda x: np.exp(-x ** 2 / (2 * sx() ** 2)), x_range=[-4, 4], color=WARM, stroke_width=3))
        fillX = always_redraw(lambda: axX.get_area(
            axX.plot(lambda x: np.exp(-x ** 2 / (2 * sx() ** 2)), x_range=[-4, 4]),
            x_range=[-4, 4], color=WARM, opacity=0.2))
        sx_brace = always_redraw(lambda: MathTex(
            r"\sigma_x=1/\sqrt{4a}", font_size=22, color=WARM).move_to([-3.2, 0.35, 0]))

        axP = Axes(x_range=[-4, 4, 1], y_range=[0, 1.1, 0.5], x_length=6.0, y_length=2.4,
                   axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                                "font_size": 18}).move_to([-3.2, -1.9, 0])
        axP_lab = MathTex(r"|\psi(p)|^2", font_size=26, color=COOL).next_to(axP, UP, buff=0.1)
        psiP = always_redraw(lambda: axP.plot(
            lambda p: np.exp(-p ** 2 / (2 * sp() ** 2)), x_range=[-4, 4], color=COOL, stroke_width=3))
        fillP = always_redraw(lambda: axP.get_area(
            axP.plot(lambda p: np.exp(-p ** 2 / (2 * sp() ** 2)), x_range=[-4, 4]),
            x_range=[-4, 4], color=COOL, opacity=0.2))
        sp_brace = always_redraw(lambda: MathTex(
            r"\sigma_p=\hbar\sqrt{a}", font_size=22, color=COOL).move_to([-3.2, -3.3, 0]))

        # ---------- boxed constant-value readout + area rectangle ----------
        prod_read = MathTex(r"\sigma_x\,\sigma_p=\hbar/2", font_size=30, color=WARM2).move_to([3.7, 2.6, 0])
        prod_box = SurroundingRectangle(prod_read, color=WARM2, buff=0.15, corner_radius=0.06)
        prod_cap = Text("conserved phase-space area", font_size=18, color=WARM2).next_to(prod_box, DOWN, buff=0.1)

        # the product drawn as a fixed-area rectangle
        rect_c = np.array([3.7, -0.5, 0])
        AREA = 1.4     # visual area = sigma_x*sigma_p scaled

        def rect():
            w = sx() * 1.15
            h = sp() * 1.15
            return Rectangle(width=w, height=h, fill_color=WARM2, fill_opacity=0.25,
                             stroke_color=WARM2, stroke_width=2.5).move_to(rect_c)
        rect_m = always_redraw(rect)
        rect_w = always_redraw(lambda: MathTex(r"\sigma_x", font_size=20, color=WARM).next_to(
            rect_m, DOWN, buff=0.08))
        rect_h = always_redraw(lambda: MathTex(r"\sigma_p", font_size=20, color=COOL).next_to(
            rect_m, RIGHT, buff=0.08))

        self.play(Create(axX), Create(axP), FadeIn(VGroup(axX_lab, axP_lab, prod_read, prod_box,
                  prod_cap)), run_time=1.0)
        self.add(fillX, psiX, sx_brace, fillP, psiP, sp_brace, rect_m, rect_w, rect_h)
        cap = Text("squeeze the packet narrow in x — its Fourier partner fans wide in p",
                   font_size=21).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(cap), run_time=0.5)
        self.play(a_tr.animate.set_value(2.5), run_time=4.0, rate_func=smooth)
        cap2 = Text("the product σₓσₚ = ħ/2 never moves — the rectangle keeps a constant area, just changes shape",
                    font_size=20, color=WARM2).to_edge(DOWN, buff=0.2)
        self.play(FadeOut(cap), FadeIn(cap2), run_time=0.5)
        self.play(a_tr.animate.set_value(0.3), run_time=3.0, rate_func=smooth)
        self.wait(0.6)

        # contrast: non-Gaussian pushes area above the floor
        cap3 = Text("a non-Gaussian packet only ever pushes the area ABOVE ħ/2 — the floor is never beaten",
                    font_size=20, color=HOT).to_edge(DOWN, buff=0.2)
        bad_rect = Rectangle(width=sx() * 1.15 * 1.5, height=sp() * 1.15 * 1.5,
                             fill_color=HOT, fill_opacity=0.15, stroke_color=HOT, stroke_width=2).move_to(rect_c)
        self.play(FadeOut(cap2), FadeIn(cap3), FadeIn(bad_rect), run_time=0.6)
        self.wait(1.6)
