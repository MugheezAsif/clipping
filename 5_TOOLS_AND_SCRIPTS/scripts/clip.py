"""One-command clipping pipeline. Every stage prints only a few lines (token-efficient).

  python clip.py new <url> <NN_Name> [--rights campaign:<url>|permission:<proof>|open:<policy url>] [--cookies cookies.txt]
                                                                download + captions/ASR + ranked candidates (rights default: unlicensed)
  python clip.py sheet <NN_Name> <t:dur> [...]                  1 contact sheet of source moments (check visual payoffs)
  python clip.py build <NN_Name>                                plates (auto reframe) + graphics + check + 1 snapshot sheet
  python clip.py render <NN_Name>                               render every clip to 1_READY_TO_POST/NN_Name/clips (slow: run in background)
  python clip.py frames <NN_Name> t1_bg:12.3 t1_in:40 ...       grab graded thumbnail frames
  python clip.py thumbs <NN_Name>                               build + export 9:16 and 16:9 thumbnails
  python clip.py kit <NN_Name>                                  posting files (YT, IG/FB, TikTok/X/Snap, schedule.csv) + export guard
Recipe files you write: edits.json, spec.json, names.json {"c1_slug": "01_File_Name"}, thumbs.json, copy.json
"""
import glob, json, os, re, shutil, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCR = os.path.join(ROOT, "5_TOOLS_AND_SCRIPTS", "scripts")
CACHE = os.path.expanduser("~/.clipping/cache")
VENV_PY = os.path.expanduser("~/.clipping/env/Scripts/python.exe")
SFX = os.path.join(ROOT, "5_TOOLS_AND_SCRIPTS", "hyperframes_starter_with_sound_effects")
GRADE = "eq=saturation=1.35:contrast=1.12:brightness=0.02,unsharp=5:5:0.8"


def paths(nn):
    rec = os.path.join(ROOT, "5_TOOLS_AND_SCRIPTS", "recipes", nn.lower())
    return rec, os.path.join(ROOT, "4_EDITABLE_PROJECTS", nn), os.path.join(ROOT, "1_READY_TO_POST", nn)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, errors="ignore", **kw)


def source(rec):
    return json.load(open(os.path.join(rec, "source.json")))["video"]


def py(script, *args, env=None):
    e = dict(os.environ, PYTHONIOENCODING="utf-8", **(env or {}))
    r = run([sys.executable, "-I", os.path.join(SCR, script), *args], env=e)
    if r.returncode:
        sys.exit(f"{script} failed:\n{r.stderr[-1500:]}")
    return r.stdout


def sheet(video, items, out, w=240):
    tiles = []
    for i, it in enumerate(items):
        t, d = (it.split(":") + ["6"])[:2]
        f = out + f".{i}.png"
        run(["ffmpeg", "-y", "-ss", t, "-t", d, "-i", video, "-vf", f"fps={6 / float(d)},scale={w}:{w * 9 // 16},tile=6x1", "-frames:v", "1", f])
        tiles.append(f)
    run(["ffmpeg", "-y", *sum([["-i", f] for f in tiles], []), "-filter_complex", f"vstack=inputs={len(tiles)}" if len(tiles) > 1 else "null", out])
    for f in tiles:
        os.remove(f)
    return out


def cmd_new(url, nn, *rest):
    rec, _, _ = paths(nn); os.makedirs(rec, exist_ok=True)
    vid = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", url).group(1)
    c = os.path.join(CACHE, vid); os.makedirs(c, exist_ok=True)
    ck = ["--cookies", rest[rest.index("--cookies") + 1]] if "--cookies" in rest else []
    base = [sys.executable, "-m", "yt_dlp", "--js-runtimes", "node", *ck, "-P", c, url]
    meta = run(base[:-1] + ["--skip-download", "--write-auto-subs", "--write-subs", "--sub-langs", "en-orig,en", "--sub-format", "json3",
                            "--no-simulate", "--print", "%(title)s|%(channel)s|%(duration)s", "-o", "src.%(ext)s", url])
    if meta.returncode:
        sys.exit("download failed: " + meta.stderr.strip().splitlines()[-1][:300] + "\n(age-restricted? pass --cookies cookies.txt)")
    title, channel, dur = meta.stdout.strip().splitlines()[-1].rsplit("|", 2)
    video = os.path.join(c, "video.mp4")
    if not os.path.exists(video):
        run(base[:-1] + ["-f", "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080]", "--merge-output-format", "mp4", "-o", "video.%(ext)s", url])
    # rights gate: campaign:<url> | permission:<proof> | open:<policy url> | unlicensed (see RUBRIC: Rights)
    rights = rest[rest.index("--rights") + 1] if "--rights" in rest else "unlicensed"
    json.dump({"url": url, "id": vid, "title": title, "channel": channel, "video": video, "rights": rights},
              open(os.path.join(rec, "source.json"), "w"), indent=1)
    words = os.path.join(rec, "words.json")
    subs = sorted(glob.glob(os.path.join(c, "*.en-orig.json3")) + glob.glob(os.path.join(c, "*.en.json3")))
    if subs:
        run([sys.executable, "-I", os.path.join(SCR, "tx.py"), subs[0], words])
        how = "youtube captions"
    else:
        r = run([VENV_PY, os.path.join(SCR, "asr.py"), video, words]); how = "whisper: " + r.stdout.strip()[-80:]
    out = py("candidates.py", words, "--video", video, "--top", "15")
    open(os.path.join(rec, "candidates.txt"), "w", encoding="utf-8").write(out)
    warn = "" if rights.split(":")[0] in ("campaign", "permission", "open") else \
        "\nRIGHTS: unlicensed -> expect Content ID claims/blocks. Find an active campaign (Vyro/Whop) for this video or get written permission first; re-run with --rights campaign:<url>."
    print(f"{title} | {channel} | {int(float(dur)) // 60} min | transcript: {how} | rights: {rights}{warn}\nrecipe: {rec}\n{out}")


def cmd_sheet(nn, *items):
    rec, _, _ = paths(nn); out = os.path.join(CACHE, f"{nn}_sheet.png")
    print(sheet(source(rec), items, out))


def cmd_build(nn):
    rec, proj, _ = paths(nn); env = {"CLIP_RECIPE": rec}
    print(py("plate.py", source(rec), proj, env=env).strip().replace("\n", " | "))
    py("gen.py", proj, SFX, env=env)
    snaps, bad = [], []
    for d in sorted(glob.glob(os.path.join(proj, "c*_*"))):
        dur = json.load(open(os.path.join(d, "edit.json")))["duration"]
        r = run("npx hyperframes check", cwd=d, shell=True)
        if "Check passed" not in r.stdout + r.stderr:
            bad.append(os.path.basename(d))
        run(f"npx hyperframes snapshot --at 1.0,{dur / 2:.1f},{dur - 5:.1f}", cwd=d, shell=True)
        s = max(glob.glob(os.path.join(d, ".hyperframes", "artifacts", "snapshots", "*")), key=os.path.getmtime)
        snaps += sorted(glob.glob(os.path.join(s, "frame-0[0-2]*.png")))
    out = os.path.join(CACHE, f"{nn}_build.png"); n = len(snaps); cols = 3
    fc = "".join(f"[{i}]scale=180:320[s{i}];" for i in range(n)) + "".join(f"[s{i}]" for i in range(n)) + \
         f"xstack=inputs={n}:grid={cols}x{(n + cols - 1) // cols}:fill=black" if n > 1 else "null"
    run(["ffmpeg", "-y", *sum([["-i", f] for f in snaps], []), "-filter_complex", fc, out])
    print(f"checks: {'FAILED ' + ','.join(bad) if bad else 'all passed'} | sheet (rows = clips, cols = 1s/mid/end): {out}")


def names(rec):
    p = os.path.join(rec, "names.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def cmd_render(nn):
    rec, proj, ready = paths(nn); os.makedirs(os.path.join(ready, "clips"), exist_ok=True); nm = names(rec)
    for d in sorted(glob.glob(os.path.join(proj, "c*_*"))):
        k = os.path.basename(d); out = os.path.join(ready, "clips", nm.get(k, k) + ".mp4")
        r = run(["npx", "hyperframes", "render", "-q", "delivery", "-o", out], cwd=d, shell=True)
        print(k, "ok" if os.path.exists(out) else "FAILED " + (r.stderr or r.stdout)[-200:])
    print(py("export.py", ready))


def cmd_frames(nn, *items):
    rec, proj, _ = paths(nn); a = os.path.join(proj, "thumbnails", "assets"); os.makedirs(a, exist_ok=True)
    for it in items:
        k, t = it.split(":")
        run(["ffmpeg", "-y", "-ss", t, "-i", source(rec), "-frames:v", "1", "-vf", GRADE, "-q:v", "2", os.path.join(a, k + ".jpg")])
    print(sheet_frames(a, [i.split(":")[0] for i in items], os.path.join(CACHE, f"{nn}_frames.png")))


def sheet_frames(a, keys, out):
    keys = list(keys) + list(keys[-1:]) * (len(keys) % 2)  # xstack 2xN grid needs an even count
    n = len(keys)
    fc = "".join(f"[{i}]scale=320:180[s{i}];" for i in range(n)) + "".join(f"[s{i}]" for i in range(n)) + f"xstack=inputs={n}:grid=2x{(n + 1) // 2}:fill=black"
    run(["ffmpeg", "-y", *sum([["-i", os.path.join(a, k + ".jpg")] for k in keys], []), "-filter_complex", fc, out])
    return out


def cmd_thumbs(nn):
    rec, proj, ready = paths(nn); t = os.path.join(proj, "thumbnails"); spec = json.load(open(os.path.join(rec, "thumbs.json"), encoding="utf-8"))
    first = sorted(glob.glob(os.path.join(proj, "c*_*")))[0]
    for f in ("hyperframes.json", "package.json"):
        shutil.copy(os.path.join(first, f), t)
    py("thumbs.py", os.path.join(rec, "thumbs.json"), t)
    at = ",".join(f"{i + 0.5}" for i in range(len(spec)))
    o = os.path.join(ready, "thumbnails"); os.makedirs(o, exist_ok=True)
    files = list(names(rec).values()) or [f"{i + 1:02d}" for i in range(len(spec))]
    for sub, tag in (("vertical", "Shorts_cover_9x16"), ("landscape", "YouTube_thumbnail_16x9")):
        run(f"npx hyperframes snapshot --at {at}", cwd=os.path.join(t, sub), shell=True)
        s = max(glob.glob(os.path.join(t, sub, ".hyperframes", "artifacts", "snapshots", "*")), key=os.path.getmtime)
        for i, f in enumerate(sorted(glob.glob(os.path.join(s, "frame-*.png")))[:len(spec)]):
            run(["ffmpeg", "-y", "-i", f, "-q:v", "2", os.path.join(o, f"{files[i]}__{tag}.jpg")])
    out = os.path.join(CACHE, f"{nn}_thumbs.png"); imgs = sorted(glob.glob(os.path.join(o, "*.jpg"))); n = len(imgs)
    fc = "".join(f"[{i}]scale=216:384:force_original_aspect_ratio=decrease,pad=216:384:(ow-iw)/2:(oh-ih)/2[s{i}];" for i in range(n)) + "".join(f"[s{i}]" for i in range(n)) + f"xstack=inputs={n}:grid={n // 2}x2:fill=black"
    run(["ffmpeg", "-y", *sum([["-i", f] for f in imgs], []), "-filter_complex", fc, out])
    print(f"{n} thumbnails -> {o}\nreview sheet: {out}")


def cmd_kit(nn):
    rec, _, ready = paths(nn)
    print(py("kit.py", rec, ready).strip()); print(py("export.py", ready).strip())


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    globals()["cmd_" + sys.argv[1]](*sys.argv[2:])
