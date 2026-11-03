# Nachiket · Mindset Mode India: 3D website

My self-introduction website, with a live 3D scene in the background.

## Open it
Double-click `index.html`. It opens in Chrome, Edge or Firefox. Nothing to install.

## What's on the page
- **Hero**: "नमस्ते, I'm Nachiket", with words that change (mindset, discipline, focus…).
- **About me**, **The channel** (Mindset Mode India + 4 content pillars), **How a video is born**, **What I believe** (quote), and **Let's connect**.
- **3D mind**: a glowing core with saffron/white/green orbit rings, floating shapes and stars. It moves to a new spot for each section as you scroll, follows your mouse, and gives off a burst of energy when you click or tap the background.
- Cards tilt in 3D when you hover over them. It works on phones too.

## Change the text or links
Everything you read is in `index.html`. Open it in any text editor.
- **Your real links:** look for comments that say *Replace…*. The YouTube buttons currently search YouTube for "Mindset Mode India". The **Instagram** and **Email** buttons are placeholders (`href="#"`). Put your profile link in place of the `#`, and use `mailto:you@example.com` for email.
- **Hero words that change:** `ROTATING_WORDS` at the top of `src/main.js`.

## Change the 3D scene (optional)
The 3D code is in `src/main.js`. After you edit it, rebuild `app.js`:
```bash
cd website
npm install      # first time only
npm run build
```
Each `<section>` in `index.html` has `data-x / data-y / data-z / data-amp / data-s` attributes. These set where the 3D mind sits, how far away the camera is, how much the core wobbles, and its size while that section is on screen.

Built with [three.js](https://threejs.org) (bundled into `app.js`, so it works offline apart from Google Fonts).
