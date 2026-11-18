"""Per-shot layout decision for 9:16 (OpenShorts/OpusClip-style rules). Run with the clipping venv (needs opencv).

usage: python reframe.py <video> '<json [[a,b],...]>'  -> prints JSON: per segment a list of shots
  [[a, b, "face", cx], [a, b, "panel", null], ...]   cx = face centre as a fraction of frame width
Rules: split segments on hard cuts; a shot gets "face" when one subject (or a tight group) is found in >=40% of
samples and stays within a 0.22-wide band; otherwise "panel" (blurred fill + 8:9 panel, safe for groups/wide shots).
"""
import json, os, sys, urllib.request
import cv2, numpy as np

MODEL = os.path.join(os.path.dirname(os.path.dirname(sys.executable)), "yunet.onnx")
if not os.path.exists(MODEL):
    urllib.request.urlretrieve("https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx", MODEL)
cap = cv2.VideoCapture(sys.argv[1]); segs = json.loads(sys.argv[2])
W = cap.get(cv2.CAP_PROP_FRAME_WIDTH); H = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
sw, sh = 640, int(640 * H / W)
det = cv2.FaceDetectorYN.create(MODEL, "", (sw, sh), 0.75)


def frame(t):
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000); ok, f = cap.read()
    return cv2.resize(f, (sw, sh)) if ok else None


out = []
for a, b in segs:
    ts = np.arange(a + 0.05, b - 0.05, 0.25); samples = []
    prev = None
    for t in ts:
        f = frame(t)
        if f is None:
            continue
        hsv = cv2.calcHist([cv2.cvtColor(f, cv2.COLOR_BGR2HSV)], [0, 1], None, [16, 16], [0, 180, 0, 256]); cv2.normalize(hsv, hsv)
        cut = prev is not None and cv2.compareHist(prev, hsv, cv2.HISTCMP_CORREL) < 0.55
        prev = hsv
        _, faces = det.detect(f)
        cx = None
        if faces is not None and len(faces):
            big = sorted(faces, key=lambda r: -r[2] * r[3])
            main = big[0]; xs = [r[0] + r[2] / 2 for r in big if r[2] * r[3] > 0.35 * main[2] * main[3]]
            if (max(xs) - min(xs)) / sw < 0.30:  # one subject or tight group fits a 9:16 crop
                cx = float(np.mean(xs) / sw)
        samples.append((t, cut, cx))
    shots, cur = [], []
    for s in samples:
        if s[1] and cur:
            shots.append(cur); cur = []
        cur.append(s)
    if cur:
        shots.append(cur)
    res = []
    for k, sh_ in enumerate(shots):
        s0 = a if k == 0 else round(sh_[0][0] - 0.125, 3)
        s1 = b if k == len(shots) - 1 else round(shots[k + 1][0][0] - 0.125, 3)
        xs = [c for _, _, c in sh_ if c is not None]
        if len(xs) >= 0.5 * len(sh_) and (max(xs) - min(xs)) < 0.22 and s1 - s0 >= 2.0 and 0.12 < float(np.median(xs)) < 0.88:
            res.append([s0, s1, "face", round(float(np.median(xs)), 3)])
        else:
            res.append([s0, s1, "panel", None])
    merged = []  # merge neighbours with the same layout & similar crop
    for r in res:
        if merged and (r[1] - r[0] < 1.0 or (merged[-1][2] == r[2] and (r[2] == "panel" or abs(merged[-1][3] - r[3]) < 0.12))):
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    out.append(merged)
print(json.dumps(out))
