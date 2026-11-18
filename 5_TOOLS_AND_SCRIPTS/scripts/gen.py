"""Generate a HyperFrames index.html per clip: punch-ins, hook header, rewind, captions, stickers, SFX, progress bar, CTA."""
import json, os, re, shutil, sys, html

ROOT = sys.argv[1]          # clips_v2_build
SCAFFOLD = sys.argv[2]      # clips_v2 (init'd project, has .media sfx)
only = set(sys.argv[3:])

SFX = {"whoosh": ("sfx_006", 0.218, 0.45), "pop": ("sfx_002", 0.032, 0.55), "impact": ("sfx_001", 0.755, 0.55),
       "bass": ("sfx_004", 0.101, 0.75), "cash": ("sfx_007", 9.267, 0.5), "scratch": ("sfx_008", 0.75, 0.6),
       "boing": ("sfx_009", 0.04, 0.45), "shutter": ("sfx_010", 0.758, 0.5)}

# beat kinds: sticker (white card), stamp (big red/yellow centre slam), emoji (big emoji pop), counter
CLIPS = {
 "c1_neuralink": dict(
  hook=["HE'S PARALYZED…", "BUT TYPES WITH HIS *MIND*"], rewind="⏪ HOW IS THIS POSSIBLE?",
  beats=[(5.5, "sticker", "🧠 NEURALINK • $10,000 CHIP", "pop", 2.4), (13.5, "sticker", "PARALYZED FOR 8 YEARS", "pop", 2.4),
         (20.0, "emoji", "💻", "pop", 1.4), (23.3, "sticker", "📱 TEXT WITH HIS BRAIN?", "pop", 2.0),
         (25.1, "sticker", "👀 HANDS NOT MOVING", "boing", 3.0), (32.4, "stamp", "HE TYPED \"HI\" ✅", "bass", 1.5),
         (35.5, "sticker", "🎮 GAMING WITH HIS MIND", "pop", 2.6), (40.9, "stamp", "CRUSHED US 💀", "impact", 1.6)],
  push=[11.2, 25.1, 40.9], shake=[32.4, 40.9], cta="WOULD YOU GET A BRAIN CHIP? 👇", cta_t=43.3),
 "c2_kai_arm": dict(
  hook=["HE HAD NO IDEA", "WHO HIS *DOCTOR* WAS"], rewind="⏪ 10 MINUTES EARLIER",
  beats=[(3.3, "sticker", "BORN WITHOUT AN ARM", "pop", 2.0), (5.4, "emoji", "💔", "pop", 1.2),
         (10.5, "sticker", "🎭 FAKE DOCTOR'S OFFICE", "pop", 2.6), (14.35, "counter", "$25,000|BIONIC ARM", "cash", 2.6),
         (18.6, "sticker", "👀 THE \"DOCTOR\" IS MRBEAST", "boing", 2.8), (24.2, "emoji", "😱", "pop", 1.2),
         (32.75, "stamp", "THE REAL ARM 🦾", "bass", 1.8), (37.7, "emoji", "💪", "pop", 1.2),
         (41.6, "sticker", "✅ IT ACTUALLY WORKS", "pop", 2.2), (45.15, "emoji", "🤝", "pop", 1.3)],
  push=[14.35, 32.75, 48.35], shake=[32.75], cta="SEND THIS TO SOMEONE WHO NEEDS A SMILE ❤️", cta_t=52.4),
 "c3_flying_car": dict(
  hook=["$1,000,000 RACE:", "*FLYING* CAR vs NORMAL CAR"], rewind="⏪ 5 MINUTES EARLIER",
  beats=[(7.2, "counter", "$1,000,000|ON THE LINE", "cash", 2.4), (12.4, "stamp", "✈️ vs 🚗", "whoosh", 1.4),
         (15.0, "stamp", "🏁 GO!", "impact", 1.0), (20.9, "sticker", "🌊 INTO THE OCEAN?!", "pop", 2.2),
         (23.75, "stamp", "CHEATING 😤", "boing", 1.2), (28.0, "sticker", "🛑 HAS TO STOP AT STOP SIGNS", "pop", 2.2),
         (31.9, "sticker", "😳 ALREADY HALFWAY THERE", "pop", 2.0), (37.2, "emoji", "🏖️", "pop", 1.2),
         (40.65, "stamp", "COOKED 💀", "impact", 1.2), (42.8, "sticker", "🤔 THE LOOPHOLE", "boing", 2.6),
         (48.6, "stamp", "WON BY 10 MINUTES", "bass", 1.8)],
  push=[7.2, 23.75, 48.6], shake=[15.0, 48.6], cta="WOULD YOU RIDE IN IT? ✈️👇", cta_t=50.2),
 "c4_lab_chicken": dict(
  hook=["ONE WAS KILLED.", "ONE WAS GROWN IN A *LAB*."], rewind="⏪ CAN THEY TELL?",
  beats=[(4.75, "sticker", "🐔 FARM CHICKEN", "pop", 2.2), (8.5, "sticker", "🧪 LAB-GROWN CHICKEN", "pop", 2.2),
         (11.1, "sticker", "👨‍🍳 CHEF NICK DIGIOVANNI", "pop", 2.0), (13.2, "stamp", "BLIND TASTE TEST 🙈", "whoosh", 1.6),
         (18.15, "sticker", "BITE #1", "pop", 1.4), (24.05, "sticker", "BITE #2", "pop", 1.2),
         (25.4, "emoji", "🤯", "pop", 1.3), (31.4, "sticker", "HIS GUESS: LAB-GROWN ❓", "pop", 1.0),
         (32.45, "stamp", "❌ WRONG", "bass", 1.4)],
  push=[13.2, 25.4, 32.45], shake=[32.45], cta="WOULD YOU EAT LAB-GROWN CHICKEN? 👇", cta_t=35.0),
 "c5_heat_shield": dict(
  hook=["*2,000°* BLOWTORCH", "vs HIS BARE HAND"], rewind="⏪ HOW IS THIS POSSIBLE?",
  beats=[(7.7, "sticker", "🌋 HOTTER THAN LAVA", "pop", 2.2), (10.8, "sticker", "SPACEX HEAT SHIELD TILE", "pop", 2.2),
         (12.85, "emoji", "🪶", "pop", 1.0), (16.2, "sticker", "🔥 BLOWTORCH-PROOF?", "pop", 2.2),
         (18.55, "emoji", "✋", "pop", 1.3), (26.45, "sticker", "📝 NO WAIVER SIGNED 😬", "boing", 2.4),
         (33.5, "emoji", "😰", "pop", 1.3), (36.3, "counter", "2,000°F|ON HIS HAND", "bass", 3.6),
         (40.1, "sticker", "😮 FEELS NOTHING", "pop", 2.0), (43.0, "stamp", "⚠️ DON'T TOUCH IT", "impact", 1.8)],
  push=[16.2, 38.4, 43.0], shake=[38.4], cta="WOULD YOU TRUST IT? 🔥👇", cta_t=45.4),
}

YEL = "#FFE500"


def esc(s):
    return html.escape(s, quote=True)


def hook_html(lines):
    out = []
    for ln in lines:
        plain = ln.replace("*", "")
        fs = int(min(80, 940 / (max(len(plain), 1) * 0.74)))
        words, hl = [], False
        for w in ln.split(" "):
            if w.startswith("*"):
                hl, w = True, w[1:]
            end = "*" in w
            core, _, tail = w.partition("*")
            if hl:
                words.append(f'<span class="hk-w"><span class="hl">{esc(core)}</span>{esc(tail)}</span>')
            else:
                words.append(f'<span class="hk-w">{esc(w)}</span>')
            if end:
                hl = False
        out.append(f'<div class="hk-line" style="font-size:{fs}px">' + " ".join(words) + "</div>")
    return "".join(out)


def caption_groups(words):
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if len(cur) >= 3 or w["text"][-1] in ".,?!" or (nxt and nxt["start"] - w["end"] > 0.15) or len(" ".join(x["text"] for x in cur)) > 16:
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    return groups


def build(name, spec):
    proj = os.path.join(ROOT, name)
    ed = json.load(open(os.path.join(proj, "edit.json"), encoding="utf-8"))
    D = round(ed["duration"] - 0.02, 3)
    cuts = ed["cuts"]
    cold = cuts[0]
    for f in ("hyperframes.json", "package.json"):
        shutil.copy(os.path.join(SCAFFOLD, f), proj)
    os.makedirs(os.path.join(proj, "assets", "sfx"), exist_ok=True)
    for sid, _, _ in SFX.values():
        shutil.copy(os.path.join(SCAFFOLD, ".media", "audio", "sfx", sid + ".mp3"), os.path.join(proj, "assets", "sfx"))

    els, js, audio = [], [], []
    ai = [0]

    def sfx(kind, at):
        sid, peak, vol = SFX[kind]
        start = at - peak - 0.033
        mstart = 0.0
        if start < 0:
            mstart, start = -start, 0.0
        dur = 1.4 if kind == "cash" else 2.2
        if kind == "cash":   # long file: jump straight to the ding
            mstart = max(0, peak - 0.6); start = max(0, at - 0.6 - 0.033)
        ai[0] += 1
        audio.append(f'<audio id="sfx{ai[0]}" class="clip" src="assets/sfx/{sid}.mp3" data-start="{start:.3f}" '
                     f'data-media-start="{mstart:.3f}" data-duration="{dur}" data-volume="{vol}" data-track-index="{20 + ai[0] % 4}"></audio>')

    # --- camera: hard punch-ins on cuts, eased pushes on emphasis, shakes on impacts
    scale = 1.0
    events = sorted([(c, "cut") for c in cuts] + [(p, "push") for p in spec["push"]] + [(s, "shake") for s in spec["shake"]])
    js.append('tl.set("#cam", {scale: 1.0, x: 0, y: 0, transformOrigin: "50% 47%"}, 0);')
    for t, k in events:
        if k == "cut":
            scale = 1.12 if scale < 1.06 else 1.0
            js.append(f'tl.set("#cam", {{scale: {scale}}}, {t});')
        elif k == "push":
            scale = round(scale + 0.09, 3)
            js.append(f'tl.to("#cam", {{scale: {scale}, duration: 0.28, ease: "power3.out"}}, {t - 0.05});')
        else:
            js.append(f'tl.to("#cam", {{keyframes: [{{x: 16, y: -8}}, {{x: -14, y: 10}}, {{x: 10, y: -6}}, {{x: -6, y: 4}}, {{x: 0, y: 0}}], duration: 0.3, ease: "none"}}, {t});')
    for c in cuts[1:]:
        if cuts.index(c) % 2 == 0:
            sfx("whoosh", c)

    # --- hook: big during the cold open, then docks as a compact header
    els.append(f'<div id="hook" class="clip" data-start="0" data-duration="{D}" data-track-index="5"><div id="hook-in">{hook_html(spec["hook"])}</div></div>')
    js.append('tl.fromTo("#hook .hk-w", {opacity: 0, scale: 0.6}, {opacity: 1, scale: 1, duration: 0.22, ease: "back.out(2.2)", stagger: 0.07}, 0.05);')
    js.append(f'tl.fromTo("#hook-in", {{scale: 1, y: 0}}, {{scale: 0.62, y: -38, duration: 0.45, ease: "power3.inOut"}}, {cold + 1.2});')
    sfx("impact", 0.12)

    # --- rewind transition after the cold open
    els.append(f'<div id="flash" class="clip" data-start="{cold - 0.02:.3f}" data-duration="0.3" data-track-index="6"></div>')
    js.append(f'tl.fromTo("#flash", {{opacity: 0.95}}, {{opacity: 0, duration: 0.28, ease: "power2.out"}}, {cold - 0.02});')
    els.append(f'<div id="rewind" class="clip" data-start="{cold:.3f}" data-duration="1.5" data-track-index="7"><div id="rw-in">{esc(spec["rewind"])}</div></div>')
    js.append(f'tl.fromTo("#rw-in", {{scale: 1.6, opacity: 0, rotation: -6}}, {{scale: 1, opacity: 1, rotation: -3, duration: 0.25, ease: "back.out(2)"}}, {cold});')
    js.append(f'tl.to("#rw-in", {{scale: 0.7, opacity: 0, duration: 0.18, ease: "power3.in"}}, {cold + 1.28});')
    sfx("scratch", cold)

    # --- beats
    for i, (t, kind, text, snd, hold) in enumerate(spec["beats"]):
        bid = f"b{i}"
        if kind == "counter":
            num, label = text.split("|")
            target = int("".join(ch for ch in num if ch.isdigit()))
            prefix = "$" if num.startswith("$") else ""
            suffix = num.split(str(target)[-1])[-1] if not prefix else ""
            suffix = re.sub(r"^[^0-9]*[0-9,]+", "", num)   # keeps units like " FT", "°F"
            els.append(f'<div id="{bid}" class="clip beat counter" data-start="{t - 0.6:.3f}" data-duration="{hold + 0.6:.3f}" data-track-index="{8 + i % 3}">'
                       f'<div class="ct-in"><div class="ct-num" id="{bid}n">{prefix}0{suffix}</div><div class="ct-lbl">{esc(label)}</div></div></div>')
            js.append(f'tl.fromTo("#{bid} .ct-in", {{scale: 0.3, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)"}}, {t - 0.6});')
            js.append(f'(function(){{const o={{v:0}}; tl.to(o, {{v: {target}, duration: 0.6, ease: "power2.out", onUpdate(){{document.getElementById("{bid}n").textContent = "{prefix}" + Math.round(o.v).toLocaleString("en-US") + "{suffix}";}}}}, {t - 0.6});}})();')
            js.append(f'tl.fromTo("#{bid} .ct-num", {{scale: 1}}, {{scale: 1.18, duration: 0.08, yoyo: true, repeat: 1, ease: "power2.out"}}, {t});')
            js.append(f'tl.to("#{bid} .ct-in", {{scale: 0.6, opacity: 0, duration: 0.16, ease: "power3.in"}}, {t + hold - 0.18});')
        else:
            cls = {"sticker": "sticker", "stamp": "stamp", "emoji": "emoji"}[kind]
            rot = (-4 if i % 2 else 3) if kind != "emoji" else (-8 if i % 2 else 8)
            els.append(f'<div id="{bid}" class="clip beat {cls}" data-start="{t:.3f}" data-duration="{hold:.3f}" data-track-index="{8 + i % 3}"><div class="bt-in">{esc(text)}</div></div>')
            start_scale = 2.2 if kind == "stamp" else 0.2
            js.append(f'tl.fromTo("#{bid} .bt-in", {{scale: {start_scale}, opacity: 0, rotation: {rot * 2}}}, {{scale: 1, opacity: 1, rotation: {rot}, duration: {0.18 if kind == "stamp" else 0.26}, ease: "{"power4.out" if kind == "stamp" else "back.out(2.4)"}"}}, {t});')
            js.append(f'tl.to("#{bid} .bt-in", {{scale: 0.5, opacity: 0, duration: 0.15, ease: "power3.in"}}, {t + hold - 0.17});')
        sfx(snd, t)

    # --- captions
    groups = caption_groups(ed["words"])
    capels = []
    for gi, g in enumerate(groups):
        gs = max(0.05, g[0]["start"] - 0.03)
        ge = min(D, (groups[gi + 1][0]["start"] - 0.01) if gi + 1 < len(groups) else g[-1]["end"] + 0.3)
        ge = max(ge, gs + 0.15)
        spans = " ".join(f'<span class="cw" id="g{gi}w{wi}">{esc(w["text"].upper())}</span>' for wi, w in enumerate(g))
        capels.append(f'<div class="clip cap" id="g{gi}" data-start="{gs:.3f}" data-duration="{ge - gs:.3f}" data-track-index="4"><div class="cap-in">{spans}</div></div>')
        js.append(f'tl.fromTo("#g{gi} .cap-in", {{scale: 0.82, y: 14}}, {{scale: 1, y: 0, duration: 0.12, ease: "back.out(2.5)"}}, {gs});')
        for wi, w in enumerate(g):
            we = g[wi + 1]["start"] if wi + 1 < len(g) else ge
            js.append(f'tl.set("#g{gi}w{wi}", {{color: "{YEL}", scale: 1.1}}, {w["start"]:.3f}); tl.set("#g{gi}w{wi}", {{color: "#ffffff", scale: 1}}, {max(we, w["start"] + 0.05):.3f});')

    # --- CTA + progress
    ct = spec["cta_t"]
    els.append(f'<div id="cta" class="clip" style="top:{spec.get("cta_y", 880)}px" data-start="{ct:.3f}" data-duration="{D - ct:.3f}" data-track-index="11"><div id="cta-in">{esc(spec["cta"])}</div></div>')
    js.append(f'tl.fromTo("#cta-in", {{y: 60, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.3, ease: "back.out(1.8)"}}, {ct});')
    sfx("pop", ct)
    js.append(f'tl.fromTo("#bar-fill", {{scaleX: 0}}, {{scaleX: 1, duration: {D}, ease: "none", transformOrigin: "0% 50%"}}, 0);')

    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
:root {{ --yel: {YEL}; --ink: #ffffff; --font-display: "Montserrat"; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
#root {{ position: relative; width: 100%; height: 100%; font-family: var(--font-display), sans-serif; font-weight: 900; overflow: hidden; }}
#camwrap {{ position: absolute; inset: 0; overflow: hidden; }}
#cam {{ position: absolute; inset: 0; }}
#plate {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
#topshade {{ position: absolute; left: 0; top: 0; width: 1080px; height: 520px; background: linear-gradient(rgba(0,0,0,.72), rgba(0,0,0,0)); }}
.stroke {{ -webkit-text-stroke: 12px #000; paint-order: stroke fill; }}
#hook {{ position: absolute; left: 0; top: 180px; width: 1080px; text-align: center; }}
#hook-in {{ transform-origin: 50% 0%; }}
.hk-line {{ font-size: 76px; line-height: 1.08; color: #fff; letter-spacing: -0.01em; }}
.hk-w {{ display: inline-block; -webkit-text-stroke: 13px #000; paint-order: stroke fill; text-shadow: 0 8px 0 rgba(0,0,0,.55); }}
.hl {{ color: var(--yel); }}
.hk-line {{ white-space: nowrap; }}
#flash {{ position: absolute; inset: 0; background: #fff; }}
#rewind {{ position: absolute; left: 0; top: 820px; width: 1080px; text-align: center; }}
#rw-in {{ display: inline-block; font-size: 66px; color: #fff; background: #E0122B; padding: 18px 34px; border-radius: 18px; box-shadow: 0 14px 0 rgba(0,0,0,.45); }}
.beat {{ position: absolute; left: 60px; width: 900px; text-align: center; }}
.sticker {{ top: 420px; }}
.sticker .bt-in {{ display: inline-block; font-size: 52px; color: #111; background: #fff; padding: 16px 30px; border-radius: 20px; box-shadow: 0 12px 0 rgba(0,0,0,.4); border: 5px solid #111; }}
.stamp {{ top: 700px; }}
.stamp .bt-in {{ display: inline-block; font-size: 104px; line-height: 1.02; color: var(--yel); -webkit-text-stroke: 16px #000; paint-order: stroke fill; text-shadow: 0 10px 0 rgba(0,0,0,.6); }}
.emoji {{ top: 560px; }}
.emoji .bt-in {{ display: inline-block; font-size: 190px; line-height: 1; filter: drop-shadow(0 12px 0 rgba(0,0,0,.4)); }}
.counter {{ top: 430px; }}
.ct-in {{ display: inline-block; background: #111; border: 6px solid var(--yel); border-radius: 26px; padding: 18px 40px 22px; box-shadow: 0 14px 0 rgba(0,0,0,.45); }}
.ct-num {{ font-size: 110px; line-height: 1; color: var(--yel); }}
.ct-lbl {{ font-size: 40px; color: #fff; margin-top: 6px; }}
.cap {{ position: absolute; left: 30px; width: 960px; top: 1150px; text-align: center; }}
.cap-in {{ display: inline-block; transform-origin: 50% 60%; }}
.cw {{ display: inline-block; font-size: 78px; line-height: 1.05; color: #fff; -webkit-text-stroke: 13px #000; paint-order: stroke fill; text-shadow: 0 7px 0 rgba(0,0,0,.6); margin: 0 16px; }}
#cta {{ position: absolute; left: 60px; width: 900px; top: 880px; text-align: center; }}
#cta-in {{ display: inline-block; font-size: 58px; line-height: 1.12; color: #111; background: var(--yel); padding: 22px 34px; border-radius: 22px; border: 6px solid #111; box-shadow: 0 14px 0 rgba(0,0,0,.45); }}
#bar {{ position: absolute; left: 0; top: 1512px; width: 1080px; height: 12px; background: rgba(0,0,0,.45); }}
#bar-fill {{ position: absolute; left: 0; top: 0; width: 1080px; height: 12px; background: var(--yel); }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
<div id="camwrap"><div id="cam">
<video id="plate" class="clip" src="assets/plate.mp4" data-start="0" data-duration="{D}" data-track-index="0" playsinline data-has-audio="true" data-volume="1"></video>
</div></div>
<div id="topshade"></div>
<div id="bar"><div id="bar-fill"></div></div>
{chr(10).join(capels)}
{chr(10).join(els)}
{chr(10).join(audio)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body>
</html>
"""
    open(os.path.join(proj, "index.html"), "w", encoding="utf-8").write(doc)
    json.dump({"id": name, "name": name}, open(os.path.join(proj, "meta.json"), "w"))
    print(name, "D", D, "groups", len(groups), "beats", len(spec["beats"]), "sfx", ai[0])


RECIPE = os.environ.get("CLIP_RECIPE")
if RECIPE and os.path.exists(os.path.join(RECIPE, "spec.json")):
    CLIPS = json.load(open(os.path.join(RECIPE, "spec.json"), encoding="utf-8"))
    for c in CLIPS.values():
        c["beats"] = [tuple(b) for b in c["beats"]]

for n, s in CLIPS.items():
    if not only or n in only:
        build(n, s)
