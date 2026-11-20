# Yawn reel: "Ubaasi kyun failti hai?" (v1, 13 of 17 clips, no voiceover yet)

Output: `reels/output/yawn-reel-v1.mp4` (1080x1920, 30 fps, 48.2s).

Clips used (plan number → upload id): 1 couple 5d3da5a5 · 2 family at the door a075d47b · 3 stage 80f21f8b · 4 train bcc4d367 · 5 teacher 9ac90f99 · 6 stadium 8ca8235d · 7 oxygen lab 75cee86f · 8 AC brain 55e6cc7d · 9 copy button 3c8a9a9d · 10 office 97562e28 · 11 dinner dfcd49d9 · 12 night phone aaa22ef6 · 13 Zoom ef7d5143, then an end card. Still missing: 14 dog/chimps, 15 screen squish, 16 newlyweds callback, 17 pass it on.

- `build_segments.py`: the hook is slow motion on the setup (minterpolate), the yawn opening, a 1.35s freeze on the widest yawn, then the turn to the door. Clips 3–13 are trimmed by 0.3s and play at 1.1x. The Flow ✦ watermark is removed with delogo.
- `audio_yw.py`: everything is synthesized. Shehnai setup, synthesized yawns for each character, record scratch and wah-wah trombone on the freeze, tiptoe pizzicato, drumroll and ta-da, train, crowd, lab bubbles and stamp, ice chime, button and boing, pressure-cooker whistle, crickets, a Zoom ding, mouth-dive gulps, and a playful pizzicato/bassoon bed.
- `mg_yw.html`: speech bubble, hearts that break, freeze doodle and reaction, spy-kit callouts, UBAASI marquee, CONTAGIOUS tape, INFECTED counter, comic pops, MYTH stamp, brain thermometer with snow, Ctrl+C keycaps, pressure gauge, Family > Dost > Strangers podium, Zzz, mouth-dive streaks, tags, kinetic captions, progress bar, and an end card with a Follow tap.
- `compose.py`: push-in on every shot, zoom punches and shake on the gags, whip blur on cuts, grade and grain, the graphics layer, and the logo at 860,1700.
