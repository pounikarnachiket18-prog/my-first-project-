# Royal Enfield reel: "Ye bike asli mein British thi"

Paper-craft reel built from 15 Google Flow clips: 3 hook clips, your 10 story clips (01 skipped; 02 used for the global pie), and clips A, B and C. Output: `reels/output/royal-enfield-reel.mp4` (1080x1920, 30 fps, 55.8s).

Order: Hook 1 (chapri; freeze frame at 2.4s with a record scratch) → Hook 2 (memory) → Hook 3 (England closes) → 04 → 05 → 06 → 07 → 08 → A → 09 → 10 → B → 03 → 02 → C. Clips A and 09 are graded faded; B, 03, 02 and C are graded brighter.

Sound (`audio_re.py`, all synthesized): patakas and revving on the hook, a record scratch on the freeze, a gramophone tune in Hook 2 that slows in Hook 3 with rain, a gate clang and a teardrop plink, then the "dug-dug" heartbeat. The heartbeat slows through A and 09, goes silent, and comes back after a kick-start in 10, with an upbeat bed from there.

Watermark: `reels/assets/mindset-mode-logo-80.png` sits at 860,1700 and covers the Flow ✦ mark.

Rebuild: put the trimmed segments in `seg/` (see `list.txt`), then run `node render_overlays.js`, `python3 audio_re.py` and `python3 assemble.py`.
