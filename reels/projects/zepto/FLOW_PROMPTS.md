# Zepto reel: "Zepto paise kaise kamata hai… phir bhi loss kyun?" 🛵💸

**Same look as the credit card reel:** a 3D cardboard and papercraft miniature set with a cute mascot, warm cinematic light, bold Hinglish captions and the red **M** badge.
**Length:** 14 shots × 4s = **56 s**. After trimming 0.35 s per cut (as in credit card) it comes to about 52 s.
**Format:** 9:16 · **Language:** Hinglish · **Voice:** Devika (ElevenLabs)
**Tool:** Google Flow (Veo 3.1), 4s clips at 720×1280, upscaled to 1080×1920.
**Captions and badge:** reuse `reels/projects/credit-card/render_overlays.js` and `captions.json` (on the `claude/credit-card-rewards-reel-rgo6f6` branch), or CapCut.

## Why it's built this way (from @mindset_mode_co Insights)
| What the data showed | What this reel does |
|---|---|
| Credit card had the most shares per view but the **worst opening (60% skipped)** | Same look and numbered "Kamaai #" format, but the opener shows a **contradiction** (Zomato's 32%-skip formula) and the loss number lands by 0:06 |
| Story reels (Kodak, BlackBerry) held viewers longest (about 16 s); list reels about 9–11 s | A short **rise story** (19-year-old dropouts, dark stores) comes before the money list |
| Viewers leave around 10–15 s | The best surprise, the "dark stores" secret, is revealed by 0:16 |
| The credit card reel was 72 s | This one is about 52 s |
| Comments were almost zero | The CTA is an easy personal question: "Last Zepto se kya mangaya?" |

---

## 0. Rules
1. **4s per shot.** If Flow makes 8s, keep the best 4. The action is at the start of every prompt.
2. **No text, numbers or logos inside the AI video.** Veo garbles them. Every number, "Zepto" and the title go on as captions afterwards.
3. **No real people and no real brand logos, uniforms or app screens.** Papercraft characters like the bankers in the credit card reel are fine.
4. **Cuts:** hard cuts, as in credit card. For the big turn (shot 13) use a paper crumple or tear, like the crumpled-paper beat in credit card.
5. **Audio:** every prompt says *no dialogue, no music*. Devika's voiceover, music and SFX go on afterwards, ducked as before.
6. Test on **Veo 3.1 Fast**, regenerate the keepers on **Quality**, and use **Portrait 9:16**.
7. Cover the Flow ✦ mark with the red **M** badge, bottom right, as in every previous reel.

## 1. Style line: paste at the END of every prompt
> Handcrafted 3D papercraft and cardboard miniature diorama, stop-motion look, sets built from corrugated cardboard, kraft paper and painted paper cutouts, warm cinematic lighting, shallow depth of field, soft bokeh, rich warm palette of kraft brown, mustard yellow, teal sky blue and red, with deep purple accents. 4 seconds. Vertical 9:16. No dialogue, no music. No on-screen text, no letters, no numbers, no logos, no brand names.

## 2. Make the mascot ingredient FIRST: "Thaila" 🛍️
It belongs to the same family as the credit card mascot (same googly eyes, white gloves and yellow shoes), so your page feels like one series.
```
A cute cartoon mascot character made of papercraft: a deep-purple (#4A1A8C) paper grocery delivery bag standing upright, with two folded paper handles on top like ears, big round white googly eyes with black pupils, a small happy open mouth, white cartoon gloves, thin dark legs and chunky yellow cartoon shoes. Slight paper-fold texture, a thin hot-pink paper stripe across the front. Full body, friendly standing pose, on a kraft-paper desk in a warm cardboard room, soft studio lighting, shallow depth of field. No text, no letters, no logos on the bag.
```
Generate 4 versions, pick the cutest, and upload it as the **ingredient** in every shot below that says *Ingredient: Thaila*.

Optional second ingredient, **the rider:**
```
Papercraft miniature character: a delivery rider on a small cardboard scooter, plain deep-purple paper jacket, white paper helmet with a dark visor, an insulated cardboard delivery box on the back with no printing. Side view in a warm cardboard street diorama, shallow depth of field. No text, no logos.
```

---

## 3. The 14 shots
Caption colours follow the credit card reel: white text, key word **yellow**, danger word **red**.

### SHOT 1 · 0:00–0:04 · HOOK / TITLE · Ingredients: Thaila, rider
```
A cardboard miniature Mumbai apartment building at dusk with warm glowing windows. The front door bursts open and the papercraft delivery rider zooms out on his cardboard scooter with Thaila sitting proudly on the back, gloves raised, as a big cardboard stopwatch on the wall spins its hand fast. Camera: low-angle 35mm, quick push-in toward Thaila. [STYLE LINE]
```
**Title (top, like the credit card title):** `ZEPTO` (yellow) / `10 minute mein…`
**Caption:** `10 minute mein delivery… phir bhi` **`₹3,367 crore`** (red) `ka loss?`
**SFX:** doorbell, scooter rev, ticking

### SHOT 2 · 0:04–0:08 · THE LOSS · Ingredient: Thaila
```
On a kraft-paper desk, Thaila proudly holds up a big shiny cardboard gold coin with both gloves; the coin suddenly cracks in half and the pieces fall through a crack that opens in the desk. Thaila's googly eyes go huge in shock and its paper handles droop. Camera: 50mm medium close-up, slight push-in on the shocked face. [STYLE LINE]
```
**Caption:** `Ek saal mein` **`₹3,367 crore`** (red) `ka loss… toh` **`kamaata`** (yellow) `kaise hai?`
**SFX:** crack, coins falling, sad trombone tail

### SHOT 3 · 0:08–0:12 · THE RISE
```
Two papercraft young men with backpacks and paper-cut smiles walk out of a grand cardboard university archway with tall columns, then step onto a miniature cardboard Mumbai promenade by a painted paper sea; one unrolls a big blank paper blueprint and the other points at it excitedly. Camera: 35mm tracking shot moving backward in front of them. [STYLE LINE]
```
**Caption:** `Shuru kiya do` **`19 saal`** (yellow) `ke Stanford dropouts ne… 2021 mein`
**SFX:** whoosh, pencil scribble

### SHOT 4 · 0:12–0:16 · RAAZ: DARK STORES · Ingredient: Thaila
```
A narrow cardboard residential lane at night lit by a paper street lamp. Thaila walks up to an ordinary-looking cardboard building, grabs a corrugated-cardboard shutter with both gloves and heaves it up, revealing a glowing interior packed with tall paper racks of unbranded groceries: noodle packets, milk cartons, chips, fruit. Warm light floods over Thaila's amazed face. Camera: 35mm, slow push-in toward the glowing doorway. [STYLE LINE]
```
**Caption:** `Raaz:` **`DARK STORES`** (yellow) `, ghar ke paas chhupe chhote godown`
**SFX:** shutter rattle, light hum

### SHOT 5 · 0:16–0:20 · 1,100+ STORES · Ingredient: Thaila
```
Thaila stands on a giant papercraft map of India laid on a cardboard table and hops from city to city, sticking little purple paper map pins into the map one after another; each pin glows with a soft pink circle as dozens more pop up across the map by themselves. Camera: high-angle 35mm looking down, slowly rising. [STYLE LINE]
```
**Caption:** `Customer andar nahi jaata… India mein` **`1,100+`** (yellow) `aise stores`
**SFX:** a pop for each pin

### SHOT 6 · 0:20–0:24 · THE SPEED · Ingredient: Thaila
```
Inside the cardboard dark store, small pink lights blink on specific paper shelves in sequence. Thaila opens its bag-mouth wide and leaps from shelf to shelf as each lit item, a noodle packet, a milk carton, a bag of chips, flies straight into it; then its paper handles fold shut with a satisfied pop. Camera: 35mm handheld-style tracking shot, fast and playful. [STYLE LINE]
```
**Caption:** `Order aaya → rack pe light →` **`minute bhar mein pack`** (yellow)
**SFX:** ding, fast ticking, tape rip

### SHOT 7 · 0:24–0:28 · THE RIDE · Ingredients: Thaila, rider
```
The papercraft rider speeds along a winding cardboard road through a miniature neighbourhood of paper houses and paper trees, with Thaila tucked in the delivery box on the back, gloves up, enjoying the wind. Layers of scenery slide past in parallax. Camera: side tracking shot at scooter height, 35mm. [STYLE LINE]
```
**Caption:** `Rider pehle se ready… ghar bas` **`2–3 km`** (yellow) `door`
**SFX:** scooter rev, whoosh

### SHOT 8 · 0:28–0:32 · KAMAAI #1: MARGIN · Ingredient: Thaila
```
At a cardboard grocery counter, a single unbranded paper noodle packet sits with a paper price tag hanging off it. Thaila takes a pair of paper scissors, snips a thin sliver off the price tag, and the sliver curls into a shiny cardboard gold coin, which Thaila drops into a small purple paper piggy bank with a happy wink. Camera: 50mm close-up at counter height. [STYLE LINE]
```
**Caption:** **`Kamaai #1:`** (yellow) `har product pe` **`margin`** (yellow)
**SFX:** cash register ka-ching

### SHOT 9 · 0:32–0:36 · KAMAAI #2: FEES · Ingredient: Thaila
```
A cardboard receipt printer on the counter prints a long white paper receipt that keeps unrolling; Thaila pulls it along with both gloves, and with every blank line that comes out a small cardboard gold coin pops off the receipt and drops into a growing pile at Thaila's yellow shoes. Camera: 35mm medium shot, slight tilt down to the coin pile. [STYLE LINE]
```
**Caption:** **`Kamaai #2:`** (yellow) `handling fee + delivery fee +` **`small cart fee`** (red)
**SFX:** printer buzz, three coin drops

### SHOT 10 · 0:36–0:40 · KAMAAI #3 + #4: ADS AND PASS · Ingredient: Thaila
```
A giant cardboard smartphone stands on the desk showing a grid of small unbranded paper product cards; the top card lights up in a spotlight with a glowing gold paper frame, while a papercraft businessman's hand in a suit sleeve slides a stack of paper banknotes behind the phone. Thaila peeks around the side of the phone, sees it, and gasps, then proudly holds up a shiny purple paper membership card with a gold star. Camera: 35mm, starting on the phone, then a quick pan to Thaila. [STYLE LINE]
```
**Caption:** **`Kamaai #3:`** (yellow) `jo product sabse upar…` **`usne paise diye`** (red) → **`#4:`** (yellow) `Zepto Pass`
**SFX:** spotlight "dun", sly sting, sparkle

### SHOT 11 · 0:40–0:44 · WHY THE LOSS: THE RACE · Ingredient: Thaila
```
Three papercraft riders on cardboard scooters, one purple, one yellow and one orange, race neck and neck on a cardboard race track in a miniature stadium; paper banknotes fly out of the back of the purple scooter and curl into small orange paper flames, while Thaila clings to the purple scooter's delivery box with wide panicked eyes. Camera: low-angle 24mm tracking shot, fast. [STYLE LINE]
```
**Caption:** `Phir loss kyun? Blinkit, Instamart se race mein…` **`paisa jalta hai`** (red)
**SFX:** engines, fire crackle

### SHOT 12 · 0:44–0:48 · THE NUMBERS · Ingredient: Thaila
```
On a kraft-paper desk, two cardboard bar-chart columns grow: a tall deep-purple cardboard bar rises upward on the left, while on the right a red cardboard bar grows downward below the desk line into a widening crack. Thaila stands between them, looks up at the tall bar and then down at the red one, and covers its eyes with both gloves. Camera: 50mm medium shot, slow tilt down. [STYLE LINE]
```
**Caption:** `Sales` **`₹9,669 Cr`** (yellow) `vs loss` **`₹3,367 Cr`** (red) `·` **`▲177%`** (red)
**SFX:** bar rise, hit on 177%

### SHOT 13 · 0:48–0:52 · THE TWIST · Ingredient: Thaila
```
The clip starts on a sheet of crumpled white paper filling the frame, which uncrumples to reveal a cosy cardboard bedroom at midnight with a paper moon in the window. A papercraft person lying in bed taps a glowing paper phone to order one tiny packet; on the bedside table Thaila slowly turns toward the camera and gives one slow wink. Camera: slow push-in toward Thaila. [STYLE LINE]
```
**Caption:** `Matlab Zepto ka asli product… grocery nahi,` **`aapki 10-minute wali aadat`** (yellow)
**SFX:** paper crumple, clock tick slowing, deep "bwong"

### SHOT 14 · 0:52–0:56 · CTA · Ingredient: Thaila
```
A warm cardboard room filled with falling colourful paper confetti; Thaila stands on a desk waving both gloves at the camera and then jumps up happily, its paper handles flapping. Camera: 35mm, static, centred. [STYLE LINE]
```
**Follow card (as in credit card):** `Follow @mindset_mode_co` / `for more money secrets`
**Caption:** `Last Zepto se kya mangaya?` **`Comment karo ↓`** (yellow)
**SFX:** confetti pop, doorbell (loops into shot 1)

---

## 4. Voiceover v2: the "4 jebein" script (Devika, about 58–60 s at 1.1×)
The list captions change from "Kamaai #1–4" to **"Jeb #1–4"**.
```
[ding-dong] Aapki Maggi 10 minute mein aati hai… aur Zepto ke ek saal mein 3,367 crore chale jaate hain. [record scratch]
Kaise? Aur end mein bataunga… Zepto asal mein bechta kya hai.
2021. Do 19 saal ke ladke. Stanford chhoda… sapna nahi.
Aapke mohalle mein ek dukaan hai… jismein aap kabhi ghus nahi sakte. Naam? Dark store.
Bahar se godown, andar poora supermarket. India mein 1,100 se zyada.
Order aaya — stopwatch on. Shelf pe light, haath, bag band.
Aur rider? Wo pehle se gate pe khada hai.
Ab paisa. Zepto ki chaar jebein. Jeb ek: har product pe margin.
Jeb do: handling fee, delivery fee, small-cart fee. Chhoti… par roz.
Jeb teen, sabse chalaak: jo product sabse upar dikhe… usne paise diye hain. Jeb chaar: Zepto Pass.
Chaar jebein bhari… phir bhi khaali kyun? Kyunki Blinkit, Instamart se race hai… aur speed sasti nahi aati.
FY25: 9,669 crore ki sales… 3,367 crore ka loss. Pichhle saal se 177 percent zyada.
Toh Zepto bech kya raha hai? Grocery nahi… [1 sec silence] aadat. Ek baar 10 minute ki aadat lagi… toh 30 minute bhi late lagta hai.
Sach batao, last Zepto se kya mangaya? Comment karo… aur bhejo us dost ko jo ek Maggi ke liye bhi Zepto karta hai.
```
Delivery: like a friend telling a secret. Go fast through the lists, and slow down, almost whispering, on "aadat". Pause briefly before every number.

---

## 5. Fact sheet (for the pinned comment and replies)
- **FY25 (year to March 2025):** net loss **₹3,367.3 crore**, up **177%** from ₹1,214.7 crore in FY24. Total sales **₹9,668.8 crore**, up 129%, from audited filings with the Ministry of Corporate Affairs. The sales figure *includes other income*, so call it "sales", not "revenue".
- **Dark stores:** about **1,100+**. Counts differ by date and source (1,139 as of 31 March 2026; 1,255 in another report).
- **Founders:** Aadit Palicha and Kaivalya Vohra, both about **19** when Zepto launched in **2021**. They left Stanford, where they had been studying computer science. Zepto was their second startup, after KiranaKart.
- **"2–3 km" is the typical reported radius of a dark store, not an official Zepto figure.** If you're unsure, change the caption to "bas kuch km door".
- **How it earns:** product margins (the core), handling, delivery and small-cart fees, ads (sponsored listings), and the Zepto Pass subscription. Ad revenue figures vary widely between sources, so **don't quote an ads number**.
- **Don't mention the IPO.** Reports conflict on whether it's paused.

Sources: [Free Press Journal: FY25 loss](https://www.freepressjournal.in/business/zeptos-losses-explode-177-to-3367-crore-in-fy25-despite-sales-doubling) · [Analytics Insight: FY25 sales](https://www.analyticsinsight.net/news/zepto-fy25-sales-surge-129-to-rs-9669-crore-while-net-loss-widens) · [Outlook Business: dark stores and IPO](https://www.outlookbusiness.com/corporate/zepto-ipo-roadmap-12000-cr-issue-eyes-june-listing-amid-burn-reduction) · [Inc42: revenue engine](https://inc42.com/features/zepto-revenue-engine-outrun-quick-commerce-costs/) · [Business Today: 19-year-old founders](https://www.businesstoday.in/latest/corporate/story/how-two-19-year-old-stanford-dropouts-founded-zepto-312034-2021-11-12) · [Bloomberg: teenage Stanford dropouts](https://www.bloomberg.com/news/articles/2021-10-31/teenage-stanford-dropouts-grocery-startup-gets-60-million) · [Entrepreneur India: KiranaKart](https://india.entrepreneur.com/starting-a-business/the-delivery-wonderboys/447692)

---

## 6. Cover, caption and posting

**Cover:** a frame from shot 2 (Thaila shocked, coin cracking) with the title `ZEPTO` (yellow) / `10 min delivery… phir bhi` / `₹3,367 CR LOSS?` (red)

**Caption:**
```
Zepto 10 minute mein deliver karta hai… phir bhi ₹3,367 crore ka loss? 🛵💸

2 dropouts, 19 saal, aur dark stores ka raaz. Zepto kaise kamaata hai, 4 tareeke 1 minute mein 👆
Aakhri tak dekhna… asli product end mein pata chalega 👀

👇 Comment karo: Last Zepto se kya mangaya?
📲 Us dost ko bhejo jo ek Maggi ke liye bhi Zepto karta hai
🔖 Save karo

Source: Zepto FY25 audited results (MCA filings)
Follow @mindset_mode_co for more money secrets 🇮🇳

#zepto #quickcommerce #businessinhindi #businesscasestudy #hindiexplainer
```

**Posting checklist:**
- **Fix the handle on the Follow card.** The credit card reel's card says **@mindset_mode_in**, but your account is now **@mindset_mode_co**.
- Turn on Instagram's **AI label** ("AI info").
- Post at **7:30 PM IST**. Your evening reels got the most shares; this tests it again.
- In the first hour, reply to every comment and pin the fact-sheet comment.
- Share it to your story with a poll: "10 min delivery chahiye? Haan / Nahi".
- **Thaila can become your second mascot**, after the credit card one. Next: "Thaila roasts Swiggy / Blinkit / D-Mart".
