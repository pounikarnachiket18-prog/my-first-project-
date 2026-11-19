# House reel style: "Papercraft Mascot Explainer"

**This is the default style for every new reel.** Use it unless the user asks for something else.
The reference reel is "Credit card paise kaise kamata hai?" (71 s, Hinglish), and this file describes it.

## Look
- **3D papercraft / stop-motion diorama.** Everything looks hand-made from cardboard, coloured paper and paper-mache: buildings, desks, shops, vaults and coins.
- Warm, cosy, cinematic lighting with soft depth of field. Palette: kraft brown, mustard yellow, sky blue, brick red, navy.
- **Mascot = the topic as a cute character.** A navy-blue card with gold and light-blue diagonal stripes and a gold chip, plus big googly eyes, a smile, white cartoon gloves, thin legs and yellow shoes.
  - Keep the mascot identical in every shot.
  - For a non-card topic, make the topic object the mascot in the same way (phone, coin, note, etc.).
  - The mascot acts out every point: points, winks, carries coins, peeks out of vaults, wears sunglasses at the end.
- Supporting characters are paper people: bankers in suits, a shopkeeper with a moustache, a boardroom.
- Indian setting: kirana shops, a "BANK" building with columns, street ATMs, ₹ coins and notes.

## Structure (60–75 s)
1. **Hook (0–4 s):** A wide establishing diorama, e.g. a city at night with a BANK building.
   - Big title at the top: line 1 in **yellow, all caps** (the topic); lines 2–3 in **white** (the question in Hinglish).
2. **Myth or setup:** "X free lagta hai na?" Then a "Galat!" reveal.
3. **Numbered points:** "Kamaai #1:", "#2:", and so on. Each point gets 1–3 shots with one clear number (~2%, ₹20, 18% GST).
4. **Outro:** The mascot doing a cool pose, then a wallet or paper close-up as the end card.

## Motion and transitions
- Every shot moves: a slow push-in, a gentle pan, or the mascot animating. Shots run about 2–4 s.
- **Zoom-through match cuts** are the signature: push into an object (calendar, coin, vault door, paper) until it fills the frame, then reveal the next scene.
- Paper textures (crumpled paper ball, folded sheet, kraft paper) work as wipes between sections.

## Motion graphics on top (always add them)
Paper-sticker overlays from `tools/reel_fx.py`, set per shot as `"fx"` in `shots.json` (types are listed in that file). Keep them above y≈1200 so they never cover the captions.
- **Step tracker** at the top for "how it works" sections: numbered dots, with the active one in yellow and pulsing and finished ones ticked in green.
- **Counters** for every number (₹19, ₹23, ₹100/din) that count up and bump, with a small navy label underneath.
- **Stickers:** cream, yellow, navy or red pills with an outline, drop shadow, pop-in and a slight wobble.
- **Stamp slam** (APPROVED) with shake and flash; a **scramble** for encrypted or secret text; a **stopwatch** for "kuch seconds".
- **Ticked checklist** for checks; a **route** (dotted line and travelling packet) for "data goes from A to B"; **pulse** rings; floating **?** marks for confusion.
- Every pop, count, slam and tick has a sound cue.

## Clip library
`library/card-mascot/` has the mascot's AI animations from earlier reels; see the README there for what happens when in each clip. Use them first, with `"media"` clip segments (in/out and slow-mo), and fill the gaps with AI stills or `papercraft.py` scenes.

## Captions (burned in, bottom third)
- 2–3 lines, centred, bold rounded sans (Inter / Poppins Bold), white with a black outline and shadow.
- **Keywords highlighted:** yellow for labels and numbers (`Kamaai #1`, `~2% fee`, `₹0`), red for the punch words (`Galat!`, `paise kamane ki machine`, `right?`, `18% GST`).
- Captions follow the voiceover line by line.
- Language is **Hinglish** in Roman script: "Bill time pe bharte ho? Toh card aapse ₹0 kamata hai… right?"

## Branding
- A small red circle with a white **"M"** logo sits bottom-right, about 60 px from the edges at 1080 px wide, on every frame.
- The Instagram handle is @nachiiiiiiiket.

## Audio
- A Hinglish voiceover runs the whole reel, friendly and fast, with no dead air.
- A light upbeat music bed sits under it, with small pops, whooshes and coin sounds on the beats.

## Pipeline
1. **Script:** Hinglish VO lines. Each line becomes one caption and gets a shot description.
2. **Images:** Generate one 9:16 image per shot with the prompt template below, using Canva `generate-image` or any image AI.
   - Make one AI master shot of the mascot first, and pass it as the reference for every other shot.
   - If image AI isn't available (e.g. no credits), cut the mascot out of the master shot with OpenCV GrabCut.
     Then build the scenes in code with `tools/papercraft.py` (cut-paper shapes with grain, bevels and drop shadows).
     See `projects/atm-kaise/scenes.py` for a full example.
3. **Motion:** Animate each image into a 2–4 s clip.
   - Best: Kling, Veo or Runway image-to-video, with a motion prompt per shot.
   - Fallback: `tools/paper_reel.py`, which does push-in / pan / zoom-through on stills.
4. **Voiceover:** Hinglish AI voice (ElevenLabs etc.), or the user records it.
5. **Assemble:** `python3 tools/paper_reel.py projects/<name>` stitches the shots, burns the captions in this style, adds the M logo, then mixes the VO and music.

### Image prompt template
```
3D papercraft stop-motion diorama, vertical 9:16, handcrafted cardboard and coloured paper textures,
warm cinematic lighting, soft depth of field, cosy. Mascot: a cute cartoon debit card character
(navy blue card with gold and light-blue diagonal stripes, gold chip, big googly eyes, smile,
white cartoon gloves, thin legs, yellow shoes). SCENE: <what happens>. Indian setting. No text
except <sign text if needed>. Leave the bottom third simple for captions.
```
