"""Entry #7 — The tiling identity forcing a nonzero drift (ITFNS §5.4, Step 4)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, GRAYM

SIGMA_MAX = 1.25   # final std dev


class TilingIdentityDrift(Scene):
    def construct(self):
        sig = ValueTracker(0.02)     # current std dev of C-density
        mu_on = ValueTracker(0.0)    # 0 = no drift (Act 1), 1 = drift (Act 2)

        # ---------- Left panel: density of contraction values C ----------
        axL = Axes(x_range=[-3.5, 4.5, 1], y_range=[0, 1.0, 0.5],
                   x_length=6.0, y_length=3.4,
                   axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                                "font_size": 20}).move_to([-3.4, 0.3, 0])
        axL_x = MathTex(r"C", font_size=26, color=GRAYM).next_to(axL.x_axis, RIGHT, buff=0.1)
        titleL = MathTex(r"\text{density of contraction values } C_k",
                         font_size=30).next_to(axL, UP, buff=0.25)

        def mu_val():
            return mu_on.get_value() * sig.get_value() ** 2 / 2

        def gauss():
            s = sig.get_value()
            mu = mu_val()
            return axL.plot(lambda x: np.exp(-(x - mu) ** 2 / (2 * s ** 2)),
                            x_range=[-3.5, 4.5], color=WARM, stroke_width=3)
        curveL = always_redraw(gauss)
        fillL = always_redraw(lambda: axL.get_area(gauss(), x_range=[-3.5, 4.5],
                                                   color=WARM, opacity=0.25))
        mean_line = always_redraw(lambda: DashedLine(
            axL.c2p(mu_val(), 0), axL.c2p(mu_val(), 1.05),
            color=WARM2, stroke_width=2.5))
        mean_lab = always_redraw(lambda: MathTex(
            r"\mu=" + f"{mu_val():.2f}", font_size=26, color=WARM2).move_to([-1.6, -1.9, 0]))
        sig_lab = always_redraw(lambda: MathTex(
            r"\sigma^2=\Delta t/\tau=" + f"{sig.get_value()**2:.2f}",
            font_size=26, color=WARM).move_to([-4.6, -1.9, 0]))

        # ---------- Right panel: the pinned sum ----------
        axR = Axes(x_range=[0, 1, 1], y_range=[0.8, 2.2, 0.2],
                   x_length=4.2, y_length=3.4,
                   axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False},
                   y_axis_config={"font_size": 20, "include_numbers": True}).move_to([3.6, 0.3, 0])
        target = DashedLine(axR.c2p(0, 1), axR.c2p(1, 1), color=COOL, stroke_width=3)
        target_lab = MathTex(r"\tfrac1M\sum_k e^{-C_k}=1\ \text{(exact)}",
                             font_size=24, color=COOL).next_to(axR, UP, buff=0.2)

        def sum_val():
            # <e^-C> for Gaussian C ~ N(mu, sig^2) = exp(-mu + sig^2/2)
            s = sig.get_value()
            mu = mu_val()
            return np.exp(-mu + s ** 2 / 2)

        dot = always_redraw(lambda: Dot(
            axR.c2p(0.5, np.clip(sum_val(), 0.8, 2.2)),
            color=HOT if mu_on.get_value() < 0.5 else COOL, radius=0.1))
        dot_val = always_redraw(lambda: MathTex(
            f"{sum_val():.2f}", font_size=26,
            color=HOT if mu_on.get_value() < 0.5 else COOL).next_to(
            axR.c2p(0.5, np.clip(sum_val(), 0.8, 2.2)), RIGHT, buff=0.2))
        gap_shade = always_redraw(lambda: (
            axR.get_area(
                axR.plot(lambda x: np.clip(sum_val(), 0.8, 2.2), x_range=[0.35, 0.65]),
                x_range=[0.35, 0.65],
                bounded_graph=axR.plot(lambda x: 1.0, x_range=[0.35, 0.65]),
                color=HOT, opacity=0.2)
            if mu_on.get_value() < 0.5 and sum_val() > 1.02 else VMobject()))

        self.play(
            Create(axL), Create(axR), FadeIn(VGroup(axL_x, titleL, target, target_lab)),
            run_time=1.0)
        self.add(fillL, curveL, mean_line, mean_lab, sig_lab, gap_shade, dot, dot_val)

        # ---------- Act 1: density centered at 0, widening — sum runs away ----------
        cap1 = Text("Act 1 — hold the mean at 0 as the density widens", font_size=22).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(cap1), run_time=0.5)
        self.play(sig.animate.set_value(SIGMA_MAX), run_time=4.5, rate_func=smooth)
        cap1b = Text("the pinned sum climbs off 1 toward e^{Δt/2τ} — the constraint is broken",
                     font_size=21, color=HOT).to_edge(DOWN, buff=0.2)
        self.play(FadeOut(cap1), FadeIn(cap1b), run_time=0.5)
        self.wait(1.8)

        # ---------- Act 2: replay with drift — sum locks on 1 ----------
        self.play(sig.animate.set_value(0.02), run_time=1.2, rate_func=smooth)
        cap2 = Text("Act 2 — now let the whole density drift right at rate μ = σ²/2 as it widens",
                    font_size=21, color=COOL).to_edge(DOWN, buff=0.2)
        self.play(FadeOut(cap1b), FadeIn(cap2), mu_on.animate.set_value(1.0), run_time=0.8)
        self.play(sig.animate.set_value(SIGMA_MAX), run_time=4.5, rate_func=smooth)
        cap2b = Text("the sum locks exactly on 1 — conservation forces net contraction μ = σ²/2 > 0",
                     font_size=21, color=COOL).to_edge(DOWN, buff=0.2)
        self.play(FadeOut(cap2), FadeIn(cap2b), run_time=0.5)
        self.wait(2.0)
