"""Entry #8 — Fractal attractor by stretch–thin–fold (ITFNS §5.4).

Compressible horseshoe (Cantor cross-section) vs. incompressible (fills box),
side by side. Density-image rendering.
"""

from manim import *
import numpy as np
from itfns import WARM, HOT, COOL, GRAYM, WARM2

RES = 260
NPTS = 90_000
N_ITER = 7
SIDE = 3.3


def horseshoe(p, area_loss):
    """Stack-baker: stretch x by 2, cut at x=0.5, thin each strip by c and stack.
    c=0.34 -> compressible (total height 2c<1, Cantor gap in y, fractal);
    c=0.5  -> incompressible (strips tile [0,1] exactly, fills the box)."""
    c = 0.34 if area_loss else 0.5
    x, y = p[:, 0], p[:, 1]
    left = x < 0.5
    nx = np.where(left, 2 * x, 2 * x - 1)            # stretch + cut
    ny = np.where(left, y * c, y * c + (1 - c))      # bottom strip / top strip
    return np.column_stack([nx, ny])


def colorize(dens, warm=True):
    d = np.clip(dens, 0, 1) ** 0.5
    if warm:
        rgb = np.stack([np.clip(d*1.7,0,1), np.clip(d*0.62*1.5,0,1), np.clip(d*0.29*1.2,0,1)], -1)
    else:
        rgb = np.stack([np.clip(d*0.36*1.4,0,1), np.clip(d*0.66*1.4,0,1), np.clip(d*1.0,0,1)], -1)
    return (rgb * 255).astype(np.uint8)


def dens_image(p):
    H, _, _ = np.histogram2d(p[:, 1], p[:, 0], bins=RES, range=[[0, 1], [0, 1]])
    H = H[::-1]
    return H / (NPTS / (RES * RES)) / 5.0


class FractalAttractorStretchFold(Scene):
    def construct(self):
        rng = np.random.default_rng(4)
        base = rng.uniform(0.05, 0.95, (NPTS, 2))

        comp = [base.copy()]
        inc = [base.copy()]
        for _ in range(N_ITER):
            comp.append(horseshoe(comp[-1], True))
            inc.append(horseshoe(inc[-1], False))

        prog = ValueTracker(0.0)
        LCX, RCX = -3.4, 1.9
        CY = 0.4

        def img_for(seq, cx, warm):
            def mk():
                it = min(int(np.floor(prog.get_value())), N_ITER)
                p = seq[it]
                im = ImageMobject(colorize(dens_image(p), warm))
                im.height = SIDE
                im.move_to([cx, CY, 0])
                return im
            return mk

        # use redraw-by-updater to avoid Image flicker
        imgL = ImageMobject(colorize(dens_image(comp[0]), True)); imgL.height = SIDE; imgL.move_to([LCX, CY, 0])
        imgR = ImageMobject(colorize(dens_image(inc[0]), False)); imgR.height = SIDE; imgR.move_to([RCX, CY, 0])

        def updL(m):
            it = min(int(round(prog.get_value())), N_ITER)
            nm = ImageMobject(colorize(dens_image(comp[it]), True)); nm.height = SIDE; nm.move_to([LCX, CY, 0])
            m.pixel_array = nm.pixel_array

        def updR(m):
            it = min(int(round(prog.get_value())), N_ITER)
            nm = ImageMobject(colorize(dens_image(inc[it]), False)); nm.height = SIDE; nm.move_to([RCX, CY, 0])
            m.pixel_array = nm.pixel_array
        imgL.add_updater(updL); imgR.add_updater(updR)

        boxL = Square(SIDE, color=GRAYM, stroke_width=2).move_to([LCX, CY, 0])
        boxR = Square(SIDE, color=GRAYM, stroke_width=2).move_to([RCX, CY, 0])
        titL = Text("compressible  λ₊+λ₋ < 0", font_size=20, color=WARM).next_to(boxL, UP, buff=0.15)
        titR = Text("incompressible  λ₊+λ₋ = 0", font_size=20, color=COOL).next_to(boxR, UP, buff=0.15)

        # dimension readouts
        lam_p, lam_m = np.log(2), np.log(0.34)
        df_comp = 1 + lam_p / abs(lam_m)
        df_read = always_redraw(lambda: MathTex(
            r"d_f = 1 + \frac{\lambda_+}{|\lambda_-|} = " + f"{df_comp:.2f}",
            font_size=26, color=WARM2).next_to(boxL, DOWN, buff=0.3))
        df_read2 = MathTex(r"d_f = 2\ \text{(fills the box)}", font_size=26,
                           color=COOL).next_to(boxR, DOWN, buff=0.3)

        iter_read = always_redraw(lambda: Text(
            f"iteration {min(int(round(prog.get_value())), N_ITER)}",
            font_size=20, color=GRAYM).move_to([-0.75, -3.0, 0]))

        cap = Text("each cycle: stretch along λ₊, thin faster along λ₋, fold back (horseshoe)",
                   font_size=22).to_edge(DOWN, buff=0.15)

        self.add(imgL, imgR)
        self.play(FadeIn(VGroup(boxL, boxR, titL, titR, df_read2)),
                  FadeIn(VGroup(df_read, iter_read)), FadeIn(cap), run_time=1.0)
        self.wait(0.6)
        self.play(FadeOut(cap), run_time=0.3)
        self.play(prog.animate.set_value(N_ITER), run_time=9.0, rate_func=linear)
        cap2 = Text("compressible flow concentrates onto a Cantor-layered fractal;  incompressible fills — fractal iff Σλᵢ < 0",
                    font_size=20, color=WARM).to_edge(DOWN, buff=0.15)
        self.play(FadeIn(cap2), run_time=0.5)
        self.wait(2.0)
        imgL.clear_updaters(); imgR.clear_updaters()
