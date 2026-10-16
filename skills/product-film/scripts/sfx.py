"""Synthesises the UI sound layer from out/cues.json (written by render.mjs) into out/sfx.wav."""
import json, wave, sys
import numpy as np

SR = 44100
cues = json.load(open('out/cues.json'))
out = np.zeros(int((cues['duration'] + 1) * SR), dtype=np.float64)
rnd = np.random.default_rng(5)


def env(n, decay):
    return np.exp(-np.arange(n) / (decay * SR))


def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, 'same')


def put(t, sig):
    i = max(0, int(t * SR))
    j = min(len(out), i + len(sig))
    out[i:j] += sig[:j - i]


def click():
    n = int(.06 * SR); t = np.arange(n) / SR
    return .20 * np.sin(2 * np.pi * 1700 * t) * env(n, .008) + .10 * rnd.standard_normal(n) * env(n, .002)


def key():
    n = int(.03 * SR); t = np.arange(n) / SR
    return .045 * np.sin(2 * np.pi * rnd.uniform(2300, 3100) * t) * env(n, .004)


def ding():
    n = int(.6 * SR); t = np.arange(n) / SR
    return (.09 * np.sin(2 * np.pi * 1318.5 * t) + .06 * np.sin(2 * np.pi * 1975.5 * t)) * env(n, .12)


def impact(amp=.5):
    n = int(1.1 * SR); t = np.arange(n) / SR
    f = 42 + 95 * np.exp(-t / .06)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .28)
    air = lowpass(rnd.standard_normal(n), 24) * env(n, .09) * 1.6
    return amp * (body + .35 * air)


def whoosh(d=.5, amp=.11):
    n = int(d * SR); x = np.linspace(0, 1, n)
    return amp * lowpass(rnd.standard_normal(n), 14) * 3 * np.sin(np.pi * x) ** 2


def riser(d):
    n = int(d * SR); x = np.linspace(0, 1, n)
    tone = np.sin(2 * np.pi * np.cumsum(180 * 2 ** (x * 2.6)) / SR)
    return x ** 2 * (.07 * tone + .22 * lowpass(rnd.standard_normal(n), 8))


for c in cues['sfx']:
    k, t = c['k'], c['t']
    if k == 'click': put(t, click())
    elif k == 'key': put(t, key())
    elif k == 'ding': put(t, ding())
    elif k == 'impact': put(t, impact())
    elif k == 'slam': put(t, impact(.34))
    elif k == 'whoosh': put(t - .25, whoosh())
    elif k == 'riser': put(t, riser(c['d']))

peak = np.abs(out).max()
if peak > .8: out *= .8 / peak
w = wave.open('out/sfx.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
print(f'sfx.wav  {len(cues["sfx"])} cues  peak {min(peak, .8):.2f}')
