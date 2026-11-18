# OpusClip + competitors: feature teardown (checked Nov 2026)

Bias flag: most feature detail comes from vendor pages/blogs (opus.pro, submagic.co comparison pages are competitor-written). User sentiment comes from review aggregators (eesel, G2, Trustpilot quotes via eesel). Few direct Reddit threads were found.

## 1. How OpusClip picks clips

### Takeaway
It's an LLM/multimodal ranker. It scores candidate segments on four qualitative axes (Hook, Flow, Value, Trend), plus prompt relevance in ClipAnything, and conditions on a detected genre. No weights are published. Users say the score is unreliable and selection often loses context.

### Cited Findings
- Virality Score is 0–99 per clip, sorted high to low by default. Free plan can't see it. — [help.opus.pro](https://help.opus.pro/docs/article/virality-score.md)
- The four factors: **Hook** (opening grabs attention and relates to the main topic), **Flow** (logical progression, satisfying ending), **Value** (useful, emotionally resonant, personally connecting), **Trend** (fits current trends/interests). No numeric sub-score weights are documented. — [help.opus.pro](https://help.opus.pro/docs/article/virality-score.md)
- One reviewer saw per-factor letter grades (all A on a 98 clip), with the transcript and source timestamp shown. — via [search summary of marcandrews.com](https://marcandrews.com/?p=6263) (unverified detail)
- ClipAnything signals:
  - visual: per-frame objects, scenes, actions, on-screen text, style
  - audio: active speaker plus non-speech events (laughter, cheering, SFX, music), "not limited to transcript"
  - sentiment: happiness, surprise, arguments
  - each scene is "rated based on its virality potential"

  — [opus.pro/clipanything](https://www.opus.pro/clipanything)
- Modes: **Hands-Free** auto-detects the genre and applies "the best prompts" from a narrative library. **Custom** lets you pick a genre and type a natural-language prompt (scene, action, character, emotion, topic). ClipBasic accepts only keywords spoken in the video. Clips run up to 15 min. — [opus.pro/clipanything](https://www.opus.pro/clipanything)
- With ClipAnything, the score adds a check that the clip matches the prompt. — [help.opus.pro](https://help.opus.pro/docs/article/virality-score.md)
- Users report:
  - the AI "misses the point" and cuts jokes before the punchline
  - it drops context sentences
  - low-scored clips sometimes outperform "winners"

  — [eesel.ai review roundup](https://www.eesel.ai/blog/opusclip-reviews) (citing Reddit r/podcasting, sendshort, Submagic)
- A G2 reviewer used "maybe 40%" of clips. — via [G2](https://www.g2.com/products/opusclip) (search summary)
- OpusClip's own 13.5M-clip analysis (Jan–Mar 2026, vendor data, correlational):
  - outcome/product-showcase hooks got ~2x the views of the worst hook type; story-setup openers ranked last
  - 80.2% of viral-tier clips have burned-in captions, 78.6% animated
  - viral-tier median length 41 s vs 50 s overall
  - a mixed niche + broad hashtag strategy got 2.5x the median views of niche-only

  — [opus.pro blog](https://www.opus.pro/blog/anatomy-of-a-viral-tiktok-2026)

### Inferences
- The score is most likely an LLM judging the transcript plus vision features against a rubric. We can reproduce the rubric locally (an LLM prompt that scores Hook/Flow/Value/Trend 1–10 with a rationale) and keep a human final pick, which is what reviewers end up doing anyway.
- The "genre → prompt library" idea is cheap to copy: per-genre prompt presets (e.g. challenge/stunt video → "reveal, failure, cash moment, reaction").
- Their biggest weakness (context loss, cut punchlines) is what our manual pick plus cold-open restructuring already solves.

### Gaps
- No published weights, model details or accuracy validation for the Virality Score. No independent A/B study of score vs. real views was found.

## 2. Reframing / layouts

### Takeaway
It detects faces/speakers and screenshare, then picks from a whitelist of layouts the user enables in the brand kit. The rules are simple and replicable.

### Cited Findings
- Layouts:
  - **Fill**: crop to the speaker
  - **Fit**: 4:3 with padding
  - **Split**: 2 speakers
  - **Three** / **Four** speakers
  - **Screenshare**: screen on top, speaker below
  - **Gameplay**: speaker in the top 30%, game in the bottom 70%

  — [help.opus.pro layout](https://help.opus.pro/docs/article/layout-and-reframing.md)
- Decision rules:
  - the AI auto-detects speakers and screenshare and applies only the layouts enabled in "Clip layout settings"
  - Split needs both speakers in the same source frame; Three/Four need 3+ in frame
  - Screenshare needs a screen plus 1 speaker, otherwise it falls back to another layout
  - "Pin first speaker" keeps the speaker order fixed

  — [same](https://help.opus.pro/docs/article/layout-and-reframing.md)
- Auto Reframe tracks moving/active speakers and can't be manually toggled. — [help.opus.pro](https://help.opus.pro/docs/article/layout-and-reframing)
- The Business tier lists a "genre-specific reframing model". — [opus.pro pricing via search](https://opus.pro/pricing)
- Klap "AI Reframe 2" offers split screen, screencast and gaming layouts. — [klap.app](https://klap.app/)
- Riverside lets you choose a focus speaker and layout per platform preset. — [riverside.com/magic-clips](https://riverside.com/magic-clips)
- Users say reframing is "decent for simple talking-head videos". — [eesel.ai](https://www.eesel.ai/blog/opusclip-reviews)

### Inferences
- A local equivalent:
  - face detection (MediaPipe/YOLO-face) per 0.5 s
  - smooth the crop center (EMA plus a dead-zone, so the frame doesn't jitter)
  - active speaker = the face with the most mouth movement, or the face matching the diarized speaker
  - if 2 faces are far apart, use a split layout
  - apply the crop with an ffmpeg `crop` driven by a sendcmd/expression file

## 3. Editing features (captions, B-roll, hooks, cleanup, brand, languages)

### Takeaway
They all converge on the same kit: animated word captions with keyword/emoji highlight, an auto "headline" hook overlay, filler/silence removal, AI/stock B-roll, brand templates and translation. We already have most of it except auto-B-roll, filler removal and translation.

### Cited Findings
- OpusClip "Auto headline" (formerly Auto hook) auto-generates a one-line text overlay at clip start, styled in the brand template (font, weight 700, background, radius). — [help.opus.pro auto-headline](https://help.opus.pro/docs/article/auto-headline) / [brand template](https://help.opus.pro/docs/article/how-to-add-a-brand-template.md)
- Caption templates include an emoji plus keyword highlighter (reportedly on all plans). Important words get color, size or animation. — [opus.pro blog](https://www.opus.pro/blog/best-video-editors-with-caption-features) (vendor; plan detail from a secondary source)
- Brand template holds:
  - caption style
  - logo/CTA
  - intro/outro
  - AI emojis
  - auto transitions
  - aspect ratio
  - a vocabulary list for proper nouns

  — [help.opus.pro](https://help.opus.pro/docs/article/how-to-add-a-brand-template.md) / secondary review
- Filler-word ("um/uh"), pause and dead-air removal shows candidates before removing them. AI B-roll is either stock or AI-generated, triggered by selecting transcript text. — [opus.pro editor/tools](https://opus.pro/tools/automatically-edit-out-ums-in-video)
- Submagic:
  - auto contextual B-roll (Storyblocks, transcript-matched)
  - silence removal
  - AI hook titles
  - captions in 48 languages
  - zooms, SFX, transitions
  - Magic Clips is a paid add-on with no virality score

  — [submagic.co](https://www.submagic.co/features/magic-clips) / [submagic vs opus](https://www.submagic.co/alternatives/opus-clip)
- Captions (Mirage) AI Edit: auto cuts, zooms, B-roll, generated music/SFX, eye-contact fix, 100+ subtitle languages. — [captions.ai](https://www.captions.ai/)
- Vizard: AI captions, AI emoji, AI B-roll, 100+ caption languages, "Vizard Agent". — [vizard.ai](https://vizard.ai/)
- Captions are reported to contain errors that are hard to fix in the OpusClip editor. — [eesel.ai](https://www.eesel.ai/blog/opusclip-reviews)

### Gaps
- No vendor documents how keyword highlights are chosen (likely an LLM pick of nouns/numbers).
- No evidence B-roll improves retention for our genre (MrBeast-style footage is already visual-heavy).

## 4. Publishing and analytics

### Takeaway
OpusClip's scheduler plus AI copy is Pro-gated, and users report it as unreliable. Our manual posting kit covers the copy side.

### Cited Findings
- Auto-posting targets YouTube/Shorts, IG Reels, TikTok, FB Pages, LinkedIn and X. AI titles, descriptions and hashtags. "1-click posting and analytics". Clip Analytics and real-time trend analysis on higher tiers. — [opus.pro/calendar](https://www.opus.pro/calendar), [opus.pro/pricing](https://opus.pro/pricing)
- The scheduler is Pro-only. Reports say it drops connections and fails silently, with TikTok worst. — [frankx.ai](https://frankx.ai/blog/ultimate-opus-clip-workflow-2026), [autoclip.dev](https://autoclip.dev/compare/autoclip-vs-opus-clip) (competitor), [eesel](https://www.eesel.ai/blog/opusclip-reviews)
- Klap schedules to TikTok, YouTube, IG, LinkedIn and FB. — [klap.app](https://klap.app/)

### Gaps
- No evidence that OpusClip's analytics feeds back into clip selection (a closed loop). It appears to be reporting only.

## 5. What matters vs gimmicks

### Takeaway
Users value speed, active-speaker reframing and hook titles. They distrust the virality score, auto clip selection and the scheduler.

### Cited Findings
- Praised: speed and ideas ("pretty good at giving me ideas"), and reframing on simple setups. — [eesel.ai](https://www.eesel.ai/blog/opusclip-reviews)
- Praised (unverified quotes): "Active speaker tracking actually works", "hook titles are surprisingly good". — search summary of a review mirror; low confidence
- Complaints:
  - context loss
  - an unreliable score
  - caption errors
  - a clunky editor
  - credit burn (1 credit = 1 min of source)
  - billing/cancellation issues on Trustpilot

  — [eesel.ai](https://www.eesel.ai/blog/opusclip-reviews)
- Output quality depends mostly on input quality. — [fritz.ai](https://fritz.ai/opusclip-ai-review/), [stateshift](https://blog.stateshift.com/?p=3969)

### Inferences
- **Matters:** hook text, animated captions, tight length (~30–45 s), good reframing, human-checked selection.
- **Gimmicky for us:** the numeric virality score as a decider, AI-generated B-roll, eye-contact fix, and auto-scheduling (fragile, and our CLAUDE.md forbids posting without asking anyway).

## 6. Pricing (what we're replacing)

### Cited Findings
- **OpusClip:** Free 60 credits/min/mo, watermarked, exports expire in 3 days. Starter $15/mo, 150 credits, no scheduler. Pro $29/mo ($14.50 annual), 300/mo, scheduler, 2 seats. Business custom. — [castmagic](https://www.castmagic.io/blog/opus-clip-pricing), [eesel](https://eesel.ai/blog/opusclip-pricing). Toolradar's Pro figure (400 min) conflicts.
- **Klap:** $29 / $79 / $189 per month monthly ($14.50 / $39.50 / $94.50 annual) for 100 / 300 / 1,000 clips. — [klap.app](https://klap.app/)
- **Submagic:** from $19/mo ($12 annual), Magic Clips add-on +$19/mo. — [revid.ai](https://www.revid.ai/blog/submagic-alternatives), [submagic.co](https://www.submagic.co/alternatives/opus-clip)
- **Captions:** Pro $9.99, Max $24.99. — [aivideocut](https://www.aivideocut.com/blog/best-captions-ai-alternatives)
- **Vizard:** sources conflict ($14.50–$29/user). — [aitoolsatlas](https://aitoolsatlas.ai/tools/vizard/vs)
- **Riverside Magic Clips:** described as free inside Riverside plans (Pro €24). — [riverside.com](https://riverside.com/magic-clips)

### Gaps
- No reliable current pricing for Munch or 2short.ai. Their feature detail is thin and comes from competitor pages: Munch "trend-aware" selection ([submagic.co](https://www.submagic.co/alternatives/the-best-alternative-to-get-munch)); 2short has auto moments, aspect ratios and animated subs ([invideo](https://invideo.io/blog/opusclip-alternatives-for-editing-long-videos-into-shorts/)).

## Ranked: features to replicate locally (open tools)

1. **LLM moment scorer (Hook/Flow/Value/Trend + payoff/emotion), human final pick.**
   - Feed the WhisperX word transcript in ~60–90 s windows to an LLM with our rubric. Output JSON with start/end, the 4 sub-scores, payoff timestamp and a one-line why.
   - Add audio-event boosts: laughter/cheer peaks via PANNs or YAMNet, plus loudness spikes from ffmpeg `ebur128`.
   - Rule: the clip must contain its setup sentence and end after the reaction. This fixes OpusClip's #1 complaint.
2. **Genre prompt presets.** A small JSON of per-genre "find" prompts, like Opus Hands-Free (e.g. stunt/challenge: reveal, fail, money, last-to-leave).
3. **Auto headline / hook generator.** The LLM writes 5 hook variants of ≤6 words, picks a yellow keyword, and leads with the outcome. Outcome hooks beat story-setup hooks per [Opus data](https://www.opus.pro/blog/anatomy-of-a-viral-tiktok-2026).
4. **Active-speaker reframe + layout rules.**
   - MediaPipe/YOLO face boxes every 0.5 s, plus a mouth-motion active-speaker signal or pyannote diarization mapped to faces.
   - Smoothed crop path driven through ffmpeg.
   - Auto Split when 2 faces are in frame and both speak within 5 s.
   - Gameplay/screen layout = stacked crops.
5. **Filler/silence tightening.**
   - Whisper word gaps over 0.35 s plus the um/uh list produce cut points. Alternatives: ffmpeg `silencedetect`, or auto-editor (open source).
   - Show the cut list before applying, as Opus does.
6. **Keyword + emoji highlight in captions.** The LLM tags 1–2 words per line (numbers, money, names) and an optional emoji. This fits into our existing word-caption renderer.
7. **Proper-noun vocabulary list.** Pass Whisper `initial_prompt`, or run a post-correction dictionary (names, brands).
8. **Posting copy + hashtags.** Already have it. Add the mixed niche + broad hashtag mix and a ~30–45 s length target per the [Opus data](https://www.opus.pro/blog/anatomy-of-a-viral-tiktok-2026) (vendor and correlational).
9. **Translation (optional).** Whisper translate or an LLM for caption tracks in ES/PT/HI. Only matters if multi-language channels are planned.
10. **Skip / low priority:** a numeric virality score as a decider, AI-generated B-roll, eye-contact fix, and auto-scheduler (fragile per reviews; posting needs user approval anyway).
