# my-first-project-
My first project while learning GitHub.

My First Project

Hello! I am learning GitHub from scratch.

About This Project

This is my first repository. I am using it to understand how GitHub works.

My Learning Goals

* Learn GitHub basics.
* Understand repositories and commits.
* Learn programming.
* Build my first website.
* Explore artificial intelligence.

My Progress

I have successfully created my first GitHub repository!

## My 3D website
Open `website/index.html` to see my 3D self-introduction site (Nachiket · Mindset Mode India). See [`website/README.md`](website/README.md) to edit it.

## Content Creation Toolkit

**Setup (once):** `bash setup.sh` installs everything: Node packages (gsap, sharp), Python packages (numpy, scipy, pillow), checks ffmpeg and Playwright, and builds the sound-effects library.

### Image Studio (in your browser)
Open `image-studio/index.html` in Chrome, Edge or Firefox. Double-click the file; there's nothing to install.
- **Find images:** search 800M+ free images on Openverse. By default it shows only **CC0 / public-domain** images, which need no credit and are OK for commercial use. You can also pick random photo backgrounds, or Pixabay (needs a free API key).
- **Editor:** reel/story (1080×1920), Instagram post, YouTube thumbnail and other sizes; drag to frame, adjust brightness/contrast/blur, add a dark fade, bold headline text (`*word*` = highlighted), Hindi font, and an `@handle` watermark. Export as PNG or JPG, or copy to the clipboard.
- You can also drop, paste or upload your own photos.

### Caption Studio (in your browser)
Open `caption-studio/index.html`. Pick a topic and pillar to get hooks, then build a caption with key points, a call to action and hashtags, in English, Hinglish or Hindi, for Instagram Reels or YouTube Shorts. Save captions to an idea bank and track each one from Idea to Posted. See [`caption-studio/README.md`](caption-studio/README.md).

### Download free images from the terminal
```bash
cd reels
npm run find-images -- "city night" --tall --count 8   # -> reels/downloads/city-night/ + credits.txt
```

### Reels
See [`reels/README.md`](reels/README.md).

### Documentary → motion graphics
[`reels/projects/rbi-motion`](reels/projects/rbi-motion/README.md) turns the 2-minute `RBI_Documentary.mp4` into a 48-second vertical motion-graphics reel. Output: `reels/output/rbi-motion.mp4`.
