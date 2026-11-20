# Royal Enfield: motion-graphics cut

Output: `reels/output/royal-enfield-reel-motion.mp4` (1080x1920, 30 fps, 57.9s, about 9 Mbps, with Devika's voiceover).

## Pipeline
1. `vo_lines.json`: start and end of each voiceover line, found from the pauses in the voiceover (sped up 1.13x, starts at 2.4s).
2. `build_segments.py`: retimes each clip to its line (0.8x–1.46x speed), removes the Flow ✦ watermark (delogo), and builds Hook 1 as play → 2s freeze → tail. It writes `timeline2.json`. The "Oh! Wow… DREAM BIKE!" banner text is baked into segment 05.
3. `audio_mg.py`: synthesized soundtrack on the new timing (patakas, scratch and stamp, gramophone, rain, clang, a dug-dug heartbeat that flatlines, then the kick-start), plus typewriter, counter and tap sounds for the graphics. It writes `beats.json`.
4. `mg.html` + `render_mg.js`: a canvas motion-graphics layer drawn frame by frame:
   - kinetic word-by-word captions
   - the freeze-frame RUKO! stamp, doodle circle and "GALI KA DON" tag
   - a BULLET-O-METER HUD (needle, rolling year odometer that rewinds for the flashback, live heartbeat line that turns red with NO PULSE)
   - typewriter location and date tags
   - PATAAK/DUG/VROOOM comic pops, sparks, speed lines, rain, film scratches, dust, shockwaves and light leaks
   - a 12,38,659 counter card, a Follow-button tap with confetti, and a progress bar
5. `compose.py`: camera moves with zoompan (a push-in on every shot, zoom punches and shake on impacts), whip blur on cuts, a grade with vignette and grain, the graphics layer piped in as PNG frames, the logo, and the soundtrack with the voiceover ducking it.
