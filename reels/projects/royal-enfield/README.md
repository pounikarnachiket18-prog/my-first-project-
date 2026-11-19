# Royal Enfield reel: "Ye bike asli mein British thi"

Paper-craft reel built from 15 Google Flow clips: 3 hook clips, your 10 story clips (01 skipped; 02 used for the global pie), and clips A, B and C. Output: `reels/output/royal-enfield-reel.mp4` (1080x1920, 30 fps, 55.8s).

Order: Hook 1 (chapri; freeze frame at 2.4s with a record scratch) → Hook 2 (memory) → Hook 3 (England closes) → 04 → 05 → 06 → 07 → 08 → A → 09 → 10 → B → 03 → 02 → C. Clips A and 09 are graded faded; B, 03, 02 and C are graded brighter.

Sound (`audio_re.py`, all synthesized): patakas and revving on the hook, a record scratch on the freeze, a gramophone tune in Hook 2 that slows in Hook 3 with rain, a gate clang and a teardrop plink, then the "dug-dug" heartbeat. The heartbeat slows through A and 09, goes silent, and comes back after a kick-start in 10, with an upbeat bed from there.

Watermark: `reels/assets/mindset-mode-logo-80.png` sits at 860,1700 and covers the Flow ✦ mark.

Rebuild: put the trimmed segments in `seg/` (see `list.txt`), then run `node render_overlays.js`, `python3 audio_re.py` and `python3 assemble.py`.

## Banner text and voiceover
- Clip 05's blank banner gets "Oh! Wow… DREAM BIKE!" (`banner_text.js` → `ov/bannertext.png`). It fades in 2.35s into the clip, once the banner has fully unrolled.
- `reels/output/royal-enfield-reel-voiceover.mp4` adds Devika's voiceover, sped up 1.13x from 59.9s to 53.0s (`voiceover_53s.mp3`). It starts at 2.4s on the freeze frame, and the music and SFX duck under it.

## Motion-graphics version
`reels/output/royal-enfield-reel-mg.mp4`: the voiceover reel with a full motion-graphics layer in `mg/`.
- Paper-strip kinetic captions (word-by-word pops, marker highlights) that cover the old captions.
- Comic "RUKO!" burst with a Union Jack on the black-and-white freeze frame; speed lines and pataka sparks on the hook.
- Era stamps (1970, 1955, 1994…), a progress road with a bike, paper-tear / flash / dip-to-black transitions.
- Per-clip graphics: CLOSED stamp, tricolour confetti, DUG! words, RUTBA level bar, England→India ship map,
  Army crate label, mileage bars, crashing GHAATA chart, repair-mode bar, bullseye, Ladakh route, 12,00,000+ counter,
  model chips and a FOLLOW end card that covers the old banner.
- Camera punch-zooms and shake, sepia flashback, grain and vignette, plus synced SFX on top of the voiceover mix.

Rebuild: `node mg/render_mg.cjs` (needs Playwright), then `python3 mg/compose.py` (needs ffmpeg, numpy, scipy).
