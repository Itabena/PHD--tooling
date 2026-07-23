"""Entry #26 — Brownian motion: ballistic-to-diffusive crossover & FDT (ITFNS A.10)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, COOL2, GRAYM

GAMMA = 1.0     # friction (relaxation rate)


class BrownianBallisticToDiffusiveCrossover(Scene):
    def construct(self):
        t_tr = ValueTracker(0.0)

        # ---------- left: tracer in a fog of kicks ----------
        box = Square(3.0, color=GRAYM, stroke_width=2).move_to([-4.0, 0.5, 0])
        rng = np.random.default_rng(1)
        # precompute a langevin trajectory of the tracer
        NT = 900
        dt = 0.02
        v = 0.0
        xs = [np.array([-4.0, 0.5])]
        vel = np.array([0.4, 0.2])
        traj = [xs[0].copy()]
        for k in range(NT):
            kick = rng.normal(0, 1.4, 2)
            vel = vel * (1 - GAMMA * dt) + kick * np.sqrt(dt)
            p = traj[-1] + vel * dt * 0.35
            # reflect in box
            for d in range(2):
                lo, hi = (-4.0 if d == 0 else 0.5) - 1.35, (-4.0 if d == 0 else 0.5) + 1.35
                if p[d] < lo or p[d] > hi:
                    vel[d] *= -1
                    p[d] = np.clip(p[d], lo, hi)
            traj.append(p.copy())
        traj = np.array(traj)

        def tracer():
            k = int(np.clip(t_tr.get_value() / dt, 0, NT))
            return Dot([traj[k][0], traj[k][1], 0], radius=0.13, color=WARM)
        tracer_m = always_redraw(tracer)

        def path():
            k = int(np.clip(t_tr.get_value() / dt, 1, NT))
            return VMobject().set_points_as_corners(
                [np.array([traj[j][0], traj[j][1], 0]) for j in range(k)]).set_stroke(WARM2, 1.5, opacity=0.5)
        path_m = always_redraw(path)
        fog = VGroup(*[Dot([-4.0 + rng.uniform(-1.3, 1.3), 0.5 + rng.uniform(-1.3, 1.3), 0],
                           radius=0.03, color=COOL, fill_opacity=0.5) for _ in range(40)])
        box_lab = Text("heavy tracer in a fog of kicks", font_size=18, color=GRAYM).next_to(box, UP, buff=0.15)

        # ---------- right: MSD log-log ----------
        ax = Axes(x_range=[-1.5, 1.5, 1], y_range=[-3, 1.5, 1], x_length=6.0, y_length=4.6,
                  axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False, "font_size": 16}).move_to([3.0, 0.3, 0])
        ax_x = MathTex(r"\log t", font_size=22, color=GRAYM).next_to(ax.x_axis, RIGHT, buff=0.1)
        ax_y = MathTex(r"\log\langle\Delta r^2\rangle", font_size=22, color=GRAYM).next_to(ax.y_axis, UP, buff=0.05).shift(LEFT*1.2)

        # MSD(t) = 2 v0^2/gamma^2 (gamma t - 1 + e^{-gamma t}) form: ballistic t^2 then diffusive t
        def msd(t):
            g = GAMMA
            return 2 * (g * t - 1 + np.exp(-g * t)) / g ** 2 + 1e-4
        knee = 1.0 / GAMMA
        # slope-2 and slope-1 reference lines
        ball_ref = ax.plot(lambda lt: 2 * lt - 1.2, x_range=[-1.5, np.log10(knee)], color=GRAYM, stroke_width=1.5)
        ball_ref_d = DashedVMobject(ball_ref, num_dashes=15)
        diff_ref = ax.plot(lambda lt: 1 * lt - 0.15, x_range=[np.log10(knee) - 0.2, 1.5], color=GRAYM, stroke_width=1.5)
        diff_ref_d = DashedVMobject(diff_ref, num_dashes=15)
        ball_lab = Text("slope 2 (ballistic)", font_size=16, color=WARM).move_to(ax.c2p(-0.9, 0.6))
        diff_lab = Text("slope 1 (diffusive)", font_size=16, color=COOL).move_to(ax.c2p(0.95, -1.0))
        knee_line = DashedLine(ax.c2p(np.log10(knee), -3), ax.c2p(np.log10(knee), 1.5),
                               color=HOT, stroke_width=1.5)
        knee_lab = MathTex(r"t\sim 1/\gamma", font_size=18, color=HOT).move_to(ax.c2p(0.5, 1.25))

        curve = VMobject().set_stroke(WARM2, 3.5)

        def upd_curve(m):
            tv = max(t_tr.get_value(), 0.03)
            ts = np.logspace(-1.5, np.log10(max(tv, 0.05)), 60)
            pts = [ax.c2p(np.log10(t), np.log10(msd(t))) for t in ts if -1.5 <= np.log10(t) <= 1.5]
            if len(pts) < 2:
                pts = [ax.c2p(-1.5, np.log10(msd(10 ** -1.5)))] * 2
            m.set_points_as_corners(pts)
        curve.add_updater(upd_curve)

        fdt = MathTex(r"\gamma=\frac{1}{2TM}\int C(t)\,dt\ :\ \text{fluctuation} = \text{dissipation}",
                      font_size=22, color=WARM).to_edge(DOWN, buff=0.25)

        self.play(FadeIn(VGroup(box, box_lab, fog)),
                  Create(ax), FadeIn(VGroup(ax_x, ax_y, ball_ref_d, diff_ref_d, ball_lab, diff_lab,
                  knee_line, knee_lab)), run_time=1.2)
        self.add(tracer_m, path_m, curve)
        cap = Text("a heavy particle bombarded by light molecules — track its mean-squared displacement",
                   font_size=20).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(cap), run_time=0.5)
        self.play(t_tr.animate.set_value(16), run_time=8.0, rate_func=linear)
        cap2 = Text("short times: ballistic (slope 2); past t ~ 1/γ friction randomizes velocity → diffusive (slope 1)",
                    font_size=19, color=COOL).to_edge(DOWN, buff=0.25)
        self.play(FadeOut(cap), FadeIn(cap2), run_time=0.5)
        self.wait(1.2)
        self.play(FadeOut(cap2), FadeIn(fdt), run_time=0.5)
        self.wait(1.6)
        curve.clear_updaters()
