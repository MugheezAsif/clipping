# The Best Part: a viral Shorts clipping pipeline

> **ONLY THE BEST MOMENTS.** Turn one long YouTube video into 5 ready-to-post vertical clips (YouTube Shorts, Instagram + Facebook Reels, TikTok, X, Snapchat), each with motion-graphics edits, two custom thumbnails and a complete posting kit.

This repo is the full setup behind **The Best Part**, a clipping channel. It holds the Python pipeline, the editing rules, the research it's built on, the brand kit and the recipe (the cut list and creative plan) for every video clipped so far.

---

## Contents
- [The idea](#the-idea)
- [What one run produces](#what-one-run-produces)
- [How the pipeline works](#how-the-pipeline-works)
- [Repository layout](#repository-layout)
- [Setup](#setup)
- [Usage](#usage)
- [Recipe files](#recipe-files)
- [Quality rules the scripts enforce](#quality-rules-the-scripts-enforce)
- [Thumbnails](#thumbnails)
- [Posting](#posting)
- [Clipped so far](#clipped-so-far)
- [What isn't in this repo](#what-isnt-in-this-repo)
- [Copyright](#copyright)

## The idea

Long videos are full of moments that would go viral as Shorts if someone cut them well. Most clipping channels simply crop the video and burn in captions. This pipeline re-edits every clip so it's original work:

1. **Find** the strongest moments automatically (a hype-density score from word timings, caps, loudness, money and stakes words). A human then picks with a 25-point rubric.
2. **Restructure** each clip: open on the outcome (cold open), rewind, tell the story, hard-cut right after the reaction. Clips run 30 to 45 s, 58 s at most.
3. **Re-edit**: auto-reframe to 9:16 per shot, punch-ins, a ≤6-word hook with one yellow keyword, word-by-word captions, stickers, stamps, counters, SFX and a progress bar.
4. **Package**: two thumbnails per clip in different design styles, three titles from three formulas, and captions plus hashtags tuned per platform.
5. **Guard**: every master file is checked and auto-fixed for platform specs and loudness before it reaches the posting folder.

## What one run produces

For each source video (`NN_Name`), `1_READY_TO_POST/NN_Name/` gets:

| Output | Details |
|---|---|
| `clips/` | 5 × MP4 master, 1080×1920, H.264, AAC 48 kHz, 30 fps, faststart, ≤95 MB, −14 to −15 LUFS, true peak ≤ −1 dBTP |
| `thumbnails/` | Per clip: a `__Shorts_cover_9x16.jpg` (1080×1920) and a `__YouTube_thumbnail_16x9.jpg` (1280×720) |
| `YOUTUBE_CAPTIONS.md` | 3 titles, description, 12–15 hashtags, tags, pinned comment, posting order |
| `INSTAGRAM_CAPTIONS.md` | Instagram caption (5 hashtags, the platform cap), alt text and a separate Facebook caption (12–15 hashtags) |
| `TIKTOK_X_SNAP_CAPTIONS.md` | TikTok caption (12–15 hashtags), X post (≤280 chars), Snapchat Spotlight caption |
| `schedule.csv` | One clip per day at 18:00, in the recommended order |

## How the pipeline works

```
YouTube URL
   │  clip.py new        yt-dlp download → YouTube captions or GPU Whisper (asr.py) → words.json
   │                     candidates.py ranks the top 15 non-overlapping moments → candidates.txt
   ▼
Pick clips (RUBRIC.md, score ≥18/25)  ──  clip.py sheet: contact sheet to check the visual payoff
   │
   │  edits.json · settings.json · names.json · spec.json   (you write these small recipe files)
   ▼
clip.py build        reframe.py   per-shot layout: face crop on close-ups, blurred panel on wide shots
                     plate.py     the edited 9:16 plate + remapped word timings
                     gen.py       a HyperFrames (HTML → video) project per clip: hook, captions, graphics, SFX
                     → automatic checks + one review sheet
   ▼
clip.py render       render.py → 1_READY_TO_POST/NN_Name/clips  + export.py guard
   ▼
clip.py frames / thumbs      graded frames → thumbs.py (7 styles, rembg cutouts) → 9:16 + 16:9 thumbnails
   ▼
clip.py kit          kit.py: copy.json → captions for every platform + schedule.csv + copy check + export guard
```

Every stage prints only a few lines and one review image, so it stays fast to drive (also from an AI coding assistant).

## Repository layout

```
.
├── 1_READY_TO_POST/              one folder per video: caption kits + schedule (clips and thumbnails stay local)
├── 2_RESEARCH_AND_KNOWLEDGE/
│   ├── CLIPPING_KNOWLEDGE.md     the living playbook: rules, lessons, changelog, backlog, results log
│   ├── Full_Research_Report.md   the original research on what makes Shorts go viral
│   ├── reports/                  strategy + monetization ("Clipping strategy upgrade.md")
│   └── research_notes/
├── 5_TOOLS_AND_SCRIPTS/
│   ├── scripts/                  the pipeline (see below)
│   ├── recipes/nn_name/          per-video recipe JSONs (cut list, graphics, thumbnails, copy)
│   ├── RUBRIC.md                 clip scoring, title formulas, thumbnail style picker
│   ├── hyperframes_starter_with_sound_effects/   SFX library + HyperFrames starter
│   └── requirements.txt
├── 6_BRAND_ASSETS/               The Best Part: logos (SVG), profile pictures, banners, watermark
├── CLAUDE.md                     workflow rules for the AI assistant that drives the pipeline
└── README.md
```

| Script | Job |
|---|---|
| `clip.py` | The single entry point: `new`, `sheet`, `build`, `render`, `frames`, `thumbs`, `kit` |
| `asr.py` | GPU word-level transcription (faster-whisper large-v3-turbo) for videos without captions |
| `candidates.py` | Ranks clip candidates by hype density per 30 s |
| `reframe.py` | Per-shot 9:16 layout decision (OpenCV + MediaPipe face detection) |
| `plate.py` | Builds the edited 9:16 plate per clip and remaps word timings |
| `gen.py` | Generates the HyperFrames composition: punch-ins, hook header, rewind tag, captions, stickers, SFX, progress bar |
| `render.py` | Renders compositions to MP4 |
| `thumbs.py` | Thumbnails v2: 7 styles, 6 palettes, Anton / Bebas Neue / Montserrat 900 |
| `cutout.py` | Subject cutouts with rembg (`u2net_human_seg`) for sticker-style thumbnails |
| `kit.py` | Writes every posting file from one `copy.json` and checks titles and hashtags |
| `export.py` | Platform + loudness guard; re-encodes, remuxes and peak-limits in place |

## Setup

Requirements: **Windows, macOS or Linux**, **Python 3.10+**, **FFmpeg** (with `ffprobe`) on `PATH`, **Node.js 18+** (for [HyperFrames](https://www.npmjs.com/package/hyperframes) via `npx`) and, optionally, an NVIDIA GPU for Whisper.

```bash
python -m venv ~/.clipping/env
~/.clipping/env/Scripts/pip install -r 5_TOOLS_AND_SCRIPTS/requirements.txt
```

On macOS/Linux use `~/.clipping/env/bin/pip`. Source videos and render caches live in `~/.clipping/cache` and rembg models in `~/.clipping/models`, never inside the repo.

## Usage

```bash
cd 5_TOOLS_AND_SCRIPTS/scripts
python clip.py new https://www.youtube.com/watch?v=VIDEO_ID 10_Name     # add --cookies cookies.txt if YouTube asks for sign-in
python clip.py sheet 10_Name 512:6 1340:8                                 # check visual payoffs
python clip.py build 10_Name                                              # after writing the recipe files
python clip.py render 10_Name                                             # slow: run in the background
python clip.py frames 10_Name t1_bg:12.3 t1_in:40
python clip.py thumbs 10_Name
python clip.py kit 10_Name
```

Each new source video takes the next number (`NN_Name`) in `1_READY_TO_POST`, `4_EDITABLE_PROJECTS` and `5_TOOLS_AND_SCRIPTS/recipes`.

## Recipe files

All creative decisions live in small JSON files in `5_TOOLS_AND_SCRIPTS/recipes/nn_name/`; scripts generate everything else.

| File | Holds |
|---|---|
| `source.json` | URL, title, channel, duration (written by `new`) |
| `edits.json` | Per clip: segments `[a, b]` or `[a, b, "wide"]`, cold open first |
| `settings.json` | `{"layout": "auto"}` (+ `"tighten": true` for podcasts and streams) |
| `names.json` | `{"c1_slug": "01_File_Name"}` |
| `spec.json` | Per clip: hook, keyword, beats `[t, type, text, sfx, dur]` (sticker, stamp, counter, emoji), push, shake, CTA |
| `thumbs.json` | Per clip: style, palette, text lines, frames, cutout and focus options |
| `copy.json` | Titles, story, debate question, pinned comment, hashtags, tags, IG hook, share prompt, alt text, posting order |

## Quality rules the scripts enforce

- **Structure:** one payoff and one high-arousal emotion per clip; open on the outcome, rewind, ≤58 s (aim 30–45), hard cut ≤1 s after the reaction.
- **Hook:** ≤6 words with one yellow keyword; no graphics in the rewind window (+1.5 s).
- **Safe area:** text stays inside y 170–1330 and clear of the right-hand ~120 px (platform UI).
- **Export guard (`export.py`):** fixes size, codec, frame rate and faststart; measures loudness and applies an oversampled limiter when true peak is above −1 dBTP.
- **Copy check (`kit.py`):** title 1 ≤50 chars, ≤1 emoji, no shouting, three different title formulas, thumbnail text never repeats the title, YouTube hashtags 12–15 (never more than 15, or YouTube ignores them all).

## Thumbnails

`thumbs.py` builds both sizes from one plan, using a different style for each clip in a video:

| Style | Best for |
|---|---|
| `sticker` | A big reaction face cut out over the scene |
| `bignum` | A huge number or money figure |
| `vs` | Two sides, a challenge or a before/after |
| `callout` | A ring or arrow on the thing to look at |
| `reveal` | A blurred or hidden payoff |
| `cinema` | A dramatic wide frame with letterbox text |
| `stack` | Stacked panels that tell a mini story |

The thumbnail text adds information the title doesn't have; the palettes rotate through yellow, red, cyan, green, pink and orange.

## Posting

Publish natively for full reach: **YouTube Studio**, **Meta Business Suite → Create reel** (Facebook + Instagram together, with *Customize for each platform*), the **TikTok** web scheduler, and **X** and **Snapchat** by hand. Post one clip per day in the order from the kit, then log the 1/3/7-day results in `CLIPPING_KNOWLEDGE.md` §12.

## Clipped so far

<details>
<summary>9 videos · 45 clips (click to expand)</summary>

### 01_Futuristic_Tech: "$1 vs $1,000,000,000 Futuristic Tech!" (with thumbnails)
| # | Clip | Length |
|---|---|---|
| 01 | Neuralink Mind Control | 46 s |
| 02 | Kai's Bionic Arm | 56 s |
| 03 | Flying Car Million Dollar Race | 52 s |
| 04 | Lab-Grown Chicken Taste Test | 38 s |
| 05 | Blowtorch vs Bare Hand | 48 s |

### 02_Nuclear_Bunker: "$1 vs $1,000,000,000 Nuclear Bunker!" (with thumbnails)
| # | Clip | Length | Thumbnails |
|---|---|---|---|
| 01 | $1 Bunker vs Bomb | 34 s | 9:16 cover + 16:9 |
| 02 | Real-Life Iron Man Bunker | 56 s | 9:16 cover + 16:9 |
| 03 | JFK's Secret Bunker | 35 s | 9:16 cover + 16:9 |
| 04 | $50M Bunker Under a Normal House | 52 s | 9:16 cover + 16:9 |
| 05 | He Touched the Button (Top Secret Bunker) | 51 s | 9:16 cover + 16:9 |

### 03_500K_Experiences: "$1 vs $500,000 Experiences!" (with thumbnails)
| # | Clip | Length | Thumbnails |
|---|---|---|---|
| 01 | The $1 Camel Ride | 27 s | 9:16 cover + 16:9 |
| 02 | Charged by an Elephant | 46 s | 9:16 cover + 16:9 |
| 03 | He Gave a Stranger a Lamborghini | 37 s | 9:16 cover + 16:9 |
| 04 | Skydiving, His Biggest Fear | 56 s | 9:16 cover + 16:9 |
| 05 | Top of the Tallest Building | 53 s | 9:16 cover + 16:9 |

### 04_Lose_150_Lbs: "Lose 150 Lbs Together, Win $250,000" (with thumbnails)
| # | Clip | Length | Thumbnails |
|---|---|---|---|
| 01 | Lose 150 Lbs, Win $250K | 54 s | 9:16 cover + 16:9 |
| 02 | Family Sees Them for the First Time | 54 s | 9:16 cover + 16:9 |
| 03 | Pull a Truck 300 Laps, Win 2 Cars | 56 s | 9:16 cover + 16:9 |
| 04 | Pick a Briefcase, Win $25K | 59 s | 9:16 cover + 16:9 |
| 05 | Climb a Net Into a Helicopter | 59 s | 9:16 cover + 16:9 |

### 05_Extreme_Places: "I Survived The Most Extreme Places On Earth" (first video made with pipeline v2)
| # | Clip | Hook |
|---|---|---|
| 01 | Lost by 8 Minutes After 28 Hours | The photo-finish scoreboard |
| 02 | Antarctic Whiteout | 50 mph winds, "I'm blinded" |
| 03 | Amazon River Current | Swimming the Amazon against the current |
| 04 | Desert Skeleton, Die Trying | A skeleton in the desert |
| 05 | Everything That Can Kill Us | The Amazon kill list |

### 06_Beast_Games_S2E2: "Beast Games | Season 2 Episode 2"
| # | Clip | Hook |
|---|---|---|
| 01 | One Jump for 5 Million | Johnny's final jump for the flag (cliffhanger) |
| 02 | The Tower Collapsed | 30% of the tower gone in a second |
| 03 | Out Before a Ball Was Thrown | Eliminated for touching the red line |
| 04 | Balls Collided Midair | Two dodgeballs collide in midair |
| 05 | The Assassin Got Assassinated | Season 1's Akira, out in one game |

### 07_Lose_100_Lbs: "Lose 100 LBs, Win $250,000!" (v2 thumbnails)
| # | Clip | Hook |
|---|---|---|
| 01 | $1,000 Every Second He Hangs | A 100 ft dead hang, 6 s → 60 s |
| 02 | $1,000 Per Push-Up | 31 push-ups = $31,000 |
| 03 | Drop One Bill, Lose $40K | A $40,000 carry with no drops |
| 04 | His First Pull-Up Ever | A lifelong dream |
| 05 | 100 Lbs Gone in 178 Days | The final weigh-in and family reunion |

### 08_Grocery_Store_1M: "Eat Everything In A Grocery Store, Win $1,000,000"
| # | Clip | Hook |
|---|---|---|
| 01 | Blindfolded Shopping Chaos | MrBeast's crew shops blindfolded |
| 02 | Lamborghini in a Grocery Store | A Lambo drives into the store |
| 03 | He Asked Her Parents First | Asks permission, then proposes on day 202 |
| 04 | The Last Bite After 202 Days | The final meal in front of a crowd |
| 05 | Every Wasted Calorie Costs $1 | The rule, then only 6,614 calories wasted |

### 09_Beat_Pro_Athlete: "Beat Professional Athlete, Win $100,000"
| # | Clip | Hook |
|---|---|---|
| 01 | Beat Haaland for $100K | A target shootout at Manchester City |
| 02 | We Beat a Gold Medalist | Alyssa Liu, 100 spins vs grabbing bags |
| 03 | Gordon Ramsay Idiot Sandwich | The meme, live |
| 04 | 1.5-Inch Beam, 100 Ft Up | Simone Biles, $250K for foster kids |
| 05 | 1v1 vs LeBron for $100K | Most 3s in 1 minute, decided by one shot |


</details>

## What isn't in this repo

To keep the repo small and safe, `.gitignore` leaves out finished clips and thumbnails, the old plain clips, the editable render projects (`4_EDITABLE_PROJECTS`, regenerated by `clip.py build`), raw transcripts, source videos and any `cookies.txt`. A cookies export contains your YouTube sign-in: delete it after use and never commit it.

## Copyright

The scripts, rules, research and brand assets are this project's own work. Clipped footage belongs to its creators (so far, MrBeast). Clips posted outside a creator's official clipping program can be claimed or demonetized. Every posting kit includes a credit line to the original video.
