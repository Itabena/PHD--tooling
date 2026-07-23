"""Entry #1 — Maxwell's demon: sorting, then the erasure bill (ITFNS §3.2)."""

from manim import *
import numpy as np
from itfns import WARM, WARM2, HOT, COOL, GRAYM, VIOLET

# box geometry
BX0, BX1 = -4.6, 4.6
BY0, BY1 = 0.7, 3.6
GAP0, GAP1 = 1.3, 3.0          # door opening in the middle wall
DT = 1 / 30
T_TOTAL = 17.5
SORT_T0, SORT_T1 = 0.5, 9.2      # demon active
ERASE_T0, ERASE_T1 = 11.0, 14.0  # tape reset
N_FAST, N_SLOW = 14, 14
TAPE_N = 12


def simulate():
    rng = np.random.default_rng(27)
    n = N_FAST + N_SLOW
    fast = np.array([True] * N_FAST + [False] * N_SLOW)
    pos = np.column_stack([
        rng.uniform(BX0 + 0.3, BX1 - 0.3, n),
        rng.uniform(BY0 + 0.3, BY1 - 0.3, n),
    ])
    # keep initial positions off the wall
    pos[np.abs(pos[:, 0]) < 0.35, 0] += 0.7
    speed = np.where(fast, 3.2, 1.6)
    ang = rng.uniform(0.2, 0.75, n)
    sx = rng.choice([-1, 1], n)
    sy = rng.choice([-1, 1], n)
    vel = np.column_stack([np.cos(ang) * sx, np.sin(ang) * sy]) * speed[:, None]
    steps = int(T_TOTAL / DT) + 2
    traj = np.zeros((steps, n, 2))
    crossings = []          # (time, molecule index)
    for s in range(steps):
        t = s * DT
        traj[s] = pos
        if s % 15 == 7:  # gentle direction jitter: stand-in for collisions
            th = rng.normal(0, 0.4, n)
            c, si = np.cos(th), np.sin(th)
            vel = np.column_stack([vel[:, 0] * c - vel[:, 1] * si,
                                   vel[:, 0] * si + vel[:, 1] * c])
        new = pos + vel * DT
        # outer walls
        for i in range(n):
            if new[i, 0] < BX0 + 0.15 or new[i, 0] > BX1 - 0.15:
                vel[i, 0] *= -1
            if new[i, 1] < BY0 + 0.15 or new[i, 1] > BY1 - 0.15:
                vel[i, 1] *= -1
        new = pos + vel * DT
        # middle wall / demon door
        for i in range(n):
            if (pos[i, 0] < 0) != (new[i, 0] < 0):  # attempts to cross
                in_gap = GAP0 < new[i, 1] < GAP1
                allowed = (
                    SORT_T0 < t < SORT_T1 and in_gap and
                    ((fast[i] and vel[i, 0] > 0) or (not fast[i] and vel[i, 0] < 0))
                )
                if allowed:
                    crossings.append(t)
                else:
                    vel[i, 0] *= -1
                    new[i] = pos[i] + vel[i] * DT
        pos = new
    return traj, fast, np.array(crossings)


TRAJ, FAST, CROSS = simulate()


def bits_at(t):
    return int(np.searchsorted(CROSS, t))


def sortedness(t):
    s = min(int(t / DT), TRAJ.shape[0] - 1)
    correct = np.sum((TRAJ[s, :, 0] > 0) == FAST)
    return max(0.0, (correct / len(FAST) - 0.5) / 0.5)


class MaxwellDemon(Scene):
    def construct(self):
        t_tr = ValueTracker(0.0)
        t_tr.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(t_tr)
        T = t_tr.get_value

        # ---------- the box ----------
        box = Rectangle(width=BX1 - BX0, height=BY1 - BY0, color=GRAYM,
                        stroke_width=2.5).move_to([(BX0 + BX1) / 2, (BY0 + BY1) / 2, 0])
        wall_lo = Line([0, BY0, 0], [0, GAP0, 0], color=GRAYM, stroke_width=2.5)
        wall_hi = Line([0, GAP1, 0], [0, BY1, 0], color=GRAYM, stroke_width=2.5)
        door = DashedLine([0, GAP0, 0], [0, GAP1, 0], color=VIOLET, dash_length=0.07)
        demon = VGroup(
            Circle(radius=0.15, color=VIOLET, fill_opacity=1, fill_color=VIOLET),
            Dot([-0.05, 0.03, 0], radius=0.025, color=BLACK),
            Dot([0.05, 0.03, 0], radius=0.025, color=BLACK),
        ).move_to([0, BY1 + 0.28, 0])
        demon_lab = Text("demon", font_size=18, color=VIOLET).next_to(demon, RIGHT, buff=0.12)
        side_lab_L = Text("slow / cold", font_size=19, color=COOL).move_to([BX0 + 1.1, BY1 - 0.25, 0])
        side_lab_R = Text("fast / hot", font_size=19, color=WARM).move_to([BX1 - 1.1, BY1 - 0.25, 0])

        def mol_dots():
            s = min(int(T() / DT), TRAJ.shape[0] - 1)
            g = VGroup()
            for i in range(len(FAST)):
                g.add(Dot([TRAJ[s, i, 0], TRAJ[s, i, 1], 0], radius=0.085,
                          color=WARM if FAST[i] else COOL))
            return g
        mols = always_redraw(mol_dots)

        # ---------- memory tape ----------
        tape_lab = Text("memory tape", font_size=19, color=GRAYM).move_to([-5.55, -0.35, 0])
        cell_w = 0.62

        def tape():
            b = bits_at(T())
            filled = min(b, TAPE_N)
            if T() > ERASE_T0:
                frac = min(1.0, (T() - ERASE_T0) / (ERASE_T1 - ERASE_T0))
                filled = int(round(min(b, TAPE_N) * (1 - frac)))
            g = VGroup()
            for k in range(TAPE_N):
                x = -3.6 + k * cell_w
                sq = Square(0.5, color=GRAYM, stroke_width=2).move_to([x, -0.35, 0])
                txt = Text("1" if k < filled else "0", font_size=22,
                           color=WARM2 if k < filled else GRAYM).move_to([x, -0.35, 0])
                if k < filled:
                    sq.set_fill(WARM2, opacity=0.25)
                g.add(sq, txt)
            return g
        tape_g = always_redraw(tape)
        bit_read = always_redraw(lambda: MathTex(
            r"I = " + f"{bits_at(T())}" + r"\ \text{bits}", font_size=30, color=WARM2
        ).move_to([4.6, -0.35, 0]))

        # ---------- ledger bars ----------
        BAR_Y = -2.95
        BAR_H = 1.55
        n_final = bits_at(1e9)

        def W_extract(t):
            return BAR_H * bits_at(t) / n_final

        def S_box(t):
            return BAR_H * (1 - 0.75 * sortedness(t))

        def W_erase(t):
            if t < ERASE_T0:
                return 0.0
            frac = min(1.0, (t - ERASE_T0) / (ERASE_T1 - ERASE_T0))
            return W_extract(t) * frac

        def bar(x, h_fn, color):
            return always_redraw(lambda: Rectangle(
                width=0.85, height=max(h_fn(T()), 1e-3), fill_color=color,
                fill_opacity=0.85, stroke_width=1, stroke_color=color,
            ).move_to([x, BAR_Y + max(h_fn(T()), 1e-3) / 2, 0]))

        bars = VGroup(bar(-4.3, S_box, COOL), bar(-2.4, W_extract, WARM),
                      bar(-0.5, W_erase, HOT))
        ledger_base = Line([-5.0, BAR_Y, 0], [0.4, BAR_Y, 0], color=GRAYM, stroke_width=2)
        bar_labs = VGroup(
            MathTex(r"S_{\text{box}}", font_size=27, color=COOL).move_to([-4.3, BAR_Y - 0.32, 0]),
            MathTex(r"T\,I\ \text{extractable}", font_size=27, color=WARM).move_to([-2.4, BAR_Y - 0.32, 0]),
            MathTex(r"W_{\text{eras}}", font_size=27, color=HOT).move_to([-0.5, BAR_Y - 0.32, 0]),
        )
        ledger_lab = Text("the ledger", font_size=19, color=GRAYM).move_to([-4.6, BAR_Y + BAR_H + 0.35, 0])

        net = always_redraw(lambda: MathTex(
            r"\text{net} = TI - W_{\text{eras}} = " +
            f"{(W_extract(T()) - W_erase(T())) / BAR_H * n_final:.1f}" + r"\,T\ln 2",
            font_size=30, color=WHITE,
        ).move_to([3.4, BAR_Y + 1.15, 0]))

        # clock
        clock = always_redraw(lambda: VGroup(
            Circle(radius=0.28, color=GRAYM, stroke_width=2),
            Line(ORIGIN, 0.24 * np.array([
                np.sin(2 * np.pi * T() / T_TOTAL), np.cos(2 * np.pi * T() / T_TOTAL), 0
            ]), color=WHITE, stroke_width=2.5),
        ).move_to([6.4, 3.55, 0]))

        static = VGroup(box, wall_lo, wall_hi, door, demon, demon_lab,
                        side_lab_L, side_lab_R, tape_lab, bit_read,
                        ledger_base, bar_labs, ledger_lab, clock)

        caps = [
            Text("the demon sorts: fast → right, slow → left — each pass costs one recorded bit",
                 font_size=22).to_edge(DOWN, buff=0.12),
            Text("the box's entropy fell 'for free' — but the debt is sitting on the tape",
                 font_size=22, color=WARM2).to_edge(DOWN, buff=0.12),
            Text("to run a cycle the tape must be reset: erasing dumps T ln 2 of heat per bit",
                 font_size=22, color=HOT).to_edge(DOWN, buff=0.12),
            Text("box + demon + memory together: W_eras + W_meas ≥ T·I — demon exorcised",
                 font_size=23, color=WHITE).to_edge(DOWN, buff=0.12),
        ]

        self.add(mols, tape_g, bars, net)
        self.play(FadeIn(static), FadeIn(caps[0]), run_time=0.9)
        # sorting runs on the shared clock until SORT_T1
        self.wait(SORT_T1 - T() + 0.6)
        self.play(FadeOut(caps[0]), FadeIn(caps[1]), run_time=0.5)
        self.wait(max(0.1, ERASE_T0 - T()))
        # erase beat: heat glyphs out of the tape
        self.play(FadeOut(caps[1]), FadeIn(caps[2]), run_time=0.5)
        glyphs = VGroup(*[
            MathTex(r"T\ln 2", font_size=24, color=HOT).move_to([-3.0 + k * 1.5, -0.75, 0])
            for k in range(5)
        ])
        self.play(
            LaggedStart(*[
                g.animate(rate_func=rate_functions.ease_out_sine).shift(DOWN * 0.9).set_opacity(0)
                for g in glyphs
            ], lag_ratio=0.25),
            run_time=ERASE_T1 - T() - 0.2,
        )
        # final: the true isolated system
        self.play(FadeOut(caps[2]), FadeIn(caps[3]), run_time=0.5)
        sysbox = DashedVMobject(RoundedRectangle(
            width=13.4, height=7.0, corner_radius=0.25, color=GRAYM, stroke_width=2.5,
        ).move_to([0, 0.05, 0]), num_dashes=90)
        sys_lab = Text("box + demon + memory: the true isolated system",
                       font_size=19, color=GRAYM).move_to([0, -3.85, 0]).shift(UP * 7.5)
        self.play(Create(sysbox), run_time=1.0)
        self.wait(1.6)
