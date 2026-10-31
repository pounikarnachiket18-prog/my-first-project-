#!/usr/bin/env bash
# One-time setup for the content-creation toolkit. Run from the repo root: bash setup.sh
set -euo pipefail
cd "$(dirname "$0")"

need() { command -v "$1" >/dev/null 2>&1; }
echo "== Checking system tools"
for t in node npm python3 ffmpeg; do
  if need "$t"; then echo "  ok  $t"; else
    echo "  MISSING $t"
    case "$t" in node|npm) apt=nodejs; br=node;; python3) apt=python3-pip; br=python;; *) apt=$t; br=$t;; esac
    if need apt-get; then sudo apt-get update -qq && sudo apt-get install -y -qq "$apt" $( [ "$apt" = nodejs ] && echo npm )
    elif need brew; then brew install "$br"
    else echo "    please install $t manually"; fi
  fi
done

echo "== Installing Node packages (gsap, sharp)"
(cd reels && npm install --no-fund --no-audit)

echo "== Installing Python packages (numpy, scipy, pillow)"
python3 -m pip install -q -r reels/requirements.txt 2>/dev/null || python3 -m pip install -q --user -r reels/requirements.txt || python3 -m pip install -q --break-system-packages -r reels/requirements.txt

echo "== Checking Playwright + Chromium (used to render reels)"
if (cd reels && node -e "require('playwright')" 2>/dev/null) || node -e "require('playwright')" 2>/dev/null; then echo "  ok  playwright"
else (cd reels && npm install --no-save --no-fund --no-audit playwright && npx playwright install chromium); fi

echo "== Building the sound-effects library"
(cd reels && npm run -s sfx)

cat <<'MSG'

All set.
  Image Studio (find free images + make thumbnails/posts): open image-studio/index.html in your browser
  Download free images from the terminal:                 cd reels && npm run find-images -- "city night" --tall
  Render a reel:                                          cd reels && node tools/render.mjs projects/phone-enemy
MSG
