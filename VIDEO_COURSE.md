# Making Videos with Claude Code — a beginner course

A step-by-step course for using Claude Code to make videos, built around the tools that are already in this repo.

---

## The big idea (read this first)

**Claude Code doesn't "draw" a video. It writes code, and that code makes the video.**

You describe what you want in plain words. Claude writes the files (HTML, Python, ffmpeg commands), runs them, looks at the result, and fixes what's wrong. You are the **director**. Claude is the **editor, animator and programmer**.

Because the video is code:
- every change is just a sentence ("make the title bigger", "slow down scene 3"),
- every version can be saved in git and brought back later,
- you can reuse one video as a template for the next ten.

---

## The 3 ways to make video with code

| Method | Good for | Tools | In this repo |
|---|---|---|---|
| **1. Animated web page → video** | Reels, kinetic text, motion graphics, explainers | HTML + CSS + GSAP, recorded frame by frame with Playwright | `reels/` (the `phone-enemy` reel) |
| **2. Edit existing media** | Slideshows from photos, trimming clips, adding music or captions, resizing for different platforms | `ffmpeg` | `RBI_Documentary.mp4` was built this way |
| **3. Python scripts** | Data animations, charts that move, generated images | Pillow, numpy, MoviePy | `reels/tools/sfx.py` (it synthesizes the sound effects) |

**Start with method 1.** Your reels pipeline already works, and it gives the best-looking results.

---

## The workflow (use it for every video)

```
1. SCRIPT      → what is said and shown, second by second
2. STORYBOARD  → list of scenes: duration, text, visual, sound
3. BUILD       → Claude writes the code
4. PREVIEW     → still frames (contact sheet), not the full video
5. RENDER      → the final MP4
6. REVIEW      → you watch it and give notes
7. ITERATE     → back to step 3 with specific notes
8. COMMIT      → save the version in git
```

Previewing before rendering matters: a contact sheet takes seconds, while a full render takes minutes.

---

## Lesson 1 — How to talk to Claude about a video

A weak prompt:
> make a reel about saving money

A strong prompt:
> Make a new reel in `reels/projects/save-money`, copied from `phone-enemy`.
> - Format: 1080×1920, 30 fps, **25 seconds**
> - Audience: Indian college students. Language: Hinglish.
> - Hook (0–3s): "Salary aate hi khatam?" in huge red text with a glitch
> - Body: 3 tips, about 6 seconds each, one big word per beat
> - End (last 4s): "Follow for more" plus my handle @myhandle
> - Style: dark background, red accent, same as phone-enemy
> - Render a **preview contact sheet first** and show it to me before the full render.

**The checklist for every video prompt:**
1. **Where:** which folder or project
2. **Format:** size (1080×1920 for reels/shorts, 1920×1080 for YouTube), fps, duration
3. **Who:** audience and language
4. **What:** the script, or the topic and key points
5. **Look:** colors, fonts, a reference ("like phone-enemy")
6. **Process:** "preview first", "render only seconds 6–10"

---

## Lesson 2 — Your first hands-on exercise

Tell Claude, one message at a time:

1. `Run bash setup.sh and tell me if anything failed.`
2. `Render a preview of the phone-enemy reel and show me the contact sheet.`
3. `Change the hook text to "Tumhara phone tumhara dushman hai" and re-render only the first 4 seconds.`
4. `Commit this change with a clear message.`

What you learn: setup, preview vs. render, partial renders, saving versions.

---

## Lesson 3 — Giving good feedback (the iterate step)

Vague notes get vague fixes. Point to **a time, a thing, and a change**:

| ❌ Vague | ✅ Specific |
|---|---|
| "It's boring" | "Scenes 2–4 feel slow. Cut each from 6s to 4s and add a `whoosh` on every word." |
| "Text looks bad" | "At 0:08 the second line touches the edge. Make it 20% smaller." |
| "Change the music" | "Lower the sound effects by half after 0:15." |

Tip: ask Claude to *"render a frame at 8.5 seconds and show it to me"* when you want to discuss one exact moment.

---

## Lesson 4 — Editing real media with ffmpeg

Things you can just ask for:
- "Make a 30-second slideshow from the photos in `reels/downloads/city-night/`, 3 seconds each, slow zoom, with a fade between them."
- "Cut `RBI_Documentary.mp4` from 0:20 to 0:50 and save it as a 9:16 vertical clip with a blurred background."
- "Add burned-in captions from `captions.srt`."
- "Make a 1280×720 thumbnail from the frame at 0:12."

You don't need to learn ffmpeg yourself. It still helps to ask *"explain the command you used"* so you learn as you go.

---

## Lesson 5 — Scripts first

Claude is a strong scriptwriter. You have a **HypoExplained** skill set up (4-minute Hinglish scripts). Ask:
> Write a HypoExplained script on UPI, then turn it into a storyboard table of scenes, and then build it as a 16:9 video.

That one prompt covers steps 1 → 3 of the workflow.

---

## Lesson 6 — Make your own reusable template

After two or three videos, ask:
> Look at my reels. Turn the common parts into a template so a new reel only needs a `script.json` file with the lines, timings and colors.

From then on, a new video = write a JSON file + one render command.

---

## Good habits

- **One change per message** while you're learning. It's easier to see what each one did.
- **Commit after every version you like:** "commit this as v2".
- **Don't commit big MP4s** to git if you can avoid it. They make the repo heavy. `reels/output/` is the place for renders. Ask Claude about Git LFS if you want to keep them.
- **Image rights:** use CC0 / public-domain images (the Image Studio and `find-images` default to these) or your own photos.
- **Ask "why"** whenever Claude does something you don't understand. That's how you learn.

## What Claude Code can't do (yet)

- It can't film real footage or generate realistic AI video clips the way Sora or Veo do. It makes **motion graphics, edits and animations**.
- It needs a text-to-speech tool or your own recording for a real **voiceover**. Record yourself, drop the file in, and ask Claude to sync the animation to it.
- It can't "watch" a video in real time, but it **can look at still frames**. That's why previews and contact sheets matter.

---

## Your progress

- [ ] Lesson 1: Wrote a strong video prompt
- [ ] Lesson 2: Rendered a preview and a partial render
- [ ] Lesson 3: Iterated with specific feedback
- [ ] Lesson 4: Edited real media with ffmpeg
- [ ] Lesson 5: Script → storyboard → video
- [ ] Lesson 6: Built my own template
