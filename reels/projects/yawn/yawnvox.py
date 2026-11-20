"""Source-filter yawn synthesizer: inhale -> voiced 'aaah' (high, gliding down) -> 'ohh' -> closed-mouth 'mmm' + vocal fry.
Time-varying formant resonators (block-wise IIR) on a glottal harmonic source plus aspiration noise."""
import numpy as np
from scipy import signal

SR = 48000
_rng = np.random.default_rng(21)

KINDS = {   # base f0 (Hz), formant scale, breathiness, vibrato depth, vibrato rate, duration scale
    "man":    (108, 1.00, 0.55, 0.015, 5.0, 1.00),
    "woman":  (215, 1.12, 0.60, 0.018, 5.5, 0.95),
    "dadi":   (195, 1.10, 0.75, 0.045, 7.0, 1.10),
    "kid":    (290, 1.25, 0.50, 0.020, 6.0, 0.80),
    "mascot": (400, 1.30, 0.30, 0.030, 6.5, 0.90),
    "dog":    (520, 1.45, 0.85, 0.060, 8.0, 0.70),
    "chimp":  (330, 1.30, 0.90, 0.050, 9.0, 0.75),
}

def _interp(t, pts):
    xs, ys = zip(*pts); return np.interp(t, xs, ys)

def _resonate(x, F, Bw, block=240):
    y = np.zeros_like(x); zi = np.zeros(2)
    for i in range(0, len(x), block):
        f = float(F[min(i, len(F) - 1)]); bw = float(Bw[min(i, len(Bw) - 1)])
        r = np.exp(-np.pi * bw / SR); th = 2 * np.pi * f / SR
        a = [1.0, -2 * r * np.cos(th), r * r]; b = [(1 - r * r) * 0.5]
        seg, zi = signal.lfilter(b, a, x[i:i + block], zi=zi); y[i:i + block] = seg
    return y

def yawn(kind="man", length=1.0, seed=None):
    """Returns (audio, onset) where onset is the time (s) from the start to the loud voiced 'aaah' -
    place the sound at (visual_yawn_time - onset)."""
    rng = np.random.default_rng(seed) if seed is not None else _rng
    f0b, fs, br, vd, vr, ds = KINDS[kind]
    D = 2.0 * ds * length
    n = int(SR * D); t = np.arange(n) / SR; k = t / D
    inh = 0.24                                    # fraction spent inhaling
    # ---- pitch contour (relative to base): starts high, glides down, ends in fry
    f0 = f0b * _interp(k, [(0, 1.7), (inh, 1.75), (inh + .05, 2.0), (.45, 1.65), (.7, 1.2), (.85, .95), (1, .75)])
    f0 *= 1 + vd * np.sin(2 * np.pi * vr * t) + 0.012 * signal.lfilter([1], [1, -0.995], rng.normal(size=n)) * 0.05
    ph = 2 * np.pi * np.cumsum(f0) / SR
    nh = int(min(40, (SR / 2.2) / f0.max()))
    src = sum(np.sin(h * ph) / (h ** 1.3) for h in range(1, nh + 1))
    # vocal fry in the last 15%: irregular low pulses
    fry = np.zeros(n); i = int(n * .82)
    while i < n:
        fry[i] = 1.0; i += int(SR / (38 + rng.random() * 25))
    fry = signal.lfilter([1, -0.95], [1], fry) * 3
    voiced_env = _interp(k, [(0, 0), (inh, 0), (inh + .04, .9), (.32, 1), (.6, .85), (.82, .45), (.95, .12), (1, 0)])
    fry_env = _interp(k, [(0, 0), (.8, 0), (.88, .5), (1, 0)])
    glott = src * voiced_env + fry * fry_env
    # ---- aspiration / breath noise: strong during inhale, lighter during voicing
    noise = rng.normal(size=n)
    breath_env = _interp(k, [(0, 0), (.08, .35), (inh * .9, .7), (inh, .45), (.5, .35), (.85, .2), (1, 0)]) * br
    exc = glott + noise * breath_env * 2.2
    # ---- formants: 'h-aa' (inhale, open) -> 'aa' -> 'oh' -> 'mm' (lips closed)
    F1 = fs * _interp(k, [(0, 650), (inh, 760), (.45, 780), (.68, 560), (.82, 420), (1, 280)])
    F2 = fs * _interp(k, [(0, 1150), (inh, 1250), (.45, 1220), (.68, 900), (.82, 820), (1, 1000)])
    F3 = fs * _interp(k, [(0, 2500), (.5, 2600), (1, 2300)])
    B1 = _interp(k, [(0, 160), (.5, 110), (1, 140)]); B2 = _interp(k, [(0, 200), (1, 180)]); B3 = np.full(n, 260)
    out = _resonate(exc, F1, B1) * 1.0 + _resonate(exc, F2, B2) * 0.55 + _resonate(exc, F3, B3) * 0.22
    # closed-mouth nasal 'mmm' at the end: low-passed
    mm = signal.lfilter(*signal.butter(2, 450 / (SR / 2)), out)
    w = np.clip((k - .8) / .15, 0, 1)
    out = out * (1 - w) + mm * w * 2.0
    # gentle lip smack at the very end
    sm = int(n * .985)
    if sm < n - 400: out[sm:sm + 400] += signal.lfilter([1], [1, -.9], rng.normal(size=400)) * np.exp(-np.arange(400) / 60) * .15
    out *= np.minimum(1, t / 0.02) * np.minimum(1, (D - t) / 0.04)
    out = out / (np.max(np.abs(out)) or 1)
    return out, D * (inh + .04)
