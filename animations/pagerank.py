"""Entry #2 — PageRank as a random surfer converging to a stationary rank (ITFNS §4.1)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, COOL2, GRAYM, VIOLET

NODES = {
    0: (-5.2, 2.5), 1: (-2.8, 3.1), 2: (-4.5, 0.5), 3: (-3.5, -1.7),
    4: (-1.2, 1.5), 5: (-0.7, -1.1), 6: (-1.7, -2.6),
}
ADJ = {0: [1, 4], 1: [2, 4], 2: [0, 1, 3], 3: [6], 4: [1, 5], 5: [], 6: [3]}
N = 7
D = 0.85
NTOK = 60
STEP = 0.4
NAIVE_T0, NAIVE_T1 = 1.0, 7.4       # naive walk
TELE_T0 = 9.0                        # teleportation on
T_TOTAL = 17.5


def google_stationary():
    G = np.zeros((N, N))
    for i in range(N):
        outs = ADJ[i]
        for j in range(N):
            if not outs:
                G[i, j] = 1 / N
            else:
                G[i, j] = D * (1 / len(outs) if j in outs else 0) + (1 - D) / N
    p = np.ones(N) / N
    for _ in range(500):
        p = p @ G
    return p


PSTAR = google_stationary()


def simulate():
    rng = np.random.default_rng(3)
    tok = rng.integers(0, N, NTOK)
    steps = int(T_TOTAL / STEP) + 3
    hist = np.zeros((steps, NTOK), dtype=int)
    for s in range(steps):
        hist[s] = tok
        t = NAIVE_T0 + s * STEP
        tele = t >= TELE_T0
        new = tok.copy()
        for k in range(NTOK):
            i = tok[k]
            outs = ADJ[i]
            if tele:
                if not outs or rng.random() > D:
                    new[k] = rng.integers(0, N)
                else:
                    new[k] = outs[rng.integers(0, len(outs))]
            else:
                if outs:
                    new[k] = outs[rng.integers(0, len(outs))]
        tok = new
    return hist


HIST = simulate()
RNG_J = np.random.default_rng(11)
JIT = RNG_J.normal(0, 0.16, (NTOK, 2))


def step_of(t):
    if t < NAIVE_T0:
        return 0, 0.0
    s = (t - NAIVE_T0) / STEP
    return min(int(s), HIST.shape[0] - 2), min(s % 1, 1.0)


def counts_at(t):
    s, _ = step_of(t)
    return np.bincount(HIST[s], minlength=N) / NTOK


class PageRankSurfer(Scene):
    def construct(self):
        t_tr = ValueTracker(0.0)
        t_tr.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(t_tr)
        T = t_tr.get_value

        # ---------- graph ----------
        def npos(i):
            return np.array([*NODES[i], 0])

        circles = VGroup()
        for i in range(N):
            c = Circle(radius=0.42, color=COOL2, stroke_width=2.5)
            c.move_to(npos(i))
            circles.add(c)

        def node_fill():
            cn = counts_at(T())
            g = VGroup()
            for i in range(N):
                g.add(Circle(radius=0.42, stroke_width=0, fill_color=WARM,
                             fill_opacity=min(0.95, 0.06 + 1.6 * cn[i])).move_to(npos(i)))
            return g
        fills = always_redraw(node_fill)

        edges = VGroup()
        for i, outs in ADJ.items():
            for j in outs:
                v = npos(j) - npos(i)
                u = v / np.linalg.norm(v)
                edges.add(Arrow(npos(i) + u * 0.45, npos(j) - u * 0.45,
                                color=GRAYM, stroke_width=2.5,
                                max_tip_length_to_length_ratio=0.09, buff=0))
        sink_lab = Text("sink", font_size=19, color=HOT).next_to(npos(5) + RIGHT * 0.3, RIGHT, buff=0.1)
        loop_lab = Text("loop", font_size=19, color=HOT).move_to([-3.3, -2.75, 0])

        def tokens():
            s, frac = step_of(T())
            f = rate_functions.smooth(frac)
            g = VGroup()
            for k in range(NTOK):
                a, b = npos(HIST[s][k]), npos(HIST[s + 1][k])
                p = a + (b - a) * f + np.array([*JIT[k], 0])
                g.add(Dot(p, radius=0.045, color=WARM2, fill_opacity=0.9))
            return g
        toks = always_redraw(tokens)

        # ---------- rank bar chart ----------
        BX, BY = 2.6, -2.6
        BW, BH = 0.5, 3.4

        def rankbars():
            cn = counts_at(T())
            g = VGroup()
            for i in range(N):
                x = BX + i * 0.62
                h = max(BH * cn[i], 1e-3)
                g.add(Rectangle(width=BW, height=h, fill_color=WARM, fill_opacity=0.85,
                                stroke_width=0).move_to([x, BY + h / 2, 0]))
            return g
        rbars = always_redraw(rankbars)
        bbase = Line([BX - 0.45, BY, 0], [BX + (N - 1) * 0.62 + 0.45, BY, 0],
                     color=GRAYM, stroke_width=2)
        blabs = VGroup(*[
            Text(str(i), font_size=18, color=GRAYM).move_to([BX + i * 0.62, BY - 0.25, 0])
            for i in range(N)
        ])
        btitle = MathTex(r"\text{rank vector } p", font_size=30).move_to(
            [BX + 3 * 0.62, BY + BH + 0.55, 0])
        # stationary targets (revealed in beat 2)
        targets = VGroup(*[
            Line([BX + i * 0.62 - 0.3, BY + BH * PSTAR[i], 0],
                 [BX + i * 0.62 + 0.3, BY + BH * PSTAR[i], 0],
                 color=COOL, stroke_width=3)
            for i in range(N)
        ])
        targ_lab = MathTex(r"p\,\hat G = p", font_size=30, color=COOL).move_to(
            [BX + 3 * 0.62, BY + BH + 0.05, 0])

        caps = [
            Text("a cloud of surfers follows random links — the sink swallows them, the loop traps them",
                 font_size=21).to_edge(DOWN, buff=0.12),
            Text("teleportation: with probability 1 − d jump to a random page (d = 0.85)",
                 font_size=22, color=COOL).to_edge(DOWN, buff=0.12),
            Text("brightness settles to the stationary rank — the dominant eigenvector, at rate set by λ₂",
                 font_size=21, color=WARM).to_edge(DOWN, buff=0.12),
            Text("final rank = long-run fraction of time the surfer spends on each page",
                 font_size=22).to_edge(DOWN, buff=0.12),
        ]

        self.add(fills, toks, rbars)
        self.play(FadeIn(VGroup(circles, edges, sink_lab, loop_lab, bbase, blabs, btitle)),
                  FadeIn(caps[0]), run_time=0.9)
        self.wait(NAIVE_T1 - T())
        self.play(FadeOut(caps[0]), FadeIn(caps[1]), run_time=0.5)
        self.wait(max(0.1, TELE_T0 - T() + 0.8))
        self.play(FadeIn(targets), FadeIn(targ_lab), run_time=0.6)
        self.play(FadeOut(caps[1]), FadeIn(caps[2]), run_time=0.5)
        self.wait(max(0.1, T_TOTAL - 2.6 - T()))
        # final: nodes sized by rank
        final_nodes = VGroup(*[
            Circle(radius=0.25 + 1.1 * PSTAR[i], color=WARM, stroke_width=3).move_to(npos(i))
            for i in range(N)
        ])
        self.play(FadeOut(caps[2]), FadeIn(caps[3]),
                  Transform(circles, final_nodes), run_time=0.9)
        self.wait(1.4)
