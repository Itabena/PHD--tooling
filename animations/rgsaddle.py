"""Entry #21 — RG flow to an unstable fixed point: critical surface & universality (ITFNS A.9)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, COOL2, GRAYM, VIOLET

# Coupling space (K1,K2). Three fixed points:
#  - disordered sink at origin O=(0,0)  (cool)
#  - ordered sink at P=(2.4,2.4)        (warm)
#  - saddle (unstable FP) at S=(1.2,1.2)
O = np.array([0.0, 0.0])
Pord = np.array([2.4, 2.4])
Sad = np.array([1.2, 1.2])


def flow(p):
    """A vector field with two sinks and a saddle between them along the diagonal."""
    x, y = p
    # attract to nearest sink across the separatrix (the anti-diagonal through Sad)
    # component along diagonal d=(1,1)/sqrt2 pushes away from saddle (unstable)
    d = np.array([1, 1]) / np.sqrt(2)
    n = np.array([1, -1]) / np.sqrt(2)
    rel = p - Sad
    s_par = rel @ d      # coordinate along diagonal
    s_perp = rel @ n     # across
    # along diagonal: cubic double-well -> pushed to +/- (toward Pord / O)
    v_par = s_par - 0.25 * s_par ** 3     # unstable at 0, stable near +/-2
    v_perp = -1.3 * s_perp                 # stable across (inflowing separatrix)
    v = v_par * d + v_perp * n
    return v


def integrate(p0, steps=60, dt=0.06):
    p = np.array(p0, float)
    pts = [p.copy()]
    for _ in range(steps):
        p = p + flow(p) * dt
        p = np.clip(p, -0.6, 3.2)
        pts.append(p.copy())
    return np.array(pts)


class RGFlowUnstableFixedPointCriticalSurface(Scene):
    def construct(self):
        ax = Axes(x_range=[-0.5, 3.1, 1], y_range=[-0.5, 3.1, 1], x_length=6.5, y_length=6.0,
                  axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                               "font_size": 20}).move_to([-2.6, 0, 0])
        xlab = MathTex(r"K_1", font_size=26, color=GRAYM).next_to(ax.x_axis, RIGHT, buff=0.1)
        ylab = MathTex(r"K_2", font_size=26, color=GRAYM).next_to(ax.y_axis, UP, buff=0.1)

        def p2s(p):
            return ax.c2p(p[0], p[1])

        # streamlines (static field)
        streams = VGroup()
        rng = np.random.default_rng(0)
        for _ in range(70):
            p0 = rng.uniform([-0.3, -0.3], [3.0, 3.0])
            tr = integrate(p0, steps=30, dt=0.05)
            pts = [p2s(p) for p in tr]
            streams.add(VMobject().set_points_as_corners(pts).set_stroke(GRAYM, 1, opacity=0.22))

        # fixed points
        o_dot = Dot(p2s(O), color=COOL, radius=0.12)
        o_lab = Text("disordered sink", font_size=17, color=COOL).next_to(o_dot, DL, buff=0.1)
        p_dot = Dot(p2s(Pord), color=WARM, radius=0.12)
        p_lab = Text("ordered sink", font_size=17, color=WARM).next_to(p_dot, UR, buff=0.05)
        s_dot = Dot(p2s(Sad), color=HOT, radius=0.13)
        s_lab = Text("unstable FP (saddle)", font_size=17, color=HOT).next_to(s_dot, RIGHT, buff=0.15)

        # critical surface = inflowing separatrix (anti-diagonal through saddle)
        crit_pts = []
        for t in np.linspace(-1.6, 1.6, 40):
            crit_pts.append(p2s(Sad + t * np.array([1, -1]) / np.sqrt(2)))
        crit = VMobject().set_points_as_corners(crit_pts).set_stroke(VIOLET, 3.5)
        crit_lab = Text("critical surface", font_size=18, color=VIOLET).move_to(ax.c2p(2.4, 0.3))

        self.play(Create(ax), FadeIn(VGroup(xlab, ylab)), run_time=0.8)
        self.play(Create(streams), run_time=1.5)
        self.play(FadeIn(VGroup(o_dot, o_lab, p_dot, p_lab, s_dot, s_lab)), run_time=0.8)

        # ---------- Beat 1: release dots, colored by destination ----------
        cap1 = Text("release many microscopic theories — each flows to one sink",
                    font_size=21).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(cap1), run_time=0.5)
        seeds = rng.uniform([0.0, 0.0], [2.8, 2.8], (14, 2))
        dots = VGroup()
        trajs = []
        for sd in seeds:
            tr = integrate(sd, steps=60)
            col = WARM if tr[-1].sum() > Sad.sum() else COOL
            d = Dot(p2s(sd), radius=0.07, color=col)
            dots.add(d)
            trajs.append((d, tr, col))
        self.play(FadeIn(dots), run_time=0.4)
        self.play(*[MoveAlongPath(d, VMobject().set_points_as_corners([p2s(p) for p in tr]))
                    for d, tr, _ in trajs], run_time=3.0, rate_func=linear)
        self.play(FadeIn(crit), FadeIn(crit_lab), run_time=0.8)
        self.wait(0.8)

        # ---------- Beat 2: two different starts on the critical surface flow together ----------
        cap2 = Text("two very different theories, both on the critical surface, flow to the same fixed point — universality",
                    font_size=19, color=VIOLET).to_edge(DOWN, buff=0.25)
        self.play(FadeOut(cap1), FadeIn(cap2), run_time=0.5)
        a0 = Sad + 1.3 * np.array([1, -1]) / np.sqrt(2)
        b0 = Sad - 1.3 * np.array([1, -1]) / np.sqrt(2)
        da = Dot(p2s(a0), radius=0.09, color=WARM2)
        db = Dot(p2s(b0), radius=0.09, color=COOL2)
        ta = integrate(a0, steps=60)
        tb = integrate(b0, steps=60)
        self.play(FadeIn(VGroup(da, db)), run_time=0.4)
        self.play(MoveAlongPath(da, VMobject().set_points_as_corners([p2s(p) for p in ta])),
                  MoveAlongPath(db, VMobject().set_points_as_corners([p2s(p) for p in tb])),
                  run_time=3.0, rate_func=linear)
        self.wait(1.0)

        # ---------- Beat 3: tune one knob across the surface, flip destination ----------
        cap3 = Text("tuning one knob (temperature) across the surface flips the destination — one relevant direction",
                    font_size=19, color=WARM).to_edge(DOWN, buff=0.25)
        self.play(FadeOut(cap2), FadeIn(cap3), run_time=0.5)
        knob = Dot(p2s(Sad + 0.25 * np.array([1, 1]) / np.sqrt(2)), radius=0.1, color=WHITE)
        self.play(FadeIn(knob), run_time=0.3)
        tk = integrate(Sad + 0.25 * np.array([1, 1]) / np.sqrt(2), steps=60)
        self.play(MoveAlongPath(knob, VMobject().set_points_as_corners([p2s(p) for p in tk])),
                  run_time=2.5, rate_func=linear)
        self.wait(1.4)
