# Clipping knowledge base

Everything we have learned about turning long-form video into viral short clips. **This is a living document: read it before every clipping job, and update it after every job** (see "How to update" at the bottom).

- Full sourced report: [Full_Research_Report.md](Full_Research_Report.md)
- Raw research notes (one file per topic): [research_notes/](research_notes/)
- Evidence tags used below: **[P]** platform or first-party, **[A]** academic, **[J]** independent journalism, **[I]** insider (e.g. ex-MrBeast staff), **[V]** tool vendor (no controlled tests, treat as a starting default), **[O]** our own observation from a job.

---

## Changelog

| Date | What changed |
|---|---|
| 2026-11-19 | Copyright strategy: rights gate. `clip.py new --rights` stores campaign/permission/open/unlicensed in `source.json`; `kit.py` warns on unlicensed and adds a claim/block playbook to every kit; RUBRIC: Rights; research in `research_notes/copyright_and_content_id.md`. |
| 2026-11-18 | Job 10: "I Built A City To Save Kids From Illegal Labor" (`v9QtM6qnG50`, 19 min), 5 clips (Isaac's dream home, kid-designed playground, field → city, 325-kid school, clean water) + 10 v2 thumbnails (stack, callout, vs, cinema, bignum) + kits with 13 hashtags each. `clip.py frames` sheet now works with an odd number of frames. Repo pushed to GitHub. |
| 2026-11-18 | Hashtags 12–15 per post: YouTube (max 15), TikTok and Facebook (own caption in Create reel → *Customize for each platform*); Instagram stays at 5 (platform cap since Dec 2025); X 2, Snapchat 2. `kit.py` merges and checks the counts. Job 09 kit regenerated. |
| 2026-11-18 | `export.py` loudness guard: prints LUFS/dBTP per clip, auto-limits true peak > −1 dBTP (oversampled limiter, video copied), warns when loudness is outside −16 to −13.5. |
| 2026-11-18 | Job 9: "Beat Professional Athlete, Win $100,000" (`_c2e1NcI3Sc`, 22 min), 5 clips (Haaland, Alyssa Liu, Gordon Ramsay, Simone Biles, LeBron) + 10 v2 thumbnails (callout, stack, vs, cinema, bignum) + kits. Checked for duplicates first (no earlier job). |
| 2026-11-18 | Job 8: "Eat Everything In A Grocery Store, Win $1,000,000" (`plN7JMbadRg`, 58 min), 5 clips + 10 v2 thumbnails (sticker, callout, reveal, cinema, bignum) + kits. |
| 2026-11-18 | Job 7: "Lose 100 LBs, Win $250,000!" (`pe_ejTiIcSs`, 37 min), 5 clips + 10 v2 thumbnails (bignum, callout, sticker, cinema, stack) + kits. `thumbs.json` now accepts `ath` (ring spot for 16:9). |
| 2026-11-17 | **Thumbnails v2 + titles:** `thumbs.py` now has 7 styles (sticker, bignum, vs, callout, reveal, cinema, stack) with AI subject cut-outs (`cutout.py`, rembg u2net_human_seg/isnet). There is a style picker and title formulas in RUBRIC, and a title checker in `kit.py`. Job 06 thumbnails and titles were redone. Old generator: `thumbs_v1.py`. |
| 2026-11-17 | Job 6: "Beast Games S2E2" (`djNKtbONGGg`, 55 min), 5 clips + 10 thumbs + kits. Fixed `clip.py` for titles containing "\|" and the thumbnail sheet grid. |
| 2026-11-17 | Job 5 (first with v2): "I Survived The Most Extreme Places On Earth" (`gTKS8SAwUzE`), 5 clips + 10 thumbs + kits for 6 platforms. Added a per-segment `"wide"` layout and a per-clip `cta_y`. |
| 2026-11-17 | **Upgrade v2:** research on OpusClip/competitors, open-source clippers, multi-platform publishing and monetization (`reports/Clipping strategy upgrade.md`). New one-command pipeline `clip.py` (new/sheet/build/render/frames/thumbs/kit), `candidates.py` hype ranker, `RUBRIC.md`, GPU Whisper `asr.py`, per-shot face reframe `reframe.py`, pause `tighten`, `kit.py` (YT/IG-FB/TikTok-X-Snap + schedule.csv), `export.py` platform guard. Env `~/.clipping/env`. |
| 2026-11-17 | Job 4: 5 clips + 10 thumbnails + YT/IG kits from "Lose 150 Lbs Together, Win $250,000" (`RE3_PGwDwhw`, 43 min). Sponsor segment cut. |
| 2026-11-17 | Added YouTube tags tables and `INSTAGRAM_CAPTIONS.md` (hook first line, 5 hashtags, send/save prompt, alt text) for all 3 videos; rules in `CLAUDE.md`. |
| 2026-11-17 | Job 3: 5 clips + 10 thumbnails from "$1 vs $500,000 Experiences!" (`Xj0Jtjg3lHQ`). Counters now keep units ("900 FT"); `thumbs.py` always refreshes image copies. |
| 2026-11-17 | Job 2: 5 clips + thumbnails (9:16 Shorts cover + 16:9) from MrBeast "$1 vs $1,000,000,000 Nuclear Bunker!" (`_AbFXuGDRTs`). Folders are now per video (`01_Futuristic_Tech`, `02_Nuclear_Bunker`). The scripts read a per-video **recipe** (`5_TOOLS_AND_SCRIPTS/recipes/<nn_name>/`: `edits.json`, `words.json`, `spec.json`, `thumbs.json`) via the `CLIP_RECIPE` env var. Added `thumbs.py`. |
| 2026-11-17 | Folder reorganized into `Documents/clipping` (1_READY_TO_POST … 5_TOOLS_AND_SCRIPTS); YouTube posting captions added in `1_READY_TO_POST/YOUTUBE_CAPTIONS.md`. |
| 2026-11-17 | v1: initial deep research (4 tracks: editing techniques, virality psychology, platform algorithms, clipping industry). First job: 5 clips from MrBeast "$1 vs $1,000,000,000 Futuristic Tech!" (`pAnGwRiQ4-4`), v1 plain cuts and then v2 with motion graphics. |

---

## 1. The core idea

> Pro clippers don't **shorten** a video. They **rebuild** each clip around its payoff.

1. **Open on the payoff** (the result, the reaction face, the stakes) and then rewind to the setup. [V][I]
2. **New information every 10–15 s.** What holds viewers is the speed of new information, not how fast you cut (Mario Joos, former MrBeast retention strategist). [I]
3. **A visual event every 2–4 s** (cut, punch-in, graphic). Sources disagree on the exact rate (2–7 s). [V]
4. **Hard cut within about 1 s of the final reaction.** No wind-down and no outro. [V][I]
5. **Visible re-narration is required.** Lightly edited reposts are now demoted or demonetized on all three platforms (§6). [P]

## 2. Hooks (first 1–3 seconds)

- TikTok: over 63% of its highest-CTR **ads** state the key message in the first 3 s. That is a share of top performers, not a lift figure. [P]
- YouTube Shorts metric that matters: **viewed vs. swiped away** (no official benchmark). [P]
- 84.6% of hooks from million-view videos are **statements, not questions**, and almost none repeat, so copy the *mechanism*, not the line. [V]
- Mechanisms that work for MrBeast-type footage:
  - a **stakes frame plus a 3–6 word overlay** stating the stakes or the number ("$1,000,000 RACE: FLYING CAR vs NORMAL CAR")
  - a **flash-forward** of the payoff, then a rewind tag ("⏪ 5 MINUTES EARLIER")
  - a question only when it invites a guess ("Which one was grown in a lab?")
- Curiosity research (Loewenstein's information-gap model): curiosity peaks at a **specific** gap that promises closure. Vague ("you won't believe this") and obvious gaps both underperform. [A]
- The hook must promise only what the footage delivers (MrBeast handbook "packaging match" rule; it is also a platform rule). [I][P]

## 3. Structure template (30–60 s clip)

| Time | Beat |
|---|---|
| 0–2 s | Payoff flash or stakes frame + 3–6 word overlay (opens loop A) |
| 2–8 s | One sentence of context or rules (overlay if possible) |
| 8–15 s | Escalation or a raised stake (opens loop B) |
| 40–60% of runtime | Re-hook: a reversal, failure or "but then…" |
| Last 15–20% | Payoff, kept short (closes loop A) |
| ≤1 s after the reaction | Hard cut, which feeds the loop |

Length by moment type: reveals 20–35 s · challenges 30–50 s · reactions and comedy 15–30 s · giving or philanthropy 30–60 s. [V]

## 4. Visual layer: house style (what our pipeline uses)

| Element | Spec we use | Basis |
|---|---|---|
| Canvas | 1080×1920, 30 fps, H.264/AAC | [P][V] |
| Footage framing | 8:9 center crop of 16:9 source (960×1080 → 1080×1215) at y=300, blurred and darkened fill behind | [O]. The research default is a face-tracked full 9:16 crop; we haven't built face tracking yet (see backlog) |
| Punch-ins | Hard alternate 100% ↔ 112% on every jump cut; eased +9% push (0.28 s, power3.out) on emphasis beats; 0.3 s shake on impacts | [V]: 110–115% hard, +8–12% eased |
| Hook header | 2 lines, Montserrat 900, white with 13 px black stroke, one yellow keyword. Large during the cold open, then shrinks to a compact header for the rest | [V][O] |
| Rewind tag | Red pill "⏪ X MINUTES EARLIER" plus a white flash at the cold-open cut, with a record-scratch SFX | [O] |
| Captions | 1–3 words per group, Montserrat 900 at 78 px, white with 13 px black stroke, active word yellow `#FFE500` at 1.1× scale, top at y≈1150, 16 px gaps between words | [V]: 70–90 px, Hormozi yellow `#F7C204` |
| Stickers | White card with black border, ±3–4° tilt, back-out pop. Used for context ("🐔 FARM CHICKEN") | [V]: "show the thing when you mention it" |
| Stamps | Big yellow stroked slam text for payoffs ("❌ WRONG", "COOKED 💀") | [O] |
| Counters | Count-up box for money and numbers ($25,000, $1,000,000, 2,000°F) | [V]: count-up whenever money is said |
| Emoji pops | 190 px, sparse, only on emotional words | [V]. 2026 trend: "Dynamic Minimalism", so don't overuse |
| Progress bar | 12 px yellow bar under the footage panel | No evidence it helps [V]. Keep or drop as a test |
| End prompt | Yellow card in the last ~2.5 s with a **debate** question ("WOULD YOU EAT LAB-GROWN CHICKEN? 👇") or a send prompt | [P]: no "comment YES" bait |

**Safe zones (1080×1920):**
- Nothing important above y≈170 (status and search bar), or above ≈270 to be conservative.
- All text inside y 170–1330.
- Keep text out of the right ≈120–150 px (button rail).
- Below y 1330, decoration only.
- Meta ads rule: 14% top, 35% bottom, 6% on each side. [P][V]

## 5. Sound

- Original audio carries the clip. If you add music, duck it 6–12 dB under speech (30–80 ms attack, 250–700 ms release). [V]
- SFX follow motion:
  - whoosh on transitions (every other cut, not all)
  - pop on text or stickers
  - impact or bass hit on stamps and payoffs
  - one riser into a hit at the biggest reveal
  - cash register on money counters
  - record scratch on the rewind
  - boing on comedic beats [V][O]
- Rotate samples; never put SFX over key words; don't stack them. [V]
- Master: **-14 to -15 LUFS integrated, -1 to -1.5 dBTP** (we normalize the plate to -15 LUFS / -1.5 dBTP before adding SFX). [P for YouTube, V for others]
- Our SFX library (from Openverse/Freesound, via `npx hyperframes media-use resolve --type sfx`):
  - sfx_001 impact, CC0
  - sfx_002 pop, CC0
  - sfx_004 bass impact, CC0
  - sfx_006 whoosh, CC0
  - sfx_007 cash register, **CC BY: credit "Cash Register" by GowlerMusic (freesound.org/s/360453)**
  - sfx_008 record scratch, CC0
  - sfx_009 boing, CC0
  - sfx_010 camera shutter, CC0
  - Rejected: sfx_003 (sounds like an inhale, not a riser) and sfx_005 (clap, not a ding). **We still need a real riser and a ding.**

## 6. Platforms: signals, lengths, originality

**Ranking signals**
- **Instagram Reels:** watch time, likes per reach and **sends per reach** (Mosseri, early 2025). Sends weigh slightly more for non-follower reach. [P]
- **YouTube Shorts:** since 2025-03-31 every start or replay counts as a public view. Engaged views still drive monetization and the Partner Program, so judge on engaged views and viewed-vs-swiped. [P]
- **TikTok:** no published weights. Third parties rank completion and watch time first, then shares, then rewatches, saves and comments. [V]

**Lengths**
- **YouTube Shorts:** up to 3 min, **but any Short over 60 s with a Content ID claim is blocked worldwide**. Keep clips of other creators' footage ≤60 s. [P]
- **Instagram Reels:** 90–179 s gained +7.4% reach vs baseline; under 90 s was about baseline; **≥3 min lost 49.3%** (Buffer, 2.73M Reels, Nov 2026). Only Reels ≤3 min are recommended to non-followers. [V, large dataset]
- **TikTok:** Creator Rewards needs ≥60 s; otherwise length follows the payoff. [V]

**Originality and reposts**
- **Instagram:** reposts are replaced by the original. Accounts with 10+ unoriginal reposts in 30 days lose recommendations. Covers all formats since 2026-04-30. Voiceovers, reactions and material edits are exempt. [P/J]
- **TikTok:** unoriginal content without "new, creative edits" is ineligible for For You (around 2025-09-13). [P/J]
- **YouTube:** the reused-content policy is channel-level. **Permission from the creator does NOT exempt you.** Added storyline, commentary and substantial A/V edits are OK. [P]
- No platform defines "substantial". Safest: restructure, overlays, graphics, and ideally voiceover or commentary. [O]

**Engagement bait**
- TikTok removes from For You anything that tries to "trick or manipulate" engagement. Meta demotes "comment YES" bait. [P]
- Use real debate prompts instead.

## 7. Psychology of sharing

- High-arousal emotions (**awe**, anger, anxiety, amusement) drive sharing; sadness suppresses it (Berger & Milkman, ~7,000 NYT articles; text-based, 2012). [A]
- MrBeast mapping:
  - scale, money and danger produce awe
  - giving produces uplift, so cut the sad build-up short and lead with the joy
  - taste tests and bets produce amusement plus debate
  - stunts produce suspense
- **Social currency → sends:** "send this to the friend who…". **Practical value → saves:** rankings, "which is worth it". [A][V]
- **Loops:** sentence loop (the last line completes the first), visual match (end frame = frame 1), or reveal-then-rewind. Loop lift figures are anecdotal. [V]

## 8. The clipping business

- **Whop Content Rewards:** median ≈ **$1.09 per 1K views** (mode $1.00), median cap $200 per clip; tech and health campaigns ≈ $2 per 1K (707 campaigns, Nov 2026). [V, marketplace data]
- **MrBeast:** pays personal clippers **$50 per 100K views**. His program **Vyro** launched Oct 2025, ~$3 per 1K reported. [J]
- **Clipping (agency):** $300–1,500 per 1M views, 23,300 clippers. **N3on:** $1.4M to 303 clippers in 5 weeks. [J]
- **Workflow:** score 5–15 candidate moments per source, post the best 3–5, make a distinct variant per account, spend under ~15 min per clip, post 3–5 a day. It's "like fishing". [V][J]
- **Common rejections:** missed brief details, missing ad disclosure, reusing an edit across campaigns, submitting >30 min after posting, botted views. [P marketplace rules]
- **Copyright (2026-11-19):** no edit makes another creator's footage safe from Content ID; only a license (campaign for that exact video, or written permission) stops claims/blocks. Claims aren't strikes; disputes need a license or real fair use. See `research_notes/copyright_and_content_id.md`. [P]
- **Rights:** official programs grant a narrow, revocable license. Unofficial clipping relies on weak fair use and risks Content ID claims, strikes and demotion. [J][P]

## 9. Our pipeline (how we actually do it)

1. `python -m yt_dlp` downloads captions (`--write-auto-subs --sub-format json3`, use `en-orig`) and the 1080p video (`--js-runtimes node`). Word-level timings come from the json3 captions.
2. Read the full transcript. Pick moments with **one clear payoff and one high-arousal emotion**.
3. Write an **edit list** of source in/out ranges, with the cold-open teaser first and filler lines removed (see `5_TOOLS_AND_SCRIPTS/scripts/edits.json`).
4. `5_TOOLS_AND_SCRIPTS/scripts/plate.py`: ffmpeg cuts each segment, builds the 9:16 plate (blur fill + 8:9 panel), concatenates, normalizes loudness, and remaps word timings into the edited timeline (`edit.json`).
5. `5_TOOLS_AND_SCRIPTS/scripts/gen.py`: generates a HyperFrames `index.html` per clip with punch-ins, hook header, rewind, captions, stickers, stamps, counters, SFX, progress bar and end prompt, driven by a per-clip beat list.
6. `npx hyperframes check`, then `snapshot --at …`, then a visual review, then `npx hyperframes render -q delivery`.
8. **Thumbnails** (`scripts/thumbs.py` + the recipe's `thumbs.json`):
   - Pick 1 main frame and 1 inset frame per clip from 1 fps contact sheets. Prefer the payoff object or a reaction face.
   - Grade with ffmpeg (`eq=saturation=1.35:contrast=1.12`, `unsharp`).
   - Build two HyperFrames still projects (vertical 1080×1920, landscape 1280×720), `snapshot` them, and export JPGs under 2 MB.
   - Style: 2-line headline (white line, then yellow line, thick black stroke, −3° tilt), a red price/label badge, a circular inset with a white + red ring, and a red arrow (landscape only).

**Commands for a new video** (from `Documents/clipping`):
```
export CLIP_RECIPE="<abs path>/5_TOOLS_AND_SCRIPTS/recipes/<nn_name>"
python -I 5_TOOLS_AND_SCRIPTS/scripts/plate.py <source.mp4> "<abs path>/4_EDITABLE_PROJECTS/<NN_Name>"
python -I 5_TOOLS_AND_SCRIPTS/scripts/gen.py "<abs path>/4_EDITABLE_PROJECTS/<NN_Name>" "<abs path>/5_TOOLS_AND_SCRIPTS/hyperframes_starter_with_sound_effects"
python -I 5_TOOLS_AND_SCRIPTS/scripts/thumbs.py <recipe>/thumbs.json 4_EDITABLE_PROJECTS/<NN_Name>/thumbnails
```
7. Run the per-clip checklist in the report (19 steps) before posting.

**Tool notes**
- OpusClip connector: account had **0 credits** on 2026-11-17, so the AI clipping isn't usable until credits are added.
- HyperFrames `check` warns that one big generated `index.html` should be split into sub-compositions. That's harmless for rendering but worse for hand-editing in the Studio.

## 10. Lessons learned from jobs [O]

- **MrBeast footage has no silences.** A music bed runs under everything and it's already tightly edited, so `silencedetect` finds nothing. Tightening has to come from **cutting whole low-value lines** and reordering, not from removing pauses.
- MrBeast's source video has **its own burned-in text** at the bottom of some shots ("GIVE YOU A MILLION DOLL…", "10 MINUTES"), which gets cropped and can clash with our captions. Options: crop higher, or cover it with the caption band.
- Caption bugs we hit:
  - words collided because the stroke ate the gap (fixed with 16 px margins)
  - a hook keyword followed by punctuation (`*LAB*.`) broke the highlight parser (fixed with a regex)
  - long hook lines wrapped (fixed with per-line auto font size and `nowrap`)
- YouTube auto-caption word timings are good enough for word-by-word captions, but start cuts ~0.1 s before a word's start time and end ~0.1–0.2 s after.
- Keep graphics out of the rewind tag's window (cold-open cut + ~1.5 s); a sticker placed there collided with the "⏪" tag in clip 1. Always check with `snapshot` at every beat time before rendering.
- v2 render check: all 5 clips 1080×1920, -14.6 to -15.3 LUFS, true peak ≤ -1 dBTP; HyperFrames render ≈50 s per 45 s clip.
- **Job 2 (Nuclear Bunker):**
  - Visual payoffs (explosion, flamethrower) don't show up in the transcript. Always check a 1 fps contact sheet around the payoff before setting the cold open. The explosion sat 3–5 s after "drop the ball".
  - Multi-word hook highlights (`*IRON MAN*`) broke the one-word parser, which now tracks highlight state across words.
  - **Vertical thumbnails:** cropping a 16:9 frame straight to 9:16 put faces behind the headline. The fix is a blurred band on top for the headline, with the sharp image starting at y≈470.
  - **16:9 thumbnails:** check the text doesn't cover the face. Clip 5 needed its headline moved to the bottom.
- Job 3: timestamps on a 0.5–1 fps contact sheet can be about 1 s off, so confirm the exact thumbnail frame with a 2 fps scan. Place a counter on the shot that matches it (the $50K safari counter first landed on submarine footage).
- Job 4 (43-min video): grep the transcript for high-signal words (weigh, $, cry, car, scared…), then read only those line ranges. That cut transcript tokens by ~70%. For story videos (a challenge arc), pick each milestone as its own clip.
- Job 5: on-screen scoreboards and maps get cut by the 8:9 panel. Mark those segments `[a,b,"wide"]` and move the CTA (`cta_y`: 310) so it doesn't cover them. Always verify the winner on screen: the transcript implied the wrong team won.
- Write recipe JSON compactly (no indent); pretty JSON gets echoed back as large diffs and wastes tokens.
- Upgrade v2 tests:
  - GPU Whisper turbo transcribes 3 min of audio in 11 s.
  - Reframe needs ≥2 s shots, or it flickers.
  - `candidates.py` cuts transcript reading from ~25k to ~1.5k tokens on a 43-min video.
  - The Windows app sandbox redirects `%LOCALAPPDATA%`, so keep tools in `~/.clipping`.
  - A clip open in another app blocks re-encoding; `export.py` reports it as LOCKED.
- Restructuring took the v1 clips from 55–93 s down to 38–56 s, all under the 60 s Shorts Content-ID limit.

- Beast Games / competition shows: the episode-ending cliffhanger (a $5M jump) is a strong clip, so end on the jump and ask "Did he make it?". Overhead game shots need the `wide` layout; a panel crop shows only an empty floor.
- Use a stylized replay frame (glow and slow-mo graphics) as the thumbnail background; it beats raw overhead frames.

- Thumbnails: when the thumbnail text repeated the title, it wasted the second line of information. Now image + thumbnail text + title each tell a different part. Cut-outs: `u2net_human_seg` keeps raised arms; `isnet` lost an arm against a white sky.
- Titles: 3 different formulas (hook + open loop, quote, curiosity) give A/B options. Keep them short (≤50 chars) because Shorts titles get cut off on mobile.

- Cut-outs: pick a close frame where the subject is alone. Wide or group frames shrink the subject on `sticker`/`bignum`. Burned-in source captions stay in the cut-out, so avoid frames that have them.
- Check figures against on-screen graphics: the results screen said "222 LBS / 100.7 KG" (100.7 is kg, not pounds lost). The start was 324 lb, so the real loss was 102 lb.
- YouTube auto-captions mishear background lines ("four codes"). Delete those words from `words.json` before building.

- Long "days in a place" videos: combine a setup from early on with its payoff much later in one clip (asking her parents → the proposal at the exit; the $1-per-wasted-calorie rule → only 6,614 wasted). Long-arc callbacks make the strongest stories.
- `callout` ring colour: a red ring on a red subject (the Lambo) loses contrast. Next time try `pal` cyan or yellow for the arrow and frame the subject differently.

- Before every new job, check for duplicates: grep the video ID in `recipes/*/source.json` and `copy.json`, and compare the title with the `1_READY_TO_POST` folders.
- `cta_y` must stay clear of the caption band (around y 1100–1250). Use 330 (top) when a stamp sits at centre near the end; 1200 overlapped the captions.
- Overlay scoreboards (LeBron 05–06) sit at the bottom corners of the source, so use the `wide` layout or the panel crop hides the score. Check who won from the scoreboard, not the transcript ("I won by one" was LeBron).

- True peak can exceed −1 dBTP after the size re-encode (LeBron clip, −0.5). `loudnorm` made it worse (+3.5). The fix: `aresample=192000,alimiter=limit=0.5,aresample=48000`, AAC 256k, video copied. That gave −1.9 dBTP at −14.7 LUFS.

- Hashtag limits: YouTube ignores ALL hashtags on a video with more than 15 (first 3 show above the title). Instagram caps posts at 5 (reported Dec 2025). TikTok and Facebook have no hard cap, so use 12–15 there.

- Job 10 (charity/build videos): the payoff is a reaction to a reveal, not a win, so open on the happiest line ("best day of my life") and rewind to the "before" (cramped room, flooded school). Every clip gets a clear before → after.
- `counter` beats must be `"NUMBER|LABEL"` (e.g. `"10|NEW CLASSROOMS"`); plain text crashes `gen.py`.
- Swing/action shots with a small subject: face-crop can land on legs. Split the segment and mark the action part `wide`.
- rembg on a kid mid-motion with a busy crowd behind gives fragments; switch that clip to a style without a cutout (callout/cinema) instead of hunting frames.

- Some posted clips (jobs 01–10, all unlicensed MrBeast) got blocked. Lesson: licensing, not editing, decides whether a clip stays up. Check for a campaign before choosing the video.

## 11. Research backlog (next things to learn or test)
- [ ] Money: test a $10–20 payout from Whop Content Rewards and Vyro to Pakistan before scaling; pick a second niche (Sports/Gaming/Tech, ~$1.4–2 per 1K views).
- [ ] Hook A/B: post 2 hook variants as Instagram Trial Reels and log the winner in §12.
- [ ] Active-speaker detection (Light-ASD) for two-person podcasts, only if we start clipping podcasts.

- [ ] Face-tracked full 9:16 crop instead of the 8:9 panel (the research default). Needs a per-shot subject position (e.g. `opusclip_analyze_video` or a local face detector).
- [ ] Find a real **riser** and **ding** SFX (CC0).
- [ ] Freeze-frame + arrow/circle callouts (recommended for MrBeast style, not built yet).
- [ ] Voiceover or commentary layer to make originality bulletproof on YouTube.
- [ ] A/B test: progress bar vs none; emoji-heavy vs "Dynamic Minimalism".
- [ ] A frame-by-frame analysis of MrBeast's *own* Shorts (none found in research).
- [ ] Beast Games S2: clip new episodes on release day (fresh-episode demand), and test cliffhanger vs resolved payoffs.
- [ ] A/B test thumbnail styles: log the style per clip in §12 and compare views/CTR after 7 days; drop the weakest style.
- [x] `export.py`: measures LUFS and true peak on every clip and auto-applies the oversampled limiter when it's above −1 dBTP (it warns when loudness is outside −16 to −13.5).
- [ ] A/B test hashtag count on YouTube Shorts (4 vs 12–15) with views after 7 days.
- [ ] Real retention data from posted clips (fill in §12).
- [x] Thumbnails for job 1 (Futuristic Tech) clips using `thumbs.py`.
- [ ] Research how Shorts custom thumbnails and covers are shown in 2026 (feed vs channel grid crop), and A/B test thumbnail styles.
- [ ] Compare charity/build-video clips (job 10) vs challenge clips (jobs 07–09): views and shares after 7 days.
- [ ] Ask Vyro/Whop support whether approved clips are allowlisted in the creator's Content ID (or still claimed).
- [ ] Build a list of 5–10 creators with public clipping permission or live campaigns outside MrBeast.
- [ ] Log every claim/block in §12: platform, clip, claimant, block vs monetize.

## 12. Experiment log (fill in after posting)

| Date | Clip | Platform | Variant / hook | Length | Views 24h / 7d | Viewed-vs-swiped or 3 s hold | Avg % viewed | Shares/sends | Notes (where the curve dropped) |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

Reading a retention curve:
- a cliff at 0–3 s means the hook failed
- a mid-clip dip means a re-hook is missing
- a late drop means the ending ran long
- a curve above 100% means the loop works

---

## How to update this file

1. After every job, add a **Changelog** row and any new **Lessons learned**.
2. When you post clips, log results in **§12**, then promote patterns that hold across ≥3 clips into §2–§5 tagged **[O]**.
3. When new research is done, save notes to `2_RESEARCH_AND_KNOWLEDGE/research_notes/` and the report next to this file, then merge the conclusions here with evidence tags. Replace older claims rather than stacking contradictions, and note the date.
4. Tick items off the **backlog** and add new open questions as they come up.
