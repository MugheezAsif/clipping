# Workspace rules: clipping

Purpose: turn long videos into viral Shorts/Reels/TikToks (clips + thumbnails + posting kit) for **The Best Part**.

## Token budget (always)
- Be brief: results and decisions only, no recaps or option lists.
- Drive everything through `5_TOOLS_AND_SCRIPTS/scripts/clip.py`. Its output is already compact. Never read full transcripts, JSON or logs; filter with `grep`/`tail`.
- Knowledge: read only the section you need of `2_RESEARCH_AND_KNOWLEDGE/CLIPPING_KNOWLEDGE.md` (`grep -n "^## "` first). Strategy and money: `2_RESEARCH_AND_KNOWLEDGE/reports/Clipping strategy upgrade.md`. No new research unless asked.
- Write only the small recipe files (edits/spec/names/thumbs/copy JSON). Scripts generate everything else (markdown kits, schedule, exports).
- Visual checks: use the one review sheet each `clip.py` stage prints. Long renders run in the background; don't poll.
- Skip HyperFrames structure warnings; act on errors only.

## Workflow (one video = one `NN_Name`)
1. `python clip.py new <url> NN_Name [--cookies cookies.txt]` → captions (or GPU Whisper) + ranked `candidates.txt`.
2. Pick clips with `5_TOOLS_AND_SCRIPTS/RUBRIC.md` (score ≥18/25, 30–45 s, setup + reaction inside). Check visual payoffs with `clip.py sheet NN t:dur …`.
3. Write `edits.json` (cold open first), `settings.json` `{"layout":"auto"}` (face crop per shot; add `"tighten":true` for podcasts/streams), `names.json`, `spec.json` (copy the latest recipe as a template).
4. `clip.py build NN` → review the sheet → fix → `clip.py render NN` (background; it also runs the export guard).
5. `clip.py frames NN t1_bg:12.3 t1_in:40 …` → `thumbs.json` (a different style per clip, see RUBRIC: Thumbnails; text adds info, never repeats the title) → `clip.py thumbs NN` → review the sheet.
6. `copy.json` → `clip.py kit NN` → YouTube, IG/FB, TikTok/X/Snap captions, `schedule.csv`, export guard.
- Tools env: `~/.clipping/env` (torch cu128, faster-whisper, opencv, mediapipe). Cache and sources: `~/.clipping/cache` (never in this folder).

## Folder rules
- `1_READY_TO_POST/NN_Name/`: `clips/`, `thumbnails/`, `YOUTUBE_CAPTIONS.md`, `INSTAGRAM_CAPTIONS.md`, `TIKTOK_X_SNAP_CAPTIONS.md`, `schedule.csv`. The only folder the user posts from.
- `2_RESEARCH_AND_KNOWLEDGE/`, `3_OLD_VERSION_plain_clips/`, `4_EDITABLE_PROJECTS/NN_Name/` (clip projects + thumbnails), `5_TOOLS_AND_SCRIPTS/` (scripts, `recipes/nn_name/`, RUBRIC, SFX starter), `6_BRAND_ASSETS/` (brand: **The Best Part**, crop-brackets + play mark, white on #0B0B0B, Montserrat 900, tagline "ONLY THE BEST MOMENTS").
- New source video = next number in folders 1, 4 and 5/recipes. Never mix videos in one folder.
- Filenames: `NN_Title_Case_Words.mp4`, `NN_Title__Shorts_cover_9x16.jpg` and `__YouTube_thumbnail_16x9.jpg`, no spaces.

## Clip rules
- 5 clips per video unless told otherwise. Each has one payoff and one high-arousal emotion. Open on the outcome, rewind, ≤58 s (aim 30–45), hard cut ≤1 s after the reaction.
- Hook ≤6 words with one yellow keyword. No graphics in the rewind-tag window (+1.5 s).
- Text stays inside y 170–1330 and clear of the right-hand ~120 px.
- Master file for all platforms: 1080×1920, H.264, AAC 48 kHz, 30 fps, faststart, ≤95 MB, −14 to −15 LUFS, true peak ≤ −1 dBTP (`export.py` enforces this).
- Originality matters: every clip must be visibly re-edited (restructure, hook, captions, graphics). No watermarks from other apps.

## Posting copy rules (`copy.json` → `kit.py`)
- Per clip:
  - 3 titles from 3 different formulas (RUBRIC: Titles): hook + open loop ≤50 chars matching the on-screen hook, a quote, a curiosity/why line. Fix every `title check` warning.
  - story (1–2 lines)
  - a debate question (never "comment YES")
  - a pinned comment
  - 12–15 YouTube hashtags (`hashtags`, never more than 15 or YouTube ignores all of them): #shorts, creator, 2–3 topic tags first (the first 3 show above the title), then niche + broad. TikTok and the Facebook caption reuse them automatically (merged with the IG tags, 12–15).
  - 8–10 tags (facts only)
  - an IG hook (≤125 chars)
  - a "send this to…" prompt
  - 5 IG hashtags, mixing niche and broad (Instagram's cap is 5; Facebook gets its own 12–15 caption)
  - alt text
- Credit lines and SFX credits are added automatically. Include a posting order.
- Publish natively: YouTube Studio, Meta Business Suite **Create reel** (FB + IG together), the TikTok web scheduler; X and Snapchat manually. Never post, upload or delete user files without asking.

## After every job
- Update `CLIPPING_KNOWLEDGE.md`: a one-line changelog row, one-line lessons (§10) and the backlog (§11). Update the `README.md` tables.
