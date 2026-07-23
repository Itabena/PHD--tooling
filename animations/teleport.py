"""Entry #17 — Quantum teleportation: spending a banked entangled pair (ITFNS §6.5)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, COOL2, GRAYM, VIOLET


def bloch(center, theta, phi=0.0, color=WARM, blur=False, r=0.55):
    """A small Bloch-sphere glyph with an arrow at polar angle theta."""
    circ = Circle(radius=r, color=GRAYM, stroke_width=1.5, stroke_opacity=0.6).move_to(center)
    eq = Ellipse(width=2 * r, height=0.5 * r, color=GRAYM, stroke_width=1,
                 stroke_opacity=0.4).move_to(center)
    tip = center + r * np.array([np.sin(theta) * np.cos(phi), np.cos(theta), 0])
    arr = Arrow(center, tip, color=color, buff=0, stroke_width=4,
                max_tip_length_to_length_ratio=0.25)
    g = VGroup(circ, eq, arr)
    if blur:
        g.set_opacity(0.35)
    return g


class QuantumTeleportationBankedPair(Scene):
    def construct(self):
        alice_x, bob_x = -4.3, 4.3
        top_y = 1.6

        alice_lab = Text("Alice", font_size=26, color=WARM2).move_to([alice_x, 3.2, 0])
        bob_lab = Text("Bob", font_size=26, color=COOL2).move_to([bob_x, 3.2, 0])

        # ---------- ledger ----------
        led_y = -2.5
        ledger_cells = VGroup(*[
            Square(0.5, color=VIOLET, stroke_width=2).move_to([-1.0 + i * 0.6, led_y, 0])
            for i in range(3)
        ])
        for c in ledger_cells:
            c.set_fill(VIOLET, 0.35)
        ledger_lab = Text("banked entangled pairs", font_size=20, color=VIOLET).next_to(
            ledger_cells, LEFT, buff=0.3)

        # ---------- Beat 1: resource + unknown qubit ----------
        link = Line([alice_x + 0.6, top_y, 0], [bob_x - 0.6, top_y, 0],
                    color=VIOLET, stroke_width=3)
        link_glow = Line([alice_x + 0.6, top_y, 0], [bob_x - 0.6, top_y, 0],
                         color=VIOLET, stroke_width=8, stroke_opacity=0.25)
        a1 = LabeledDot(Text("A₁", font_size=16, color=BLACK), color=VIOLET).move_to([alice_x + 0.6, top_y, 0])
        b1 = LabeledDot(Text("B₁", font_size=16, color=BLACK), color=VIOLET).move_to([bob_x - 0.6, top_y, 0])
        link_lab = Text("shared Bell pair (a known resource)", font_size=19, color=VIOLET).move_to([0, top_y + 0.55, 0])

        theta0 = 0.9
        a0 = bloch([alice_x, -0.3, 0], theta0, color=WARM, blur=True)
        a0_lab = MathTex(r"|\psi\rangle=\alpha|0\rangle+\beta|1\rangle", font_size=24,
                         color=WARM).next_to(a0, DOWN, buff=0.15)
        a0_note = Text("unknown direction (hidden)", font_size=17, color=GRAYM).next_to(a0, UP, buff=0.1)

        self.play(FadeIn(VGroup(alice_lab, bob_lab, ledger_cells, ledger_lab)), run_time=0.8)
        self.play(Create(link), FadeIn(VGroup(link_glow, a1, b1, link_lab)), run_time=1.0)
        self.play(FadeIn(VGroup(a0, a0_lab, a0_note)), run_time=0.8)
        cap1 = Text("Alice holds an unknown qubit and shares a Bell pair with Bob",
                    font_size=21).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(cap1), run_time=0.5)
        self.wait(1.0)

        # ---------- Beat 2: Bell measurement ----------
        cap2 = Text("Alice makes a joint Bell measurement — one of four equally likely outcomes",
                    font_size=21, color=WARM2).to_edge(DOWN, buff=0.3)
        self.play(FadeOut(cap1), FadeIn(cap2), run_time=0.5)
        # merge a0 and a1 into an outcome box
        outcomes = VGroup(*[
            Square(0.55, color=WARM2, stroke_width=2).move_to([alice_x - 0.9 + i * 0.62, -0.3, 0])
            for i in range(4)
        ])
        outcome_labs = VGroup(*[
            Text(s, font_size=15, color=WARM2).move_to(outcomes[i])
            for i, s in enumerate(["00", "01", "10", "11"])
        ])
        chosen = 2  # "10"
        self.play(a0.animate.move_to([alice_x - 0.3, -0.3, 0]),
                  a1.animate.move_to([alice_x - 0.3, -0.3, 0]),
                  FadeOut(VGroup(a0_lab, a0_note)), run_time=0.8)
        self.play(FadeOut(a0), FadeOut(a1), FadeIn(outcomes), FadeIn(outcome_labs), run_time=0.6)
        self.play(outcomes[chosen].animate.set_fill(WARM2, 0.8),
                  Flash(outcomes[chosen], color=WARM2), run_time=0.7)
        marginal = Text("Alice's marginal stays 50/50 — she learns nothing about the direction",
                        font_size=18, color=GRAYM).move_to([alice_x, -1.5, 0])
        self.play(FadeIn(marginal), run_time=0.5)
        # Bob's qubit snaps to a rotated arrow; link goes dark, ledger drops
        b_arrow = bloch([bob_x, -0.3, 0], theta0 + 1.8, color=COOL, r=0.55)
        self.play(link.animate.set_opacity(0.15), link_glow.animate.set_opacity(0),
                  FadeIn(b_arrow), ledger_cells[2].animate.set_fill(BLACK, 0).set_stroke(GRAYM, 1),
                  run_time=0.9)
        bob_note = Text("Bob's qubit: original, up to one of 4 fixed rotations", font_size=17,
                        color=COOL).next_to(b_arrow, DOWN, buff=0.15)
        self.play(FadeIn(bob_note), run_time=0.4)
        self.wait(1.2)

        # ---------- Beat 3: 2 classical bits + correction ----------
        cap3 = Text("Alice sends 2 classical bits; Bob applies the matching correction",
                    font_size=21, color=COOL2).to_edge(DOWN, buff=0.3)
        self.play(FadeOut(cap2), FadeOut(marginal), FadeIn(cap3), run_time=0.5)
        bits = VGroup(Text("1", font_size=24, color=WHITE), Text("0", font_size=24, color=WHITE)).arrange(RIGHT, buff=0.2)
        bits.move_to([alice_x + 0.5, 0.6, 0])
        wire = DashedLine([alice_x + 1.0, 0.6, 0], [bob_x - 1.0, 0.6, 0], color=GRAYM, stroke_width=1.5)
        self.play(Create(wire), FadeIn(bits), run_time=0.5)
        self.play(bits.animate.move_to([bob_x - 0.5, 0.6, 0]), run_time=1.3, rate_func=linear)
        # Bob corrects: arrow rotates to exact original
        b_final = bloch([bob_x, -0.3, 0], theta0, color=WARM, r=0.55)
        self.play(Transform(b_arrow, b_final), FadeOut(bob_note), run_time=1.0)
        b_final_lab = Text("exact original, reconstructed", font_size=18, color=WARM).next_to(
            b_arrow, DOWN, buff=0.15)
        self.play(FadeIn(b_final_lab), run_time=0.4)

        final = MathTex(r"S(\rho_{AB}\mid\rho_B)<0:\ \text{one banked teleportation, now spent}",
                        font_size=26, color=WHITE).to_edge(DOWN, buff=0.3)
        self.play(FadeOut(cap3), FadeIn(final), run_time=0.6)
        self.wait(1.8)
