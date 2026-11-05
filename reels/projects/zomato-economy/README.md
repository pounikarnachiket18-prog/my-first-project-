# Zomato Economy — reel

The user's clips and Hindi voiceover, cut into a 75.7 s vertical reel (1080×1920, 30 fps, -14 LUFS).
Output: `reels/output/zomato-economy.mp4` (plus `-cover.jpg` and `-contact.jpg`).

```bash
python3 vo.py      # tighten the voiceover to 75 s (shorter pauses, laugh at the end cut, x1.08 pitch-safe)
python3 audio.py   # original music bed + sound design + dramatic sting + mix -> build/mix.wav
python3 build.py   # picture + mux -> ../../output/zomato-economy.mp4
python3 build.py --preview            # 30-frame contact sheet
python3 build.py --frames 12.5,61.9   # check single frames -> build/check.jpg
```

## Story order (English meaning of the Hindi voiceover)

| Time | Voiceover | Visual |
|---|---|---|
| 0:00 | How Zomato really makes money | ₹500 note shatters → ZOMATO |
| 0:02 | You order ₹500 of food… | note → phone → TOTAL ₹500 |
| 0:07 | …how much of that does Zomato earn? | ZOMATO + ? |
| 0:10 | Zomato doesn't run restaurants or cook | The Great Indian Feast, chef |
| 0:15 | It connects customers, restaurants and delivery partners | ecosystem + Zomato circle |
| 0:19 | 1. Commission on every order | restaurant owner, orders |
| 0:23 | In return: new customers, more orders | owner + coins, Mumbai rider |
| 0:27 | Delivery charges and platform fees | checkout, receipt lines |
| 0:32 | Convenience is a business | The Hidden Cost of Convenience |
| 0:34 | Restaurants buy ads | food ad cards |
| 0:38 | Zomato Gold subscriptions | gold card |
| 0:43 | But — not all of it is profit | night rider, coin jar |
| 0:48 | Delivery, tech, marketing, operations cost money | expenses collage |
| 0:53 | Q2 FY27: net order value ₹11,445 cr | rider, map |
| 1:01 | Adjusted revenue ₹3,879 cr | bars, card |
| 1:04 | Adjusted EBITDA ₹627 cr | red bar |
| 1:07 | Zomato turns convenience into business | delivery at the door, gift opens |
| 1:12 | Follow Mindset Mode India | brand card |

## Fixes made to the AI clips
- Wrong/garbled titles covered with clean paper banners: "Doomscrolling" (2 clips), "Vox" logo, "A layered paper journey", garbled map counter title.
- Avoided frames with typos: "PLATFORM CFEE", "KITCHEN KITCHEN", "ORDER TOAR", "TADXUAN", the ₹4,780 / ₹3,686 / ₹13,8xx flashes.
- The Gemini sparkle on every clip is covered by a small Mindset Mode "M" badge.
- Unused: `question_unused.mp4`, `kitchen_unused.jpg` (has "KITCHEN KITCHEN").
