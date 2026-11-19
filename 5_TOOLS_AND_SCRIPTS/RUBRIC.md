# Clip-picking rubric (stage 2 after `candidates.py`)

Read only `candidates.txt` (top 15). For each candidate, score 1–5:

| Factor | 5 = |
|---|---|
| **Hook** | the first 2 s can show the outcome, the stakes or a shocked face |
| **Flow** | setup sentence AND reaction both inside the window; no "as I said earlier" |
| **Value** | money, danger, a reveal, a twist, an emotion, or a fact people repeat |
| **Payoff** | a clear peak you can cold-open on, then cut ≤1 s after the reaction |
| **Trend** | topic or person people search or argue about right now |

Rules:
- Total ≥ 18/25 to keep. Drop any with SPONSOR or a missing setup. Drop overlaps > 50 %.
- Rerank the survivors head to head (best first). Keep 5 (or what the user asked for).
- Target 30–45 s (max 58). Extend the window to include the setup line, and trim filler.
- Confirm visual payoffs with one contact sheet (`clip.py sheet`) before writing `edits.json`.

Genre presets (what wins):
- **Challenge / MrBeast:** money reveal, elimination, stunt fail, emotional giveaway, bet loophole.
- **Podcast / interview:** contrarian claim, story with a punchline, a heated disagreement, an "I've never said this" confession.
- **Gaming:** clutch play, rage or fail, a glitch or easter egg, "you can do THIS?!" discovery, a funny NPC. Use gameplay full-frame and the facecam on top if present.
- **Sports:** last-second play, an unbelievable stat, a fight or celebration, a post-game quote.
- **Tech / science:** "this shouldn't be possible" demo, a price reveal, before/after, a world-first.

Hook lines: ≤6 words, outcome first, one yellow keyword. Write 3 variants per clip (they go to `copy.json` titles).

## Titles (3 per clip, 3 different formulas; `kit.py` checks them)
1. **Hook + open loop** (title 1 must match the on-screen hook, ≤50 chars): "One Jump for $5 Million… Did He Make It?"
2. **Quote**: the most charged real line, in quotes: "\"Sit Down and Lose… or Take the Risk?\""
3. **Curiosity / why / number**: "Why Strong Team Lost 30% in One Second", "10 Seconds to Throw… Then This Happened"
- Front-load the number or the stakes; use specific numbers ($5,000,000, 30%, 7:44); at most 1 emoji, at the end; no ALL-CAPS words; never reveal the outcome; never invent facts.

## Thumbnails (`thumbs.json`, `thumbs.py` v2): a different style for every clip of a video
| Payoff type | Style |
|---|---|
| money or stat | `bignum` (giant number, subject cut-out in front) |
| one person's big moment or emotion | `sticker` (giant word behind the cut-out subject) |
| rivals, teams, A vs B | `vs` (diagonal split) |
| a detail to look at (object, mistake) | `callout` (red ring + arrow, `at` [x%,y%]) |
| cliffhanger or hidden outcome | `reveal` (blurred "?" spot + reaction cut-out) |
| serious or dramatic | `cinema` (letterbox, thin type) |
| before/after, return/exit | `stack` (two cards + arrow) |
- Thumbnail text is 1–4 words that ADD info to the title (never repeat it). Image + thumbnail text + title = 3 different pieces of the story.
- Cut-outs: `"cut":"tN_x.jpg"` (people: default model; objects: `"cutm":"isnet-general-use"`). Pick frames with a clear face/pose and a clean background.
- Rotate palettes (`yellow red cyan green pink orange`) so the channel grid looks varied; match colour to emotion (green money, red danger, cyan wow, pink drama).

## Rights (check before clipping: blocked clips earn nothing)
| `--rights` | Means | Post? |
|---|---|---|
| `campaign:<url>` | An active Vyro / Whop Content Rewards campaign lists **this exact video** | Yes, then submit links |
| `permission:<proof>` | Written OK from the creator (email/DM screenshot saved) | Yes |
| `open:<policy url>` | The creator publicly allows clipping (stated policy) | Yes, follow their rules |
| `unlicensed` (default) | None of the above | Expect claims/blocks: prefer finding a campaign or another video |
- Order of choice for the next video: 1) a live campaign with budget left, 2) a creator who allows clipping, 3) unlicensed only as a portfolio test.
- Claimed or blocked: check *who* claimed in YouTube Studio → Copyright. Music → *Erase song* / *Trim*. Creator's footage → accept (no strike), drop it from the schedule. Dispute only with a license.
- Never: mirror/flip, pitch-shift, zoom-crop or remove watermarks to dodge matching, or re-upload a blocked clip. That's evasion and leads to strikes and termination.
- Keep clips ≤58 s, add our own hook, captions, graphics and structure (originality for IG/TikTok reach), credit the creator.
