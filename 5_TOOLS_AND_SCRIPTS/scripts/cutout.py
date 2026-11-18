"""Cut the subject out of a frame (transparent PNG) for sticker-style thumbnails. Runs in ~/.clipping/env.

usage: python cutout.py <in.jpg> <out.png> [model]   (default: u2net_human_seg for people; objects: isnet-general-use)
Models download once to ~/.clipping/models.
"""
import os, sys
os.environ.setdefault("U2NET_HOME", os.path.expanduser("~/.clipping/models"))
from rembg import new_session, remove
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
model = sys.argv[3] if len(sys.argv) > 3 else "u2net_human_seg"
img = Image.open(src).convert("RGB")
out = remove(img, session=new_session(model), post_process_mask=True)
bbox = out.getchannel("A").point(lambda a: 255 if a > 40 else 0).getbbox()
out = out.crop((max(bbox[0] - 8, 0), max(bbox[1] - 8, 0), min(bbox[2] + 8, out.width), min(bbox[3] + 8, out.height))) if bbox else out
out.save(dst)
print(os.path.basename(dst), "subject bbox:", bbox)
