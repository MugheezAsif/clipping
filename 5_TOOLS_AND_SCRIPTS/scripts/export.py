"""Platform guard: make every clip in <ready_dir>/clips safe for YouTube, IG/FB Reels, TikTok, X, Snapchat.

usage: python export.py <ready_dir> [--max-mb 95]
Checks: 1080x1920, H.264 + AAC 48 kHz, ~30 fps, <=60 s (warn), size <= max-mb, faststart (moov first).
Loudness: measures integrated LUFS + true peak; if true peak > -1 dBTP, applies an oversampled limiter (video copied) until <= -1.2.
Fixes in place: re-encodes oversize files (CRF 19, capped bitrate), remuxes non-faststart files. Prints one line per clip.
"""
import glob, json, os, re, subprocess, sys

ready = sys.argv[1]
maxmb = float(sys.argv[sys.argv.index("--max-mb") + 1]) if "--max-mb" in sys.argv else 95.0


def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate",
                        "-of", "json", f], capture_output=True, text=True)
    return json.loads(r.stdout)


def faststart(f):
    with open(f, "rb") as h:
        head = h.read(1 << 16)
    m, d = head.find(b"moov"), head.find(b"mdat")
    return m != -1 and (d == -1 or m < d)


def loud(f):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True, errors="ignore")
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr); tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    return (float(i[-1]) if i else None), (float(tp[-1]) if tp else None)


def fix_peak(f):
    """Oversampled limiter, video copied; tries stronger limits until true peak <= -1.2 dBTP."""
    tmp = f + ".peak.mp4"
    for lim in (0.75, 0.62, 0.5, 0.4):
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", f, "-c:v", "copy", "-af",
                        f"aresample=192000,alimiter=limit={lim}:attack=0.5:release=40:level=false,aresample=48000",
                        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", tmp], check=True)
        i, tp = loud(tmp)
        if tp is not None and tp <= -1.2:
            break
    try:
        os.replace(tmp, f); return i, tp, "peak-limited"
    except PermissionError:
        os.remove(tmp); return None, None, "LOCKED (file open in another app) - close it and re-run"


for f in sorted(glob.glob(os.path.join(ready, "clips", "*.mp4"))):
    p = probe(f); fmt = p["format"]; v = next(s for s in p["streams"] if s["codec_type"] == "video")
    a = next((s for s in p["streams"] if s["codec_type"] == "audio"), {})
    dur, mb = float(fmt["duration"]), int(fmt["size"]) / 1e6
    issues = []
    if (v["width"], v["height"]) != (1080, 1920): issues.append(f"size {v['width']}x{v['height']}")
    if v["codec_name"] != "h264": issues.append(v["codec_name"])
    if a.get("codec_name") != "aac" or a.get("sample_rate") != "48000": issues.append("audio")
    n, d = map(int, v["r_frame_rate"].split("/"))
    if abs(n / d - 30) > 0.1: issues.append(f"{n / d:.2f}fps")
    tmp = f + ".tmp.mp4"; action = "ok"
    if mb > maxmb or issues:
        kb = int(min(9000, maxmb * 8000 / dur * 0.92))  # video kbps that lands under the cap
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", f, "-vf", "scale=1080:1920,fps=30",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", f"{kb}k", "-bufsize", f"{kb * 2}k",
                        "-g", "60", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                        "-movflags", "+faststart", tmp], check=True)
        try:
            os.replace(tmp, f); action = f"re-encoded ({mb:.0f}MB->{os.path.getsize(f) / 1e6:.0f}MB)"
        except PermissionError:
            os.remove(tmp); action = "LOCKED (file open in another app) - close it and re-run"
    elif not faststart(f):
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", f, "-c", "copy", "-movflags", "+faststart", tmp], check=True)
        try:
            os.replace(tmp, f); action = "faststart"
        except PermissionError:
            os.remove(tmp); action = "LOCKED (file open in another app) - close it and re-run"
    i, tp = loud(f)
    if tp is not None and tp > -1.0 and "LOCKED" not in action:
        i, tp, act2 = fix_peak(f); action = act2 if action == "ok" else action + " + " + act2
    lv = f" {i:.1f}LUFS {tp:.1f}dBTP" if i is not None and tp is not None else ""
    if i is not None and not -16.0 <= i <= -13.5: lv += " WARN loudness"
    warn = " WARN >60s (Shorts Content-ID risk)" if dur > 60.5 else ""
    print(f"{os.path.basename(f)}: {dur:.1f}s {os.path.getsize(f) / 1e6:.0f}MB {action}{lv}{' ' + ','.join(issues) if issues else ''}{warn}")
