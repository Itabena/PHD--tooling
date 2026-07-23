# ITFNS lecture-note animations — source collector

Source code for all 28 animations/diagrams in the **Animation plan** of the
*Information Theory for Natural Scientists* (ITFNS) lecture notes. Each `.py` here
generates one asset that is embedded in a note under
`z-Assets/ITFNS-animations/<chapter>/` in the Obsidian vault
(`Documents/My Projects/Phd/Notes_phd`).

One file = one entry. `itfns.py` holds the shared colour palette every scene imports;
`build_gif.sh` is the render pipeline.

## Setup

```bash
python -m venv manim-venv          # Python 3.13 (NOT 3.14 yet)
manim-venv/Scripts/pip install -r requirements.txt
# plus, on PATH: ffmpeg ; and gifsicle (npm install gifsicle)
```

## Render a GIF

```bash
# build_gif.sh <pyfile> <SceneClass> <output.gif> <vault-chapter-folder>
bash build_gif.sh kelly.py KellyWealthFan kelly-geometric-vs-arithmetic-wealth.gif ch3-maxent-gambling
```
It renders at 720p30 via manim, converts to a 16 fps looping GIF (ffmpeg palette),
optimises with `gifsicle -O3`, and copies the result into the vault asset folder.
Static SVGs (`spherepack.py`, `cantor_mpl.py`, `cointree.py`, `rdcurve.py`) are plain
matplotlib scripts — just run them: `python cointree.py`.

## What each file is — and how "real" the simulation is

**Tier A — genuine stochastic simulation** (actual RNG; the shown quantities are
*measured* from samples). Also copied to `Coding/simulations/ITFNS-simulations/`.

| file | entry | scene class | concept |
|---|---|---|---|
| `demon.py` | #1 | `MaxwellDemon` | Maxwell's demon: sorting + erasure ledger (2D molecular dynamics) |
| `pagerank.py` | #2 | `PageRankSurfer` | PageRank random surfer (60 tokens, real walks + teleport) |
| `phenotype.py` | #3 | `PhenotypeSwitching` | phenotype switching (random environment sequence) |
| `kelly.py` | #4 | `KellyWealthFan` | Kelly criterion (120×60 real coin-flip wealth paths) |
| `mixing.py` | #6 | `PhaseSpaceMixing` | phase-space mixing (120k points through baker's map) |
| `fractal.py` | #8 | `FractalAttractorStretchFold` | fractal attractor (90k points, stretch–fold) |
| `diffusion.py` | #10 | `DiffusionLatticeWalkContinuumLimit` | diffusion (4000 real ±1 walkers) |
| `rgclt.py` | #11 | `RGFlowGaussianFixedPointCLT` | RG → Gaussian / CLT (200k real samples) |
| `bandit.py` | #18 | `MultiArmedBanditGittinsIndex` | Gittins bandit (real win/loss, Beta posteriors) |
| `brownian.py` | #26 | `BrownianBallisticToDiffusiveCrossover` | Brownian crossover (Langevin tracer; MSD curve is analytic) |

**Tier B — exact math** (the true formula / exact construction plotted; deterministic).

| file | entry | scene class | concept |
|---|---|---|---|
| `stretching.py` | #5 | `PhaseSpaceStretching` | phase-space stretching, coarse-grained entropy |
| `tiling.py` | #7 | `TilingIdentityDrift` | tiling-identity forced drift |
| `legendre.py` | #9 | `LegendreTransformEnvelope` | Legendre transform as tangent envelope |
| `convexity.py` | #12 | `ConvexityOvershootCosh` | convexity overshoot ⟨e^Λ⟩=cosh a |
| `waterfill.py` | #13 | `WaterFillingParallelGaussianChannels` | water-filling |
| `ratefunc.py` | #14 | `RateFunctionLegendreLargeDeviation` | rate function as Legendre transform |
| `ent_entropy.py` | #20 | `EntanglementEntropyPartVsWhole` | entanglement: part > whole |
| `rgsaddle.py` | #21 | `RGFlowUnstableFixedPointCriticalSurface` | RG saddle flow, critical surface (ODE integration) |
| `ringwalk.py` | #22 | `RingWalkRelaxationFourierModes` | ring walk relaxation (exact Markov iteration) |
| `wavepacket.py` | #23 | `MinimumUncertaintyWavepacketSqueeze` | wave-packet Fourier squeeze |
| `inverted.py` | #24 | `InvertedPotentialPacketDriftSpread` | inverted-potential packet |
| `spherepack.py` | #15 | (SVG) | channel-capacity sphere packing (static) |
| `cantor_mpl.py` | #16 | (SVG) | Cantor box-counting (static) |
| `cointree.py` | #27 | (SVG) | counterfeit-coin ternary tree (static) |
| `rdcurve.py` | #28 | (SVG) | rate-distortion curve (static) |

**Tier C — schematic illustration** (physically motivated but staged; NOT derived
from a state-space solver — caption as "schematic" in the notes).

| file | entry | scene class | concept |
|---|---|---|---|
| `teleport.py` | #17 | `QuantumTeleportationBankedPair` | quantum teleportation (scripted protocol beats) |
| `blackhole.py` | #19 | `BlackHoleAreaLawBekenstein` | black-hole area law (schematic glyphs + real r² vs r³ bars) |
| `otoc.py` | #25 | `OtocScramblingLightCone` | OTOC light cone (phenomenological cone profile) |

## House style (shared visual language)

warm = expansion/growth · cool = loss/contraction/conserved · muted gray = fixed grids ·
boxed constant-value readouts for conserved quantities · dark background · GIFs 720p,
16 fps, looping, < 8 MB.

## Performance note (learned the hard way)

Never put a **continuously-changing** `MathTex`/`DecimalNumber` inside `always_redraw` —
manim recompiles LaTeX every frame (10+ min renders). Use discrete `Transform`
checkpoints for animated numbers. `always_redraw` is fine for geometry and for
constant-string `MathTex` (cache hits). For point clouds, render a density image
(`ImageMobject` + 2D histogram), not thousands of `Dot`s.
