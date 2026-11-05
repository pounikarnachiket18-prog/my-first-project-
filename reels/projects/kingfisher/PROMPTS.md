# Kingfisher reel: prompts for 7 new clips

Full order (every clip plays in full, 4 s each, 9:16):

**COLD → A → B → C → D → E → 1 … 12 → tree → logo → LOOP**, then back to COLD.

21 clips × 4 s = **84 s**:
- 0–4 s: cold open, with the airport chime and the "now boarding" announcement
- 4–79 s: your 75 s voiceover
- last 4 s: LOOP, with the chime and the "flight cancelled" announcement

LOOP ends on COLD's first frame, so the reel repeats with no visible restart.

Save the files in `clips/` as `cold.mp4`, `A.mp4` … `E.mp4`, `loop.mp4`. `clean.sh` picks them up automatically.

## How to get perfect transitions
Every clip **ends on one flat full-frame colour, and the next clip starts on that same colour.** Your existing clips already join this way.
1. Use the generator's **image-to-video / first-and-last-frame** option (Veo "Frames to video", Kling, Hailuo, Runway, Luma).
2. Make the clips **in order**. Use the last frame of each clip as the first frame of the next one. If you send each clip to me, I'll extract the exact frame for you.
3. For clip E, upload `output/kingfisher-prompt-frames/END-FRAME-for-new-clip-E.png` as the **last frame**. It is clip 1's exact first frame, so E → 1 joins with no visible cut.

## Style block: paste at the start of EVERY prompt
> 2D paper-cut stop-motion collage animation, layered matte craft paper with visible paper grain and soft drop shadows, flat colours. Warm cream paper background (#F0ECDA). Palette: Kingfisher red (#CD2628), mustard yellow (#EBBA37), teal (#74BECC), navy blue. Vertical 9:16, 4 seconds, smooth motion. No people, no faces, no extra text or logos except what is described.

---

## Clip COLD: cold open (make this one FIRST)
**Start:** a crumpled ball of red paper (#CD2628) lying in the centre of plain cream paper (#F0ECDA), with a soft shadow. Hold still for half a second.
**Action:** the ball slowly un-crumples as if time runs backwards. It flattens, unfolds and refolds itself into a red paper-cut kingfisher bird with teal and yellow wing feathers. The bird flaps once and flies straight up out of the top of the frame.
**End frame:** plain cream paper (#F0ECDA) filling the whole frame, with nothing on it.
*Send this clip to me first. Its first frame becomes the end frame for LOOP.*

## Clip A: hook ("Ek waqt tha…")
**Start:** full-frame plain cream paper (#F0ECDA).
**Action:** A red paper-cut kingfisher bird with teal and yellow wing feathers flies in from the left, makes one graceful loop and leaves a trail of small gold paper sparkles. It turns and flies straight at the camera with its wings spread wide.
**End frame:** the red wing covers the whole frame. Full-frame flat solid red paper (#CD2628), nothing else visible.

## Clip B: "luxury ki pehchaan"
**Start:** full-frame flat solid red paper (#CD2628).
**Action:** The red paper splits down the middle and slides apart like theatre curtains. Behind it is a cream paper stage. A red carpet rolls toward the camera while a golden paper crown, a champagne glass and gold sparkles pop up in layers.
**End frame:** the golden crown rises to the centre and grows until it fills the frame. Full-frame flat solid mustard yellow paper (#EBBA37).

## Clip C: "2005 mein… naya dream"
**Start:** full-frame flat solid mustard yellow paper (#EBBA37).
**Action:** The yellow paper tears open from the centre with ragged paper edges. Behind it is a large red paper desk calendar on cream paper showing the year "2005". Red, teal and yellow paper confetti bursts around it.
**End frame:** the calendar page flips up and the page underneath is plain teal. The camera pushes in until teal fills the frame. Full-frame flat solid teal paper (#74BECC).

## Clip D: "flying ka experience hi badal gaya"
**Start:** full-frame flat solid teal paper sky (#74BECC).
**Action:** Layered cream paper clouds slide in at different depths (parallax). A small red paper airplane flies across and draws a smooth curved dotted white flight path. Gold sparkles twinkle.
**End frame:** two big cream paper clouds slide in from the left and right and meet in the centre. Full-frame flat plain cream paper (#F0ECDA).

## Clip E: handoff into clip 1
**Start:** full-frame flat plain cream paper (#F0ECDA), extreme close-up on the paper texture.
**Action:** The camera slowly pulls back. A red paper boarding pass drifts down from the top, spins once and lands on a cream paper gatefold card lying flat in the centre. The card's two panels fold closed over it with a soft paper flap.
**End frame (use END-FRAME-for-new-clip-E.png):** a closed cream gatefold paper card, centred on cream paper background, left panel wider than the right panel, soft shadow, no other objects.

## Clip LOOP: the ending that loops back to the start
**Start (use `START-FRAME-for-LOOP-clip.png`):** the last frame of the logo outro, the MINDSET MODE INDIA card on a soft blurred background.
**Action:** the logo card lifts off the page. Its blue, teal and red paper frame folds inward, and the whole card scrunches up into a crumpled red paper ball that drops and rolls to the centre of plain cream paper.
**End frame (use `START-FRAME-of-COLD.png`, which I'll make from your cold clip):** a crumpled red paper ball (#CD2628) in the centre of plain cream paper (#F0ECDA), with a soft shadow. This is identical to COLD's first frame.

