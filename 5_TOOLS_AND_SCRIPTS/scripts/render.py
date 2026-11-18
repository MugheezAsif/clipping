import json, os, re, subprocess, sys

SCR = os.path.dirname(os.path.abspath(__file__))
WORDS = json.load(open(os.path.join(SCR, "words.json"), encoding="utf-8"))
SRC = sys.argv[1]
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

CLIPS = [
    ("01_neuralink_mind_control", 41.2, 96.8, "PARALYZED MAN BEATS US\\NUSING ONLY HIS MIND"),
    ("02_kai_bionic_arm", 97.0, 190.2, "HE THOUGHT HE WAS GETTING\\NA NORMAL ARM..."),
    ("03_flying_car_million_bet", 197.5, 281.9, "$1,000,000 BET:\\NFLYING CAR vs NORMAL CAR"),
    ("04_lab_chicken_taste_test", 502.2, 560.9, "ONE WAS KILLED.\\NONE WAS GROWN IN A LAB."),
    ("05_blowtorch_heat_shield", 1028.4, 1088.9, "2,000° BLOWTORCH\\Nvs MY BARE HAND"),
]

JUNK = re.compile(r"\[[^\]]*\]|>>")


def clean(w):
    return JUNK.sub("", w).strip().upper()


def ts(s):
    s = max(0, s)
    h = int(s // 3600); m = int(s % 3600 // 60); sec = s % 60
    return f"{h}:{m:02d}:{sec:05.2f}"


HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Arial Black,66,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,7,3,8,60,60,250,1
Style: Cap,Arial Black,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,1,0,0,0,100,100,0,0,1,8,4,2,60,60,400,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

YELLOW = "{\\c&H00E5FF&}"
WHITE = "{\\c&HFFFFFF&}"


def build_ass(start, end, hook):
    ws = []
    for t, w in WORDS:
        s = t / 1000
        if start - 0.05 <= s < end:
            for piece in clean(w).split():
                ws.append([s - start, piece])
    # chunk: max 3 words, break after punctuation or a pause
    chunks, cur = [], []
    for i, (s, w) in enumerate(ws):
        cur.append([s, w])
        nxt = ws[i + 1][0] if i + 1 < len(ws) else None
        if len(cur) >= 3 or w[-1] in ".,?!" or (nxt is not None and nxt - s > 0.7):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    dur = end - start
    lines = [f"Dialogue: 1,{ts(0)},{ts(dur)},Hook,,0,0,0,,{{\\fad(150,0)}}{hook}"]
    for ci, ch in enumerate(chunks):
        nxt_chunk = chunks[ci + 1][0][0] if ci + 1 < len(chunks) else dur
        for wi, (s, _) in enumerate(ch):
            e = ch[wi + 1][0] if wi + 1 < len(ch) else min(nxt_chunk, s + 0.9)
            if e <= s:
                continue
            txt = " ".join((YELLOW if j == wi else WHITE) + w for j, (_, w) in enumerate(ch))
            pop = "{\\fscx85\\fscy85\\t(0,90,\\fscx100\\fscy100)}" if wi == 0 else ""
            lines.append(f"Dialogue: 0,{ts(s)},{ts(e)},Cap,,0,0,0,,{pop}{txt}")
    return HEADER + "\n".join(lines) + "\n"


only = set(sys.argv[3:])
for name, a, b, hook in CLIPS:
    if only and name[:2] not in only:
        continue
    ass_name = name + ".ass"
    with open(os.path.join(OUT, ass_name), "w", encoding="utf-8") as f:
        f.write(build_ass(a, b, hook))
    vf = (
        "[0:v]split[a][b];"
        "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.18[bg];"
        "[b]crop=1280:1080,scale=1080:912[fg];"
        f"[bg][fg]overlay=0:504,ass={ass_name},format=yuv420p[v]"
    )
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{a:.2f}", "-t", f"{b - a:.2f}", "-i", SRC,
        "-filter_complex", vf, "-map", "[v]", "-map", "0:a",
        "-af", f"loudnorm=I=-14:TP=-1:LRA=11,afade=t=in:d=0.05,afade=t=out:st={b - a - 0.25:.2f}:d=0.25",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart",
        name + ".mp4",
    ]
    print("rendering", name, f"{b - a:.1f}s", flush=True)
    subprocess.run(cmd, cwd=OUT, check=True)
    os.remove(os.path.join(OUT, ass_name))
print("done")
