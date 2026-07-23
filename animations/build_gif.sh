#!/bin/bash
# usage: ./build_gif.sh <pyfile> <SceneName> <gifname> <vault-subfolder>
set -e
cd "$(dirname "$0")"
./manim-venv/Scripts/manim.exe render -qm "$1" "$2" 2>&1 | tail -2
base="${1%.py}"
V="media/videos/$base/720p30/$2.mp4"
ffmpeg -y -v error -i "$V" -vf "fps=16,split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" -loop 0 "tmp_$3"
./node_modules/gifsicle/vendor/gifsicle.exe -O3 "tmp_$3" -o "$3"
rm "tmp_$3"
DEST="/c/Users/itama/Documents/My Projects/Phd/Notes_phd/z-Assets/ITFNS-animations/$4"
mkdir -p "$DEST"
cp "$3" "$DEST/"
ls -la "$3" | awk '{printf "SIZE %.2f MB\n", $5/1048576}'
ffprobe -v error -show_entries format=duration -of csv=p=0 "$V"
