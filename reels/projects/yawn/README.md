# Yawn reel: "Ubaasi kyun failti hai?" (v1, 13 of 17 clips, no voiceover yet)

Output: `reels/output/yawn-reel-v1.mp4` (1080x1920, 30 fps, 48.2s).

Clips used (plan number → upload id): 1 couple 5d3da5a5 · 2 family at the door a075d47b · 3 stage 80f21f8b · 4 train bcc4d367 · 5 teacher 9ac90f99 · 6 stadium 8ca8235d · 7 oxygen lab 75cee86f · 8 AC brain 55e6cc7d · 9 copy button 3c8a9a9d · 10 office 97562e28 · 11 dinner dfcd49d9 · 12 night phone aaa22ef6 · 13 Zoom ef7d5143, then an end card. Still missing: 14 dog/chimps, 15 screen squish, 16 newlyweds callback, 17 pass it on.

- `build_segments.py`: the hook is slow motion on the setup (minterpolate), the yawn opening, a 1.35s freeze on the widest yawn, then the turn to the door. Clips 3–13 are trimmed by 0.3s and play at 1.1x. The Flow ✦ watermark is removed with delogo.
- `audio_yw.py`: everything is synthesized. Shehnai setup, synthesized yawns for each character, record scratch and wah-wah trombone on the freeze, tiptoe pizzicato, drumroll and ta-da, train, crowd, lab bubbles and stamp, ice chime, button and boing, pressure-cooker whistle, crickets, a Zoom ding, mouth-dive gulps, and a playful pizzicato/bassoon bed.
- `mg_yw.html`: speech bubble, hearts that break, freeze doodle and reaction, spy-kit callouts, UBAASI marquee, CONTAGIOUS tape, INFECTED counter, comic pops, MYTH stamp, brain thermometer with snow, Ctrl+C keycaps, pressure gauge, Family > Dost > Strangers podium, Zzz, mouth-dive streaks, tags, kinetic captions, progress bar, and an end card with a Follow tap.
- `compose.py`: push-in on every shot, zoom punches and shake on the gags, whip blur on cuts, grade and grain, the graphics layer, and the logo at 860,1700.


## Full cut (20 clips): `reels/output/yawn-reel-full.mp4` (69.1s)
Order: hook (couple) → door (family) → stage title → train → teacher → hero (24297194) → stadium → umpire (a42120d8) → lab → AC brain → copy → office → dinner → night → mummy (ad7e6e5c) → Zoom → dog/chimps (d1a5df19) → screen squish (ac391af5) → newlyweds callback (d8d072de) → pass it on (978b14c9, held 3s for the CTA).

Added for the full cut: "THE CONTAGIOUS VILLAIN" title with a BRAAAM hit, widescreen bars, lens flare and SLO-MO FAIL for the hero, HOWZAT/NOT OUT for the umpire, OYE!! for mummy with a cat meow, Copied 🐶 and chimp callouts with a woof, a glass crack and smudge with knock-knock on the screen squish, a shehnai reprise on the callback, and a finale with a magic shimmer, the counter rolling to 10 lakh, "Kitni aayi?", a share button and the Follow tap. Every story beat is timed from the source footage (`beats` in `timeline.json`).

## Audio fix (v2)
- The earlier exports had 96 kHz AAC audio (loudnorm upsamples internally), which many phones play as silence, and a quiet first ~2s. All reels are now 48 kHz. `compose.py` outputs `-ar 48000`; the final loudness uses two-pass linear loudnorm (-14 LUFS).
- New realistic yawns come from `yawnvox.py`: a source-filter synth with an inhale, then a high voiced "aaah" gliding down, then "ohh", then a closed-mouth "mmm" with vocal fry. There are voices for man, woman, Dadi, kid, mascot, dog and chimp, with one or more yawns in every scene and the music ducking under them.
