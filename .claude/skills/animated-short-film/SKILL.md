---
name: animated-short-film
description: >-
  Turn one sentence into a painterly cinematic short film: moving paintings,
  character and action stories, chases, rooftop dives and similarly textured
  films. Writes the story, the image prompts for character, location and object
  sheets, and one timestamped master video prompt with a style lock. Use for
  reference-preserving image-to-video prompts, character and environment
  consistency, causal shot planning, sound cues or repairs to this visual style.
  Supports single-frame and separate character/location references. Do not use
  for UI animation, generic video editing or realistic live action.
---

# Animated short film

Make a designed painting move through a readable story. The reference images carry
the visual identity; the motion prompt preserves it. "Painterly" here means rough
painted shapes and cinematic staging, not glossy 3D.

This skill writes prompts. It never generates images or video and it never submits
paid jobs. The user takes every prompt into the image or video tool of their choice,
generates there, and comes back with the result. Everything happens in the chat:
no input folders, no brief files to fill in.

Sections:

1. Start with the idea
2. Inspect and lock the visual world
3. Build the reference pack (plate prompts)
4. Separate identity from place
5. Write a story before the camera list
6. Assemble the master prompt (style locks + skeleton)
7. Hand off the prompts
8. Sound follows the rendered action
9. Review and repair
10. Deliver

---

## 1. Start with the idea

The user runs `/animate` and describes the film in one line. Ask only what blocks
the work, in one short message: duration (default 30 seconds), format (default
16:9 landscape, 1920x1080; vertical 9:16 for social), and whether they already have
reference images or want the skill to write the plate prompts. A quick action beat
usually fits 10-15 seconds. State the choice and continue.

For prompts or a storyboard, produce those. Never add approval gates for routine
decisions. An old chat or sample prompt is not a new instruction.

This is a generative image-to-video recipe. Never substitute a pan or zoom over a
still for actor motion. If the user edits in a timeline tool afterwards, the
generated clips go through that workflow.

The video model needs to accept multiple image references and run the requested
duration. The user picks the model; the master prompt is written tool-agnostic and
gets a settings table (section 7).

---

## 2. Inspect and lock the visual world

Open the actual images before writing prompts. Inspect reference videos at roughly
one-second intervals and in playback when available. Record:

- brush shape and edges, line work, shadow planes, surface finish
- palette, accent color, time of day
- hero silhouette, face, hair, clothing, shoes
- vehicle, signature props (count and attachment point)
- route and final composition

Preserve chunky flat color planes, rough brushstrokes, broken edges, graphic light
and shadow, loose backgrounds, and steam/clouds/spray as painted masses. Bright
colors are valid; do not force "muted palette" wording onto a bright source.
If "cel-shaded" produces clean TV-anime line work, specify rough painted shadow
planes instead.

Use the original plates. Never silently re-render an approved frame in another image
model to "prepare" it for animation; repaints lose the look. A technical resize is
different from a repaint: keep the original, make a separate derivative only if a
tool limit requires it, and inspect it. Check existing crops and baked-in black bars
before deciding output framing; keep them on purpose or crop with a note, and never
add a second layer of bars.

Use visual descriptors rather than depending on an artist's name.

---

## 3. Build the reference pack (plate prompts)

If the user has no plates, write the prompts so they can create matching originals
in their image tool (Midjourney, Nano Banana, GPT Image, Firefly, etc.). Keep one
coherent world rather than picking each asset in isolation. A nighttime alley cannot
silently replace a sunlit road in one continuous journey; a time-of-day change needs
a story transition or a new plate.

Every plate prompt is followed by a settings table (section 7).

**Character sheet**

> One original [role], [age/build], [face/hair], [specific wardrobe], [shoes],
> [one signature prop and attachment]. Full-body front, side and back views of the
> SAME person on a plain pale-grey ground; constant face, proportions, colors and
> accessories. Chunky painterly concept art, rough edges, flat shadow planes,
> visible brushwork. No labels or watermark.

If the image tool has an identity or character-reference control, tell the user to
use the chosen hero image through it.

**Environment plate**

> A single wide 16:9 location plate of [place], with [foreground route], [midground
> obstacle], [recognizable background landmark], [lighting and palette]. Bold
> irregular painted shapes, graphic shadows, loose atmospheric distance. No people.

Keep props/vehicles only when they are intentionally part of the scene. Do not paint
the hero into every plate when using a separate identity-reference workflow.

**Vehicle sheet**

> Same original [vehicle] from useful views, [silhouette/wheels/color], [distinctive
> feature]; no rider. Painted reflection planes and rough marks matching the world.

Verify wheels, controls, seat and luggage before accepting it.

**Example pack that works for an urban chase** (build your own equivalents):

| Plate | Role |
| --- | --- |
| Officer sheet | Identity: three views of one lean officer, blue cap/shirt, cream trousers, black boots, one clipped radio. A turnaround is one person, not three. |
| Courier sheet | Identity + vehicle: short dark-blue hair, oversized orange-red windbreaker, black shorts, white shoes, shoulder bag, blue bicycle. |
| Ramen bar | Opening/ritual: warm saturated interior, red sign, counter, big rough steam strokes. Do not invent legible sign text. |
| Miami strip | Street: pastel art-deco, palms, blue sky, painted wet-road highlights. |
| Highway | Route: curving elevated highway, skyline, big cumulus brush shapes. |
| Drawbridge | Obstacle: raised spans over water, warning lights, white painted clouds. Match approach direction and landing side. |
| Garage | Destination: concrete columns, dark interior, daylight opening. |
| Boardwalk | Coda: timber waterfront, ferris wheel, palms, ocean, graphic cloud streaks. Daylit. |

Inspect file contents rather than trusting names. A file called "character sheet"
may actually be a grid of video screenshots; never use that as an identity input.
Never use a gallery screenshot, grid, Markdown table or contact sheet as a model
reference. Use original individual images with explicit roles.

A trained-looking painterly surface is not proof of identity continuity: check
faces, clothes, wheels, bags and hands separately.

---

## 4. Separate identity from place

Choose the simplest strategy that can tell the story.

**One start frame:** use an already composed character/action image as the actual
first frame. Describe that exact opening, then animate forward from it.

**Separate references:** keep the character sheet, vehicle and clean environment
plates separate and combine them in a model that explicitly supports multiple
references. This avoids redrawing the hero differently in every environment. Use one
coherent environment as the start frame where supported; the hero may enter the
empty shot. A multi-view character sheet is an identity input, never the opening
composition.

Create an ordered manifest: filename, role, visual facts, beat it serves. Use the
same order in the prompt and in the upload. Verify body-relative left/right against
the image; copied prose can disagree with the picture.

Lock the hero in one consistent sentence. For a prop, lock count, attachment, hand
and state: "one radio clipped to the same shoulder; he presses that attached radio"
avoids the model inventing a second hand-held radio. Give hero and pursuer distinct
silhouettes and vehicles. One hero is a default, not a ban on necessary supporting
cast.

---

## 5. Write a story before the camera list

Write one sentence containing **goal, obstacle, response, payoff**. A collection of
stunts is not a story. Use 4-6 story beats for 30 seconds, then subdivide into
motivated shots. Each beat causes the next. Establish the obstacle before overcoming
it, and the destination before arriving there.

| Intent | Timing grammar |
| --- | --- |
| 10s action burst | Already moving at 0.0s; timestamped beats around 1-1.5s; detail inserts are punctuation, about 0.25s, showing a decision (gear change, grip, lever), not an idle detail. |
| 15s continuous stunt | Clear launch, traversal, payoff; one physically coherent moving camera. Keep atmosphere brief unless requested. |
| 30s character story | Meaningful ritual/preparation, trigger, launch, escalating route, decisive action, wide coda. During action vary angles roughly every 1.5-2s. |

A quiet ritual must reveal identity or set up the plot, not justify an idle
five-second hold. An explicit slow opening from the user takes precedence.

For every timed beat write **place, action, camera, continuing state, sound**. Use
strong verbs and a visible consequence. Map screen direction and travel between
places; avoid instant night-day-night changes. Choose either a continuous take or an
edited sequence; never demand an unbroken camera and instant angle changes in the
same prompt.

Vary the whole structure between films. Do not repeat "pass lens, low track, jump,
hand insert, face, charge" with different vehicles. Give each subject its own
problem, camera relationship, climax and ending. A brief slow-motion apex can
emphasize a jump; return to speed for the landing and visibly absorb the impact.

### Structure A: 10s cause-and-effect burst

- 0-1.5s: already at speed as a recognizable obstacle appears.
- 1.5-3s: choose a route.
- 3-4.5s: commitment creates a new danger.
- 4.5-6s: solve it with the character's unique skill.
- 6-8s: climax and physical consequence.
- 8-10s: escape or arrival with a clean final silhouette.

Change this when it becomes predictable across a set.

### Structure B: 15s pier getaway, continuous camera

- 0-2.5s: runner already sprinting, low tracking behind; bag bounces with stride.
- 2.5-5s: widen to reveal distinct pursuers losing ground.
- 5-7.5s: arc alongside as the waiting boat becomes visible.
- 7.5-9.5s: camera descends with the leap; feet land, boat rocks, bag goes down,
  hand takes the wheel.
- 9.5-12.5s: stern view, throttle, nose lifts, wake expands.
- 12.5-15s: rise along the wake; abandoned pier recedes.

Keep the same bag, boat and route. Simplify the hand-off if the model cannot do that
many actions cleanly in the time.

### Structure C: 30s worked example, The Last Ferry

Goal: a courier must reach the ferry before its ramp lifts. The departure bell
triggers the ride; a blocked lane forces a detour; a timed jump resolves it.
References: courier sheet, parcel, quay, waterfront lane, ferry ramp.

| Seconds | Beat and camera | State and sound |
| --- | --- | --- |
| 0-3 | Medium shot: courier tightens the bag strap; camera reveals the ferry beyond the quay. | One sealed parcel in one bag; strap tug, harbor ambience. |
| 3-5 | Departure bell; courier looks to the ramp and pushes off on the bicycle. | Target and countdown established. |
| 5-10 | Hub-height track along the quay; a delivery trolley rolls into the lane. | Same bicycle, forward travel, chain and tires. |
| 10-15 | Wide geography: lane blocked, narrow side passage available; she turns into it. | Motivated route change; bell continues in distance. |
| 15-20 | Side/rear tracking through the passage; short stair drop, knees absorb landing. | Parcel stays secured; no vehicle morph. |
| 20-25 | Ramp starts lifting. Approach, short launch, side-wide apex, landing on deck. | Gap visible before jump; wheel contact and body compression. |
| 25-28 | Brakes, dismounts, hands the SAME parcel to a distinct deckhand. | If two identities break, end with the parcel placed at a marked delivery point. |
| 28-30 | Pull back: small courier and bicycle on the ferry, city receding. | Objective resolved; harbor sound, optional musical button. |

Keep daylight consistent. Use motivated cuts, not an impossible unbroken camera.

### Proven 30s story shapes (urban chase set)

| Shape | Sequence | Lesson |
| --- | --- | --- |
| Cop chase, drawbridge | Ramen ritual ~0-6, motorcycle departure ~6-11, black-car pursuit ~11-21, raised bridge forces a stop ~21-25, officer resolves + wide ~25-30 | Trigger, shared route, physical obstacle that ends the pursuit. Both vehicles establish the chase. |
| Biker bridge jump | Boot/glove prep + face ~0-7, mount and launch ~7-10, street/highway ~10-17, bridge launch/apex/landing ~17-23, garage stop, shades, wide ~23-30 | Preparation introduces character; varied road-level, rear, aerial and side-wide angles serve one journey. |
| Courier ride | Bridge approach + identity ~0-5, ramp leap ~5-10, art-deco street ~10-17, alley/spray ~17-23, boardwalk stop, parcel reveal, wide ~23-30 | A persistent bag/parcel creates an objective beyond riding. Watch lighting across locations. |
| Car chase | Eyes in rearview ~0-2, speeding car, traffic, drift ~2-10, police + tunnel ~10-17, bridge flight + landing ~17-23, crash/escape/drift ~23-30 | Escalate obstacles, keep the apex brief inside a bigger phrase, give the landing weight. Painted cars drift toward smooth CGI; guard against it. |
| Rooftop dive (15s) | Launch from water tower, vertical fall through a skyscraper canyon, crouched street landing, rise | Specify the landing plane, not just "jump". |

---

## 6. Assemble the master prompt

Order: **opening style lock, reference roles, hero/prop/world locks, exact opening,
timestamped causal beats, physics/continuity, audio choice, closing style lock.**
Use the source's visible properties, not every adjective below. Timing is a request
to a generative model, not an edit guarantee; the user validates the rendered result.

### Opening style lock

> CRITICAL STYLE LOCK: animate the supplied image's painted visual language
> throughout. A moving 2D digital painting: broad irregular color planes, visible
> rough brush marks, ragged painted edges, simplified shadow shapes, loose background
> detail. Skin and fabric retain painted texture; clouds, smoke and spray remain bold
> brush shapes. Preserve the reference palette and lighting. Never convert it to
> photorealism, glossy CGI, smooth plastic surfaces or clean vector/anime outlines.
> Do not restyle.

### Closing style lock

> From first frame to last, the same painted world, character design and rough edges
> remain visible. No new captions or watermarks. No shift to realism or glossy 3D.

Add-ons:

- Vehicles: "Metal is described by a few painted reflection shapes, not a
  mirror-polished automotive render. Road and water highlights remain broad strokes."
- Wide/medium shots: call out painted texture on clothes and faces.
- If a close-up loses the look, widen it or supply a matching close-up plate instead
  of piling on negatives.
- "No text" means no unwanted overlays. Do not demand removal of signs, emblems or
  intentional source design unless asked.
- The lock is prompt text. Never invent a parameter like `style_lock`.

### Full prompt skeleton

```text
[OPENING STYLE LOCK adapted to source]
Reference 1: [identity, or starting composition; say which].
Reference 2: [location/vehicle role].
Reference 3: [next location role].
Exact first frame: [describe the real start image; who is present or enters].
Hero: [one fixed identity sentence]. Props: [counts, locations, state].
World: [palette, time, geography]. Story goal: [goal and obstacle].
Editing: [continuous take OR motivated cuts, with direction maintained].
0.0-[t]s: [place, action, camera, consequence, sound].
[t]-[t]s: [caused by preceding action; continuing identity and object state].
...
[last interval]: [visible payoff, then final composition].
Continuity: [hero count; distinct pursuers if any; prop persistence; route].
Motion: [forward travel, credible contact, weight, launch and landing].
Audio: [native diegetic / silent for custom mix / other requested treatment].
[CLOSING STYLE LOCK]
```

Keep image numbering aligned with the order the user uploads the references. If the
video model uses named reference roles, tell the user how to map the numbers.

Keep mechanics legible even when stylized: tires grip before sliding, a launch has
an approach, a jump has a matching landing, debris stays where it fell. A vertical
rooftop dive ends at street level. Resolve the narrative instead of ending
mid-stunt.

---

## 7. Hand off the prompts

The skill does not generate. Every prompt the user has to run elsewhere is handed
over as a copy-ready code block followed by a settings table:

| Setting | Value |
| --- | --- |
| Model | [image model of choice, e.g. Nano Banana / GPT Image / Midjourney] or [video model of choice that accepts multiple references, e.g. Seedance / Kling] |
| Type | image / image-to-video |
| Aspect | 16:9 or 9:16 as decided in section 1 |
| Duration | for video prompts, the requested length |
| References | ordered list of files to attach, same order as in the prompt |

Deliver the plate prompts first (character, environment, vehicle/object, in the
order of the manifest), wait for the user to generate and come back with the images,
inspect them (section 2), then deliver the master prompt. Do not deliver the master
prompt before the plates exist; it has to describe the real images.

Tell the user to run one representative test before scaling into a batch, and to
reuse completed generations after interruptions rather than regenerating.

Keep the user's files where they are. If no structure exists and the user wants
one, suggest `references/`, `prompts/`, `renders/`, `final/`. Never overwrite an
accepted master.

---

## 8. Sound follows the rendered action

Choose one: native diegetic audio from the video model, custom sound, or diegetic
audio plus music.

- Native sound gives coherent ambience and events. Keep a copy of any native mix.
- For precise custom effects, generate a clean silent picture when possible, or use
  separately controllable stems.
- Never stack a second score over baked-in music without a deliberate mix.

After picture review, build a cue list from **actual** event times, not the planned
timestamps. Layer in this order: continuous engine / bicycle chain / wind, setting
ambience, discrete contact and handling (footsteps, grips, latches), major impacts,
then restrained transitions. Keep effects motivated rather than hitting every cut. A
jump can thin the bed at the apex and restore weight on landing. Repeated whooshes
do not replace engine pitch and tire contact. Keep perspective changes audible
(tunnel reflections, distant sirens).

Music is optional for this look. When a music version is requested, use the user's
licensed track or an authorized generated instrumental.

---

## 9. Review and repair

Ask the user for the rendered clip or frames from it, then inspect transitions and
sound. Sampling does not prove motion or audio quality: a one-frame flash, morph,
bad cut, reversal or audio error can sit between samples. Watch the whole clip when
possible and say what was not reviewed.

| Check | What to look for | First repair |
| --- | --- | --- |
| Look | Plastic metal, smooth skin, clean outlines replacing brush edges | Wider framing, matched plates, texture lock, fewer conflicting references |
| Identity | Face, wardrobe, bike, bag or emblem changes | One chosen identity, stable full description, fewer competing faces |
| Prop logic | Duplicated radio, changing shoulder, bag vanishes | Exact count, attachment, hand and state matching the image |
| Story | Stunts without a goal; pursuer disappears | Show goal/obstacle, shared geography, causal beats |
| Space/time | Random locations, night/day jumps, wrong landing surface | Explicit route and matched lighting; repair the transition |
| Motion | Backward travel, wheel slip, floating body, weightless landing | Clear travel vector and contact mechanics; simplify action |
| Pace | Empty opener, long frozen insert, every film the same pattern | Timestamp the action; redesign the structure |
| Ending | Abrupt cutoff or unresolved objective | Reserve time for payoff and a final wide composition |

Repair the cause, not the symptom: simplify staging, fix prop wording, widen
framing, reduce competing references, or regenerate that shot. Adding more style
adjectives or "cinematic" does not fix missing causality.

Known failures and fixes:

- "Open on a detail, then pull out" wasted half of a 10-second film. Fix: "already
  at full speed at 0.0s" and timestamp the opening action.
- A radio stayed clipped on while a second one appeared in a hand. Fix: "presses the
  existing clipped radio" and confirm which shoulder the plate uses.
- An unnamed rooftop "jump" became horizontal parkour. Fix: state vertical free fall,
  floors passing upward, street as the landing plane.
- A pursuer's face cloned the hero. Fix: separate identity references, distinct
  silhouettes, simpler framing, or an unseen driver.
- Fast cuts still felt random. Fix: rebuild cause and effect and show both parties
  in shared pursuit geography.
- Prose said "continuous" while listing many instant views. Fix: pick continuous
  take or motivated editing.
- Close-ups went smooth. Fix: widen, or supply a matching painterly close-up plate.

Reject identity changes, duplicates, backward travel, teleports, impossible landing
geography, disappearing objectives, drifting brushwork, an unmotivated empty opening
and an unresolved ending. Inherit a reference's successful visual/story grammar
without copying its defects.

---

## 10. Deliver

Keep the high-quality master the video tool exported; a larger bitrate cannot
restore lost painted detail. Avoid re-encoding when only replacing audio. Never call
an upscaled 720p generation native 1080p.

Deliver in chat: the story (one sentence plus the beat table), the plate prompts
with their settings tables, the reference map, the master prompt with its settings
table, the timed beat/sound cues, and a short QA note listing only checks actually
performed. Prompt-only requests stop at the prompt package.
