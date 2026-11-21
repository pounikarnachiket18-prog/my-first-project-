# How did the CJP protest turn violent? (20-second explainer reel)

A 1080×1920, 30 fps news-explainer reel about the Cockroach Janta Party's "Sansad Chalo" march in Delhi on 20 July 2026.
It was planned with the **shot-director** skill (`.claude/skills/shot-director`) and built with the Reels Studio toolkit (HTML + GSAP, rendered with Playwright).

```bash
cd reels
node tools/render.mjs projects/cjp-protest --preview   # contact sheet -> output/cjp-protest-contact.jpg
node tools/render.mjs projects/cjp-protest             # final -> output/cjp-protest.mp4
```

All visuals are illustrated (silhouettes, an SVG street scene and a generic colonnaded Parliament building), so there is no news footage or real person's photo to license. The street scene is built in **8 depth layers**, and a virtual camera moves through them, so near layers slide faster than far ones (real parallax, not a zoom on a flat picture).

## Brief and clocks

- **Story in one sentence:** a satirical online party, born from a "cockroach" remark, led a youth march on Parliament over alleged NEET leaks. The march hit police barricades, the clash injured about 180 people, and each side blames the other.
- **Feeling to leave with:** sober and unresolved. Tension rises, then lands on an open question, without taking a side.
- **Clocks:** *story time* runs two months (16 May → 20 July), then one afternoon. *Screen time* is 20 s. *Rhythm* is locked to a 120 BPM grid (1 beat = 0.5 s, 1 bar = 2 s). All cuts land on beats, the shots get shorter toward the clash, and the answer lands on the downbeat at 18.0 s.
- **Ratio:** 9:16. The camera mostly moves vertically (pedestal) and in depth (push/pull). Text stays between y = 200 and 1300, clear of the Instagram UI.
- **Geography:** the crowd stands on the left and marches toward screen-right; police, barricades and Parliament are on the right. That direction holds in every street shot, and the lathi charge is the only push back to the left.
- **Held moment:** shot 5, a static frame at the barricades with only a heartbeat underneath, just before the clash.
- **Fairness rule:** every contested claim carries its source on screen (POLICE SAY / CJP SAYS / REPORTED).

## Shot list

| # | In | Beat / purpose | Size · angle · lens | Subject action | Move (type, direction, speed) | Start → end frame | Holds | Sound / cut cue | Dur |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0 | Hook: the question, with the CJP's cockroach placard as the poster frame | Close-up, low angle, wide lens | A placard with the cockroach emblem raised over the crowd | Slow push in | Placard and title fill frame → slightly tighter on the placard | Title fully visible on frame 0 (cover) | Hit at 0.0, cut on bar 1 (2.0) | 2.0 |
| 2 | 2.0 | Origin: the CJI's "cockroach" remark → satire party launched online (16 May) | Medium, eye level, graphic | Profile card slides up; SATIRE stamp lands | Static (information shot) | Card enters → stamp lands | Card centred | Stamp hit at 3.4, cut at 4.5 | 2.5 |
| 3 | 4.5 | The anger: alleged NEET paper leaks → demand for the minister's resignation | Close-up on the exam sheet | LEAK? stamp lands on the paper | Tilt up, slow, paper → demand text | Exam paper → headline above it | Paper flat, no zoom | Stamp at 4.85, cut at 6.5 | 2.0 |
| 4 | 6.5 | Geography: 20 July, the march heads for Parliament; police have banned it | Extreme wide, high, then street level | Crowd advances toward screen-right | Pedestal down (crane), slow in → settle | Sky and Parliament → crowd, barricades and Parliament all in frame | Parliament as the scale reference; crowd heading right | Long whoosh, cut at 9.0 | 2.5 |
| 5 | 9.0 | **Held moment**: the two sides face each other | Wide, eye level | Crowd and police line still; police beacons pulse softly | Static, locked off | – | Both sides in frame, line held | Heartbeat + riser, cut at 10.5 | 1.5 |
| 6 | 10.5 | Police version: crowd tries to breach the barricades, stones thrown | Medium on the barricade | Stones arc from crowd to shields | Restrained handheld | Barricade centred | Crowd left, police right | Hits on stone impacts, cut at 11.5 | 1.0 |
| 7 | 11.5 | Tear gas and lathi charge (widely reported) | Medium | Canisters arc into the crowd, smoke blooms, police line pushes left | Truck left, following the canister arc | Barricade → smoke in the crowd | Handheld stays light | Thuds on landing, cut at 12.5 | 1.0 |
| 8 | 12.5 | CJP version: founder calls the police response "really cruel and evil" | Medium → close-up | Smoke thickens | Slow push into the smoke | Crowd in smoke → mostly smoke | No zoom, only parallax | Hit at 12.5, cut at 14.0 | 1.5 |
| 9 | 14.0 | The toll, with the source of each number | Close → wide | Smoke drifts; stats count up | Pull out, steady | Smoke → whole street, Parliament behind | Parliament keeps scale | Counter ticks, cut at 17.0 | 3.0 |
| 10 | 17.0 | Open question: each side blames the other; FIR registered, marches paused | Wide, high | Smoke thins | Static | – | Hold until the end | Low boom at 17.0, hit on 18.0 downbeat, tail rings out | 3.0 |

## Facts on screen and where they come from

| Claim | Source |
|---|---|
| Launched online on 16 May 2026 by Abhijeet Dipke as political satire; the name refers to remarks by the CJI and parodies the BJP | [Wikipedia](https://en.wikipedia.org/wiki/Cockroach_Janta_Party), [NPR](https://www.npr.org/2026/07/20/nx-s1-5889515/india-gen-z-cockroach-party-protests) |
| The CJI's remark compared jobless youth to "cockroaches"; he later said he meant people with fake degrees | [Gulf News](https://gulfnews.com/world/asia/india/inside-indias-gen-z-led-cjp-movement-why-did-cockroach-janta-party-protests-turn-violent-in-delhi-1.500614923) |
| Anger over alleged NEET paper leaks; demand for Education Minister Dharmendra Pradhan's resignation | [NPR](https://www.npr.org/2026/07/20/nx-s1-5889515/india-gen-z-cockroach-party-protests), [CNN](https://www.cnn.com/2026/07/22/india/india-cockroach-party-protest-anger-intl-hnk) |
| Police imposed prohibitory orders and declared the march unlawful; about 20,000 marched (one outlet's estimate) | [CNN](https://www.cnn.com/2026/07/22/india/india-cockroach-party-protest-anger-intl-hnk), [TIME](https://time.com/article/2026/07/22/india-cockroach-janta-party-protest-movement/) |
| Police say protesters tried to breach barricades and pelted stones; police used tear gas and baton charges | [Deccan Chronicle](https://www.deccanchronicle.com/nation/crime/cjps-chalo-sansad-march-turns-violent-prompting-police-action-1972600), [The Bridge Chronicle](https://www.thebridgechronicle.com/news/nation/cjp-sansad-chalo-march-delhi-police-tear-gas-lathi-charge-mp99), [Al Jazeera](https://www.aljazeera.com/news/2026/7/21/indias-cockroach-protest-movement-halts-marches-after-police-violence) |
| Dipke called the police response "really cruel and evil" | [Al Jazeera](https://www.aljazeera.com/news/2026/7/21/indias-cockroach-protest-movement-halts-marches-after-police-violence) |
| Police: 118 personnel and 60 protesters injured, 70 detained. CJP: about 150 protesters hospitalised | [ETV Bharat](https://www.etvbharat.com/en/bharat/118-police-personnel-injured-in-violent-protests-by-cjp-in-delhi-dipke-claims-police-brutalised-peaceful-students-enn26072100560), [CNN](https://www.cnn.com/2026/07/22/india/india-cockroach-party-protest-anger-intl-hnk) |
| Delhi Police Crime Branch registered an FIR | [Business Standard](https://www.business-standard.com/amp/india-news/police-register-fir-to-probe-violence-during-cjp-s-july-20-protest-126100801060_1.html) |
| The movement paused its Delhi marches but vowed to keep protesting | [Al Jazeera](https://www.aljazeera.com/news/2026/7/21/indias-cockroach-protest-movement-halts-marches-after-police-violence), [NPR](https://www.npr.org/2026/07/21/g-s1-134722/indias-youth-led-cockroach-movement-vows-to-continue-protest-after-police-crackdown) |

Reports disagree on some numbers. One outlet counted "more than 50" police and protesters injured and "over 100" detained, so the reel uses the official police figures and labels them as such. Check the latest reporting before posting.
