"""Build every posting file from one compact copy.json (saves writing long markdown by hand).

usage: python kit.py <recipe_dir> <ready_dir>
recipe_dir/copy.json:
{ "video": {"title": "...", "creator": "MrBeast", "handle": "@mrbeast", "id": "abc123"},
  "order": [3,1,2,5,4],                       # posting order (clip numbers)
  "clips": [ { "key": "c1_slug", "file": "01_Name", "titles": ["t1","t2","t3"],
               "story": "1-2 lines", "question": "debate question?", "pinned": "pinned comment",
               "hashtags": ["#shorts","#mrbeast", ... 12-15 total], "tags": "tag1, tag2, ...",   # YouTube: max 15 (more = YouTube ignores ALL); first 3 show above the title
               "ig_hook": "≤125 chars", "ig_prompt": "Send this to …", "ig_hashtags": ["#a","#b","#c","#d","#e"],
               "alt": "keywords sentence" } ] }
Writes: YOUTUBE_CAPTIONS.md, INSTAGRAM_CAPTIONS.md (IG caption + separate Facebook caption), TIKTOK_X_SNAP_CAPTIONS.md, schedule.csv
Hashtag counts: YouTube / TikTok / Facebook 12-15 (hashtags + ig_hashtags merged, deduped, capped 15); Instagram 5 (platform cap); X 2; Snapchat 2.
SFX credits are added automatically when spec.json uses the cash-register sound in that clip.
"""
import csv, datetime, json, os, subprocess, sys

R, OUT = sys.argv[1], sys.argv[2]
C = json.load(open(os.path.join(R, "copy.json"), encoding="utf-8"))
spec = json.load(open(os.path.join(R, "spec.json"), encoding="utf-8")) if os.path.exists(os.path.join(R, "spec.json")) else {}
V = C["video"]
CASH = '"Cash Register" by GowlerMusic (freesound.org/s/360453), CC BY 4.0'
SAFE = "Copyright: this is {c}'s footage. Posting outside {c}'s official clipping program can get a clip claimed or demonetized."


def dur(clip):
    f = os.path.join(OUT, "clips", clip["file"] + ".mp4")
    if not os.path.exists(f):
        return "?"
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True)
    return f"{float(r.stdout or 0):.0f} s"


def cash(clip):
    b = spec.get(clip["key"], {}).get("beats", [])
    return any(len(x) > 3 and x[3] == "cash" for x in b)


def fence(t):
    return f"```\n{t}\n```"


def big(c):
    out = []
    for h in c["hashtags"] + c["ig_hashtags"]:
        if h.lower() not in [x.lower() for x in out]: out.append(h)
    return out[:15]


order = C.get("order") or list(range(1, len(C["clips"]) + 1))
ordtxt = " → ".join(f"{n:02d}" for n in order)
yt = [f"# YouTube Shorts posting kit: {V['title']}", f"Source: {V['creator']}, **\"{V['title']}\"** (`{V.get('id','')}`)",
      "", "Each clip: `clips/` video · `thumbnails/` 9:16 cover + 16:9 · 3 titles · description · tags · pinned comment.",
      f"\n**Posting order (one per day):** {ordtxt}", "", "---"]
ig = [f"# Instagram + Facebook Reels kit: {V['title']}",
      "- Post with **Create reel** in Meta Business Suite, tick Facebook + Instagram, then *Customize for each platform*: Instagram caption (5 hashtags, the Instagram cap) and Facebook caption (12–15). Cover = `thumbnails/…__Shorts_cover_9x16.jpg`.",
      "- Paste caption; alt text in Advanced settings. Optional: Trial Reel first.", f"- **Order:** {ordtxt}", "", "---"]
tx = [f"# TikTok · X · Snapchat captions: {V['title']}", "TikTok: upload the same file, cover = 9:16 thumbnail, add caption. X: ≤280 chars. Snapchat Spotlight: short caption + 1–3 #topics.", "", "---"]
rows = []
for i, c in enumerate(C["clips"], 1):
    credit_yt = f"🎥 Clip from {V['creator']}'s \"{V['title']}\": watch the full video on their channel."
    credit_ig = f"🎥 {V['handle']}, \"{V['title']}\""
    sfx_yt = f"\n🔊 Sound: {CASH}" if cash(c) else ""
    sfx_ig = '\n🔊 "Cash Register" by GowlerMusic (CC BY 4.0)' if cash(c) else ""
    d = dur(c)
    yt += [f"\n## {i:02d}: {c['titles'][0]}", f"Video: `clips/{c['file']}.mp4` ({d}) · Thumbs: `thumbnails/{c['file']}__…`",
           "**Titles**", *[fence(t) for t in c["titles"]], "**Description**",
           fence(f"{c['story']}\n\n{c['question']}\n\n{credit_yt}{sfx_yt}\n\n{' '.join(c['hashtags'][:15])}"),
           "**Pinned comment**", fence(c["pinned"]), "**Tags**", fence(c["tags"]), "", "---"]
    ig += [f"\n## {i:02d}: {c['titles'][0]}",
           fence(f"{c['ig_hook']}\n\n{c['story']}\n\n{c['question']}\n{c.get('ig_prompt','')}\n\n{credit_ig}{sfx_ig}\n\n{' '.join(c['ig_hashtags'][:5])}"),
           f"**Alt text:** `{c['alt']}`", "**Facebook caption** (in Create reel, tick *Customize for each platform*)",
           fence(f"{c['ig_hook']}\n\n{c['story']}\n\n{c['question']}\n{c.get('ig_prompt','')}\n\n{credit_ig}{sfx_ig}\n\n{' '.join(big(c))}"), "", "---"]
    xt = f"{c['ig_hook']} {' '.join(c['ig_hashtags'][:2])}"
    tx += [f"\n## {i:02d}: {c['titles'][0]}", "**TikTok**",
           fence(f"{c['ig_hook']}\n{c['question']}\n{credit_ig}{sfx_ig}\n{' '.join(big(c))}"),
           "**X**", fence(xt[:280]), "**Snapchat**", fence(f"{c['titles'][0]} {' '.join(h for h in c['ig_hashtags'][:2])}"), "", "---"]
    rows.append({"clip": f"{i:02d}", "file": f"clips/{c['file']}.mp4", "title": c["titles"][0],
                 "cover": f"thumbnails/{c['file']}__Shorts_cover_9x16.jpg"})
camp = C.get("campaign")  # optional: {"name","url","tags":["@brand","#tag"],"disclosure":"#ad","rules":["…"]}
if camp:
    chk = [f"\n## Campaign compliance: {camp['name']} ({camp.get('url','')})",
           f"- [ ] Disclosure **at the start** of every caption: `{camp.get('disclosure','#ad')}`",
           f"- [ ] Required tags/handles in every post: `{' '.join(camp.get('tags', []))}`",
           "- [ ] Unique edit per campaign (never resubmit the same file to another campaign)",
           "- [ ] Post from the verified, connected account, then submit the link within 30 min; screenshot the analytics",
           *[f"- [ ] {r}" for r in camp.get("rules", [])]]
    yt += chk; ig += chk; tx += chk
SRC = json.load(open(os.path.join(R, "source.json"), encoding="utf-8")) if os.path.exists(os.path.join(R, "source.json")) else {}
RIGHTS = SRC.get("rights", "unlicensed")
ok = RIGHTS.split(":")[0] in ("campaign", "permission", "open")
rk = [f"\n## Rights: `{RIGHTS}`",
      "- Licensed: post, then submit the links to the campaign within its deadline. Keep the proof (campaign page or written permission) in `source.json`." if ok else
      f"- **Unlicensed.** {V['creator']}'s Content ID will match this footage: expect claims (revenue goes to them) or blocks. Before posting, look for an active campaign for this video (Vyro, Whop Content Rewards) and re-run `clip.py new … --rights campaign:<url>`.",
      "- If a clip is **claimed or blocked**: open YouTube Studio → Content → *Copyright*, see who claimed it. Music claim → use Studio's *Erase song* or *Trim*. Footage claim by the creator → accept it (no strike); don't dispute without a license (false disputes can turn into strikes). Remove blocked clips from the schedule.",
      "- Never re-upload a blocked clip with tricks (mirroring, pitch, zoom, cropping out watermarks): that is evasion and risks strikes and channel termination."]
yt += rk; ig += rk; tx += rk
yt += ["", f"**Upload settings:** not made for kids · Entertainment · pin your comment right after posting.", SAFE.format(c=V["creator"])]
for name, lines in (("YOUTUBE_CAPTIONS.md", yt), ("INSTAGRAM_CAPTIONS.md", ig), ("TIKTOK_X_SNAP_CAPTIONS.md", tx)):
    open(os.path.join(OUT, name), "w", encoding="utf-8").write("\n".join(lines) + "\n")
start = datetime.date.today() + datetime.timedelta(days=1)
with open(os.path.join(OUT, "schedule.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["date", "time", "clip", "file", "cover", "title", "platforms"])
    w.writeheader()
    for day, n in enumerate(order):
        r = rows[n - 1]
        w.writerow({"date": str(start + datetime.timedelta(days=day)), "time": "18:00", **r,
                    "platforms": "YouTube; Instagram+Facebook; TikTok; X; Snapchat"})
# title check: short, open loop, max 1 emoji, never repeat the thumbnail words (thumb + title must add different info)
import re as _re
TH = json.load(open(os.path.join(R, "thumbs.json"), encoding="utf-8")) if os.path.exists(os.path.join(R, "thumbs.json")) else []
EMO = _re.compile("[🌀-🫿☀-➿]")
warn = []
for i, c in enumerate(C["clips"]):
    th = TH[i] if i < len(TH) else {}
    words = {w for k in ("l1", "l2") for w in _re.findall(r"[A-Z0-9$,']{4,}", th.get(k, "").upper())}
    for j, t in enumerate(c["titles"]):
        n = len(EMO.sub("", t).strip())
        if n > (50 if j == 0 else 60): warn.append(f"{i+1:02d}.{j+1} too long ({n} chars)")
        if len(EMO.findall(t)) > 1: warn.append(f"{i+1:02d}.{j+1} more than 1 emoji")
        if sum(1 for w in t.split() if len(w) > 3 and w.isupper()) > 1: warn.append(f"{i+1:02d}.{j+1} shouting (caps words)")
    if th and len(words & set(_re.findall(r"[A-Z0-9$,']{4,}", c["titles"][0].upper()))) >= 2:
        warn.append(f"{i+1:02d} thumbnail text repeats title 1: make the thumbnail add new info")
    if len(c["hashtags"]) > 15: warn.append(f"{i+1:02d} YouTube hashtags >15 (YouTube would ignore all)")
    if len(big(c)) < 12: warn.append(f"{i+1:02d} only {len(big(c))} hashtags for YT/TikTok/FB (aim 12-15)")
    if len({t.split()[0].lower() for t in c["titles"]}) < 3: warn.append(f"{i+1:02d} titles start the same way: use 3 different formulas")
print("kit written:", OUT); print("copy check:", "OK" if not warn else "; ".join(warn))
print("rights:", RIGHTS, "" if ok else "-> WARN unlicensed: expect Content ID claims/blocks; find a campaign or permission before posting")
