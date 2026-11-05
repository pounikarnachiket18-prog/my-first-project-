#!/usr/bin/env bash
# Kingfisher reel, CLEAN cut: the animation exactly as made.
# All 14 clips play in full (96 frames / 4.0 s each) at original speed with
# their original audio. No frame blending, no sharpening, no burned captions.
# Vertical clips are only scaled 3x (360x640 -> 1080x1920); the two landscape
# clips sit centred on a soft-blurred copy of themselves.
# Run from reels/:  bash projects/kingfisher/clean.sh
set -euo pipefail
cd "$(dirname "$0")"
OUT=../../output/kingfisher-clean.mp4

VERTICAL=(01 02 03 04 05 06 07 08 09 10 11 12)
LANDSCAPE=(tree-landscape outro-logo)

inputs=(); fc=""; n=0
aud() { fc+="[$1:a]atrim=0:4,asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a$1];"; }
for c in "${VERTICAL[@]}"; do
  inputs+=(-i "clips/$c.mp4")
  fc+="[$n:v]scale=1080:1920:flags=lanczos,setsar=1[v$n];"; aud $n
  n=$((n+1))
done
for c in "${LANDSCAPE[@]}"; do
  inputs+=(-i "clips/$c.mp4")
  fc+="[$n:v]split[x$n][y$n];[x$n]scale=-2:1920,crop=1080:1920,boxblur=30:2[bg$n];"
  fc+="[y$n]scale=1080:-2:flags=lanczos[fg$n];[bg$n][fg$n]overlay=(W-w)/2:(H-h)/2,setsar=1[v$n];"; aud $n
  n=$((n+1))
done

for i in $(seq 0 $((n-1))); do fc+="[v$i][a$i]"; done
fc+="concat=n=$n:v=1:a=1[v][a]"

ffmpeg -v error -y "${inputs[@]}" -filter_complex "$fc" -map "[v]" -map "[a]" \
  -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -r 24 \
  -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "done -> $OUT"
