# Crops the staged portrait captures to the frame (3:4ish, 2.8 x 3.6 studs) and grades them like old oil
# portraits: a soft painterly smoothing, a warm varnish, a darker vignette and a faint canvas weave.
import sys, os, math, random
from PIL import Image, ImageFilter, ImageEnhance, ImageChops, ImageDraw
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
RAW, OUT = os.path.join(HERE, "raw"), os.path.join(HERE, "final")
W, H = 560, 720
def canvas_weave(w, h, seed=3):
    rng = np.random.default_rng(seed)
    x = np.arange(w)[None, :]; y = np.arange(h)[:, None]
    weave = 0.5 + 0.25 * np.sin(x * 1.9) * np.sin(y * 1.7) + 0.25 * rng.random((h, w))
    return Image.fromarray((weave * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
def grade(name):
    im = Image.open(os.path.join(RAW, name + ".jpg")).convert("RGB")
    cx = 775 if name != "Portrait_Vane" else 790
    top, ch = 150, 760
    cw = int(ch * W / H)
    im = im.crop((cx - cw // 2, top, cx + cw // 2, top + ch)).resize((W, H), Image.LANCZOS)
    # painterly: median smoothing a few times keeps edges, then a light unsharp
    p = im.filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.ModeFilter(3))
    p = Image.blend(im, p, 0.65).filter(ImageFilter.UnsharpMask(2, 60, 2))
    a = np.asarray(p).astype(np.float32) / 255.0
    # warm varnish: lift reds, sink blues, a gentle S curve
    a[..., 0] = a[..., 0] * 1.06 + 0.02
    a[..., 1] = a[..., 1] * 1.0 + 0.005
    a[..., 2] = a[..., 2] * 0.86
    a = np.clip(a, 0, 1)
    a = a * a * (3 - 2 * a) * 0.55 + a * 0.45
    # vignette, stronger at the bottom corners
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.4) / (H * 0.75)) ** 2)
    v = np.clip(1.2 - d ** 2.4, 0.35, 1.0)[..., None]
    a = a * v
    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    out = ImageEnhance.Color(out).enhance(0.88)
    weave = canvas_weave(W, H).convert("RGB")
    out = ImageChops.overlay(out, Image.blend(Image.new("RGB", (W, H), (128, 128, 128)), weave, 0.22))
    out.save(os.path.join(OUT, name + ".png"))
if __name__ == "__main__":
    names = [f[:-4] for f in sorted(os.listdir(RAW)) if f.endswith(".jpg")]
    for n in names:
        grade(n)
    # contact sheet
    sheet = Image.new("RGB", (W // 2 * 5, H // 2 * 3), (20, 20, 20))
    for i, n in enumerate(names):
        t = Image.open(os.path.join(OUT, n + ".png")).resize((W // 2, H // 2))
        sheet.paste(t, ((i % 5) * W // 2, (i // 5) * H // 2))
    sheet.save(os.path.join(HERE, "sheet.png"))
    print(len(names))
