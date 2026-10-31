# RBI — Motion Cut

A motion-graphics transformation of `RBI_Documentary.mp4` (the 2-minute explainer in the repo root).

| | Original documentary | Motion cut |
|---|---|---|
| Format | 1920×1080 (16:9) | 1080×1920 (9:16 reel) |
| Length | 2:05 | 0:48 |
| Style | Calm narration, slow builds, captions | Kinetic typography, animated infographics, hard cuts, camera shake, SFX on every beat |
| Output | `RBI_Documentary.mp4` | `reels/output/rbi-motion.mp4` |

## How the documentary was transformed

Every chapter of the original documentary became one fast motion-graphics scene:

| Time | Scene | Documentary chapter → motion treatment |
|---|---|---|
| 0:00 | Source | The original film plays in a "monitor", then glitches and explodes into the new style |
| 0:03 | Hook | "Every rupee… every loan… ONE institution": a 3D-spinning ₹ coin and a slam-in word |
| 0:07 | Title | Stacked title lines whip in from alternating sides |
| 0:10 | 01 Origins | Giant 1935 → 1937 → 1949 year flips on a timeline that fills as it goes |
| 0:15 | 02 Many hats | The RBI hub shoots out 6 role pills on dashed connectors: "6 jobs. 1 bank." |
| 0:20 | 03 Money | A fan of banknotes flies in and coins drop with a bounce: notes (RBI) vs coins (Govt) |
| 0:24 | 04 Inflation | The 6-member MPC pops in, and a gauge needle swings and settles on the 4% target (2–6% band) |
| 0:29 | 05 Repo rate | Money particles flow RBI → Banks → You, then REPO ▲ and REPO ▼ cascade side by side |
| 0:35 | 06 Levers | CRR / SLR / OMO cards slam in, each with a filling meter |
| 0:39 | 07 Payments | A live network with pulses running along its edges: UPI, RTGS, NEFT, cards |
| 0:42 | Outro | "Quiet. Often unseen. One goal: STABLE MONEY." and the closing ₹ lockup |

## Render

```bash
cd reels
node tools/render.mjs projects/rbi-motion --preview   # contact sheet -> output/rbi-motion-contact.jpg
node tools/render.mjs projects/rbi-motion             # final -> output/rbi-motion.mp4
```

`images/src1-4.jpg` are stills taken from the original documentary for the opening "source" shot. To grab different ones:

```bash
ffmpeg -ss 30 -i ../../../RBI_Documentary.mp4 -frames:v 1 -vf scale=1280:-1 images/src2.jpg
```

## Make your own documentary → motion cut

1. List the documentary's chapters and pull **one key fact or number** from each.
2. Give each chapter **one visual idea**: a counter, a chart, a diagram, a big word.
3. Copy this folder and edit the `TIMELINE` section of `index.html`. Each scene is a block of roughly 4–6 seconds.
4. Preview with `--preview`, then render.
