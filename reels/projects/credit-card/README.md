# Credit card reel: "Credit card paise kaise kamata hai?"

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

## Voiceover version
`reels/output/credit-card-reel-voiceover.mp4` adds the ElevenLabs voiceover (Devika), sped up 1.096x from 76.7s to 70.0s with pitch kept (`voiceover_70s.mp3`). It starts at 0.15s, and the music and SFX duck under the voice:
```bash
ffmpeg -i credit_card_reel.mp4 -i vo70.wav -filter_complex "[1:a]adelay=150|150,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.5:LRA=7,asplit=2[vo][sc];[0:a]volume=0.55[bed];[bed][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[duck];[duck][vo]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k credit_card_reel_vo.mp4
```
