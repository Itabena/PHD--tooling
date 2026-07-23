"""Entry #5 — Phase-space stretching, folding, coarse-grained entropy growth (ITFNS §5.3)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, GRAYM

EPS = 0.6              # grain / grid cell size
CX, CY = -3.4, 0.3    # center of phase-space panel
GRID_N = 9            # cells each direction (odd -> centered)


class PhaseSpaceStretching(Scene):
    def construct(self):
        t_tr = ValueTracker(0.0)

        # ---------- phase-space panel with fixed gray grid ----------
        # grid lines at half-integer multiples so the origin sits at a CELL CENTER
        grid = VGroup()
        half = GRID_N // 2
        edge = (half + 0.5) * EPS
        for i in range(-half - 1, half + 2):
            gx = CX + (i + 0.5) * EPS
            gy = CY + (i + 0.5) * EPS
            if abs(gx - CX) <= edge + 1e-6:
                grid.add(Line([gx, CY - edge, 0], [gx, CY + edge, 0],
                              color=GRAYM, stroke_width=1, stroke_opacity=0.5))
            if abs(gy - CY) <= edge + 1e-6:
                grid.add(Line([CX - edge, gy, 0], [CX + edge, gy, 0],
                              color=GRAYM, stroke_width=1, stroke_opacity=0.5))
        axes_arrows = VGroup(
            Arrow([CX - edge - 0.1, CY, 0], [CX + edge + 0.35, CY, 0],
                  color=GRAYM, stroke_width=2, buff=0, max_tip_length_to_length_ratio=0.04),
            Arrow([CX, CY - edge - 0.1, 0], [CX, CY + edge + 0.35, 0],
                  color=GRAYM, stroke_width=2, buff=0, max_tip_length_to_length_ratio=0.04),
        )
        xlab = MathTex(r"x\ (\dot x=\lambda x)", font_size=24, color=GRAYM).next_to(
            axes_arrows[0], RIGHT, buff=0.05)
        ylab = MathTex(r"y\ (\dot y=-\lambda y)", font_size=24, color=GRAYM).next_to(
            axes_arrows[1].get_top(), RIGHT, buff=0.12)

        # the evolving grain, centered on the origin: length L=eps*e^t, width w=eps*e^-t
        def grain():
            t = t_tr.get_value()
            L = min(EPS * np.exp(t), 2 * edge)
            w = EPS * np.exp(-t)
            rect = Rectangle(width=L, height=w, fill_color=WARM, fill_opacity=0.6,
                             stroke_color=WARM, stroke_width=2)
            rect.move_to([CX, CY, 0])
            return rect
        grain_m = always_redraw(grain)

        # cell index k spans [CX+(k-0.5)eps, CX+(k+0.5)eps]; k=0 is the central cell
        def nx_half(t):
            # cells a centered segment of length L=eps*e^t covers, each side of center
            L = EPS * np.exp(t)
            reach = max(0.0, (L - EPS) / 2)
            return min(int(np.ceil(reach / EPS - 1e-9)), half)

        def N_cells(t):
            w = EPS * np.exp(-t)
            nx = 2 * nx_half(t) + 1
            ny = 1 if w <= EPS else 2 * int(np.ceil((w - EPS) / (2 * EPS) - 1e-9)) + 1
            return nx * ny

        # highlight overlapped cells (translucent warm) — apparent area
        def lit_cells():
            t = t_tr.get_value()
            nx = nx_half(t)
            g = VGroup()
            for i in range(-nx, nx + 1):
                g.add(Square(EPS, fill_color=WARM, fill_opacity=0.16,
                             stroke_width=0).move_to([CX + i * EPS, CY, 0]))
            return g
        cells_m = always_redraw(lit_cells)

        # ---------- readouts (right side) ----------
        rx = 3.2
        true_read = MathTex(r"\text{true area}=L\cdot w=\epsilon^2", font_size=30, color=COOL)
        true_read.move_to([rx, 2.4, 0])
        true_box = SurroundingRectangle(true_read, color=COOL, buff=0.15, corner_radius=0.06)
        true_cap = Text("conserved (Liouville)", font_size=18, color=COOL).next_to(true_box, DOWN, buff=0.1)

        app_read = always_redraw(lambda: MathTex(
            r"\text{apparent}=N(\epsilon)\,\epsilon^2=" + f"{N_cells(t_tr.get_value())}" + r"\,\epsilon^2",
            font_size=30, color=WARM).move_to([rx, 1.1, 0]))

        ds_read = always_redraw(lambda: MathTex(
            r"\Delta S=\ln\frac{\text{apparent}}{\text{true}}=" +
            f"{np.log(max(N_cells(t_tr.get_value()),1)):.2f}",
            font_size=30, color=WARM2).move_to([rx, 0.0, 0]))

        # small entropy-vs-t plot
        ax = Axes(x_range=[0, 2.2, 1], y_range=[0, 2.2, 1], x_length=3.6, y_length=2.4,
                  axis_config={"color": GRAYM, "stroke_width": 2, "include_tip": False,
                               "font_size": 18}).move_to([rx, -2.0, 0])
        ax_lab = MathTex(r"\Delta S=\lambda t", font_size=24, color=WARM2).next_to(ax, UP, buff=0.1)
        ideal = ax.plot(lambda x: x, x_range=[0, 2.2], color=GRAYM, stroke_width=1.5)
        ideal_dash = DashedVMobject(ideal, num_dashes=22)
        dot = always_redraw(lambda: Dot(
            ax.c2p(min(t_tr.get_value(), 2.2),
                   min(np.log(max(N_cells(t_tr.get_value()), 1)), 2.2)),
            color=WARM2, radius=0.06))
        trace = VMobject().set_stroke(WARM2, 3)
        trace.add_updater(lambda m: m.set_points_as_corners([
            ax.c2p(tt, min(np.log(max(N_cells(tt), 1)), 2.2))
            for tt in np.linspace(0, min(t_tr.get_value(), 2.2), 40)
        ]) if t_tr.get_value() > 0.02 else m.set_points_as_corners([ax.c2p(0, 0), ax.c2p(0, 0)]))

        clock = always_redraw(lambda: MathTex(
            r"t=" + f"{t_tr.get_value():.2f}", font_size=28, color=WHITE).move_to([CX, CY - half * EPS - 0.7, 0]))

        self.add(grid, cells_m, grain_m)
        self.play(FadeIn(VGroup(axes_arrows, xlab, ylab, clock,
                                true_read, true_box, true_cap, ax, ax_lab, ideal_dash)),
                  FadeIn(VGroup(app_read, ds_read, dot)), run_time=1.0)
        self.add(trace)
        cap1 = Text("a resolution grain of side ε evolves under the exact flow",
                    font_size=22).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(cap1), run_time=0.5)
        self.wait(0.6)
        self.play(FadeOut(cap1), run_time=0.3)
        self.play(t_tr.animate.set_value(2.2), run_time=7.0, rate_func=linear)
        cap2 = Text("width shrank below one cell — vertical stops needing cells, horizontal keeps lighting them as eᵗ",
                    font_size=20, color=WARM).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(cap2), run_time=0.5)
        self.wait(1.8)
        # coda: reverse time briefly
        self.play(FadeOut(cap2), FadeIn(Text(
            "true area never changed — only the fixed-ε box can no longer contain the deformed set",
            font_size=20, color=COOL).to_edge(DOWN, buff=0.2)), run_time=0.5)
        self.play(t_tr.animate.set_value(0.4), run_time=2.5, rate_func=smooth)
        self.wait(1.2)
        trace.clear_updaters()
