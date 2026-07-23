"""Entry #3 — Phenotype switching: proportional betting in a bacterial colony (ITFNS §3.6)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, COOL2, GRAYM, VIOLET

# environment probabilities
P_ANTI = 0.35          # prob of "antibiotic" generation
GENS = 26
# growth factors [in antibiotic, in no-antibiotic]
G_RES = np.array([2.0, 0.6])    # resistant: thrives w/ antibiotic
G_FAST = np.array([0.3, 2.2])    # fast/vulnerable: crashes w/ antibiotic
# hedger splits population in proportion to env probs each gen


def simulate():
    rng = np.random.default_rng(5)
    env = (rng.random(GENS) >= P_ANTI).astype(int)  # 0=antibiotic,1=none
    env[2], env[6], env[14], env[20] = 0, 0, 0, 0   # scatter antibiotic hits
    wA = np.ones(GENS + 1)   # all-in resistant
    wB = np.ones(GENS + 1)   # all-in fast
    wC = np.ones(GENS + 1)   # hedger
    for t in range(GENS):
        e = env[t]
        wA[t + 1] = wA[t] * G_RES[e]
        wB[t + 1] = wB[t] * G_FAST[e]
        # hedger: fraction P_ANTI resistant, (1-P_ANTI) fast
        frac_res, frac_fast = P_ANTI, 1 - P_ANTI
        wC[t + 1] = wC[t] * (frac_res * G_RES[e] + frac_fast * G_FAST[e])
    return env, wA, wB, wC


ENV, WA, WB, WC = simulate()
LOGW = {k: np.log10(np.maximum(v, 1e-6)) for k, v in
        zip("ABC", (WA, WB, WC))}
YMIN = min(v.min() for v in LOGW.values()) - 0.3
YMAX = max(v.max() for v in LOGW.values()) + 0.3


class PhenotypeSwitching(Scene):
    def construct(self):
        gtr = ValueTracker(0.0)   # current generation (fractional)

        # ---------- environment ribbon ----------
        rib_y = 3.15
        cellw = 0.44
        x0 = -6.0

        def env_ribbon():
            g = VGroup()
            cur = int(min(gtr.get_value(), GENS - 1e-6))
            for t in range(GENS):
                x = x0 + t * cellw
                anti = ENV[t] == 0
                sq = Square(cellw * 0.92,
                            fill_color=HOT if anti else COOL2,
                            fill_opacity=0.85 if t <= cur else 0.18,
                            stroke_width=1, stroke_color=GRAYM).move_to([x, rib_y, 0])
                g.add(sq)
            return g
        ribbon = always_redraw(env_ribbon)
        rib_lab = VGroup(
            Text("antibiotic", font_size=17, color=HOT),
            Text("/  none", font_size=17, color=COOL2),
        ).arrange(RIGHT, buff=0.12).next_to([x0 + GENS * cellw / 2, rib_y, 0], UP, buff=0.18)
        marker = always_redraw(lambda: Triangle(color=WHITE, fill_opacity=1)
                               .scale(0.09).rotate(PI)
                               .move_to([x0 + min(gtr.get_value(), GENS) * cellw, rib_y + 0.4, 0]))

        # ---------- three colonies as dot clusters ----------
        centers = {"A": [-4.4, 0.9, 0], "B": [-0.1, 0.9, 0], "C": [4.3, 0.9, 0]}
        cols = {"A": WARM, "B": COOL2, "C": WARM2}
        names = {
            "A": "all-in resistant", "B": "all-in fast", "C": "hedger (switching)",
        }
        rng = np.random.default_rng(1)
        DISC = rng.uniform(-1, 1, (80, 2))
        DISC = DISC[np.linalg.norm(DISC, axis=1) < 1][:60]

        def colony(key):
            def mk():
                g = gtr.get_value()
                gi = int(min(g, GENS - 1e-6))
                frac = g - gi
                w = LOGW[key]
                lw = w[gi] + (w[min(gi + 1, GENS)] - w[gi]) * frac
                # map log-pop to a dot count (visual), min 0
                rel = (lw - YMIN) / (YMAX - YMIN)
                ndots = int(np.clip(rel * 55 + 1, 0, 60))
                grp = VGroup()
                scale = 0.55 + 0.7 * rel
                for k in range(ndots):
                    p = np.array([*(DISC[k] * scale), 0]) + np.array(centers[key])
                    grp.add(Dot(p, radius=0.06, color=cols[key], fill_opacity=0.85))
                return grp
            return always_redraw(mk)

        colonies = VGroup(*[colony(k) for k in "ABC"])
        name_labs = VGroup(*[
            Text(names[k], font_size=18, color=cols[k]).move_to(
                [centers[k][0], 2.05, 0]) for k in "ABC"
        ])

        # ---------- log-population plot ----------
        ax = Axes(
            x_range=[0, GENS, 5], y_range=[YMIN, YMAX, 1],
            x_length=11.4, y_length=2.7,
            axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                         "font_size": 20},
        ).move_to([0, -2.4, 0])
        ax_xlab = Text("generation", font_size=18, color=GRAYM).next_to(ax.x_axis, DOWN, buff=0.1).shift(RIGHT*4)
        ax_ylab = Text("log₁₀ population", font_size=18, color=GRAYM).rotate(PI/2).next_to(ax.y_axis, LEFT, buff=0.05)

        def make_curve(key):
            def mk():
                g = gtr.get_value()
                gi = int(min(g, GENS))
                pts = [ax.c2p(t, LOGW[key][t]) for t in range(gi + 1)]
                if g > gi and gi < GENS:
                    frac = g - gi
                    lw = LOGW[key][gi] + (LOGW[key][gi + 1] - LOGW[key][gi]) * frac
                    pts.append(ax.c2p(g, lw))
                if len(pts) < 2:
                    return VMobject()
                return VMobject().set_points_as_corners(pts).set_stroke(cols[key], 3)
            return always_redraw(mk)

        curves = VGroup(*[make_curve(k) for k in "ABC"])

        caps = [
            Text("three colonies face a randomly switching environment, generation by generation",
                 font_size=21).to_edge(DOWN, buff=0.1),
            Text("each specialist crashes when its bad environment hits — the hedger never does",
                 font_size=21, color=WARM2).to_edge(DOWN, buff=0.1),
            Text("splitting its bodies in proportion to the odds, the hedger compounds fastest — Kelly, unread",
                 font_size=21, color=WARM2).to_edge(DOWN, buff=0.1),
        ]

        self.add(ribbon, marker, colonies, curves)
        self.play(FadeIn(VGroup(rib_lab, name_labs, ax, ax_xlab, ax_ylab)),
                  FadeIn(caps[0]), run_time=0.9)
        self.wait(0.6)
        self.play(FadeOut(caps[0]), FadeIn(caps[1]), run_time=0.5)
        self.play(gtr.animate.set_value(10), run_time=6.0, rate_func=linear)
        self.play(FadeOut(caps[1]), FadeIn(caps[2]), run_time=0.5)
        self.play(gtr.animate.set_value(GENS), run_time=7.0, rate_func=linear)
        self.wait(1.6)
