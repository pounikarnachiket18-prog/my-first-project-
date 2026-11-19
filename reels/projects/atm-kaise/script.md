# ATM kisi bhi bank ka card kaise chalta hai?  (papercraft mascot reel)

House style: `reels/STYLE.md`. About 65 s, Hinglish. **Status:** shot `s02` is done; the other 13 images still need to be generated.

## Steps

1. **Make the 13 missing images.** Paste each prompt below into your image AI (Canva AI, Gemini, ChatGPT, Firefly…).
   - Upload `images/s02.png` as the reference so the mascot looks the same in every shot.
   - Save the results as `images/s01.png`, `images/s03.png`, … at 9:16.
   - `s01` already exists in your Canva account ("AaH1tALY…jpg"). Download it and save it as `images/s01.jpg`.
2. **Motion (optional, looks closest to the reference).** Animate each image in Kling / Veo / Runway with its motion prompt.
   - Save the clips as `clips/<id>.mp4`. Clips are used instead of the stills.
3. **Voiceover.** Record or AI-generate the VO below and save it as `vo.mp3`. Shot lengths fit the VO automatically.
4. **Render:** `cd reels && python3 tools/paper_reel.py projects/atm-kaise` → `output/atm-kaise.mp4`
   - Check first with `--preview`, which writes `output/atm-kaise-contact.jpg`.

## Voiceover script (read it like a friend explaining, fast and fun)

1. Card ek bank ka, ATM doosre bank ka… phir bhi paisa nikal aata hai. Kaise?
2. Sach yeh hai: ATM ko aapke account ka kuch pata hi nahi hota!
3. Step #1: card daala, PIN dabaya… PIN turant encrypt ho jaata hai
4. Matlab ATM wale bank ko bhi aapka PIN dikhta hi nahi
5. Step #2: request jaati hai NPCI ke NFS switch pe… India ka ATM exchange
6. Card ke pehle kuch digits se pata chalta hai… card kaunse bank ka hai
7. Step #3: aapka bank check karta hai: PIN sahi? Balance hai? Limit bachi hai?
8. Sab theek? Account se paisa kata… aur reply gaya: APPROVED!
9. Step #4: ATM se cash bahar… aur yeh sab kuch seconds mein!
10. Par ATM doosre bank ka tha… toh aapka bank usse ₹19 fee deta hai
11. Isiliye doosre bank ke ATM pe free limit: metro mein 3, baaki shehron mein 5
12. Uske baad har transaction pe ₹23 tak charge + GST
13. Paisa kata, cash nahi aaya? 5 din mein wapas… warna bank deta hai ₹100 roz
14. Ab pata hai ATM ke andar kya chalta hai! Follow karo, agla: UPI kaise kaam karta hai?

## Shots: image and motion prompts

### s01: Card ek bank ka, ATM doosre bank ka… phir bhi paisa nikal aata hai. Kaise?
**Image prompt** *(upload s02.png as the mascot reference)*:
```
3D papercraft stop-motion diorama, vertical 9:16, handcrafted cardboard and coloured paper textures, warm cinematic lighting, soft depth of field, cosy. Mascot: a cute cartoon debit card character (navy blue card with gold and light-blue diagonal stripes, gold chip, big googly eyes, smile, white cartoon gloves, thin legs, yellow shoes). Indian setting. Leave the bottom third simple for captions. SCENE: Wide establishing shot of a papercraft Indian city street at night, a cardboard bank building with columns and a sign that says BANK, next to it a small street ATM kiosk with a glowing orange sign that says ATM, warm lit windows, paper buildings around. No mascot.
```
**Motion prompt:** Slow cinematic push-in towards the glowing ATM kiosk, windows flicker softly.

### s02: Sach yeh hai: ATM ko aapke account ka kuch pata hi nahi hota!
**Done:** `images/s02.png`

### s03: Step #1: card daala, PIN dabaya… PIN turant encrypt ho jaata hai
**Image prompt** *(upload s02.png as the mascot reference)*:
```
3D papercraft stop-motion diorama, vertical 9:16, handcrafted cardboard and coloured paper textures, warm cinematic lighting, soft depth of field, cosy. Mascot: a cute cartoon debit card character (navy blue card with gold and light-blue diagonal stripes, gold chip, big googly eyes, smile, white cartoon gloves, thin legs, yellow shoes). Indian setting. Leave the bottom third simple for captions. SCENE: Close-up of a papercraft ATM keypad with chunky paper buttons, the mascot's white glove pressing a button, the card mascot half inserted into the card slot, smiling.
```
**Motion prompt:** Glove presses keys one by one, camera slowly pushes in.

### s04: Matlab ATM wale bank ko bhi aapka PIN dikhta hi nahi
**Image prompt**:
```
3D papercraft stop-motion diorama, vertical 9:16, handcrafted cardboard and coloured paper textures, warm cinematic lighting, soft depth of field, cosy. Mascot: a cute cartoon debit card character (navy blue card with gold and light-blue diagonal stripes, gold chip, big googly eyes, smile, white cartoon gloves, thin legs, yellow shoes). Indian setting. Leave the bottom third simple for captions. SCENE: A sealed paper envelope locked with a big shiny gold paper padlock, floating in front of a papercraft ATM screen, four asterisk symbols on the envelope.
```
**Motion prompt:** Padlock clicks shut, camera zooms into the padlock until it fills the frame.

### s05: Step #2: request jaati hai NPCI ke NFS switch pe… India ka ATM exchange
**Image prompt**:
```
3D papercraft stop-motion diorama, vertical 9:16, handcrafted cardboard and coloured paper textures, warm cinematic lighting, soft depth of field, cosy. Mascot: a cute cartoon debit card character (navy blue card with gold and light-blue diagonal stripes, gold chip, big googly eyes, smile, white cartoon gloves, thin legs, yellow shoes). Indian setting. Leave the bottom third simple for captions. SCENE: A big papercraft telephone-exchange building in the centre with a sign that says NFS, paper wires and string connecting it to many small colourful cardboard bank buildings around it, glowing paper signals travelling along the wires.
```
**Motion prompt:** Slow pan across the network, glowing signals race along the wires to the centre.

### s06: Card ke pehle kuch digits se pata chalta hai… card kaunse bank ka hai
**Image prompt** *(upload s02.png as the mascot reference)*:
```
3D papercraft stop-motion diorama, vertical 9:16, handcrafted cardboard and coloured paper textures, warm cinematic lighting, soft depth of field, cosy. Mascot: a cute cartoon debit card character (navy blue card with gold and light-blue diagonal stripes, gold chip, big googly eyes, smile, white cartoon gloves, thin legs, yellow shoes). Indian setting. Leave the bottom third simple for captions. SCENE: The mascot holding a big paper magnifying glass over its own card number, the first digits glowing gold, paper office background.
```
**Motion prompt:** Mascot moves the magnifying glass, digits light up, slow push-in.

### s07: Step #3: aapka bank check karta hai: PIN sahi? Balance hai? Limit bachi hai?
**Image prompt** *(upload s02.png as the mascot reference)*:
```
3D papercraft stop-motion diorama, vertical 9:16, handcrafted cardboard and coloured paper textures, warm cinematic lighting, soft depth of field, cosy. Mascot: a cute cartoon debit card character (navy blue card with gold and light-blue diagonal stripes, gold chip, big googly eyes, smile, white cartoon gloves, thin legs, yellow shoes). Indian setting. Leave the bottom third simple for captions. SCENE: Papercraft bank office, a paper banker in a suit at a desk ticking a checklist on a clipboard with three green checkmarks, the mascot watching nervously from the side.
```
**Motion prompt:** Banker ticks the three boxes one after another, gentle pan.

### s08: Sab theek? Account se paisa kata… aur reply gaya: APPROVED!
**Image prompt** *(upload s02.png as the mascot reference)*:
```
3D papercraft stop-motion diorama, vertical 9:16, handcrafted cardboard and coloured paper textures, warm cinematic lighting, soft depth of field, cosy. Mascot: a cute cartoon debit card character (navy blue card with gold and light-blue diagonal stripes, gold chip, big googly eyes, smile, white cartoon gloves, thin legs, yellow shoes). Indian setting. Leave the bottom third simple for captions. SCENE: A paper banker's hand slamming a big red rubber stamp on a paper form that says APPROVED in green, the mascot cheering in the background.
```
**Motion prompt:** Stamp slams down, little paper confetti pops, camera zooms into the APPROVED stamp.

### s09: Step #4: ATM se cash bahar… aur yeh sab kuch seconds mein!
**Image prompt** *(upload s02.png as the mascot reference)*:
```
3D papercraft stop-motion diorama, vertical 9:16, handcrafted cardboard and coloured paper textures, warm cinematic lighting, soft depth of field, cosy. Mascot: a cute cartoon debit card character (navy blue card with gold and light-blue diagonal stripes, gold chip, big googly eyes, smile, white cartoon gloves, thin legs, yellow shoes). Indian setting. Leave the bottom third simple for captions. SCENE: A papercraft ATM dispensing a stack of paper Indian rupee notes, the mascot happily catching the notes with both gloves, warm light.
```
**Motion prompt:** Notes slide out of the slot, mascot catches them and jumps, push-in.

### s10: Par ATM doosre bank ka tha… toh aapka bank usse ₹19 fee deta hai
**Image prompt** *(upload s02.png as the mascot reference)*:
```
3D papercraft stop-motion diorama, vertical 9:16, handcrafted cardboard and coloured paper textures, warm cinematic lighting, soft depth of field, cosy. Mascot: a cute cartoon debit card character (navy blue card with gold and light-blue diagonal stripes, gold chip, big googly eyes, smile, white cartoon gloves, thin legs, yellow shoes). Indian setting. Leave the bottom third simple for captions. SCENE: The mascot carrying a giant shiny gold paper rupee coin from one cardboard bank building on the left to another cardboard bank building on the right, papercraft street.
```
**Motion prompt:** Mascot walks left to right carrying the coin, camera pans with it.

### s11: Isiliye doosre bank ke ATM pe free limit: metro mein 3, baaki shehron mein 5
**Image prompt** *(upload s02.png as the mascot reference)*:
```
3D papercraft stop-motion diorama, vertical 9:16, handcrafted cardboard and coloured paper textures, warm cinematic lighting, soft depth of field, cosy. Mascot: a cute cartoon debit card character (navy blue card with gold and light-blue diagonal stripes, gold chip, big googly eyes, smile, white cartoon gloves, thin legs, yellow shoes). Indian setting. Leave the bottom third simple for captions. SCENE: A papercraft desk calendar with the numbers 3 and 5 circled in red paper, the mascot pointing at it with a glove, paper office desk.
```
**Motion prompt:** Mascot taps the calendar, camera zooms into the calendar page.

### s12: Uske baad har transaction pe ₹23 tak charge + GST
**Image prompt** *(upload s02.png as the mascot reference)*:
```
3D papercraft stop-motion diorama, vertical 9:16, handcrafted cardboard and coloured paper textures, warm cinematic lighting, soft depth of field, cosy. Mascot: a cute cartoon debit card character (navy blue card with gold and light-blue diagonal stripes, gold chip, big googly eyes, smile, white cartoon gloves, thin legs, yellow shoes). Indian setting. Leave the bottom third simple for captions. SCENE: The mascot looking shocked, eyes wide, holding a long paper receipt that curls to the floor, red paper rupee symbols floating around.
```
**Motion prompt:** Receipt unrolls longer and longer, mascot's eyes widen, push-in.

### s13: Paisa kata, cash nahi aaya? 5 din mein wapas… warna bank deta hai ₹100 roz
**Image prompt** *(upload s02.png as the mascot reference)*:
```
3D papercraft stop-motion diorama, vertical 9:16, handcrafted cardboard and coloured paper textures, warm cinematic lighting, soft depth of field, cosy. Mascot: a cute cartoon debit card character (navy blue card with gold and light-blue diagonal stripes, gold chip, big googly eyes, smile, white cartoon gloves, thin legs, yellow shoes). Indian setting. Leave the bottom third simple for captions. SCENE: A papercraft ATM with a red X error on its screen and an empty cash slot, the worried mascot next to it, then a paper banker handing the mascot a paper rupee note with an apologetic smile.
```
**Motion prompt:** Screen blinks red, banker hands over a note, mascot relaxes, slow push-in.

### s14: Ab pata hai ATM ke andar kya chalta hai! Follow karo, agla: UPI kaise kaam karta hai?
**Image prompt** *(upload s02.png as the mascot reference)*:
```
3D papercraft stop-motion diorama, vertical 9:16, handcrafted cardboard and coloured paper textures, warm cinematic lighting, soft depth of field, cosy. Mascot: a cute cartoon debit card character (navy blue card with gold and light-blue diagonal stripes, gold chip, big googly eyes, smile, white cartoon gloves, thin legs, yellow shoes). Indian setting. Leave the bottom third simple for captions. SCENE: The mascot wearing cool black paper sunglasses, one glove adjusting them, confident pose on a wooden papercraft desk with pencils and books.
```
**Motion prompt:** Mascot slides on sunglasses and gives a thumbs up, slow push-in.

## Fact check (India, Nov 2026)

- ATMs talk to banks through switches, mainly NPCI's National Financial Switch (NFS), plus the RuPay, Visa and Mastercard networks.
- The interchange fee your bank pays the ATM's bank is ₹19 per cash withdrawal. It is set by the ATM networks and has applied since 1 May 2025.
- Free transactions at other banks' ATMs: 3 a month in the six metros, 5 elsewhere. After that the customer charge is capped at ₹23 + taxes (from 1 May 2025).
- Failed withdrawal but account debited: the bank must reverse it by T+5 days, or pay ₹100 per day of delay (RBI TAT circular, 2019).
- Sources: [RBI notification](https://website.rbi.org.in/web/rbi/-/notifications/usage-of-automated-teller-machines-cash-recycler-machines-review-of-interchange-fee-and-customer-charges-12111) and [Business Standard](https://www.business-standard.com/finance/news/rbi-allows-banks-to-charge-customers-rs-23-per-atm-transaction-from-may-1-125032801031_1.html)

## Caption for the post

Card ek bank ka, ATM doosre bank ka… phir bhi paisa kaise nikalta hai? 🏧 Save karo aur us dost ko bhejo jo hamesha doosre bank ke ATM use karta hai 😅
#ATM #Banking #NPCI #FinanceIndia #MoneyFacts #Hinglish
