"""Entry #18 — Multi-armed bandit: the index that explores on its own (ITFNS A.6)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, COOL2, GRAYM, VIOLET

TRUE_P = [0.35, 0.55, 0.72]     # unknown win probabilities
N_TURNS = 48
BETA_DISC = 0.92                 # discount


def beta_pdf(x, w, l):
    a, b = w + 1, l + 1
    from math import lgamma
    logB = lgamma(a) + lgamma(b) - lgamma(a + b)
    return np.exp((a - 1) * np.log(np.clip(x, 1e-6, 1)) +
                  (b - 1) * np.log(np.clip(1 - x, 1e-6, 1)) - logB)


def gittins_approx(w, l):
    """Cheap index: posterior mean + exploration bonus that shrinks with evidence."""
    a, b = w + 1, l + 1
    mean = a / (a + b)
    n = a + b
    var = mean * (1 - mean) / (n + 1)
    return mean + 1.6 * np.sqrt(var)


def run():
    rng = np.random.default_rng(2)
    W = [0, 0, 0]; L = [0, 0, 0]
    hist = []
    total = 0
    for t in range(N_TURNS):
        idx = [gittins_approx(W[i], L[i]) for i in range(3)]
        arm = int(np.argmax(idx))
        win = rng.random() < TRUE_P[arm]
        if win:
            W[arm] += 1; total += 1
        else:
            L[arm] += 1
        hist.append((arm, win, list(W), list(L), list(idx), total))
    return hist


HIST = run()


class MultiArmedBanditGittinsIndex(Scene):
    def construct(self):
        step = ValueTracker(0)
        centers_x = [-4.0, 0.0, 4.0]
        names = ["arm 1", "arm 2", "arm 3"]

        def state_at(s):
            s = int(min(max(s, 0), N_TURNS - 1))
            return HIST[s]

        # posterior curves
        def posterior(i):
            def mk():
                s = int(round(step.get_value()))
                _, _, W, L, idx, _ = state_at(s)
                xs = np.linspace(0, 1, 60)
                ys = beta_pdf(xs, W[i], L[i])
                ys = ys / max(ys.max(), 1e-6)  # normalize height
                cx = centers_x[i]
                pts = [[cx - 1.1 + x * 2.2, 0.4 + y * 1.5, 0] for x, y in zip(xs, ys)]
                curve = VMobject().set_points_as_corners([np.array(p) for p in pts]).set_stroke(WARM, 3)
                return curve
            return always_redraw(mk)

        posts = VGroup(*[posterior(i) for i in range(3)])
        axes_lines = VGroup(*[
            Line([cx - 1.1, 0.4, 0], [cx + 1.1, 0.4, 0], color=GRAYM, stroke_width=1.5)
            for cx in centers_x
        ])
        true_marks = VGroup(*[
            DashedLine([centers_x[i] - 1.1 + TRUE_P[i] * 2.2, 0.4, 0],
                       [centers_x[i] - 1.1 + TRUE_P[i] * 2.2, 2.1, 0],
                       color=GRAYM, stroke_width=1.5, dash_length=0.06)
            for i in range(3)
        ])
        true_labs = VGroup(*[
            MathTex(r"s_" + str(i + 1) + r"=" + f"{TRUE_P[i]:.2f}", font_size=18, color=GRAYM).move_to(
                [centers_x[i], 2.4, 0]) for i in range(3)
        ])

        # index bars
        def index_bar(i):
            def mk():
                s = int(round(step.get_value()))
                _, _, W, L, idx, _ = state_at(s)
                h = idx[i] * 2.4
                arm_now = state_at(s)[0]
                col = HOT if arm_now == i else WARM2
                return Rectangle(width=0.5, height=max(h, 1e-3), fill_color=col, fill_opacity=0.85,
                                 stroke_width=0).move_to([centers_x[i], -2.4 + h / 2, 0])
            return always_redraw(mk)
        idx_bars = VGroup(*[index_bar(i) for i in range(3)])
        idx_base = Line([-5.2, -2.4, 0], [5.2, -2.4, 0], color=GRAYM, stroke_width=2)
        idx_lab = VGroup(*[
            Text(names[i], font_size=18, color=GRAYM).move_to([centers_x[i], -2.75, 0])
            for i in range(3)
        ])
        idx_title = Text("Gittins index (bar) — highest one is played", font_size=20, color=WARM2).move_to([0, -0.6, 0])

        # played highlight + running reward
        played = always_redraw(lambda: Text(
            "playing " + names[state_at(int(round(step.get_value())))[0]] +
            ("  — win" if state_at(int(round(step.get_value())))[1] else "  — loss"),
            font_size=20, color=(WARM if state_at(int(round(step.get_value())))[1] else COOL)
        ).move_to([0, 3.3, 0]))
        reward = always_redraw(lambda: Text(
            f"total reward: {state_at(int(round(step.get_value())))[5]}",
            font_size=20, color=WARM).move_to([4.3, 3.3, 0]))
        turn_lab = always_redraw(lambda: Text(
            f"turn {int(round(step.get_value())) + 1}/{N_TURNS}", font_size=18, color=GRAYM).move_to([-4.3, 3.3, 0]))

        self.add(posts, idx_bars, played, reward, turn_lab)
        self.play(FadeIn(VGroup(axes_lines, true_marks, true_labs, idx_base, idx_lab, idx_title)),
                  run_time=1.0)
        cap = Text("each turn: play the highest-index arm, update its Beta posterior, watch the index move",
                   font_size=21).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(cap), run_time=0.5)
        self.play(step.animate.set_value(N_TURNS - 1), run_time=9.0, rate_func=linear)
        cap2 = Text("a played arm's posterior sharpens and its index creeps down — when a rival overtakes, it switches on its own (exploration, automatic)",
                    font_size=17, color=WARM2).to_edge(DOWN, buff=0.2)
        self.play(FadeOut(cap), FadeIn(cap2), run_time=0.5)
        self.wait(2.0)
