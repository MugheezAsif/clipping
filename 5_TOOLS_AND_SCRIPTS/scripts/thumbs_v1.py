"""Build MrBeast-style thumbnails (vertical 1080x1920 Shorts cover + 1280x720 YouTube) as HyperFrames still projects.

usage: python thumbs.py <thumbs.json> <project_dir>   (project_dir/assets holds the graded frames)
then:  npx hyperframes snapshot --at 0.5,1.5,... in project_dir/vertical and project_dir/landscape
"""
import html, json, os, sys

spec = json.load(open(sys.argv[1], encoding="utf-8"))
proj = sys.argv[2]
esc = lambda s: html.escape(s, quote=True)

ARROW = ('<svg viewBox="0 0 200 120" width="{w}" height="{h}"><path d="M8 70 Q 70 10 150 48" fill="none" stroke="#000" '
         'stroke-width="30" stroke-linecap="round"/><path d="M8 70 Q 70 10 150 48" fill="none" stroke="#FF2A2A" stroke-width="18" '
         'stroke-linecap="round"/><path d="M128 18 L192 58 L122 86 Z" fill="#FF2A2A" stroke="#000" stroke-width="8" stroke-linejoin="round"/></svg>')


def fit(text, maxw, base, k=0.74):
    return int(min(base, maxw / (max(len(text), 1) * k)))


def page(W, H, items, vertical):
    scenes = []
    for i, t in enumerate(items):
        v = t["v"] if vertical else t["h"]
        maxw = 980 if vertical else 700
        f1, f2 = fit(t["l1"], maxw, 150 if vertical else 104), fit(t["l2"], maxw, 175 if vertical else 120)
        inset_size = 430 if vertical else 300
        scenes.append(f"""
<div id="th{i}" class="clip th" data-start="{i}" data-duration="1" data-track-index="{i}">
  {f'<img class="bg" src="assets/{t["bg"][:-4]}_blur.jpg" /><img class="bgv" src="assets/{t["bg"]}" style="top:{v.get("top", 430)}px; height:{H - v.get("top", 430)}px; object-position:{v["bgpos"]}" />' if vertical else f'<img class="bg" src="assets/{t["bg"]}" style="object-position:{v["bgpos"]}" />'}
  <div class="shade"></div>
  <div class="head" style="left:{v['head'][0]}px; top:{v['head'][1]}px; width:{maxw + 40}px; text-align:{v.get('align', 'center')}">
    <div class="l1" style="font-size:{f1}px">{esc(t['l1'])}</div>
    <div class="l2" style="font-size:{f2}px">{esc(t['l2'])}</div>
  </div>
  <div class="inset" style="left:{v['inset'][0]}px; top:{v['inset'][1]}px; width:{inset_size}px; height:{inset_size}px">
    <img src="assets/{t['in']}" style="object-position:{t.get('inpos', '50% 50%')}" />
  </div>
  {'' if vertical or not v.get('arrow') else ''}<div class="arrow" {'hidden' if vertical else ''} style="left:{v['arrow'][0]}px; top:{v['arrow'][1]}px; transform: rotate({v['arrow'][2]}deg)">{ARROW.format(w=260 if vertical else 190, h=156 if vertical else 114)}</div>
  <div class="badge" style="left:{v['badge'][0]}px; top:{v['badge'][1]}px; font-size:{86 if vertical else 60}px">{esc(t['badge'])}</div>
</div>""")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
#root {{ position: relative; width: 100%; height: 100%; font-family: "Montserrat", sans-serif; font-weight: 900; }}
.th {{ position: absolute; inset: 0; overflow: hidden; }}
.bg {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
.bgv {{ position: absolute; left: 0; width: {W}px; object-fit: cover; box-shadow: 0 -20px 60px rgba(0,0,0,.8); }}
.shade {{ position: absolute; inset: 0; background: linear-gradient({'180deg' if vertical else '90deg'}, rgba(0,0,0,.62) 0%, rgba(0,0,0,0) 42%, rgba(0,0,0,0) 70%, rgba(0,0,0,.35) 100%); }}
.head {{ position: absolute; transform: rotate(-3deg); line-height: 1.0; }}
.l1, .l2 {{ white-space: nowrap; -webkit-text-stroke: {20 if vertical else 14}px #000; paint-order: stroke fill; text-shadow: 0 {12 if vertical else 8}px 0 rgba(0,0,0,.7); letter-spacing: -0.01em; }}
.l1 {{ color: #fff; }}
.l2 {{ color: #FFE500; }}
.inset {{ position: absolute; border-radius: 50%; overflow: hidden; border: {14 if vertical else 10}px solid #fff; box-shadow: 0 0 0 {10 if vertical else 7}px #FF2A2A, 0 18px 40px rgba(0,0,0,.6); }}
.inset img {{ width: 100%; height: 100%; object-fit: cover; }}
.arrow {{ position: absolute; transform-origin: 50% 50%; }}
.badge {{ position: absolute; color: #fff; background: #FF2A2A; padding: 10px 26px 14px; border-radius: 22px; border: {8 if vertical else 6}px solid #000; transform: rotate(6deg); box-shadow: 0 12px 0 rgba(0,0,0,.55); white-space: nowrap; }}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{len(items)}" data-width="{W}" data-height="{H}">
{''.join(scenes)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
window.__timelines["main"] = tl;
</script>
</body></html>
"""


for sub, W, H, vert in (("vertical", 1080, 1920, True), ("landscape", 1280, 720, False)):
    d = os.path.join(proj, sub)
    os.makedirs(os.path.join(d, "assets"), exist_ok=True)
    for t in spec:
        for k in ("bg", "in", "blur"):
            if k == "blur":
                t_b = t["bg"][:-4] + "_blur.jpg"
                if not os.path.exists(os.path.join(d, "assets", t_b)):
                    import subprocess
                    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", os.path.join(proj, "assets", t["bg"]),
                                    "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=45,eq=brightness=-0.25",
                                    os.path.join(d, "assets", t_b)], check=True)
                continue
            src = os.path.join(proj, "assets", t[k])
            dst = os.path.join(d, "assets", t[k])
            with open(src, "rb") as a, open(dst, "wb") as b:   # always refresh, never keep stale copies
                b.write(a.read())
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page(W, H, spec, vert))
    for f in ("hyperframes.json", "package.json"):
        s = os.path.join(proj, "..", spec[0].get("_scaffold_from", "c1_one_dollar_bunker"), f)
        if os.path.exists(s):
            open(os.path.join(d, f), "w", encoding="utf-8").write(open(s, encoding="utf-8").read())
    print("built", d)
