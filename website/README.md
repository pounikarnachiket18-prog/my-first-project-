# Nachiket · Mindset Mode India: 3D website

My self-introduction website, with a live 3D scene in the background.

## Open it
Double-click `index.html`. It opens in Chrome, Edge or Firefox. Nothing to install.

## What's on the page
- **Hero**: "नमस्ते, I'm Nachiket", with words that change (mindset, discipline, focus…).
- **About me**, **The channel** (Mindset Mode India + 4 content pillars), **How a video is born**, **What I believe** (quote), and **Let's connect**.
- **3D mind**: a glowing core with saffron/white/green orbit rings, floating shapes and stars. It moves to a new spot for each section as you scroll, follows your mouse, and gives off a burst of energy when you click or tap the background.
- **Pixel-art 3D icons** float in front of the core (speech bubble, lightbulb, screen, camera, remote, envelope). When you move to a new section, the cubes fly apart and rebuild as the next icon. Click the background and the icon breaks apart and rebuilds itself.
- **Motion-graphics effects:** heading letters fly in and assemble, hand-drawn circles and underlines draw themselves, a typewriter with a block cursor, a curved 3D film strip, a video-editing timeline that pixel scissors cut in two, slice lines on the contact heading, confetti cubes, a background colour for each section, and a big "MINDSET MODE INDIA" ending with a colour flash.
- **Painted, cinematic layer:** a watercolour ink-smoke sky that changes colour per section, a new **"The churn"** section (purple ink smoke, a pixel kalash and ink-bleed text), a **flaming arrow** that lights a **ring of fire** around the quote, and a night-sky ending with a snowy mountain, a rising crescent moon and a handwritten "imagined & created by Nachiket" signature.
- **Nachiket's photo**: a small avatar in the hero, and an arched, temple-style portrait in the About section that assembles from big pixels into a sharp photo. To change the photo, replace `assets/nachiket.jpg` (portrait) and `assets/nachiket-avatar.jpg` (small round avatar).
- **Shiv Tandav** (scroll-driven video): the Tandav video plays from its first frame to its last as you scroll through the section, with lines from the Shiv Tandav Stotram and damru beats. The video is stored as numbered frames in `assets/tandav/` (8 per second). To use a different video, run `ffmpeg -i your-video.mp4 -vf "fps=8,scale=540:-2" -q:v 5 assets/tandav/%03d.jpg` and set `VIDEO_FRAMES` in `src/tandav.js` to the number of frames. A hand-drawn dancer (`src/tandav.js`) shows while the frames load.
- **Background video for the whole page:** the same Tandav video also plays behind every section, from its first frame at the top of the page to its last frame at the bottom, dimmed under the 3D scene. On desktop the blood-red moon sits behind the glowing core like a halo. It's drawn inside the sky shader (`src/cinematic.js`, fed from `src/main.js`). Note: Chrome blocks this when you open `index.html` straight from your computer, so the site then skips the background video. To see everything locally, run `npx serve` in the `website` folder and open the address it prints.
- **Sound** (press the Sound button; it starts off because browsers block autoplay): a tanpura-style Sa–Pa drone, whooshes when you change section, 8-bit blips as the icons rebuild, typewriter clicks, pencil scribbles, a deep rumble for the churn, the arrow's whistle and impact, crackling fire, a scissors snip, sparkles when you click, and a temple bell at the end. Every sound is generated live in the browser, so there are no audio files. The code is in `src/sound.js`.
- Cards tilt in 3D when you hover over them. It works on phones too, and the effects switch off for people who turn on "reduce motion".

## Change the text or links
Everything you read is in `index.html`. Open it in any text editor.
- **Links:** Instagram goes to [@nachiiiiiiiket](https://www.instagram.com/nachiiiiiiiket/), and Email opens a message to nachiketpounikar15@gmail.com. The address is also shown on the page with a **Copy email** button. The YouTube buttons currently search YouTube for "Mindset Mode India"; put your channel's link there when you want.
- **Hero words that get typed:** `ROTATING_WORDS` at the top of `src/main.js`.
- **Film-strip frames:** the `FILM` list in `src/effects.js`.
- **Pixel icons:** `src/icons.js`. Each icon is a small grid of letters, and each letter is a colour. Pick the icon for a section with `data-icon` in `index.html`.

## Change the 3D scene (optional)
The 3D code is in `src/main.js`. After you edit it, rebuild `app.js`:
```bash
cd website
npm install      # first time only
npm run build
```
Each `<section>` in `index.html` has `data-x / data-y / data-z / data-amp / data-s` attributes. These set where the 3D mind sits, how far away the camera is, how much the core wobbles, and its size while that section is on screen. `data-icon` picks the pixel icon and `data-bg` sets the background tint. The optional `data-ix / data-iy / data-is` move and resize the icon.

Built with [three.js](https://threejs.org) (bundled into `app.js`, so it works offline apart from Google Fonts).

## Put it online (Netlify, free)
`netlify.toml` in the repo root tells Netlify what to publish, so there is nothing to configure.

1. Go to **https://app.netlify.com** and sign up with **GitHub**.
2. Click **Add new project → Import an existing project → GitHub** and pick **my-first-project-**.
3. Netlify reads the settings by itself. Click **Deploy**.
4. Open **Project configuration → Change project name** and pick a name, e.g. `mindsetmodeindia`, for **https://mindsetmodeindia.netlify.app**.

Every change pushed to `main` redeploys automatically.

**Vercel instead?** Import the repo at https://vercel.com/new, set **Root Directory** to `website` (the settings come from `website/vercel.json`), and deploy.

**GitHub Pages (optional backup):** turn on Settings → Pages → Source: GitHub Actions, then run **Deploy website** from the Actions tab.
