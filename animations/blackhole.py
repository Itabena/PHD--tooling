"""Entry #19 — Black hole: Hawking pairs, area law, Bekenstein bound (ITFNS §6.6)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, COOL2, GRAYM, VIOLET


class BlackHoleAreaLawBekenstein(Scene):
    def construct(self):
        r_tr = ValueTracker(1.3)     # horizon radius
        hole_c = np.array([-3.3, 0.4, 0])

        def hole():
            r = r_tr.get_value()
            disk = Circle(radius=r, color=BLACK, fill_color="#050505", fill_opacity=1,
                          stroke_width=0).move_to(hole_c)
            ring = Circle(radius=r, color=WARM2, stroke_width=4).move_to(hole_c)
            ring2 = Circle(radius=r, color=WARM, stroke_width=9, stroke_opacity=0.3).move_to(hole_c)
            return VGroup(ring2, disk, ring)
        hole_m = always_redraw(hole)
        rh_lab = always_redraw(lambda: MathTex(
            r"r_h=\frac{2GM}{c^2}", font_size=26, color=WARM2).move_to(hole_c + np.array([0, -2.6, 0])))

        # ---------- Hawking pairs on the ring ----------
        rng = np.random.default_rng(3)
        pair_angles = rng.uniform(0, 2 * np.pi, 7)

        def pairs():
            r = r_tr.get_value()
            g = VGroup()
            for a in pair_angles:
                base = hole_c + r * np.array([np.cos(a), np.sin(a), 0])
                out = base + 0.5 * np.array([np.cos(a), np.sin(a), 0])
                inn = base - 0.35 * np.array([np.cos(a), np.sin(a), 0])
                g.add(Dot(out, radius=0.06, color=WARM))       # escaping (warm)
                g.add(Dot(inn, radius=0.06, color=COOL))       # infalling (cool)
                g.add(Line(inn, out, color=VIOLET, stroke_width=1, stroke_opacity=0.4))
            return g
        pairs_m = always_redraw(pairs)
        hawking_lab = Text("Hawking pairs: the entanglement across the horizon is the entropy",
                           font_size=18, color=VIOLET).move_to([-3.3, 3.3, 0])

        # ---------- area vs volume bars ----------
        BX, BY0, BH = 1.6, -2.6, 4.4
        r0 = 1.3

        def area_bar():
            r = r_tr.get_value()
            h = min(BH * (r / 2.4) ** 2, BH)
            return Rectangle(width=0.7, height=max(h, 1e-3), fill_color=WARM, fill_opacity=0.85,
                             stroke_width=0).move_to([BX, BY0 + h / 2, 0])
        area_m = always_redraw(area_bar)

        def vol_bar():
            r = r_tr.get_value()
            h = min(BH * (r / 2.4) ** 3, BH)
            return Rectangle(width=0.7, height=max(h, 1e-3), fill_color=COOL, fill_opacity=0.5,
                             stroke_width=0).move_to([BX + 1.5, BY0 + h / 2, 0])
        vol_m = always_redraw(vol_bar)
        bar_axis = Line([BX - 0.5, BY0, 0], [BX + 2.0, BY0, 0], color=GRAYM, stroke_width=2)
        area_lab = VGroup(MathTex(r"\text{area}\propto r_h^2", font_size=22, color=WARM),
                          Text("= entropy", font_size=15, color=WARM)).arrange(DOWN, buff=0.05).scale(0.9).move_to([BX, BY0 - 0.6, 0])
        vol_lab = MathTex(r"\text{volume}\propto r_h^3", font_size=22, color=COOL).scale(0.9).move_to([BX + 1.5, BY0 - 0.55, 0])
        s_read = always_redraw(lambda: MathTex(
            r"S_{BH}\sim r_h^2/l_P^2", font_size=26, color=WARM2).move_to([BX + 0.7, BY0 + BH + 0.4, 0]))

        # ---------- right: entropy readouts ----------
        ext_lab = MathTex(r"S\le \frac{2\pi k R E}{\hbar c}\ \text{(Bekenstein)}",
                          font_size=26, color=WARM2).move_to([4.7, 1.5, 0])

        self.play(FadeIn(hole_m), FadeIn(VGroup(rh_lab, hawking_lab, bar_axis, area_lab, vol_lab)),
                  run_time=1.0)
        self.add(pairs_m, area_m, vol_m, s_read)
        cap1 = Text("entropy scales with horizon AREA, not volume — the holographic surprise",
                    font_size=21, color=WARM).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(cap1), run_time=0.5)
        self.play(r_tr.animate.set_value(2.1), run_time=4.0, rate_func=smooth)
        self.wait(0.6)

        # ---------- Beat 2: drop a body in, horizon swells ----------
        cap2 = Text("drop in a body of energy E and entropy S — it vanishes, but the horizon swells to pay for it",
                    font_size=20, color=HOT).to_edge(DOWN, buff=0.25)
        self.play(FadeOut(cap1), FadeIn(cap2), FadeIn(ext_lab), run_time=0.5)
        parcel = VGroup(
            Dot([1.0, 2.4, 0], radius=0.16, color=HOT),
            Text("E, S", font_size=16, color=HOT).move_to([1.0, 2.4, 0]).shift(UP * 0.32),
        )
        self.play(FadeIn(parcel), run_time=0.4)
        self.play(parcel.animate.move_to(hole_c).scale(0.2), run_time=1.2)
        self.play(FadeOut(parcel), r_tr.animate.set_value(2.4), run_time=1.2)
        cap3 = Text("the horizon's area-entropy gain always covers the entropy that fell in — S ≤ RE/ħc",
                    font_size=20, color=WARM).to_edge(DOWN, buff=0.25)
        self.play(FadeOut(cap2), FadeIn(cap3), run_time=0.5)
        self.wait(1.2)
        final = Text("maximal entropy for a size = a black hole; information on the boundary, not the bulk (holography)",
                     font_size=19, color=WARM2).to_edge(DOWN, buff=0.25)
        self.play(FadeOut(cap3), FadeIn(final), run_time=0.5)
        self.wait(1.6)
