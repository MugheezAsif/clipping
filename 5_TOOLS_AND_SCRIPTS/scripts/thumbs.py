"""Thumbnails v2: a library of 7 distinct styles (9:16 Shorts cover 1080x1920 + 16:9 YouTube 1280x720) as HyperFrames stills.

usage: python thumbs.py <thumbs.json> <project_dir>     (project_dir/assets holds graded frames from `clip.py frames`)
thumbs.json = list, one item per clip (use a DIFFERENT style for every clip of a video):
  {"style": "sticker|bignum|vs|callout|reveal|cinema|stack",
   "l1": "small line", "l2": "BIG LINE", "tag": "chip text",           # thumbnail text must NOT repeat the title/hook
   "bg": "t1_bg.jpg", "in": "t1_in.jpg",                               # main frame, second frame (vs/stack)
   "cut": "t1_x.jpg", "cutm": "u2net_human_seg|isnet-general-use",     # subject cut out (sticker/bignum/reveal)
   "pal": "yellow|red|cyan|green|pink|orange", "pos": "50% 50%", "inpos": "50% 50%",
   "at": [x%, y%], "ath": [x%, y%] (16:9, optional), "r": 150}                                         # callout ring / reveal blur spot (vertical %)
Styles:
  sticker  blurred tinted bg, giant word BEHIND the cut-out subject (depth), white outline + colour glow
  bignum   graphic colour burst, huge number/money, subject in front: for money/stat payoffs
  vs       diagonal split of two frames + VS badge: for rivals, teams, A vs B
  callout  full frame, hand-drawn red ring + arrow on the key object: for "look at this" moments
  reveal   payoff spot blurred with a "?" (curiosity gap), optional reaction cut-out: for cliffhangers
  cinema   letterbox, cinematic grade, thin type: for dramatic/serious moments
  stack    two framed cards (then -> now) with arrow: for before/after, setup/payoff
"""
import html, json, os, subprocess, sys

spec = json.load(open(sys.argv[1], encoding="utf-8"))
proj = sys.argv[2]
VENV_PY = os.path.expanduser("~/.clipping/env/Scripts/python.exe")
CUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cutout.py")
esc = lambda s: html.escape(str(s), quote=True)
PAL = {"yellow": ("#FFE500", "#3a2a00"), "red": ("#FF2A2A", "#3a0008"), "cyan": ("#00E5FF", "#00222e"),
       "green": ("#2BFF6A", "#00280f"), "pink": ("#FF3DB8", "#33001f"), "orange": ("#FF8A00", "#331a00")}
K = {"anton": 0.5, "mont": 0.74, "bebas": 0.42}


def fit(text, maxw, base, font="anton"):
    return int(min(base, maxw / (max(len(text), 1) * K[font])))


def cut_png(t, assets):
    src = os.path.join(proj, "assets", t["cut"]); name = t["cut"][:-4] + "_cut.png"; dst = os.path.join(assets, name)
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        r = subprocess.run([VENV_PY, CUT, src, dst, t.get("cutm", "u2net_human_seg")], capture_output=True, text=True)
        if r.returncode:
            sys.exit("cutout failed: " + r.stderr[-400:])
    return name


def img(src, style="", cls="full"):
    return f'<img class="{cls}" src="assets/{src}" style="{style}" />'


def txt(s, size, color="#fff", font="anton", stroke=None, extra=""):
    st = stroke if stroke is not None else max(6, size // 9)
    fam = {"anton": "'Anton'", "mont": "'Montserrat'", "bebas": "'Bebas Neue'"}[font]
    return (f'<div class="t" style="font-family:{fam};font-size:{size}px;color:{color};-webkit-text-stroke:{st}px #000;'
            f'{extra}">{esc(s)}</div>')


def chip(s, acc, size, extra=""):
    return f'<div class="chip" style="background:{acc};font-size:{size}px;{extra}">{esc(s)}</div>' if s else ""


def outline(acc, px):
    d = " ".join(f"drop-shadow({x}px {y}px 0 #fff)" for x, y in ((px, 0), (-px, 0), (0, px), (0, -px)))
    return f"filter:{d} drop-shadow(0 0 {px * 6}px {acc}) drop-shadow(0 {px * 3}px {px * 4}px rgba(0,0,0,.6));"


def scene(t, W, H, v):
    acc, dark = PAL.get(t.get("pal", "yellow"), PAL["yellow"])
    st, pos, ipos = t.get("style", "callout"), t.get("pos", "50% 50%"), t.get("inpos", "50% 50%")
    l1, l2, tag = t.get("l1", ""), t.get("l2", ""), t.get("tag", "")
    u = W / 1080 if v else W / 1280
    o = []
    if st == "sticker":
        o += [img(t["bg"][:-4] + "_blur.jpg"),
              f'<div class="full" style="background:radial-gradient(circle at 50% {45 if v else 50}%, {acc}99, transparent 62%),linear-gradient(180deg,#000b,#0000 35%,#0000 70%,#000d)"></div>']
        if v:
            o += [f'<div class="abs" style="left:0;width:100%;top:{int(H*.27)}px;text-align:center;transform:rotate(-4deg)">{txt(l2, fit(l2, W*.94, 400), acc)}</div>',
                  img(t["_cut"], f"bottom:0;left:50%;transform:translateX(-50%);height:{int(H*.70)}px;max-width:{W}px;{outline(acc, 9)}", "abs"),
                  f'<div class="abs" style="top:190px;width:100%;text-align:center">{chip(l1, "#000", fit(l1, W*.8, 92, "mont"), f"color:#fff;border-color:{acc}")}</div>',
                  f'<div class="abs" style="bottom:150px;width:100%;text-align:center">{chip(tag, acc, 84, "transform:rotate(3deg)")}</div>']
        else:
            o += [f'<div class="abs" style="left:36px;top:{int(H*.30)}px;width:{int(W*.64)}px;transform:rotate(-4deg)">{txt(l2, fit(l2, W*.62, 230), acc)}</div>',
                  img(t["_cut"], f"bottom:0;right:10px;height:{H}px;max-width:{int(W*.55)}px;{outline(acc, 6)}", "abs"),
                  f'<div class="abs" style="left:40px;top:40px">{chip(l1, "#000", fit(l1, W*.5, 58, "mont"), f"color:#fff;border-color:{acc}")}</div>',
                  f'<div class="abs" style="left:40px;bottom:44px">{chip(tag, acc, 54)}</div>']
    elif st == "bignum":
        o += [f'<div class="full" style="background:radial-gradient(circle at 50% 42%, {acc} 0%, {dark} 78%)"></div>',
              f'<div class="full rays"></div>', img(t["bg"], f"object-position:{pos};opacity:.16;mix-blend-mode:luminosity")]
        if v:
            o += [f'<div class="abs" style="top:{int(H*.17)}px;width:100%;text-align:center;transform:rotate(-3deg)">{txt(l2, fit(l2, W*.96, 470), "#fff", stroke=18, extra="text-shadow:0 18px 0 #000")}</div>',
                  img(t["_cut"], f"bottom:0;left:50%;transform:translateX(-50%);height:{int(H*.62)}px;max-width:{W}px;{outline('#000', 8)}", "abs"),
                  f'<div class="abs" style="top:150px;width:100%;text-align:center">{chip(l1, "#000", fit(l1, W*.8, 88, "mont"), "color:#fff")}</div>',
                  f'<div class="abs" style="bottom:140px;width:100%;text-align:center">{chip(tag, "#fff", 80, "color:#000;transform:rotate(-3deg)")}</div>']
        else:
            o += [f'<div class="abs" style="left:30px;top:{int(H*.26)}px;width:{int(W*.66)}px;transform:rotate(-3deg)">{txt(l2, fit(l2, W*.64, 270), "#fff", stroke=12, extra="text-shadow:0 10px 0 #000")}</div>',
                  img(t["_cut"], f"bottom:0;right:0;height:{int(H*.98)}px;max-width:{int(W*.5)}px;{outline('#000', 6)}", "abs"),
                  f'<div class="abs" style="left:40px;top:40px">{chip(l1, "#000", fit(l1, W*.5, 56, "mont"), "color:#fff")}</div>',
                  f'<div class="abs" style="left:40px;bottom:40px">{chip(tag, "#fff", 50, "color:#000")}</div>']
    elif st == "vs":
        if v:
            o += [img(t["bg"], f"top:0;height:{int(H*.56)}px;object-position:{pos};clip-path:polygon(0 0,100% 0,100% 78.6%,0 100%)", "abs cov"),
                  img(t["in"], f"top:{int(H*.44)}px;height:{int(H*.56)}px;object-position:{ipos};clip-path:polygon(0 21.4%,100% 0,100% 100%,0 100%)", "abs cov"),
                  f'<div class="abs seam" style="left:-20%;width:140%;top:{H//2 - 9}px;height:18px;background:{acc};transform:rotate(-12deg)"></div>',
                  f'<div class="abs" style="top:230px;left:50px">{chip(l1, "#000", fit(l1, W*.7, 96, "mont"), f"color:#fff;border-color:{acc};transform:rotate(-4deg)")}</div>',
                  f'<div class="abs" style="bottom:230px;right:50px">{chip(l2, "#000", fit(l2, W*.7, 96, "mont"), f"color:#fff;border-color:{acc};transform:rotate(-4deg)")}</div>']
        else:
            o += [img(t["bg"], f"left:0;width:{int(W*.56)}px;object-position:{pos};clip-path:polygon(0 0,100% 0,78.6% 100%,0 100%)", "abs cov"),
                  img(t["in"], f"left:{int(W*.44)}px;width:{int(W*.56)}px;object-position:{ipos};clip-path:polygon(21.4% 0,100% 0,100% 100%,0 100%)", "abs cov"),
                  f'<div class="abs seam" style="top:-20%;height:140%;left:{W//2 - 8}px;width:16px;background:{acc};transform:rotate(12deg)"></div>',
                  f'<div class="abs" style="bottom:40px;left:36px">{chip(l1, "#000", fit(l1, W*.38, 60, "mont"), f"color:#fff;border-color:{acc}")}</div>',
                  f'<div class="abs" style="bottom:40px;right:36px">{chip(l2, "#000", fit(l2, W*.38, 60, "mont"), f"color:#fff;border-color:{acc}")}</div>']
        d = int(300 * u) if v else 190
        o += [f'<div class="abs vs" style="left:{W//2 - d//2}px;top:{H//2 - d//2}px;width:{d}px;height:{d}px;background:{acc}">{txt("VS", int(d*.5), "#fff")}</div>']
        if tag:
            o += [f'<div class="abs" style="{"top:" + str(int(H*.47)) + "px;left:40px" if v else "top:36px;left:" + str(W//2 - 160) + "px"}">{chip(tag, "#fff", 70 if v else 46, "color:#000;transform:rotate(-12deg)")}</div>']
    elif st == "callout":
        x, y = t.get("at" if v else "ath", t.get("at", [50, 50])); r = t.get("r", 150) * (1 if v else .6)
        o += [img(t["bg"], f"object-position:{pos}", "full"), '<div class="full" style="background:linear-gradient(180deg,#000a,#0000 30%)"></div>']
        cx, cy = W * x / 100, H * y / 100
        o += [f'<svg class="abs" style="left:{cx - r*1.3}px;top:{cy - r}px" width="{r*2.6}" height="{r*2}" viewBox="0 0 260 200">'
              f'<ellipse cx="130" cy="100" rx="118" ry="88" fill="none" stroke="#000" stroke-width="22" transform="rotate(-8 130 100)"/>'
              f'<ellipse cx="130" cy="100" rx="118" ry="88" fill="none" stroke="#FF2A2A" stroke-width="12" transform="rotate(-8 130 100)"/>'
              f'<path d="M30 70 Q 120 -6 238 74" fill="none" stroke="#FF2A2A" stroke-width="7" stroke-linecap="round"/></svg>']
        flip = x > 55; aw = int(260 * (1 if v else .7))
        ax = cx - r * 1.3 - aw * .85 if not flip else cx + r * 1.3 - aw * .15
        o += [f'<svg class="abs" style="left:{ax}px;top:{cy - r - aw*.55}px;transform:rotate({35 if not flip else -35}deg) scaleX({-1 if flip else 1})" width="{aw}" height="{int(aw*.6)}" viewBox="0 0 200 120">'
              '<path d="M8 40 Q 80 30 150 70" fill="none" stroke="#000" stroke-width="30" stroke-linecap="round"/>'
              f'<path d="M8 40 Q 80 30 150 70" fill="none" stroke="{acc}" stroke-width="18" stroke-linecap="round"/>'
              f'<path d="M126 44 L194 92 L118 104 Z" fill="{acc}" stroke="#000" stroke-width="8" stroke-linejoin="round"/></svg>']
        if v:
            o += [f'<div class="abs" style="top:180px;width:100%;text-align:center;transform:rotate(-2deg)">{txt(l1, fit(l1, W*.9, 120, "mont"), "#fff", "mont")}{txt(l2, fit(l2, W*.92, 150, "mont"), acc, "mont")}</div>',
                  f'<div class="abs" style="bottom:170px;width:100%;text-align:center">{chip(tag, "#FF2A2A", 80, "color:#fff")}</div>']
        else:
            o += [f'<div class="abs" style="top:28px;left:34px;transform:rotate(-2deg)">{txt(l1, fit(l1, W*.5, 76, "mont"), "#fff", "mont")}{txt(l2, fit(l2, W*.55, 92, "mont"), acc, "mont")}</div>',
                  f'<div class="abs" style="bottom:36px;left:36px">{chip(tag, "#FF2A2A", 50, "color:#fff")}</div>']
    elif st == "reveal":
        x, y = t.get("at" if v else "ath", t.get("at", [50, 50])); r = t.get("r", 230) * (1 if v else .55)
        cx, cy = W * x / 100, H * y / 100
        o += [img(t["bg"], f"object-position:{pos}", "full"), '<div class="full" style="background:linear-gradient(180deg,#000c,#0000 28%,#0000 66%,#000e)"></div>',
              f'<div class="abs" style="left:{cx - r}px;top:{cy - r}px;width:{2*r}px;height:{2*r}px;border-radius:50%;backdrop-filter:blur({int(26*u) if v else 14}px) brightness(.9);'
              f'border:{int(12*u) if v else 7}px dashed {acc};box-shadow:0 0 0 {int(10*u) if v else 6}px #000"></div>',
              f'<div class="abs" style="left:{cx - r}px;top:{cy - r}px;width:{2*r}px;height:{2*r}px;display:flex;align-items:center;justify-content:center">{txt("?", int(r*1.4), acc, stroke=int(r*.12))}</div>']
        if t.get("_cut"):
            o += [img(t["_cut"], f"bottom:0;left:-20px;height:{int(H*(.40 if v else .78))}px;max-width:{int(W*(.6 if v else .38))}px;{outline(acc, 7 if v else 5)}", "abs")]
        if v:
            o += [f'<div class="abs" style="top:170px;width:100%;text-align:center">{txt(l1, fit(l1, W*.9, 130), "#fff")}</div>',
                  f'<div class="abs" style="bottom:200px;right:40px;text-align:right;transform:rotate(-3deg)">{txt(l2, fit(l2, W*.6, 140), acc)}</div>']
        else:
            o += [f'<div class="abs" style="top:24px;left:34px">{txt(l1, fit(l1, W*.6, 92), "#fff")}</div>',
                  f'<div class="abs" style="bottom:30px;right:34px;text-align:right">{txt(l2, fit(l2, W*.5, 96), acc)}</div>']
    elif st == "cinema":
        bar = 250 if v else 0
        o += [img(t["bg"], f"object-position:{pos};filter:contrast(1.18) saturate(1.25)", "full"),
              '<div class="full" style="background:radial-gradient(ellipse at 50% 45%, #0000 40%, #000c 100%)"></div>']
        if v:
            o += [f'<div class="abs" style="top:0;left:0;width:100%;height:{bar}px;background:#000"></div>',
                  f'<div class="abs" style="bottom:0;left:0;width:100%;height:{int(H*.27)}px;background:linear-gradient(180deg,#0000,#000 30%)"></div>',
                  f'<div class="abs" style="bottom:{int(H*.075)}px;width:100%;text-align:center">'
                  f'{txt(l1, fit(l1, W*.8, 70, "bebas"), "#fff", "bebas", 0, "letter-spacing:.32em")}'
                  f'<div style="width:180px;height:6px;background:{acc};margin:18px auto"></div>'
                  f'{txt(l2, fit(l2, W*.92, 230, "bebas"), acc, "bebas", 0, "text-shadow:0 8px 30px #000")}</div>',
                  f'<div class="abs" style="top:{bar//2 - 30}px;left:50px">{chip(tag, "transparent", 44, f"color:#fff;border-color:{acc};letter-spacing:.2em")}</div>']
        else:
            o += ['<div class="full" style="background:linear-gradient(90deg,#000e,#0000 60%)"></div>',
                  '<div class="abs" style="top:0;width:100%;height:56px;background:#000"></div><div class="abs" style="bottom:0;width:100%;height:56px;background:#000"></div>',
                  f'<div class="abs" style="left:56px;top:{int(H*.36)}px">{txt(l1, fit(l1, W*.5, 52, "bebas"), "#fff", "bebas", 0, "letter-spacing:.3em")}'
                  f'<div style="width:120px;height:5px;background:{acc};margin:12px 0"></div>{txt(l2, fit(l2, W*.6, 150, "bebas"), acc, "bebas", 0, "text-shadow:0 6px 24px #000")}</div>',
                  f'<div class="abs" style="top:11px;left:56px">{chip(tag, "transparent", 26, f"color:#fff;border-color:{acc};letter-spacing:.2em;padding:2px 14px")}</div>']
    elif st == "stack":
        o += [img(t["bg"][:-4] + "_blur.jpg"), f'<div class="full" style="background:{dark};opacity:.55"></div>']
        if v:
            cw, ch, x0 = int(W*.88), int(H*.33), int(W*.06)
            o += [img(t["bg"], f"left:{x0}px;top:{int(H*.17)}px;width:{cw}px;height:{ch}px;object-position:{pos};transform:rotate(-2deg)", "abs card"),
                  img(t["in"], f"left:{x0}px;top:{int(H*.56)}px;width:{cw}px;height:{ch}px;object-position:{ipos};transform:rotate(2deg)", "abs card"),
                  f'<div class="abs" style="left:{x0 + 30}px;top:{int(H*.17) - 40}px">{chip(l1, "#fff", fit(l1, W*.7, 74, "mont"), "color:#000;transform:rotate(-4deg)")}</div>',
                  f'<div class="abs" style="right:{x0 + 30}px;top:{int(H*.56) + ch - 50}px">{chip(l2, acc, fit(l2, W*.7, 84, "mont"), "color:#000;transform:rotate(3deg)")}</div>',
                  f'<div class="abs vs" style="left:{W//2 - 85}px;top:{int(H*.505) - 85}px;width:170px;height:170px;background:{acc}">{txt("↓", 120, "#fff")}</div>',
                  f'<div class="abs" style="top:70px;width:100%;text-align:center">{txt(tag, fit(tag, W*.9, 120), "#fff")}</div>']
        else:
            cw, ch = int(W*.44), int(H*.6)
            o += [img(t["bg"], f"left:{int(W*.04)}px;top:{int(H*.25)}px;width:{cw}px;height:{ch}px;object-position:{pos};transform:rotate(-2deg)", "abs card"),
                  img(t["in"], f"left:{int(W*.52)}px;top:{int(H*.25)}px;width:{cw}px;height:{ch}px;object-position:{ipos};transform:rotate(2deg)", "abs card"),
                  f'<div class="abs" style="left:{int(W*.06)}px;top:{int(H*.25) + ch - 30}px">{chip(l1, "#fff", fit(l1, W*.38, 46, "mont"), "color:#000")}</div>',
                  f'<div class="abs" style="left:{int(W*.55)}px;top:{int(H*.25) + ch - 30}px">{chip(l2, acc, fit(l2, W*.38, 50, "mont"), "color:#000")}</div>',
                  f'<div class="abs vs" style="left:{W//2 - 60}px;top:{int(H*.55) - 60}px;width:120px;height:120px;background:{acc}">{txt("→", 84, "#fff")}</div>',
                  f'<div class="abs" style="top:22px;width:100%;text-align:center">{txt(tag, fit(tag, W*.9, 92), "#fff")}</div>']
    return "\n  ".join(o)


def page(W, H, items, v):
    scenes = "".join(f'\n<div id="th{i}" class="clip th" data-start="{i}" data-duration="1" data-track-index="{i}">\n  {scene(t, W, H, v)}\n</div>'
                     for i, t in enumerate(items))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Bebas+Neue&family=Montserrat:wght@900&display=block" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
#root {{ position: relative; width: 100%; height: 100%; font-family: "Montserrat", sans-serif; font-weight: 900; }}
.th {{ position: absolute; inset: 0; overflow: hidden; background: #000; }}
.full {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
.abs {{ position: absolute; }}
.cov {{ width: {W}px; height: {H}px; object-fit: cover; }}
img.abs:not(.cov):not(.card) {{ object-fit: contain; object-position: 50% 100%; }}
.t {{ line-height: 1.0; white-space: nowrap; paint-order: stroke fill; letter-spacing: -0.01em; text-transform: uppercase; }}
.chip {{ display: inline-block; font-family: "Montserrat"; font-weight: 900; color: #000; padding: .08em .45em .14em; border-radius: .28em; border: {8 if H > W else 5}px solid #000; white-space: nowrap; box-shadow: 0 {10 if H > W else 6}px 0 rgba(0,0,0,.55); text-transform: uppercase; }}
.rays {{ background: repeating-conic-gradient(from 0deg at 50% 42%, rgba(255,255,255,.13) 0deg 7deg, rgba(255,255,255,0) 7deg 16deg); }}
.vs {{ border-radius: 50%; border: {12 if H > W else 8}px solid #000; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 0 {8 if H > W else 5}px #fff, 0 16px 40px rgba(0,0,0,.6); }}
.seam {{ box-shadow: 0 0 0 6px #000; }}
.card {{ object-fit: cover; border-radius: {36 if H > W else 22}px; border: {12 if H > W else 8}px solid #fff; box-shadow: 0 24px 60px rgba(0,0,0,.7); }}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{len(items)}" data-width="{W}" data-height="{H}">{scenes}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
window.__timelines["main"] = tl;
</script>
</body></html>
"""


styles = [t.get("style", "callout") for t in spec]
if len(set(styles)) < len(styles):
    print("WARN: styles repeat within this video:", styles)
for sub, W, H, vert in (("vertical", 1080, 1920, True), ("landscape", 1280, 720, False)):
    d = os.path.join(proj, sub); a = os.path.join(d, "assets")
    os.makedirs(a, exist_ok=True)
    for t in spec:
        for k in ("bg", "in"):
            if t.get(k):
                with open(os.path.join(proj, "assets", t[k]), "rb") as x, open(os.path.join(a, t[k]), "wb") as y:
                    y.write(x.read())
        if t.get("cut"):
            t["_cut"] = cut_png(t, os.path.join(proj, "assets"))
            with open(os.path.join(proj, "assets", t["_cut"]), "rb") as x, open(os.path.join(a, t["_cut"]), "wb") as y:
                y.write(x.read())
        b = os.path.join(a, t["bg"][:-4] + "_blur.jpg")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", os.path.join(proj, "assets", t["bg"]), "-vf",
                        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=40,eq=brightness=-0.22", b], check=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page(W, H, spec, vert))
print("built", len(spec), "thumbnails, styles:", ",".join(styles))
