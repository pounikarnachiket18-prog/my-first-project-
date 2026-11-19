# Card mascot clip library

These are the AI animations of the card mascot (4 s each, 720×1280, 24 fps) from the credit card reel.
Reuse them in any reel through a shot's `"media"` list in `shots.json`, for example:

```json
"media": [{"clip": "library/card-mascot/atm-cash-out.mp4", "in": 0.7, "out": 3.2, "speed": 0.6}, {"image": "s08"}]
```

`speed` < 1 gives smooth slow-mo (motion interpolated). Each clip morphs between scenes, so pick `in`/`out` for the part you need.

| File | What happens (seconds) | Used in the ATM reel for |
|---|---|---|
| `atm-cash-out.mp4` | 0–0.7 mascot at a papercraft ATM · 0.7–3.2 cash comes out, mascot happy · 3.5 fades to black | Step 4: cash out |
| `boardroom-poster.mp4` | 0.5 mascot close-up · 1.0–3.3 bankers in a boardroom study the mascot poster | Step 3: bank checks |
| `coin-split-bank-tower.mp4` | 0–0.6 coin splits · 0.9–3.2 coin flies between BANK, kirana and card-network tower · 3.5 coin close-up | ₹19 fee between banks |
| `coins-vault-bank.mp4` | 0–0.6 coin close-up · 1.0–2.5 mascot on a pile of coins, bank behind · 3.0 vault door shuts | — |
| `kids-confetti-celebrate.mp4` | 0–0.7 kraft paper · 1.0 two kids at a desk, worried · 1.8–3.9 mascot pops up, confetti | Outro |
| `night-city-bank-banker-stamp.mp4` | 0–1.9 night city, push into the BANK façade · 2.0–2.9 banker stamping at a desk · 3.0–3.9 mascot photo / mascot on desk | Hook; APPROVED stamp |
| `paper-plane-globe-bank.mp4` | 0–0.6 crumpled paper · 0.9–3.4 mascot rides a paper plane over a globe to a BANK | Request routed to your bank |
| `pos-keypad-kirana-coins.mp4` | 0.3–1.6 glove pressing a keypad, mascot at a POS machine · 1.8–3.9 kirana shopkeeper, coins | Step 1: PIN entry |
| `receipt-coins-crumple.mp4` | 0.4–2.9 mascot with a long receipt, coins fly, toy-town street · 3.4 receipt crumples into a ball | ₹23 charges |
| `shopkeeper-parcel.mp4` | 0.5 mascot close-up · 1.2–2.9 a man hands the mascot a parcel, BANK behind | ₹100/day compensation |
| `vault-desk-calendar-envelope.mp4` | 0–0.6 red vault opens · 0.6–1.9 mascot at a desk flipping a calendar · 1.9–3.7 envelope drops over its face | Free limit; encrypted PIN |
| `wallet-desk-checkmarks.mp4` | 0.5–3.0 mascot by a big wallet, ticks appear over items · 3.4 wallet close-up | (good end card) |
| `phone-shield-sofa.mp4` | mascot on a sofa, phone with a shield (security / fraud alerts) | — |
| `phone-stars-night.mp4` | mascot next to a glowing phone, stars and an hourglass (rewards / time) | — |
| `vault-shopping-street.mp4` | vault door opens onto a shopping street, shopping bags | — |
| `vault-shopping-walk.mp4` | mascot walks down a street carrying shopping bags | — |
