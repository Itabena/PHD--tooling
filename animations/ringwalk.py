"""Entry #22 — Random walk on a ring relaxing to uniform (ITFNS Ex 4.4)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, COOL2, GRAYM


def relax(N, steps, q=0.5):
    """Return P(t) arrays for a symmetric NN walk on a ring of N sites."""
    P = np.zeros(N); P[0] = 1.0
    T = np.zeros((N, N))
    for i in range(N):
        T[(i + 1) % N, i] += q          # pure nearest-neighbour hop (column-stochastic)
        T[(i - 1) % N, i] += (1 - q)
    hist = [P.copy()]
    for _ in range(steps):
        P = T @ P
        hist.append(P.copy())
    return np.array(hist)


class RingWalkRelaxationFourierModes(Scene):
    def construct(self):
        step = ValueTracker(0)
        STEPS = 40
        H9 = relax(9, STEPS)
        H8 = relax(8, STEPS)

        def ring(N, center, hist, scale=1.0):
            R = 1.15 * scale
            sites = VGroup()
            for i in range(N):
                ang = np.pi / 2 + 2 * np.pi * i / N
                sites.add(Dot(center + R * np.array([np.cos(ang), np.sin(ang), 0]),
                              radius=0.12, color=GRAYM))
            ringline = Circle(radius=R, color=GRAYM, stroke_width=1.5, stroke_opacity=0.4).move_to(center)

            def bars():
                s = int(round(step.get_value()))
                s = min(s, len(hist) - 1)
                g = VGroup()
                for i in range(N):
                    ang = np.pi / 2 + 2 * np.pi * i / N
                    pos = center + R * np.array([np.cos(ang), np.sin(ang), 0])
                    val = hist[s][i]
                    g.add(Dot(pos, radius=0.11 + 0.7 * val, color=WARM,
                              fill_opacity=min(0.3 + 2 * val, 1.0)))
                return g
            return VGroup(ringline, sites), always_redraw(bars)

        c9 = np.array([-3.2, 1.15, 0])
        c8 = np.array([3.6, 1.15, 0])
        ring9, bars9 = ring(9, c9, H9, scale=0.92)
        ring8, bars8 = ring(8, c8, H8, scale=0.92)
        lab9 = Text("N = 9 (odd): relaxes to uniform", font_size=20, color=WARM).move_to(c9 + np.array([0, 1.85, 0]))
        lab8 = Text("N = 8 (even): a checkerboard rides forever", font_size=20, color=HOT).move_to(c8 + np.array([0, 1.85, 0]))

        # Fourier mode sidebar for N=9
        def mode_amp(N, hist, n, s):
            k = 2 * np.pi * n / N
            lam = np.cos(k)  # eigenvalue of symmetric NN walk (q=1/2): cos k
            c0 = np.abs(np.sum(hist[0] * np.exp(-1j * k * np.arange(N)))) / N
            return c0 * abs(lam) ** s

        BX, BY0, BH = -5.9, -3.3, 1.7
        modes = [0, 1, 2, 3, 4]
        mode_cols = [GRAYM, WARM, WARM2, COOL, COOL2]

        def mode_bars():
            s = int(round(step.get_value()))
            g = VGroup()
            for j, n in enumerate(modes):
                amp = mode_amp(9, H9, n, s)
                h = max(BH * amp * 2.2, 1e-3)
                g.add(Rectangle(width=0.32, height=h, fill_color=mode_cols[j], fill_opacity=0.85,
                                stroke_width=0).move_to([BX + j * 0.46, BY0 + h / 2, 0]))
            return g
        mode_m = always_redraw(mode_bars)
        mode_title = MathTex(r"\text{modes } |c_n\lambda_n^t|,\ \lambda_n=\cos k_n,\ \tau\propto N^2",
                             font_size=22, color=GRAYM).move_to([BX + 1.6, BY0 + BH + 0.35, 0])

        clock = always_redraw(lambda: Text(
            f"step {int(round(step.get_value()))}", font_size=20, color=GRAYM).move_to([3.6, -2.7, 0]))

        self.add(bars9, bars8, mode_m)
        self.play(FadeIn(VGroup(ring9, ring8, lab9, lab8, mode_title, clock)), run_time=1.0)
        cap = Text("start from a single lit site; each step hops ±1 around the ring",
                   font_size=21).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(cap), run_time=0.5)
        self.play(step.animate.set_value(STEPS), run_time=8.0, rate_func=linear)
        cap2 = Text("odd N smooths to uniform (slowest mode sets τ); even N keeps a period-2 checkerboard (λ = −1) forever",
                    font_size=19, color=HOT).to_edge(DOWN, buff=0.2)
        self.play(FadeOut(cap), FadeIn(cap2), run_time=0.5)
        self.wait(1.8)
