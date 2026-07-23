"""Entry #13 — Water-filling for parallel Gaussian channels (ITFNS §3.5)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, COOL2, GRAYM

# uneven "noise floor" skyline sigma_i^2 (bin heights)
FLOORS = np.array([1.6, 0.5, 2.4, 1.1, 0.3, 1.9, 0.8, 2.1])
NB = len(FLOORS)
BW = 0.9
X0 = -5.2


class WaterFillingParallelGaussianChannels(Scene):
    def construct(self):
        level = ValueTracker(0.4)

        base_y = -2.2
        yscale = 1.5

        def yof(v):
            return base_y + v * yscale

        # noise-floor bins (muted gray, the "skyline")
        floors = VGroup()
        for i, f in enumerate(FLOORS):
            x = X0 + i * (BW + 0.15)
            floors.add(Rectangle(width=BW, height=f * yscale, fill_color=GRAYM,
                                 fill_opacity=0.55, stroke_color=GRAYM, stroke_width=1.5).move_to(
                [x, base_y + f * yscale / 2, 0]))
        floor_lab = VGroup(*[
            MathTex(r"\sigma_{" + str(i + 1) + r"}^2", font_size=20, color=GRAYM).move_to(
                [X0 + i * (BW + 0.15), base_y - 0.3, 0]) for i in range(NB)
        ])

        # water poured on top of each floor up to common level
        def water():
            L = level.get_value()
            g = VGroup()
            for i, f in enumerate(FLOORS):
                x = X0 + i * (BW + 0.15)
                if L > f:
                    h = (L - f) * yscale
                    g.add(Rectangle(width=BW, height=h, fill_color=COOL, fill_opacity=0.65,
                                    stroke_color=COOL2, stroke_width=1.5).move_to([x, yof(f) + h / 2, 0]))
            return g
        water_m = always_redraw(water)

        # rate tips (highlight above-water portion in warm)
        def tips():
            L = level.get_value()
            g = VGroup()
            for i, f in enumerate(FLOORS):
                x = X0 + i * (BW + 0.15)
                if L > f:
                    g.add(Line([x - BW / 2, yof(L), 0], [x + BW / 2, yof(L), 0],
                               color=WARM, stroke_width=4))
                else:
                    # dropped channel marker
                    g.add(Cross(Square(0.25), stroke_color=HOT, stroke_width=3).move_to(
                        [x, yof(f) + 0.25, 0]))
            return g
        tips_m = always_redraw(tips)

        water_line = always_redraw(lambda: DashedLine(
            [X0 - 0.7, yof(level.get_value()), 0], [X0 + NB * (BW + 0.15), yof(level.get_value()), 0],
            color=COOL2, stroke_width=2))
        water_lab = always_redraw(lambda: MathTex(
            r"\text{water level}", font_size=22, color=COOL2).next_to(
            [X0 + NB * (BW + 0.15) - 0.3, yof(level.get_value()), 0], RIGHT, buff=0.1))

        active_read = always_redraw(lambda: MathTex(
            r"\text{active channels: } " + f"{int(np.sum(level.get_value() > FLOORS))}" + f"/{NB}",
            font_size=26, color=WARM).move_to([3.3, 1.5, 0]))

        title = Text("water-filling: pour a distortion budget onto an uneven noise floor",
                     font_size=22).move_to([0, 3.25, 0])
        rate_note = VGroup(
            MathTex(r"R_i>0", font_size=22, color=WARM), Text("above water", font_size=16, color=WARM),
        ).arrange(RIGHT, buff=0.12).move_to([3.3, 2.4, 0])
        drop_note = VGroup(
            MathTex(r"R_i=0", font_size=22, color=HOT), Text("submerged → dropped", font_size=16, color=HOT),
        ).arrange(RIGHT, buff=0.12).move_to([3.3, 2.0, 0])

        self.play(FadeIn(VGroup(floors, floor_lab, title)), run_time=1.0)
        self.add(water_m, tips_m, water_line, water_lab, active_read)
        cap = Text("bins above the water line get rate; submerged bins are simply dropped",
                   font_size=21).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(VGroup(cap, rate_note, drop_note)), run_time=0.6)
        self.play(level.animate.set_value(2.6), run_time=5.0, rate_func=smooth)
        cap2 = Text("raise the budget: the level rises, more bins submerge and drop, total rate falls",
                    font_size=21, color=COOL2).to_edge(DOWN, buff=0.2)
        self.play(FadeOut(cap), FadeIn(cap2), run_time=0.5)
        self.wait(0.8)
        self.play(level.animate.set_value(0.9), run_time=3.5, rate_func=smooth)
        self.wait(1.4)
