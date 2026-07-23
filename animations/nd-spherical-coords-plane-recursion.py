"""From-scratch scene (not one of the 28 Animation plan entries) for the vault
note "Jacobian of $n$-Dimensional Spherical Coordinates.md" -- animates the
recursive plane-by-plane construction from that note's Parametrization
section: the (r, x1) plane and theta1 split r into x1 and a remaining radius
r*sin(theta1); that remainder becomes the hypotenuse of the next (x2, .)
plane and theta2 splits it again; and so on, until the last remainder is
x_n itself with no further split.

Demo values (n=4, r=4, theta=[55,70,35] deg) are illustrative numbers picked
to draw something concrete -- the note's own derivation is fully general in
n; only these specific numbers are this scene's own choice, not sourced from
the note.
"""
from manim import *
import numpy as np

from itfns import WARM, COOL, GRAYM, WARM2
from components import time_readout, boxed_readout

R0 = 4.0
THETAS_DEG = [55, 70, 35]
THETAS = [np.deg2rad(t) for t in THETAS_DEG]

# Precompute the recursive split: rho[0] = r, x[k] = rho[k-1]*cos(theta_k),
# rho[k] = rho[k-1]*sin(theta_k); the final leftover rho[-1] becomes x_n
# directly (no further angle to split it with).
rho = [R0]
xs = []
for th in THETAS:
    xs.append(rho[-1] * np.cos(th))
    rho.append(rho[-1] * np.sin(th))
xs.append(rho[-1])  # x_n = last remainder, terminal step
N = len(xs)

O = np.array([-4.6, -1.6, 0.0])
SCALE = 0.85


def hyp_endpoint(length, angle):
    return O + SCALE * length * np.array([np.cos(angle), np.sin(angle), 0.0])


def foot_point(length, angle):
    # perpendicular foot of the hypotenuse endpoint onto the horizontal ref
    return O + SCALE * length * np.cos(angle) * np.array([1.0, 0.0, 0.0])


class NDSphericalPlaneRecursion(Scene):
    def construct(self):
        step_tr = ValueTracker(1)

        title = Text("Recursive construction of n-D spherical coordinates", font_size=26).to_edge(UP, buff=0.35)
        subtitle = always_redraw(lambda: Text(
            f"step {min(int(step_tr.get_value()), N-1)} of {N-1} splits"
            if step_tr.get_value() < N - 0.5 else "terminal step: no angle left to split",
            font_size=20, color=GRAYM).next_to(title, DOWN, buff=0.15))

        r_lab = MathTex(f"r = {R0:.0f}\\ \\text{{(fixed)}}", font_size=28, color=COOL).to_corner(UR, buff=0.6)
        r_box = boxed_readout(r_lab, color=COOL)
        self.play(Write(title), FadeIn(subtitle), FadeIn(VGroup(r_lab, r_box)), run_time=1.0)

        ref_axis = Line(O, O + SCALE * (R0 + 0.8) * RIGHT, color=GRAYM, stroke_width=2)
        self.play(Create(ref_axis), run_time=0.5)

        tuple_labels = VGroup()
        tuple_title = Text("coordinates extracted so far:", font_size=20, color=GRAYM).to_corner(UL, buff=0.6).shift(DOWN * 0.5)
        self.play(FadeIn(tuple_title), run_time=0.4)

        current_len = R0
        current_line = Line(O, O + SCALE * R0 * RIGHT, color=WARM2, stroke_width=4)
        current_lab = MathTex(r"\rho_0=r", font_size=24, color=WARM2).next_to(current_line, UP, buff=0.12)
        self.play(Create(current_line), Write(current_lab), run_time=0.6)

        for k, th in enumerate(THETAS, start=1):
            step_tr.set_value(k)
            angle_end = hyp_endpoint(rho[k - 1], th)
            hyp = Line(O, angle_end, color=WARM2, stroke_width=4)
            arc = Angle(ref_axis, hyp, radius=0.5 + 0.05 * k, color=GRAYM)
            theta_lab = MathTex(rf"\theta_{{{k}}}", font_size=24, color=GRAYM).move_to(
                Angle(ref_axis, hyp, radius=0.9).point_from_proportion(0.5))

            self.play(Transform(current_line, hyp), FadeOut(current_lab), run_time=0.8)
            self.play(Create(arc), Write(theta_lab), run_time=0.5)

            foot = foot_point(rho[k - 1], th)
            x_leg = Line(O, foot, color=WARM, stroke_width=6)
            rho_leg = DashedLine(foot, angle_end, color=COOL, stroke_width=6)
            x_val = MathTex(rf"x_{{{k}}}={xs[k-1]:.2f}", font_size=24, color=WARM).next_to(x_leg, DOWN, buff=0.12)
            rho_val = MathTex(rf"\rho_{{{k}}}={rho[k]:.2f}", font_size=24, color=COOL).next_to(
                rho_leg, RIGHT, buff=0.12)

            self.play(Create(x_leg), Create(rho_leg), Write(x_val), Write(rho_val),
                      FadeOut(current_line), run_time=0.8)

            entry = MathTex(rf"x_{{{k}}}={xs[k-1]:.2f}", font_size=24, color=WARM)
            entry.next_to(tuple_title, DOWN, buff=0.25 + 0.4 * (k - 1)).align_to(tuple_title, LEFT)
            self.play(TransformFromCopy(x_val, entry), run_time=0.6)
            tuple_labels.add(entry)

            self.play(FadeOut(arc), FadeOut(theta_lab), FadeOut(x_leg), FadeOut(x_val), run_time=0.4)

            next_hyp = Line(O, O + SCALE * rho[k] * RIGHT, color=WARM2, stroke_width=4)
            next_lab = MathTex(rf"\rho_{{{k}}}", font_size=24, color=WARM2).next_to(next_hyp, UP, buff=0.12)
            self.play(Transform(rho_leg, next_hyp), FadeOut(rho_val), run_time=0.9)
            current_line, current_lab = rho_leg, next_lab
            self.play(Write(current_lab), run_time=0.3)

        step_tr.set_value(N - 1)
        self.wait(0.3)
        final_val = MathTex(rf"x_{{{N}}}=\rho_{{{N-1}}}={xs[-1]:.2f}", font_size=26, color=WARM).next_to(
            current_line, DOWN, buff=0.2)
        self.play(current_line.animate.set_color(WARM), FadeOut(current_lab), Write(final_val), run_time=0.8)
        entry = MathTex(rf"x_{{{N}}}={xs[-1]:.2f}", font_size=24, color=WARM)
        entry.next_to(tuple_title, DOWN, buff=0.25 + 0.4 * (N - 1)).align_to(tuple_title, LEFT)
        self.play(TransformFromCopy(final_val, entry), run_time=0.6)
        tuple_labels.add(entry)

        check_val = sum(x * x for x in xs)
        check = MathTex(
            rf"x_1^2+x_2^2+x_3^2+x_4^2={check_val:.2f}\approx r^2={R0*R0:.0f}",
            font_size=26, color=COOL).to_edge(DOWN, buff=0.5)
        check_box = boxed_readout(check, color=COOL)
        self.play(FadeIn(VGroup(check, check_box)), run_time=0.8)
        self.wait(1.5)
