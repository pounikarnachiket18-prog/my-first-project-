# Reels Studio

Motion-graphics Instagram Reels (1080×1920, 30 fps) written as HTML + GSAP, rendered frame by frame with Playwright, with original synthesized sound effects mixed in.

## Setup (once)
```bash
cd reels
npm install                      # gsap
pip install -r requirements.txt  # numpy, scipy (sound design)
# also needs: ffmpeg, and Playwright + Chromium (preinstalled here; elsewhere: npm i -D playwright && npx playwright install chromium)
npm run sfx                      # build the 21-sound SFX library into sfx/
```

## Make a reel
```bash
node tools/render.mjs projects/phone-enemy --preview   # 16 stills -> output/phone-enemy-contact.jpg
node tools/render.mjs projects/phone-enemy             # final -> output/phone-enemy.mp4
node tools/render.mjs projects/phone-enemy --from 6 --to 10   # render a section only
```

## Photos
Each project has `images.json` listing free Unsplash photos by slot. `npm run images` downloads them to `projects/<name>/images/<slot>.jpg`.
This needs network access to `unsplash.com` and `images.unsplash.com`. You can also drop your own `<slot>.jpg` into that folder.
Slots without a photo fall back to the designed graphics, so a reel always renders.

## New reel
Copy `projects/phone-enemy`, then edit the TIMELINE section of `index.html`:
- `word(html, tIn, tOut, {size, y, dark, sfx})`: kinetic text.
- `sfx(t, name, gain)`: sound cue. Names are listed in `tools/sfx.py`'s `LIBRARY`.
- `glitch()`, `shake()`, `flash()`, `zoomIn()` / `zoomOut()`, `kenburns()`: effects.
- `CONFIG.handle`: optional `@watermark`.
