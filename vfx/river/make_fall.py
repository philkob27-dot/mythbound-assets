import numpy as np
from PIL import Image
rng = np.random.default_rng(3112026)
W, H = 256, 512
# tileable 1D-ish noise: sum of sines along x (streak columns), along y with integer periods for tiling
x = np.arange(W)[None, :] / W
y = np.arange(H)[:, None] / H
a = np.zeros((H, W))
# streak columns: many thin vertical bands with random phase, each modulated along y (tileable)
for k in range(70):
    cx = rng.random()
    w = rng.uniform(0.004, 0.02)
    d = np.minimum(np.abs(x - cx), 1 - np.abs(x - cx))
    band = np.exp(-(d / w) ** 2)
    per = rng.integers(1, 4)
    ph = rng.random()
    mod = 0.55 + 0.45 * np.sin(2 * np.pi * (per * y + ph))
    # broken streak: gaps
    gs = np.sin(2 * np.pi * (rng.integers(2, 6) * y + rng.random())); gap = np.clip((gs + 0.35) / 0.5, 0, 1) ** 2
    a += band * mod * gap * rng.uniform(0.4, 1.0)
# soft body behind streaks
body = 0.28 + 0.12 * np.sin(2 * np.pi * (3 * x + 0.2)) * np.sin(2 * np.pi * (2 * y))
a = np.clip(a * 0.85 + body, 0, 1)
# fine grain, tileable via fft-filtered noise
n = rng.standard_normal((H, W))
f = np.fft.fft2(n)
fy = np.fft.fftfreq(H)[:, None]; fx = np.fft.fftfreq(W)[None, :]
filt = np.exp(-((fx / 0.08) ** 2 + (fy / 0.02) ** 2))
g = np.real(np.fft.ifft2(f * filt)); g = (g - g.min()) / (g.max() - g.min())
a = np.clip(a * (0.7 + 0.6 * g), 0, 1)
# fade the side edges so the sheet has no hard border
edge = np.clip(np.minimum(x, 1 - x) / 0.12, 0, 1)
a = a * edge
rgb = np.ones((H, W, 3)) * 255
img = np.dstack([rgb, a[..., None] * 255]).astype(np.uint8)
Image.fromarray(img, "RGBA").save("RiverFall.png")
# preview on blue
bg = np.zeros((H, W, 3)); bg[:] = (25, 110, 150)
prev = bg * (1 - a[..., None]) + np.array([210, 240, 255]) * a[..., None]
Image.fromarray(np.vstack([prev, prev]).astype(np.uint8)).save("RiverFall_preview.png")
print("ok", a.mean())
