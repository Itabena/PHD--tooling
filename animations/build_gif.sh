#!/bin/bash
# usage: ./build_gif.sh <pyfile> <SceneName> <gifname> <dest-dir> [--overwrite]
#
# <dest-dir> is the full vault path to save into, e.g.
#   ".../Notes_phd/z-Assets/ITFNS-animations/ch4-random-walks"
#   ".../Notes_phd/z-Assets/general-derivations"
# Not defaulted and not assumed to live under ITFNS-animations/ -- this
# script doesn't know "ITFNS" exists. Caller (the vault-animation skill)
# always knows the resolved destination (from Animation plan for a
# cataloged entry, or the approved target for a from-scratch scene) and
# passes it explicitly.
set -e
cd "$(dirname "$0")"

if [ -z "$4" ]; then
    echo "ERROR: destination directory is required (no default) -- pass the" >&2
    echo "full vault path to save into, e.g." >&2
    echo '  ".../Notes_phd/z-Assets/ITFNS-animations/ch4-random-walks"' >&2
    exit 1
fi
DEST="$4"

OVERWRITE=0
if [ "$5" = "--overwrite" ]; then
    OVERWRITE=1
fi
if [ -e "$DEST/$3" ] && [ "$OVERWRITE" -ne 1 ]; then
    echo "REFUSED: $DEST/$3 already exists -- pass --overwrite to replace a" >&2
    echo "committed asset intentionally, rather than clobber it as a side" >&2
    echo "effect of re-running this script." >&2
    exit 2
fi

./manim-venv/Scripts/manim.exe render -qm "$1" "$2" 2>&1 | tail -2
base="${1%.py}"
V="media/videos/$base/720p30/$2.mp4"
ffmpeg -y -v error -i "$V" -vf "fps=16,split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" -loop 0 "tmp_$3"
./node_modules/gifsicle/vendor/gifsicle.exe -O3 "tmp_$3" -o "$3"
rm "tmp_$3"
mkdir -p "$DEST"
cp "$3" "$DEST/"
ls -la "$3" | awk '{printf "SIZE %.2f MB\n", $5/1048576}'
ffprobe -v error -show_entries format=duration -of csv=p=0 "$V"
