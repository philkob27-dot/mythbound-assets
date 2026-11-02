# a soft flow-line texture for the river surface: light ripple streaks along the length, tileable both ways
import numpy as np
from PIL import Image
rng = np.random.default_rng(2026)
W, H = 256, 256
n = rng.standard_normal((H, W))
f = np.fft.fft2(n)
fy = np.fft.fftfreq(H)[:, None]; fx = np.fft.fftfreq(W)[None, :]
# long along y (flow), narrow across x
filt = np.exp(-((fx / 0.09) ** 2 + (fy / 0.005) ** 2))
g = np.real(np.fft.ifft2(f * filt)); g = (g - g.min()) / (g.max() - g.min())
# ripple lines: ridges where the noise crosses levels
lines = np.zeros_like(g)
for lv in (0.5,):
    lines += np.exp(-((g - lv) / 0.03) ** 2)
a = np.clip(lines * 0.55, 0, 1)
x = np.arange(W)[None, :] / W
a *= np.clip(np.minimum(x, 1 - x) / 0.15, 0, 1)
img = np.dstack([np.ones((H, W, 3)) * 255, a[..., None] * 255]).astype(np.uint8)
Image.fromarray(img, "RGBA").save("RiverFlow.png")
bg = np.zeros((H, W, 3)); bg[:] = (25, 110, 150)
prev = bg * (1 - a[..., None]) + 255 * a[..., None]
Image.fromarray(np.hstack([prev, prev]).astype(np.uint8)).save("RiverFlow_preview.png")
print("ok")
