"""Entry #20 — Entanglement entropy: a part with more entropy than the whole (ITFNS §6.3).

Sweeps the amplitude a of the pure two-qubit state a|00> + b|11>.
House style: warm = growth, cool = conserved/whole, boxed constant-value
readouts, dark background, swept parameter on a slider.
"""

from manim import *
import numpy as np

WARM = "#FF9E4A"   # S(rho_A) — grows
WARM2 = "#FFC94A"  # S(rho_B) — grows
HOT = "#FF5C5C"    # mutual information I
COOL = "#5CA8FF"   # the whole / conserved
GRAYM = "#9A9A9A"  # muted gray

UNIT = 1.55        # scene units per bit
BASE_Y = -2.75     # baseline of the bar chart
SQ2 = 1 / np.sqrt(2)


def H2(x: float) -> float:
    """Binary entropy in bits."""
    if x <= 1e-9 or x >= 1 - 1e-9:
        return 0.0
    return float(-x * np.log2(x) - (1 - x) * np.log2(1 - x))


class EntanglementEntropyPartVsWhole(Scene):
    def construct(self):
        a_tr = ValueTracker(1.0)
        prob = lambda: a_tr.get_value() ** 2          # a^2
        SA = lambda: H2(prob())                        # S(rho_A) = S(rho_B)

        # ---------- top: the whole-system glyph ----------
        state = MathTex(
            r"|\psi_{AB}\rangle = a\,|00\rangle + b\,|11\rangle",
            font_size=40,
        )
        state.to_edge(UP, buff=0.35)
        state_box = SurroundingRectangle(state, color=COOL, buff=0.22, corner_radius=0.08)
        whole_cap = Text("the whole system AB — pure", font_size=20, color=COOL)
        whole_cap.next_to(state_box, DOWN, buff=0.1)

        # ---------- left: amplitude slider ----------
        slider = NumberLine(
            x_range=[0, 1, 0.5], length=4.2,
            include_numbers=True, font_size=24, color=GRAYM,
        )
        slider.move_to([-4.0, 1.15, 0])
        slider_label = MathTex(r"\text{amplitude } a", font_size=30)
        slider_label.next_to(slider, UP, buff=0.45).shift(LEFT * 1.4)
        sq2_tick = Line(UP * 0.1, DOWN * 0.1, color=GRAYM).move_to(slider.n2p(SQ2))
        sq2_lab = MathTex(r"\tfrac{1}{\sqrt{2}}", font_size=24, color=GRAYM)
        sq2_lab.next_to(sq2_tick, UP, buff=0.08)
        knob = always_redraw(
            lambda: Dot(slider.n2p(a_tr.get_value()), color=WHITE, radius=0.09)
        )
        b_read = always_redraw(
            lambda: MathTex(
                r"b=\sqrt{1-a^2}=" + f"{np.sqrt(1 - prob()):.2f}",
                font_size=28, color=GRAYM,
            ).next_to(slider, DOWN, buff=0.4)
        )

        # ---------- left-lower: the reduced matrix as two blocks ----------
        rho_title = MathTex(
            r"\rho_A = \mathrm{diag}(a^2,\,b^2)", font_size=32
        ).move_to([-4.0, -0.9, 0])
        blk_base = -2.75
        blk_h = 1.35  # height of a probability-1 block

        def make_block(x, p_fn, color, lab_tex):
            bar = always_redraw(
                lambda: Rectangle(
                    width=0.75, height=max(blk_h * p_fn(), 1e-3),
                    fill_color=color, fill_opacity=0.85, stroke_width=1,
                    stroke_color=color,
                ).move_to([x, blk_base + blk_h * p_fn() / 2, 0])
            )
            lab = MathTex(lab_tex, font_size=28).move_to([x, blk_base - 0.3, 0])
            return bar, lab

        blkA, blkA_lab = make_block(-4.6, prob, COOL, r"a^2")
        blkB, blkB_lab = make_block(-3.4, lambda: 1 - prob(), COOL, r"b^2")

        # ---------- right: entropy bar chart ----------
        xs = {"AB": 0.7, "A": 2.2, "B": 3.7, "I": 5.5}
        vals = {
            "AB": lambda: 0.0,
            "A": SA,
            "B": SA,
            "I": lambda: 2 * SA(),
        }
        cols = {"AB": COOL, "A": WARM, "B": WARM2, "I": HOT}

        yaxis = Line([xs["AB"] - 0.85, BASE_Y, 0], [xs["AB"] - 0.85, BASE_Y + 2 * UNIT + 0.25, 0],
                     color=GRAYM, stroke_width=2)
        yticks = VGroup()
        for bits in (1, 2):
            t = Line(LEFT * 0.07, RIGHT * 0.07, color=GRAYM).move_to(
                [xs["AB"] - 0.85, BASE_Y + bits * UNIT, 0])
            tl = Text(f"{bits}", font_size=20, color=GRAYM).next_to(t, LEFT, buff=0.1)
            yticks.add(t, tl)
        y_unit_lab = Text("bits", font_size=20, color=GRAYM).next_to(yaxis, UP, buff=0.1)
        baseline = Line([xs["AB"] - 0.85, BASE_Y, 0], [xs["I"] + 0.8, BASE_Y, 0],
                        color=GRAYM, stroke_width=2)

        bars, readouts = VGroup(), VGroup()
        for k in xs:
            bars.add(always_redraw(lambda k=k: Rectangle(
                width=0.8, height=max(UNIT * vals[k](), 1e-3),
                fill_color=cols[k], fill_opacity=0.9,
                stroke_width=1, stroke_color=cols[k],
            ).move_to([xs[k], BASE_Y + UNIT * vals[k]() / 2, 0])))
            readouts.add(always_redraw(lambda k=k: DecimalNumber(
                vals[k](), num_decimal_places=2, font_size=26, color=cols[k],
            ).move_to([xs[k], BASE_Y + UNIT * vals[k]() + 0.25, 0])))

        bar_labels = VGroup(
            MathTex(r"S(\rho_{AB})", font_size=30, color=COOL),
            MathTex(r"S(\rho_A)", font_size=30, color=WARM),
            MathTex(r"S(\rho_B)", font_size=30, color=WARM2),
            MathTex(r"I(A{:}B)", font_size=30, color=HOT),
        )
        for lab, k in zip(bar_labels, xs):
            lab.move_to([xs[k], BASE_Y - 0.35, 0])

        # boxed constant-value readout for the conserved quantity
        zero_read = MathTex(r"S(\rho_{AB}) = 0", font_size=30, color=COOL)
        zero_read.move_to([xs["AB"], 1.3, 0])
        zero_box = SurroundingRectangle(zero_read, color=COOL, buff=0.14, corner_radius=0.06)
        zero_cap = Text("the whole knows everything", font_size=19, color=COOL)
        zero_cap.next_to(zero_box, UP, buff=0.12)
        zero_arrow = Arrow(
            zero_box.get_bottom() + DOWN * 0.05, [xs["AB"], BASE_Y + 0.45, 0],
            color=COOL, stroke_width=2, max_tip_length_to_length_ratio=0.06,
        ).set_opacity(0.6)

        # dashed classical ceiling across the I bar
        ceiling = always_redraw(lambda: DashedLine(
            [xs["I"] - 0.75, BASE_Y + UNIT * max(SA(), 1e-3), 0],
            [xs["I"] + 0.75, BASE_Y + UNIT * max(SA(), 1e-3), 0],
            color=GRAYM, dash_length=0.08,
        ))
        ceil_lab = Text("classical ceiling", font_size=18, color=GRAYM)
        ceil_lab2 = MathTex(r"\min(S_A, S_B)", font_size=24, color=GRAYM)
        ceil_group = VGroup(ceil_lab, ceil_lab2).arrange(DOWN, buff=0.08)
        ceil_group.move_to([xs["I"], 1.45, 0])

        # ---------- captions (bottom) ----------
        cap1 = Text("a = 1: a product state — no entanglement, every entropy zero",
                    font_size=22).to_edge(DOWN, buff=0.25)
        cap2 = Text("maximal entanglement: each part holds a full bit the whole doesn't have",
                    font_size=22, color=WARM).to_edge(DOWN, buff=0.25)
        cap3 = Text("I = 2 bits — twice the classical ceiling: impossible for any classical pair",
                    font_size=22, color=HOT).to_edge(DOWN, buff=0.25)
        cap4 = Text("and back: as b → 0 the parts purify again — entanglement was the whole story",
                    font_size=22).to_edge(DOWN, buff=0.25)

        # ---------- assemble ----------
        static = VGroup(
            state, state_box, whole_cap,
            slider, slider_label, sq2_tick, sq2_lab,
            rho_title, blkA_lab, blkB_lab,
            yaxis, yticks, y_unit_lab, baseline, bar_labels,
            zero_read, zero_box, zero_cap, zero_arrow, ceil_group,
        )
        self.add(knob, b_read, blkA, blkB, bars, readouts, ceiling)
        self.play(FadeIn(static), run_time=1.0)
        self.play(FadeIn(cap1), run_time=0.5)
        self.wait(1.0)

        # sweep to maximal entanglement
        self.play(FadeOut(cap1), run_time=0.3)
        self.play(a_tr.animate.set_value(SQ2), run_time=3.5, rate_func=smooth)
        self.play(FadeIn(cap2), run_time=0.4)
        self.wait(1.4)
        self.play(FadeOut(cap2), FadeIn(cap3), run_time=0.4)
        self.wait(1.8)

        # sweep on to b -> 1 (a -> 0): entropies fall back
        self.play(FadeOut(cap3), FadeIn(cap4), run_time=0.4)
        self.play(a_tr.animate.set_value(0.0), run_time=3.5, rate_func=smooth)
        self.wait(1.2)
        self.play(FadeOut(cap4), run_time=0.4)
