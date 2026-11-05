#!/usr/bin/env bash
# Kingfisher reel, CLEAN cut: the animation exactly as made.
# Every clip plays in full (96 frames / 4.0 s) at original speed with its
# original audio. No frame blending, no sharpening, no burned captions.
# Vertical clips are scaled 3x (360x640 -> 1080x1920); landscape clips are
# detected automatically and sit centred on a soft-blurred copy of themselves.
#
# Clips missing from clips/ are skipped, so new ones drop in as they arrive:
#   cold.mp4  A.mp4 B.mp4 C.mp4 D.mp4 E.mp4  01..12  tree-landscape  outro-logo  loop.mp4
# Audio extras (optional, in audio/):
#   chime.wav           airport chime at the start and at the ending   (python3 make_chime.py)
#   announce-open.wav   "Kingfisher flight 2005... ab boarding ke liye taiyaar hai."
#   announce-close.wav  "Kingfisher ki yeh flight... hamesha ke liye cancel ho chuki hai."
#
# Run from reels/:  bash projects/kingfisher/clean.sh
set -euo pipefail
cd "$(dirname "$0")"
OUT=../../output/kingfisher-clean.mp4

ORDER=(cold A B C D E 01 02 03 04 05 06 07 08 09 10 11 12 tree-landscape outro-logo loop)
ENDING_CLIP=loop   # closing chime + announcement go on this clip...
[ -f clips/loop.mp4 ] || ENDING_CLIP=outro-logo   # ...or on the logo until it exists

inputs=(); fc=""; n=0; t=0; end_t=0; used=()
for c in "${ORDER[@]}"; do
  [ -f "clips/$c.mp4" ] || continue
  inputs+=(-i "clips/$c.mp4"); used+=("$c")
  wh=$(ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0 "clips/$c.mp4")
  if [ "${wh%,*}" -gt "${wh#*,}" ]; then   # landscape -> centred on blurred copy
    fc+="[$n:v]split[x$n][y$n];[x$n]scale=-2:1920,crop=1080:1920,boxblur=30:2[bg$n];"
    fc+="[y$n]scale=1080:-2:flags=lanczos[fg$n];[bg$n][fg$n]overlay=(W-w)/2:(H-h)/2,setsar=1[v$n];"
  else
    fc+="[$n:v]scale=1080:1920:flags=lanczos,setsar=1[v$n];"
  fi
  fc+="[$n:a]atrim=0:4,asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a$n];"
  [ "$c" = "$ENDING_CLIP" ] && end_t=$t
  n=$((n+1)); t=$((t+4))
done
for i in $(seq 0 $((n-1))); do fc+="[v$i][a$i]"; done
fc+="concat=n=$n:v=1:a=1[v][clips];"
echo "clips (${#used[@]}, ${t}s): ${used[*]}"

# --- overlay layer: chime + announcements, clip audio ducks underneath ---
over=(); k=$n; labels=""
add() {  # add <file> <start-seconds> <gain>
  [ -f "$1" ] || return 0
  inputs+=(-i "$1"); local ms=$(( $2 * 1000 ))
  fc+="[$k:a]aresample=48000,aformat=channel_layouts=stereo,volume=$3,adelay=${ms}|${ms}[o$k];"
  labels+="[o$k]"; k=$((k+1))
}
add audio/chime.wav 0 0.9
add audio/announce-open.wav 1 1.0
add audio/chime.wav "$end_t" 0.9
add audio/announce-close.wav $((end_t + 1)) 1.0
m=$((k-n))
if [ $m -gt 0 ]; then
  fc+="${labels}amix=inputs=$m:normalize=0,apad[ov];[ov]asplit[ov1][ov2];"
  fc+="[clips][ov1]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350[duck];"
  fc+="[duck][ov2]amix=inputs=2:normalize=0,atrim=0:$t,alimiter=limit=0.95[a]"
else
  fc+="[clips]anull[a]"
fi

ffmpeg -v error -y "${inputs[@]}" -filter_complex "$fc" -map "[v]" -map "[a]" \
  -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -r 24 \
  -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "done -> $OUT"
