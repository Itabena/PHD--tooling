---
name: vault-animation
description: "Scaffold a ManimCE or matplotlib scene for a planned animation/diagram entry, using the house style and reusable components factored out of the 28 ITFNS lecture-note animations. Renders a GIF/SVG into the vault's z-Assets/ tree and embeds it in the target note. Creates a scene and an embed only — deciding what's worth animating, or writing explanatory prose alongside it, stays mine."
---

# vault-animation

Scaffolds the code for one animation or static diagram entry and gets it into
the vault as a rendered asset plus an embed. The governing document for how
this skill came to exist is `a - logistics/Windows handoff - Phase 4 and
extractor.md` in the vault; read it for the reasoning behind the two-repo
split (sources here, rendered assets only in the vault) if any of this looks
arbitrary.

## The rule that governs everything

**Scaffolding is the skill's; understanding is mine.** A scene script that
renders a figure or animation I specified is scaffolding, exactly like a quiz
script rendering questions I asked for. Deciding *what* is worth animating, or
writing explanatory prose into a note alongside the embed, is understanding —
that oversteps into the [[aa- Dashboard|AI Use Policy]]'s review-required
territory and must be marked `#needs-review` if it happens.

## Where the reference scenes live

`phd-tooling/animations/` is the canonical home for every scene's *source* —
one file per entry, the convention the 28 ITFNS scenes already established.
Generated GIFs/SVGs are never stored here; they live only in the vault's
`z-Assets/` tree (see `animations/README.md`). This repo is sources + render
pipeline, full stop.

- **`itfns.py`** — the shared palette (`WARM`, `WARM2`, `HOT`, `COOL`,
  `COOL2`, `GRAYM`, `VIOLET`) every scene imports. The filename is a
  historical artifact of being written ITFNS-first; the palette itself is
  course-agnostic, and a scene for a different course imports it exactly the
  same way rather than duplicating or renaming it.
- **`components.py`** — the geometry/plotting idioms that recurred across
  those 28 scenes, factored out 2026-07-23 by reading the real scenes, not
  designed in the abstract: `styled_axes` (the near-universal `Axes(...)`
  config), `time_readout` (the ValueTracker-driven numeric clock/step
  counter most scenes have some form of), `boxed_readout` (the
  `SurroundingRectangle` around a conserved-quantity readout), and
  `density_image` + `colorize_density` (the point-cloud density-image trick
  from `itfns.py`'s own performance note). **Where two source scenes
  disagreed on a detail** — the time-readout's colour/size, the
  density-image colour ramp's gamma — **the docstring flags it rather than
  silently picking one.** Read those flags before assuming a default is
  uncontroversial; they're a live open question, not a resolved one.
- Import components wherever they actually fit a new scene's shape — not
  every one of the 28 originals needed all four, and forcing one onto a
  scene that doesn't match just adds indirection.

## Workflow: scaffolding one new entry

1. **Find the entry's row** in its course/topic's own asset-organisation
   note. `Phd courses/Information theory for natural scientists/Animation
   plan.md`'s "Asset organisation & save-path instructions (for Claude
   Code)" section is both the ITFNS-specific map and the template for what a
   *new* course's equivalent note should contain: exact vault folder,
   filename, file type (gif vs. svg/png). **If no such note/section exists
   yet for a new course, stop and ask** — don't invent a save-path
   convention on the spot.
2. **Classify the entry's tier**, the same three buckets `animations/README.md`
   already uses: **A — genuine simulation** (real RNG, measured quantities),
   **B — exact math** (deterministic formula/construction), **C — schematic**
   (physically motivated but staged; caption it "schematic" in the note).
   Add a row to the README's table under the right tier.
3. **Write the scene** in `phd-tooling/animations/<name>.py` — one file, one
   entry, importing `itfns.py` for colour and `components.py` for whichever
   shared idioms fit.
4. **Render:**
   - Manim scene:
     ```
     bash build_gif.sh <file>.py <SceneClass> <output>.gif <vault-chapter-folder>
     ```
     Renders 720p30 via ManimCE, converts to a 16 fps looping palette GIF via
     ffmpeg, optimises with `gifsicle -O3`, copies straight into the vault
     folder. Needs the local render toolchain set up once per machine (below).
   - Static matplotlib script: just run it (`python <file>.py`). The
     existing four (`spherepack.py`, `cantor_mpl.py`, `cointree.py`,
     `rdcurve.py`) write straight to their vault SVG path inside the script
     itself — match that for a new static entry rather than adding an
     external copy step.
5. **Confirm house style before calling it done:** dark background (manim
   default, matches Obsidian dark mode), short side ≥ 720 px, ~15–20 fps
   if a GIF, under ~8 MB (re-run `gifsicle -O3` if not); warm = expansion,
   cool = loss/conserved, muted gray = fixed grids, boxed readout for
   anything conserved. Static diagrams: SVG preferred, coloured to stay
   legible in dark mode — never black-on-transparent, which vanishes on the
   dark canvas.
6. **Filename:** lowercase, hyphenated, descriptive, and **globally unique
   across the whole vault** — Obsidian resolves `![[embeds]]` by shortest
   path, so the chapter folder is for humans, not for disambiguation. Same
   rule the exercise screenshots already follow.
7. **Write the embed** into the target note: a short first-person-plural
   lead-in sentence first ("the animation below traces this…" — never
   dropped in cold), then `![[bare-filename.gif]]` with no path prefix.
8. **Post-insert verification, every time:** re-read the note after writing
   the embed and confirm it survived intact. Use exact-string `Edit` for
   this, not the `obsidian-phd` MCP's `edit_file` — during the original
   28-entry ITFNS batch (2026-07-20), that tool was observed silently
   downgrading `$$` → `$` math delimiters on an insert right after an
   animation embed. Re-check `$$` balance in the note after *any* edit to
   it, regardless of which tool wrote it. That specific MCP-tool bug is the
   one thing actually reproduced and recorded — a broader Obsidian-side
   "`$$` collapse" beyond it has not been personally reproduced. If a future
   session can't reproduce that either, say so rather than guard against
   something imaginary.

## Render toolchain (once per machine)

```
py -3.13 -m venv manim-venv
manim-venv/Scripts/pip install -r requirements.txt
```
Python 3.13, not 3.14 — the manim/manimpango/moderngl native-extension stack
isn't built for 3.14 yet. Also needs, outside pip: **ffmpeg** on PATH (this
machine: `choco install ffmpeg`), and a **local, not global**, gifsicle —
`npm install gifsicle` run inside `phd-tooling/animations/` itself;
`build_gif.sh` calls `node_modules/gifsicle/vendor/gifsicle.exe` directly.
`manim-venv/`, `node_modules/`, and `media/` are gitignored — machine-local
build tooling, recreated from `requirements.txt` and `npm install`, not repo
content.

## Stop and ask before

- **Creating any `z-Assets/` folder beyond the ones that already exist** for
  a course — a brand-new course's own `<course>-animations/` tree is a real
  structural decision, not a scaffolding one.
- **Touching any of the 28 existing ITFNS assets** — regenerating one
  because its source script changed is a decision to make explicitly, not an
  automatic side effect of doing something else nearby.
- **Deciding what's worth animating**, or writing prose beyond the required
  one-sentence lead-in, into a note — that's understanding, not scaffolding
  (mark `#needs-review` if it happens anyway).

## Files

- `itfns.py` — shared palette (`WARM`/`WARM2`/`HOT`/`COOL`/`COOL2`/`GRAYM`/`VIOLET`), imported by every scene regardless of which course it's for
- `components.py` — shared geometry/plotting idioms (`styled_axes`, `time_readout`, `boxed_readout`, `density_image` + `colorize_density`); flags two spots where the source scenes disagreed rather than silently resolving them
- `build_gif.sh` — `<pyfile> <SceneClass> <output.gif> <vault-chapter-folder>`; manim render → ffmpeg palette GIF → gifsicle -O3 → copy into vault
- `requirements.txt` — `manim==0.20.1`, matplotlib, numpy; Python 3.13
- the 28 existing scene files — the reference scenes `components.py` was factored out of; `README.md` has the tier classification and file → entry# → scene-class map
- `README.md` — setup, render command, tier table, house-style summary, and the "never put continuously-changing `MathTex` in `always_redraw`" performance note (10+ minute renders otherwise)

## See also

- [[a - logistics/Windows handoff - Phase 4 and extractor|Windows handoff - Phase 4 and extractor]] — Phase 4 background, the two-repo split, this skill's "Step 0"
- [[Animation plan]] — the ITFNS save-path map this skill's workflow is modeled on
- [[aa- Dashboard|AI Use Policy]] — scaffolding vs. review-required tiers
- [[a - logistics/Writing Style and Voice|Writing Style and Voice]] — governs the lead-in sentence's register
