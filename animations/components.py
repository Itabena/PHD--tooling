"""Reusable scene-building blocks factored out of the 28 ITFNS scenes.

House-style *colours* live in `itfns.py`; this module holds the shared
geometry/plotting idioms those 28 scenes each re-implemented slightly
differently (axes boilerplate, a time readout, a boxed constant-value
callout, the point-cloud density-image trick). Import both:

    from itfns import WARM, COOL, GRAYM
    from components import styled_axes, time_readout, boxed_readout, density_image, colorize_density, refuse_if_exists

Every helper here was extracted from real working scenes, not designed in
the abstract -- where two source scenes disagreed on a detail, the
docstring says so explicitly (per the standing rule: flag disagreements,
don't silently pick one). The 28 original scripts are left untouched; this
is for new scenes to build on.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Optional

import numpy as np
from manim import Axes, MathTex, SurroundingRectangle, Text, UR, always_redraw

from itfns import GRAYM


def styled_axes(x_range, y_range, x_length, y_length, font_size: int = 20, **kwargs) -> Axes:
    """The house-style `Axes(...)` config repeated near-verbatim across
    roughly half the 28 scenes (diffusion, kelly, legendre, tiling, ratexfunc,
    wavepacket, ...): muted-gray axes, stroke_width 2, no arrow tips. Only
    `font_size` actually varied in practice (18-20 across scenes) -- every
    other axis_config value was already identical -- so this bakes in the
    constant part and passes the size and any extra config through.

    A scene needing e.g. `include_numbers` on one axis (tiling.py's
    `y_axis_config`) still passes that as a kwarg; only the common
    `axis_config` defaults are baked in here.
    """
    axis_config = {"color": GRAYM, "stroke_width": 2, "include_tip": False, "font_size": font_size}
    axis_config.update(kwargs.pop("axis_config", {}))
    return Axes(x_range=x_range, y_range=y_range, x_length=x_length, y_length=y_length,
                axis_config=axis_config, **kwargs)


def boxed_readout(mobject, color, buff: float = 0.14, corner_radius: float = 0.06) -> SurroundingRectangle:
    """The boxed constant-value readout for a conserved quantity -- 5 of the
    28 scenes (convexity, ent_entropy, mixing, stretching, wavepacket) box a
    MathTex/Text in the same colour as the quantity it reads out, per
    itfns.py's house-style note ("boxed constant-value readouts for
    conserved quantities"). This is just the SurroundingRectangle call each
    of them repeated with the same three parameters.
    """
    return SurroundingRectangle(mobject, color=color, buff=buff, corner_radius=corner_radius)


def time_readout(tracker, template: Callable[[object], str], corner=UR,
                  color=GRAYM, font_size: int = 20, use_tex: bool = False):
    """A live "swept time" numeric readout driven by a ValueTracker -- some
    form of this appears in most of the 21 scenes that drive geometry off a
    ValueTracker with always_redraw.

    FLAG (2026-07-23): the handful of scenes with an explicit clock/step
    counter do not agree with each other on colour or size -- GRAYM at
    18-22pt (otoc.py, rgclt.py, ringwalk.py) vs GRAYM at 24pt (diffusion.py)
    vs WHITE at 28pt (stretching.py). This defaults to the majority (GRAYM,
    20pt) rather than averaging or silently picking the outlier; override
    per-scene when that default reads wrong against a specific composition.
    demon.py's literal rotating clock-face is a different visual idiom
    entirely (not a numeric readout) and is deliberately not folded in here.

    `template(tracker) -> str` builds the display string from the tracker's
    current value, e.g. `lambda t: f"t={t.get_value():.2f}"`.
    """
    Mobj = MathTex if use_tex else Text
    return always_redraw(lambda: Mobj(template(tracker), font_size=font_size, color=color).to_corner(corner))


def colorize_density(dens: np.ndarray, warm: bool = True) -> np.ndarray:
    """Warm/cool density-image colour ramp for point-cloud scenes -- the two
    "too many points to draw individually" scenes (fractal.py, mixing.py)
    per itfns.py's note on the ImageMobject + 2D-histogram trick.

    FLAG (2026-07-23): the two source implementations disagree slightly --
    fractal.py's gamma is 0.5 vs mixing.py's 0.55, and the warm red-channel
    scale is 1.7 vs 1.6. Both read as "warm ramp on dark" and the difference
    is subtle, but it is a real numeric difference, not a transcription slip.
    This keeps fractal.py's version because it is the parametrized
    (warm/cool) superset of mixing.py's warm-only one -- flagging the
    discrepancy rather than silently averaging the two.
    """
    d = np.clip(dens, 0, 1) ** 0.5
    if warm:
        rgb = np.stack([np.clip(d * 1.7, 0, 1), np.clip(d * 0.62 * 1.5, 0, 1), np.clip(d * 0.29 * 1.2, 0, 1)], -1)
    else:
        rgb = np.stack([np.clip(d * 0.36 * 1.4, 0, 1), np.clip(d * 0.66 * 1.4, 0, 1), np.clip(d * 1.0, 0, 1)], -1)
    return (rgb * 255).astype(np.uint8)


def density_image(points: np.ndarray, res: int, norm: Optional[float] = None) -> np.ndarray:
    """2D histogram of `points` (Nx2, columns are x then y, both assumed
    already normalized into [0, 1]) as a density grid ready for
    `colorize_density()`. `norm` is the scene's own contrast constant --
    fractal.py uses `(NPTS / (RES*RES)) * 5.0` -- passed through rather than
    guessed here, since the right value depends on point count and desired
    contrast, both scene-specific.
    """
    hist, _, _ = np.histogram2d(points[:, 1], points[:, 0], bins=res, range=[[0, 1], [0, 1]])
    hist = hist[::-1]
    if norm is not None:
        hist = hist / norm
    return hist


def refuse_if_exists(path) -> None:
    """Guard for the static-SVG scripts (spherepack.py, cantor_mpl.py,
    cointree.py, rdcurve.py), which `savefig` straight to a hardcoded vault
    path with no destination argument of their own. Call this immediately
    before the real `savefig` -- refuses (prints and exits) if the target
    already exists, unless `--overwrite` is on the command line.

    Added 2026-07-23 after cointree.py silently overwrote its own committed
    vault asset mid-session (caught via `git status` and restored by hand,
    but the script itself had no guard against it). Same principle as
    build_gif.sh's destination guard: overwriting a committed asset is a
    decision to make explicitly, not a side effect of re-running a script.
    """
    p = Path(path)
    if p.exists() and "--overwrite" not in sys.argv:
        print(
            f"REFUSED: {p} already exists -- pass --overwrite to replace a "
            "committed asset intentionally, rather than clobber it as a side "
            "effect of re-running this script.",
            file=sys.stderr,
        )
        sys.exit(2)
