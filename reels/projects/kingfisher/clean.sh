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

ORDER=(A B C D E 01 02 03 04 05 06 07 08 09 10 11 12 tree logo-card)   # all 9:16; logo-card made by make_cards.py; old 16:9 clips in clips/old-16x9/
ENDING_CLIP=loop   # closing chime + announcement go on this clip...
[ -f clips/loop.mp4 ] || ENDING_CLIP=outro-logo   # ...or on the logo until it exists

inputs=(); fc=""; n=0; t=0; end_t=0; used=(); declare -A START; WMPOS=()
CLEAN="hqdn3d=1.2:1.2:0:0"; SHARP="cas=0.55"   # clarity: undo source blockiness, crisp edges
WM=watermark.png; WMS=80   # round logo watermark, diameter in px
for c in "${ORDER[@]}"; do
  [ -f "clips/$c.mp4" ] || continue
  inputs+=(-i "clips/$c.mp4"); used+=("$c")
  wh=$(ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0 "clips/$c.mp4")
  if [ "${wh%,*}" -gt "${wh#*,}" ]; then   # landscape -> centred on blurred copy
    fc+="[$n:v]split[x$n][y$n];[x$n]scale=-2:1920,crop=1080:1920,boxblur=30:2[bg$n];"
    fc+="[y$n]$CLEAN,scale=1080:-2:flags=lanczos,$SHARP[fg$n];[bg$n][fg$n]overlay=(W-w)/2:(H-h)/2,setsar=1[c$n];"
    wx=979; wy=1162   # corner sparkle of a 640x360 clip, once centred
  else
    fc+="[$n:v]$CLEAN,scale=1080:1920:flags=lanczos,$SHARP,setsar=1[c$n];"
    wx=900; wy=1740   # corner sparkle of a 360x640 clip, scaled 3x
  fi
  if [ "$c" = "logo-card" ]; then WMPOS+=("none"); else WMPOS+=("$wx $wy"); fi
  fc+="[$n:a]atrim=0:4,asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a$n];"
  [ "$c" = "$ENDING_CLIP" ] && end_t=$t
  START[$c]=$t
  n=$((n+1)); t=$((t+4))
done
if [ -f "$WM" ]; then
  fc+="movie=$WM,format=rgba,scale=$WMS:$WMS:flags=lanczos,colorchannelmixer=aa=0.92,split=$n"
  for i in $(seq 0 $((n-1))); do fc+="[w$i]"; done; fc+=";"
  for i in $(seq 0 $((n-1))); do read -r wx wy <<<"${WMPOS[$i]}"
    if [ "$wx" = "none" ]; then fc+="[w$i]nullsink;[c$i]null[v$i];"; continue; fi
    fc+="[c$i][w$i]overlay=$((wx - WMS/2)):$((wy - WMS/2)):format=auto:eof_action=repeat[v$i];"; done
else
  for i in $(seq 0 $((n-1))); do fc+="[c$i]null[v$i];"; done
fi
for i in $(seq 0 $((n-1))); do fc+="[v$i][a$i]"; done
fc+="concat=n=$n:v=1:a=1[v][clips];"
echo "clips (${#used[@]}, ${t}s): ${used[*]}"

# --- overlay layer: chime + announcements, clip audio ducks underneath ---
over=(); k=$n; labels=""
add() {  # add <file> <start-seconds> <gain> [max-length-seconds]
  [ -f "$1" ] || return 0
  inputs+=(-i "$1"); local ms; ms=$(awk "BEGIN{printf \"%d\", $2*1000}")
  local cut=""
  if [ -n "${4:-}" ]; then cut="atrim=0:$4,afade=t=out:st=$(awk "BEGIN{print $4-0.6}"):d=0.6,"; fi
  fc+="[$k:a]aresample=48000,aformat=channel_layouts=stereo,${cut}volume=$3,adelay=${ms}|${ms}[o$k];"
  labels+="[o$k]"; k=$((k+1))
}
cue() {  # cue <clip> <seconds-into-clip> <file> <gain> [max-length] - skipped if clip absent
  [ -n "${START[$1]:-}" ] || return 0
  add "$3" "$(awk "BEGIN{print ${START[$1]}+$2}")" "$4" "${5:-}"
}
# opening chime removed along with the cold-open clip
add audio/announce-open.wav 1 1.0
# closing chime removed along with the loop clip
add audio/announce-close.wav $((end_t + 1)) 1.0

# --- meme sounds: offsets put each sound's hit on the matching frame ---
M=audio/memes
# removed on request: meme07 (sad sound at 8 s), new2 ("kaun hai re"), new4 ("kuch toh gadbad hai")
cue D   0.00 $M/new1.mp3   0.55 4    # paper plane through the clouds
cue 01  0.50 $M/new3.mp3   1.60      # India map, cities and routes pop up
cue 04  0.00 $M/meme05.mp3 0.30 4    # luxury cabin
cue 05  1.08 $M/meme02.mp3 1.00      # Among Us role reveal -> Air Deccan merges (42.2 s)
cue 06  3.13 $M/meme01.mp3 0.75      # sting -> the "!" slams in
cue 07  0.00 $M/meme06.mp3 1.50 4    # beeps -> delays, queue, unpaid salary
cue 08  0.42 $M/meme10.mp3 0.90      # "dun" sting -> DGCA stamp hits 20 October 2012
cue 09  3.13 $M/meme03.mp3 0.33      # burst -> scales snap and collapse
cue 10  0.00 $M/meme04.mp3 0.60 3.6  # empire cracks and shrinks
cue 10  3.62 $M/meme08.mp3 1.10      # short hit -> the "?" appears
cue 11  1.70 $M/meme09.mp3 0.90 1.0  # "Hello? chacha?" -> in the pause before "lesson kya hai?" (65.7 s)

# --- voiceover: each spoken line of audio/voiceover.mp3 placed on its own scene ---
#     vo <source-start> <source-end> <timeline-start>
VO=audio/voiceover.mp3; VOL=()
vo() { VOL+=("$1 $2 $3"); }
vo 13.29 14.03  0.15   # "Kingfisher" in the narrator's voice (from "Kingfisher ne Indian skies...") opens the reel
vo  4.87 11.19  1.10   # Ek waqt tha... luxury ki pehchaan thi
vo 11.90 17.74  8.29   # 2005 mein... naye sapne ke saath
vo 18.20 20.81 16.00   # Har passenger ke liye... royal safar
vo 21.38 26.98 20.00   # Sheher se sheher... udne laga
vo 27.57 34.06 28.00   # Premium seats... badal gaya
vo 34.67 39.40 35.20   # Phir 2007 mein, Air Deccan... bada ho gaya
vo 39.94 42.68 40.18   # Lekin expansion... karz bhi badhta gaya
vo 43.24 47.34 44.00   # Salaries ruk gayi... bharosa toot gaya
vo 48.14 53.74 48.35   # Phir aaya 20 October 2012... suspend  ("20 October" lands on the stamp)
vo 54.18 57.83 54.20   # Planes zameen par... licence bhi expire
vo 58.46 61.96 58.10   # Success ki misaal... failure ki kahaani
vo 62.74 65.21 62.95   # Is kahaani ka sabse bada lesson kya hai?
vo 65.72 69.81 65.67   # Sirf bade sapne... financial discipline
vo 70.33 75.91 70.01   # Kyunki empire banana mushkil hai... zyada mushkil
# closing announcement (76.66-80.20 in the recording) dropped: no room once the loop clip was removed
have_vo=0
if [ -f "$VO" ]; then
  have_vo=1; inputs+=(-i "$VO"); nv=${#VOL[@]}
  fc+="[$k:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-2:LRA=7,aresample=48000,asplit=$nv"
  for j in $(seq 0 $((nv-1))); do fc+="[vs$j]"; done; fc+=";"; vl=""
  for j in $(seq 0 $((nv-1))); do
    read -r a b s <<<"${VOL[$j]}"; ms=$(awk "BEGIN{printf \"%d\", $s*1000}")
    fc+="[vs$j]atrim=$a:$b,asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st=$(awk "BEGIN{print $b-$a-0.08}"):d=0.08,adelay=${ms}|${ms}[vl$j];"
    vl+="[vl$j]"
  done
  fc+="${vl}amix=inputs=$nv:normalize=0,aresample=48000:async=1:first_pts=0,apad,atrim=0:$t[vo];[vo]asplit=3[vo1][vo2][vo3];"
  k=$((k+1))
fi

m=$((k-n-have_vo))
if [ $m -gt 0 ]; then
  fc+="${labels}amix=inputs=$m:normalize=0,apad,atrim=0:$t[ov];"
else
  fc+="anullsrc=r=48000:cl=stereo,atrim=0:$t[ov];"
fi
if [ $have_vo = 1 ]; then
  # memes/chime dip under the voice; clip audio dips under everything
  fc+="[ov][vo1]sidechaincompress=threshold=0.06:ratio=1.8:attack=10:release=250[ovd];[ovd]asplit[ov1][ov2];"
  fc+="[ov1][vo2]amix=inputs=2:normalize=0[key];"
  fc+="[clips][key]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350[duck];"
  fc+="[duck][ov2][vo3]amix=inputs=3:normalize=0,atrim=0:$t,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]"
else
  fc+="[ov]asplit[ov1][ov2];[clips][ov1]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350[duck];"
  fc+="[duck][ov2]amix=inputs=2:normalize=0,atrim=0:$t,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]"
fi

TARGET=${TARGET:-70}   # final length in seconds; every frame is kept, frame rate rises, voice pitch unchanged
k=$(awk "BEGIN{printf \"%.6f\", $t/$TARGET}"); fps=$(awk "BEGIN{printf \"%.4f\", 24*$t/$TARGET}")
OUT=../../output/kingfisher-${TARGET}s.mp4
TITLE=title.png   # big "KINGFISHER" title in the first second (make_cards.py)
if [ -f "$TITLE" ]; then
  fc+=";movie=$TITLE,loop=loop=-1:size=1,setpts=N/24/TB,format=rgba,fade=t=in:st=0:d=0.15:alpha=1,fade=t=out:st=1.15:d=0.35:alpha=1,trim=duration=1.5[tt];[v][tt]overlay=0:0:eof_action=pass[vt]"
else
  fc+=";[v]null[vt]"
fi
fc+=";[vt]setpts=PTS/$k[vf];[a]atempo=$k,atrim=0:$TARGET[af]"

[ -n "${DUMP_FC:-}" ] && { printf "%s\n" "$fc" > "$DUMP_FC"; printf "%s\n" "${inputs[@]}" > "$DUMP_FC.inputs"; exit 0; }
ffmpeg -v error -y "${inputs[@]}" -filter_complex "$fc" -map "[vf]" -map "[af]" \
  -r "$fps" -c:v libx264 -preset slow -tune animation -crf 12 -pix_fmt yuv420p \
  -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$OUT"
echo "done -> $OUT (${TARGET}s from ${t}s, x$k, ${fps} fps)"
