# Credit card reel: "Bank aapse kaise kamata hai?"

Paper-craft reel in the Kodak style: 19 Google Flow clips (4s, 720x1280) with Hinglish captions, a logo, an original music bed and synthesized SFX. Output: `reels/output/credit-card-reel.mp4` (1080x1920, 30 fps, 71.8s).

Clip order (Flow prompt numbers): 1 opener, 2 calendar hook, 3 bank laughs, 4 swipe, 5 where the 2% goes, 6 vault, 7 spend more, 8 annual fee, 9 forex, 11 no-cost EMI, 12 ATM cash, 13 points expire, 14 insurance call, 15 minimum due, 16 co-brand, 17 realisation, 18 turn it around, 19 tips, 20 CTA. Prompt 10 (fuel surcharge) was not generated.

## Rebuild
The source clips are not in the repo. Put them as `seg/01.mp4` … `seg/19.mp4` (scaled to 1080x1920, 30 fps; every clip after the first trimmed by 0.35s), then run these from this folder:
```bash
node render_overlays.js   # captions, title, logo, disclaimer, follow banner -> ov/
python3 audio.py          # music bed + SFX -> soundtrack.wav, timeline.json
python3 assemble.py       # -> credit_card_reel.mp4
```
Edit captions and the handle in `captions.json`.
