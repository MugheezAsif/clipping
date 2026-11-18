"""Build an edited 9:16 plate per clip (blurred fill + footage panel), plus remapped word timings."""
import json, os, re, subprocess, sys

SCR = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]
OUTROOT = sys.argv[2]           # folder that will hold one project per clip
only = set(sys.argv[3:])
RECIPE = os.environ.get("CLIP_RECIPE", SCR)   # folder holding edits.json + words.json for one source video
EDITS = json.load(open(os.path.join(RECIPE, "edits.json"), encoding="utf-8"))
WORDS = json.load(open(os.path.join(RECIPE, "words.json"), encoding="utf-8"))
JUNK = re.compile(r"\[[^\]]*\]|>>")

SET = json.load(open(os.path.join(RECIPE, "settings.json"))) if os.path.exists(os.path.join(RECIPE, "settings.json")) else {}
LAYOUT = SET.get("layout", "panel")      # "panel" (old look), "auto" (face crop per shot when safe), "face"
TIGHTEN = SET.get("tighten", False)      # drop pauses > ~0.6 s between words (podcasts/streams)
VENV_PY = os.path.expanduser("~/.clipping/env/Scripts/python.exe")


def face_vf(cx, w=1920, h=1080):
    cw = int(h * 9 / 16) // 2 * 2
    x = int(min(max(cx * w - cw / 2, 0), w - cw))
    return f"crop={cw}:{h}:{x}:0,scale=1080:1920:flags=lanczos,eq=contrast=1.06:saturation=1.12,unsharp=5:5:0.6,format=yuv420p"


def tighten(a, b):
    ws = [ms / 1000 for ms, _ in WORDS if a <= ms / 1000 < b]
    out, s = [], a
    for x, y in zip(ws, ws[1:]):
        if y - x > 1.3:           # long gap after a word: keep ~0.6 s of it, cut the rest
            out.append([s, x + 0.6]); s = y - 0.08
    out.append([s, b])
    return [p for p in out if p[1] - p[0] > 0.25]


VF = ("split[a][b];"
      "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.22:saturation=1.2[bg];"
      "[b]crop=960:1080,scale=1080:1215,eq=contrast=1.06:saturation=1.12[fg];"
      "[bg][fg]overlay=0:300,format=yuv420p")
# "wide": whole 16:9 frame (for scoreboards, maps, on-screen text) letterboxed over the blurred fill
VF_WIDE = ("split[a][b];"
           "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.22:saturation=1.2[bg];"
           "[b]scale=1080:608,eq=contrast=1.06:saturation=1.12[fg];"
           "[bg][fg]overlay=0:470,format=yuv420p")

for name, segs in EDITS.items():
    if only and name not in only:
        continue
    proj = os.path.join(OUTROOT, name)
    tmp = os.path.join(proj, ".seg")
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(os.path.join(proj, "assets"), exist_ok=True)
    lst = []
    words, cuts, t = [], [], 0.0
    force = [f[0] if f else None for _, _, *f in segs]  # optional 3rd item per segment: "panel" | "wide" | "face"
    segs = [[x[0], x[1], fz] for (a, b, *_), fz in zip(segs, force) for x in (tighten(a, b) if TIGHTEN else [[a, b]])]
    shots = [[[a, b, fz or "panel", None]] for a, b, fz in segs]
    auto = [i for i, (_, _, fz) in enumerate(segs) if fz is None]
    if LAYOUT != "panel" and auto and os.path.exists(VENV_PY):
        r = subprocess.run([VENV_PY, os.path.join(SCR, "reframe.py"), SRC, json.dumps([segs[i][:2] for i in auto])], capture_output=True, text=True)
        if r.returncode == 0:
            for i, grp in zip(auto, json.loads(r.stdout.strip().splitlines()[-1])):
                shots[i] = grp
    flat = [sh for grp in shots for sh in grp]
    starts = {round(grp[0][0], 3) for grp in shots}
    for i, (a, b, lay, cx) in enumerate(flat):
        d = b - a
        vf = VF_WIDE if lay == "wide" else face_vf(cx) if (lay == "face" and cx is not None) else VF
        f = os.path.join(tmp, f"s{i:02d}.mp4")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", SRC,
                        "-vf", vf, "-af", f"afade=t=in:d=0.03,afade=t=out:st={d-0.04:.3f}:d=0.04",
                        "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-g", "30",
                        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", f.replace(".mp4", ".mov")], check=True)
        lst.append(f"file '{f.replace('.mp4', '.mov').replace(os.sep, '/')}'")
        for ms, w in WORDS:
            s = ms / 1000
            if a - 0.02 <= s < b - 0.05:
                for piece in JUNK.sub("", w).split():
                    words.append({"text": piece, "start": round(t + s - a, 3), "src": round(s, 2)})
        if i and round(a, 3) in starts:   # only real edit points get punch-ins/whooshes
            cuts.append(round(t, 3))
        t += d
    open(os.path.join(tmp, "list.txt"), "w").write("\n".join(lst))
    plate = os.path.join(proj, "assets", "plate.mp4")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "list.txt"),
                    "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-g", "30", "-r", "30",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", plate], check=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", plate],
                               capture_output=True, text=True).stdout)
    for i, w in enumerate(words):
        nxt = words[i + 1]["start"] if i + 1 < len(words) else dur
        w["end"] = round(min(nxt, w["start"] + 0.8), 3)
        w["id"] = f"w{i}"
    json.dump({"duration": dur, "cuts": cuts, "words": words}, open(os.path.join(proj, "edit.json"), "w"), indent=1)
    nf = sum(1 for x in flat if x[2] == "face")
    print(name, f"{dur:.2f}s", len(words), "words", len(cuts), "cuts", f"{nf}/{len(flat)} shots face-crop")
