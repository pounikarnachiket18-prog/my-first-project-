# Project notes for Claude

This repo belongs to Nachiket (Instagram @nachiiiiiiiket, "Mindset Mode India"). It holds Instagram Reels and a personal website.

## Reels: default style
**Every new reel uses the papercraft mascot style in `reels/STYLE.md`.** Don't ask which style to use.
- That means a 3D papercraft diorama look, a cute mascot of the topic, Hinglish voiceover, bottom captions with yellow and red keywords, and the red "M" logo bottom-right.
- Work in `reels/projects/<name>/` with `script.md` (VO and captions), `shots.json` (shots, image prompts, motion prompts) and `images/`, then assemble with `reels/tools/paper_reel.py`.
- The older HTML/GSAP motion-graphics pipeline (`reels/tools/render.mjs`, used by `rbi-motion` and `phone-enemy`) is only for when the user asks for that look.
- Facts in reels must be correct for India and current. Check numbers (RBI, NPCI, fees) before using them.
