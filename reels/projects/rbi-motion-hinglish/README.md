# RBI — Motion Cut (Hinglish)

The Hinglish version of [`rbi-motion`](../rbi-motion/README.md), with an `@handle` watermark. It's the same 48-second 1080×1920 motion-graphics transformation of `RBI_Documentary.mp4`, with all on-screen text in Hinglish.

Output: `reels/output/rbi-motion-hinglish.mp4`

## Set your handle

Open `index.html` and change one line in `CONFIG`:

```js
handle: "@yourhandle",   // <-- your Instagram/YouTube handle
```

It appears in two places:
- a watermark in the top-right corner for the whole video
- a gold **"Follow @handle"** button on the final screen

Set it to `""` to turn both off. Then re-render.

## Render

```bash
cd reels
node tools/render.mjs projects/rbi-motion-hinglish --preview   # still frames -> output/rbi-motion-hinglish-contact.jpg
node tools/render.mjs projects/rbi-motion-hinglish             # final video  -> output/rbi-motion-hinglish.mp4
```

## Script (on-screen text)

| Time | Scene | Text |
|---|---|---|
| 0:00 | Source | 2 minute ki documentary… → Ab **motion** mein. |
| 0:03 | Hook | Har rupaya… jo tumhari jeb mein hai… Har loan… sabke peeche sirf **EK** institution. |
| 0:07 | Title | INDIA KA CENTRAL BANK · The Reserve Bank of India · SIRF 45 SECOND MEIN |
| 0:10 | 01 Shuruaat | 1935 Kaam shuru · 1937 HQ shift: Bombay · 1949 Nationalise hua |
| 0:15 | 02 Kai roles | Monetary policy, Currency, Sarkar ka banker, Banks ka banker, Regulator, Forex ka rakhwala → **6 kaam. 1 bank.** |
| 0:20 | 03 Note aur sikke | Notes: RBI jaari karta hai · Coins: Sarkar banati hai, RBI ke zariye |
| 0:24 | 04 Mehangai se jung | Monetary Policy Committee: 3 RBI se, 3 Sarkar se · **4%** mehangai target, 2–6% band |
| 0:29 | 05 Repo rate | REPO ▲ → Loan mehenga → Kharcha kam → Mehangai thandi · REPO ▼ → Loan sasta → Udhaar badhta → Growth tez |
| 0:35 | 06 Aur hathiyaar | CRR, SLR, OMO |
| 0:39 | 07 Digital payments | UPI, RTGS, NEFT, Cards → Har mahine **arabon payments.** |
| 0:42 | Outro | Chupchaap. Aksar nazar se door. Ek hi maqsad: **STABLE PAISA.** → Follow @handle |
