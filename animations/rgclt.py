"""Entry #11 — RG flow to the Gaussian fixed point / CLT (ITFNS §5.5)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, GRAYM

NSAMP = 200_000
N_RG = 6


def base_sample(rng):
    # ugly: skewed bimodal, zero mean unit variance
    a = rng.exponential(1.0, NSAMP) - 1.0
    b = rng.choice([-1.7, 1.7], NSAMP) + rng.normal(0, 0.3, NSAMP)
    x = np.where(rng.random(NSAMP) < 0.5, a, b)
    x = (x - x.mean()) / x.std()
    return x


def rg_step(x):
    rng = np.random.default_rng()
    perm = rng.permutation(len(x))
    x = x[perm]
    half = len(x) // 2
    return (x[:half] + x[half:2 * half]) / np.sqrt(2)


class RGFlowGaussianFixedPointCLT(Scene):
    def construct(self):
        rng = np.random.default_rng(1)
        samples = [base_sample(rng)]
        for _ in range(N_RG):
            samples.append(rg_step(samples[-1]))

        # cumulants (standardized): kappa3 skew, kappa4 excess kurtosis
        def cumulants(x):
            m = x.mean(); s = x.std()
            z = (x - m) / s
            k3 = np.mean(z ** 3)
            k4 = np.mean(z ** 4) - 3
            return abs(k3), abs(k4)

        cums = [cumulants(s) for s in samples]

        step = ValueTracker(0)

        axM = Axes(x_range=[-4, 4, 1], y_range=[0, 0.5, 0.1], x_length=7.5, y_length=4.2,
                   axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                                "font_size": 18}).move_to([-2.6, 0.1, 0])
        gauss = axM.plot(lambda x: np.exp(-x ** 2 / 2) / np.sqrt(2 * np.pi),
                         x_range=[-4, 4], color=COOL, stroke_width=2.5)
        gauss_d = DashedVMobject(gauss, num_dashes=40)
        gauss_lab = MathTex(r"\mathcal{N}(0,1)", font_size=24, color=COOL).next_to(
            axM.c2p(1.7, 0.32), UR, buff=0.05)

        bins = np.linspace(-4, 4, 51)

        def hist():
            it = int(round(step.get_value()))
            counts, edges = np.histogram(samples[it], bins=bins, density=True)
            pts = []
            for c, e0, e1 in zip(counts, edges[:-1], edges[1:]):
                pts.append(axM.c2p((e0 + e1) / 2, c))
            return VMobject().set_points_as_corners(pts).set_stroke(WARM, 3)
        hist_m = always_redraw(hist)
        hist_fill = always_redraw(lambda: VMobject().set_points_as_corners(
            [axM.c2p(-4, 0)] + [axM.c2p((bins[i] + bins[i+1]) / 2,
             np.histogram(samples[int(round(step.get_value()))], bins=bins, density=True)[0][i])
             for i in range(len(bins) - 1)] + [axM.c2p(4, 0)]
        ).set_fill(WARM, 0.2).set_stroke(width=0))

        title = MathTex(r"\text{pairwise-sum-and-rescale:}\quad z_i=(x_{2i-1}+x_{2i})/\sqrt2",
                        font_size=32, color=WARM).next_to(axM, UP, buff=0.15)

        # cumulant bar chart (side)
        BX, BY0, BH = 4.0, -1.8, 3.0
        maxk = max(max(c) for c in cums)
        bar3 = always_redraw(lambda: Rectangle(
            width=0.55, height=max(BH * cums[int(round(step.get_value()))][0] / maxk, 1e-3),
            fill_color=HOT, fill_opacity=0.85, stroke_width=0).move_to(
            [BX, BY0 + BH * cums[int(round(step.get_value()))][0] / maxk / 2, 0]))
        bar4 = always_redraw(lambda: Rectangle(
            width=0.55, height=max(BH * cums[int(round(step.get_value()))][1] / maxk, 1e-3),
            fill_color=WARM2, fill_opacity=0.85, stroke_width=0).move_to(
            [BX + 0.9, BY0 + BH * cums[int(round(step.get_value()))][1] / maxk / 2, 0]))
        bar_axis = Line([BX - 0.5, BY0, 0], [BX + 1.5, BY0, 0], color=GRAYM, stroke_width=2)
        bl3 = VGroup(MathTex(r"|\kappa_3|", font_size=22, color=HOT),
                     Text("skew", font_size=15, color=HOT)).arrange(DOWN, buff=0.05).move_to([BX, BY0 - 0.5, 0])
        bl4 = VGroup(MathTex(r"|\kappa_4|", font_size=22, color=WARM2),
                     Text("kurtosis", font_size=15, color=WARM2)).arrange(DOWN, buff=0.05).move_to([BX + 0.9, BY0 - 0.5, 0])
        cum_title = VGroup(
            MathTex(r"\Lambda_3=2^{-1/2}", font_size=20, color=HOT),
            MathTex(r"\Lambda_4=2^{-1}", font_size=20, color=WARM2),
            Text("(irrelevant: shrink)", font_size=15, color=GRAYM),
        ).arrange(DOWN, buff=0.12).move_to([BX + 0.45, BY0 + BH + 0.6, 0])

        clock = always_redraw(lambda: Text(
            f"RG step {int(round(step.get_value()))}", font_size=22, color=GRAYM).move_to([-2.6, -2.7, 0]))

        self.play(Create(axM), Create(gauss_d), FadeIn(VGroup(gauss_lab, title, bar_axis,
                  bl3, bl4, cum_title, clock)), run_time=1.0)
        self.add(hist_fill, hist_m, bar3, bar4)
        cap = Text("start with an ugly distribution — skewed, bimodal, unit variance",
                   font_size=22).to_edge(DOWN, buff=0.15)
        self.play(FadeIn(cap), run_time=0.5)
        self.wait(0.8)
        self.play(FadeOut(cap), run_time=0.3)
        for it in range(1, N_RG + 1):
            self.play(step.animate.set_value(it), run_time=1.5, rate_func=smooth)
            self.wait(0.3)
        cap2 = Text("all perturbations die — the Gaussian fixed point is an attractor, and that attractor property is the CLT",
                    font_size=21, color=COOL).to_edge(DOWN, buff=0.15)
        self.play(FadeIn(cap2), run_time=0.5)
        self.wait(1.8)
