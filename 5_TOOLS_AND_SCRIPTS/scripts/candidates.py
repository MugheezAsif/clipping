"""Rank clip candidates from a word-timed transcript so the editor (or Claude) reads ~2k tokens, not the whole transcript.

usage: python candidates.py words.json [--video source.mp4] [--top 15] [--min 20] [--max 58]
words.json = [[ms, "word"], ...]  (tx.py output or any ASR converted to that shape)
Prints compact lines: rank, start-end, score, why, preview. Optional --video adds audio-loudness peaks.
"""
import argparse, json, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("words"); ap.add_argument("--video"); ap.add_argument("--top", type=int, default=15)
ap.add_argument("--min", type=float, default=20); ap.add_argument("--max", type=float, default=58)
a = ap.parse_args()

W = [(t / 1000, w) for t, w in json.load(open(a.words, encoding="utf-8"))]
if not W:
    sys.exit("no words")

LEX = {
    "money": r"^\$|\d{1,3}(,\d{3})+|million|billion|thousand|grand|\bk\b",
    "superlative": r"^(biggest|largest|craziest|most|best|worst|first|last|only|never|ever|tallest|fastest|world|insane|impossible)",
    "reaction": r"^(wow|whoa|woah|omg|what|wait|no|yes|dude|bro|insane|crazy|scary|terrifying|unbelievable|oh)",
    "stakes": r"^(win|won|lose|lost|die|dead|danger|fail|eliminat|challenge|bet|risk|prize|money|car|house)",
    "tag": r"\[(laughter|screaming|cheering|applause|music)\]",
}
SPONSOR = r"(sponsor|use code|promo|link in (the )?description|download (the )?app|sign up|scan (this|the) code|limited time|available at|retailers)"

# sentence ends -> candidate start points
starts = [0] + [i + 1 for i, (_, w) in enumerate(W[:-1]) if re.search(r"[.!?]$|>>", w)]
loud = {}
if a.video:  # per-second loudness via ffmpeg ebur128 momentary (cheap, one pass)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", a.video, "-vn", "-af", "ebur128=peak=none", "-f", "null", "-"],
                       capture_output=True, text=True, errors="ignore")
    for m in re.finditer(r"t:\s*([\d.]+)\s+TARGET.*?M:\s*(-?[\d.]+)", r.stderr):
        loud[int(float(m.group(1)))] = max(loud.get(int(float(m.group(1))), -99), float(m.group(2)))
    if loud:
        vals = sorted(loud.values()); p90 = vals[int(len(vals) * 0.9)]

def score(i0, i1):
    seg = W[i0:i1]; t0, t1 = seg[0][0], seg[-1][0]
    text = " ".join(w for _, w in seg)
    why, s = {}, 0.0
    for k, rx in LEX.items():
        n = sum(1 for _, w in seg if re.search(rx, w.lower().strip(".,!?\"'")) or (k == "tag" and re.search(rx, w.lower())))
        if n:
            why[k] = n
    s += 2.0 * why.get("money", 0) + 1.2 * why.get("superlative", 0) + 0.8 * why.get("reaction", 0) + 1.0 * why.get("stakes", 0) + 1.5 * why.get("tag", 0)
    caps = sum(1 for _, w in seg if len(w) > 2 and w.isupper()); s += 0.6 * caps; why["caps"] = caps or None
    turns = text.count(">>"); s += 0.4 * turns
    if re.search(SPONSOR, text.lower()):
        s -= 25; why["SPONSOR"] = 1
    if loud:
        hot = sum(1 for sec in range(int(t0), int(t1) + 1) if loud.get(sec, -99) >= p90); s += 0.8 * hot; why["loud_s"] = hot or None
    dur = t1 - t0
    s = s / max(dur, 1) * 30  # normalise to per-30s density
    # payoff = densest 4 s (best cold-open point)
    best, bt = -1, t0
    for _, (tt, _) in enumerate(seg):
        n = sum(1 for t, w in seg if tt <= t < tt + 4 and (w.isupper() or re.search(LEX["reaction"] + "|" + LEX["money"] + "|" + LEX["tag"], w.lower())))
        if n > best:
            best, bt = n, tt
    return s, {k: v for k, v in why.items() if v}, bt

cands = []
for si, i0 in enumerate(starts):
    t0 = W[i0][0] if i0 < len(W) else None
    if t0 is None:
        continue
    for i1 in range(i0 + 1, len(W)):
        d = W[i1][0] - t0
        if d < a.min:
            continue
        if d > a.max:
            break
        if re.search(r"[.!?]$", W[i1][1]) or i1 == len(W) - 1:
            sc, why, peak = score(i0, i1 + 1)
            cands.append((sc, t0, W[i1][0] + 0.6, why, peak, i0, i1))

cands.sort(key=lambda c: -c[0])
picked = []
for c in cands:
    if all(c[2] <= p[1] or c[1] >= p[2] for p in picked):
        picked.append(c)
    if len(picked) >= a.top:
        break

fmt = lambda s: f"{int(s // 60)}:{s % 60:04.1f}"
print(f"# {len(W)} words, {fmt(W[-1][0])} long. Top {len(picked)} non-overlapping candidates (score = hype density per 30 s)")
for r, (sc, t0, t1, why, peak, i0, i1) in enumerate(picked, 1):
    words = [w for _, w in W[i0:i1 + 1]]
    prev = " ".join(words[:22]) + (" … " + " ".join(words[-14:]) if len(words) > 36 else " " + " ".join(words[22:]))
    tags = ",".join(f"{k}{'' if v == 1 else v}" for k, v in why.items())
    print(f"{r:>2}. {t0:.1f}-{t1:.1f} ({fmt(t0)}, {t1 - t0:.0f}s) score {sc:.1f} | peak {peak:.1f} | {tags}\n    {prev}")
