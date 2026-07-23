"""Entry #4 — Kelly criterion: geometric vs. arithmetic wealth trajectories (ITFNS §3.6)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, COOL2, GRAYM, VIOLET

P = 0.6                 # win prob of the biased coin
N = 60                  # betting rounds
NPATH = 120
F_UNDER, F_KELLY, F_OVER = 0.10, 0.20, 0.55   # bet fractions (Kelly f*=2p-1=0.2)


def gen_paths(f, seed):
    rng = np.random.default_rng(seed)
    wins = rng.random((NPATH, N)) < P
    mult = np.where(wins, 1 + f, 1 - f)
    w = np.ones((NPATH, N + 1))
    w[:, 1:] = np.cumprod(mult, axis=1)
    return np.log10(np.maximum(w, 1e-12))


LOG = {f: gen_paths(f, s) for f, s in
       [(F_UNDER, 10), (F_KELLY, 11), (F_OVER, 12)]}


class KellyWealthFan(Scene):
    def construct(self):
        # ---------------- BEAT 1: three fans ----------------
        ax = Axes(
            x_range=[0, N, 15], y_range=[-4, 4, 2],
            x_length=11.5, y_length=5.2,
            axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                         "font_size": 22},
        ).move_to([0, -0.3, 0])
        xlab = Text("betting round", font_size=20, color=GRAYM).next_to(ax.x_axis, DOWN, buff=0.15).shift(RIGHT * 3.5)
        ylab = Text("log₁₀ wealth", font_size=20, color=GRAYM).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.1)
        title = Text("a biased coin, p = 0.6 — many sample wealth paths under three bet fractions",
                     font_size=22).to_edge(UP, buff=0.25)

        fan_specs = [(F_UNDER, COOL, "under-bet  f < p"),
                     (F_KELLY, WARM2, "Kelly  f = p"),
                     (F_OVER, HOT, "over-bet  f > p")]

        self.play(Create(ax), FadeIn(VGroup(xlab, ylab)), FadeIn(title), run_time=1.0)

        fan_groups = {}
        medians = {}
        for f, col, _ in fan_specs:
            paths = VGroup()
            for k in range(0, NPATH, 2):
                pts = [ax.c2p(t, LOG[f][k, t]) for t in range(N + 1)]
                paths.add(VMobject().set_points_as_corners(pts)
                          .set_stroke(col, 1.2, opacity=0.28))
            med = np.median(LOG[f], axis=0)
            medln = VMobject().set_points_as_corners(
                [ax.c2p(t, med[t]) for t in range(N + 1)]).set_stroke(col, 4)
            fan_groups[f] = paths
            medians[f] = medln

        legend = VGroup()
        for i, (f, col, name) in enumerate(fan_specs):
            sw = Line(ORIGIN, RIGHT * 0.4, color=col, stroke_width=4)
            tx = Text(name, font_size=19, color=col)
            row = VGroup(sw, tx).arrange(RIGHT, buff=0.15)
            legend.add(row)
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UL, buff=0.5).shift(DOWN * 1.1)

        for f, col, _ in fan_specs:
            self.play(Create(fan_groups[f]), run_time=1.3)
        self.play(*[Create(medians[f]) for f, _, _ in fan_specs],
                  FadeIn(legend), run_time=1.2)
        cap1 = Text("the f = p median grows fastest; over-betting fans out wildly and many paths crash",
                    font_size=22, color=WARM2).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(cap1), run_time=0.5)
        self.wait(2.2)

        # ---------------- BEAT 2: the arithmetic-mean trap ----------------
        self.play(
            FadeOut(fan_groups[F_UNDER]), FadeOut(fan_groups[F_KELLY]),
            FadeOut(medians[F_UNDER]), FadeOut(medians[F_KELLY]),
            FadeOut(legend), FadeOut(cap1), FadeOut(title),
            run_time=0.8,
        )
        title2 = Text("over-betting f = 0.55: the mean lies",
                      font_size=24, color=HOT).to_edge(UP, buff=0.25)
        # arithmetic mean of wealth (linear space) vs median, on the same paths
        W = np.power(10.0, LOG[F_OVER])
        amean = np.log10(np.mean(W, axis=0))
        med = np.median(LOG[F_OVER], axis=0)
        amean_ln = VMobject().set_points_as_corners(
            [ax.c2p(t, min(amean[t], 4)) for t in range(N + 1)]).set_stroke(WARM, 4)
        med_ln = VMobject().set_points_as_corners(
            [ax.c2p(t, med[t]) for t in range(N + 1)]).set_stroke(HOT, 4)
        amean_lab = Text("arithmetic mean → ∞", font_size=20, color=WARM).move_to(
            ax.c2p(N * 0.62, min(amean[N], 4) + 1.0))
        med_lab = Text("median / typical path → ruin", font_size=20, color=HOT).move_to(
            ax.c2p(N * 0.60, med[N] - 1.0))

        self.play(FadeIn(title2), run_time=0.5)
        self.play(Create(amean_ln), Create(med_ln), run_time=2.0)
        # shade divergence
        shade = ax.get_area(
            ax.plot(lambda x: np.interp(x, range(N + 1), np.minimum(amean, 4)), x_range=[0, N]),
            x_range=[0, N],
            bounded_graph=ax.plot(lambda x: np.interp(x, range(N + 1), med), x_range=[0, N]),
            color=GRAYM, opacity=0.18,
        )
        self.play(FadeIn(shade), FadeIn(amean_lab), FadeIn(med_lab), run_time=1.0)
        cap2 = Text("arithmetic mean races to ∞ while the probability of ruin → 1 — maximize the geometric mean",
                    font_size=21).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(cap2), run_time=0.5)
        self.wait(2.4)
