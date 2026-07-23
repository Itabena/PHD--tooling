"""Entry #14 — Rate function as a Legendre transform of the CGF (ITFNS A.2)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, GRAYM

# CGF of a standard-normal-ish variable: G(z)=z^2/2 (mean 0, var 1) -> H(x)=x^2/2
# use a slightly skewed CGF for interest: G(z) = z^2/2 + 0.06 z^3
A3 = 0.05


def G(z):
    return z ** 2 / 2 + A3 * z ** 3


def Gp(z):
    return z + 3 * A3 * z ** 2       # slope x = G'(z)


class RateFunctionLegendreLargeDeviation(Scene):
    def construct(self):
        zt = ValueTracker(-1.6)

        axL = Axes(x_range=[-2, 2, 1], y_range=[-1.5, 2.5, 1], x_length=5.8, y_length=5.0,
                   axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                                "font_size": 20}).move_to([-3.5, -0.1, 0])
        axL_lab = MathTex(r"G(z)\ \text{(cumulant generating fn)}", font_size=24, color=WARM).next_to(axL, UP, buff=0.15)
        Gcurve = axL.plot(G, x_range=[-1.9, 1.9], color=WARM, stroke_width=3)

        axR = Axes(x_range=[-2, 2, 1], y_range=[0, 2.5, 1], x_length=5.0, y_length=5.0,
                   axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                                "font_size": 20}).move_to([3.4, -0.1, 0])
        axR_lab = MathTex(r"H(x)\ \text{(rate function)}", font_size=24, color=COOL).next_to(axR, UP, buff=0.15)

        # H(x) via Legendre: H(x) = x z*(x) - G(z*), where G'(z*)=x.
        # Invert x = z + 3 A3 z^2 in closed form (branch through z=0).
        def zstar_of(x):
            disc = max(1 + 12 * A3 * x, 0.0)
            return (-1 + np.sqrt(disc)) / (6 * A3)

        def Hval(x):
            zs = zstar_of(x)
            return x * zs - G(zs)
        Hcurve = axR.plot(lambda x: max(Hval(x), 0), x_range=[-1.4, 1.9], color=COOL, stroke_width=3)

        def z():
            return zt.get_value()

        # support line of slope x=G'(z), tangent to G at z: y = G(z) + x*(w - z)
        def support_line():
            z0 = z()
            x = Gp(z0)
            g0 = G(z0)
            return axL.plot(lambda w: g0 + x * (w - z0), x_range=[-1.9, 1.9],
                            color=WARM2, stroke_width=2)
        supp = always_redraw(support_line)
        touch = always_redraw(lambda: Dot(axL.c2p(z(), G(z())), color=WHITE, radius=0.06))
        # y-intercept = G(z)-x*z = -H(x)
        intercept = always_redraw(lambda: Dot(
            axL.c2p(0, G(z()) - Gp(z()) * z()), color=HOT, radius=0.07))
        int_lab = always_redraw(lambda: MathTex(
            r"-H(x)", font_size=22, color=HOT).next_to(
            axL.c2p(0, G(z()) - Gp(z()) * z()), LEFT, buff=0.1))

        # build H(x) point on the right as x=G'(z) sweeps
        Hdot = always_redraw(lambda: Dot(axR.c2p(Gp(z()), max(Hval(Gp(z())), 0)),
                                         color=COOL, radius=0.08))
        Hbuilt = VMobject().set_stroke(COOL, 3)
        Hbuilt.add_updater(lambda m: m.set_points_as_corners([
            axR.c2p(Gp(zz), max(Hval(Gp(zz)), 0)) for zz in np.linspace(-1.6, z(), 50)
        ]) if z() > -1.55 else m.set_points_as_corners([axR.c2p(Gp(-1.6), 0)] * 2))

        # regime annotations on H
        zero_dot = Dot(axR.c2p(0, 0), color=WARM2, radius=0.07)
        zero_lab = VGroup(
            MathTex(r"H=0", font_size=20, color=WARM2),
            Text("LLN point", font_size=15, color=WARM2),
        ).arrange(DOWN, buff=0.05).next_to(axR.c2p(0, 0), DOWN, buff=0.15)
        quad_lab = Text("quadratic ≈ Gaussian/CLT", font_size=15, color=GRAYM).move_to(axR.c2p(0.9, 0.5))
        arms_lab = Text("convex arms:\nlarge deviations", font_size=15, color=GRAYM).move_to(axR.c2p(-1.2, 1.6))

        self.play(Create(axL), Create(axR), FadeIn(VGroup(axL_lab, axR_lab)), run_time=1.0)
        self.play(Create(Gcurve), run_time=0.8)
        self.add(supp, touch, intercept, int_lab, Hdot, Hbuilt)
        cap = Text("sweep a support line of slope x up to G(z); its intercept is −H(x)",
                   font_size=21).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(cap), FadeIn(VGroup(zero_dot, zero_lab)), run_time=0.6)
        self.play(zt.animate.set_value(1.6), run_time=6.0, rate_func=smooth)
        cap2 = Text("the tangent construction builds H(x): zero at the mean (LLN), quadratic nearby (CLT), convex arms (large deviations)",
                    font_size=19, color=COOL).to_edge(DOWN, buff=0.2)
        self.play(FadeOut(cap), FadeIn(cap2), FadeIn(VGroup(quad_lab, arms_lab)), run_time=0.6)
        self.wait(2.0)
        Hbuilt.clear_updaters()
