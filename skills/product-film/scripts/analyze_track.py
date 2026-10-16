"""Beat grid and energy map of a music track.

usage: python3 analyze_track.py <audio file>      (needs numpy and ffmpeg)

Prints tempo, the time of beat 0, how far the grid drifts across the track, the energy per
bar, and the biggest jump in energy (usually where the drums come in). Use the numbers to
decide the film's length in bars and which beat the big moment lands on.
"""
import json, subprocess, sys, tempfile, wave, os
import numpy as np

src = sys.argv[1]
tmp = os.path.join(tempfile.mkdtemp(), 't.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ac', '1', '-ar', '22050', tmp], check=True)
w = wave.open(tmp); sr = w.getframerate()
x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
dur = len(x) / sr

hop, n = 128, 1024
fr = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * np.hanning(n)
mag = np.abs(np.fft.rfft(fr, axis=1))
flux = np.maximum(0, np.diff(np.log1p(100 * mag), axis=0)).sum(1)
tt = (np.arange(len(flux)) * hop + n / 2) / sr
fps = sr / hop
k = int(fps)
env = np.maximum(flux - np.convolve(flux, np.ones(k) / k, 'same'), 0)


def comb(bpm, ph, t0=0, t1=None):
    return np.interp(np.arange(ph, t1 or tt[-1], 60 / bpm), tt, env)[int(t0 > 0):].mean()


def fit(lo, hi):
    """Best tempo and phase in a range, then the grid's drift per 10 s window."""
    ac = np.correlate(env, env, 'full')[len(env) - 1:]
    bpms = np.arange(lo, hi, 0.1); lags = 60 * fps / bpms
    rough = bpms[np.argmax([np.interp([l, 2 * l, 4 * l], np.arange(len(ac)), ac).sum() for l in lags])]
    best = (0, rough, 0)
    for b in np.arange(rough - .6, rough + .6, 0.004):
        per = 60 / b
        for ph in np.arange(0, per, per / 60):
            s = comb(b, ph)
            if s > best[0]: best = (s, b, ph)
    score, b, ph = best; per = 60 / b
    drift = []
    for t0 in range(0, int(dur) - 9, 10):
        m = (tt >= t0) & (tt < t0 + 10); offs = np.linspace(-per / 2, per / 2, 61)
        sc = [np.interp(np.arange(ph + np.ceil((t0 - ph) / per) * per + o, t0 + 10, per), tt[m], env[m]).mean() for o in offs]
        drift.append(float(offs[int(np.argmax(sc))] * 1000))
    return score, b, ph, drift


# Autocorrelation often locks onto 2/3 or 3/2 of the real pulse (a 114 BPM track reads as 76).
# The wrong grid shows up as large, cycling drift, so try each octave and keep the steadiest.
fits = [fit(lo, hi) for lo, hi in [(70, 100), (95, 135), (130, 180)]]
score, bpm, phase, drift = min(fits, key=lambda f: (round(float(np.median(np.abs(f[3]))) / 25), -f[0]))
if phase > 30 / bpm: phase -= 60 / bpm            # report the beat nearest t=0
beat = 60 / bpm; bar = 4 * beat

bars = []
for i in range(int((dur - phase) / bar)):
    a, z = int((phase + i * bar) * sr), int((phase + (i + 1) * bar) * sr)
    a = max(a, 0)
    fa, fz = int(max(phase + i * bar, 0) * fps), int((phase + (i + 1) * bar) * fps)
    bars.append((float(np.sqrt((x[a:z] ** 2).mean())), float(mag[fa:fz, 1:8].mean())))
rms = np.array([b[0] for b in bars])
jump = int(np.argmax(rms[1:] / np.maximum(rms[:-1], 1e-4))) + 1

print(f'file      {os.path.basename(src)}   {dur:.1f} s')
print(f'tempo     {bpm:.3f} BPM   beat {beat:.4f} s   bar {bar:.3f} s')
print(f'beat 0    {phase:+.3f} s')
print(f'drift     {" ".join(f"{d:+.0f}" for d in drift)}  ms per 10 s window (|x| < 20 is steady)')
print('other fits: ' + ', '.join(f'{f[1]:.1f} BPM (median drift {np.median(np.abs(f[3])):.0f} ms)' for f in fits))
print('bar  time    loudness  bass')
for i, (r, lo) in enumerate(bars[:48]):
    print(f'{i + 1:3d}  {phase + i * bar:6.2f}  {r:.3f}  {"#" * int(r * 120):<36s} {lo:5.1f}{"   <- biggest lift" if i == jump else ""}')
print(f'biggest lift: bar {jump + 1}, beat {jump * 4}, t = {phase + jump * bar:.2f} s')
print(json.dumps({'bpm': round(float(bpm), 3), 'phase': round(float(phase), 3), 'beat': round(beat, 5), 'liftBeat': jump * 4}))
