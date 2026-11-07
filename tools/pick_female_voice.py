import wave, os
import numpy as np
import sherpa_onnx

dir_ = r'E:\zhikong\tmp_voice\aishell3'
model = os.path.join(dir_, 'vits-aishell3.onnx')

cfg = sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model=model,
            lexicon=os.path.join(dir_, 'lexicon.txt'),
            tokens=os.path.join(dir_, 'tokens.txt')),
        num_threads=2),
    max_num_sentences=1)
tts = sherpa_onnx.OfflineTts(cfg)
print('speakers =', tts.num_speakers, ' sr =', tts.sample_rate)


def f0(samples, sr):
    x = np.asarray(samples, dtype=np.float32)
    # 取中间 0.4s，估计基频（自相关）
    n = int(0.4 * sr)
    if len(x) < n * 2:
        n = len(x) // 2
    seg = x[len(x)//2 - n//2: len(x)//2 + n//2]
    seg = seg - seg.mean()
    if np.max(np.abs(seg)) < 1e-4:
        return 0.0
    corr = np.correlate(seg, seg, 'full')[len(seg)-1:]
    lo, hi = int(sr/300), int(sr/70)
    if hi >= len(corr):
        hi = len(corr) - 1
    idx = lo + int(np.argmax(corr[lo:hi]))
    return sr / idx if idx else 0.0


text = '欢迎入住芯宿智选智慧酒店，请将身份证放在读卡区'
results = []
for sid in range(0, 16):
    a = tts.generate(text, sid=sid, speed=1.0)
    p = f0(a.samples, a.sample_rate)
    results.append((sid, p, a))
    print('  sid=%2d  f0=%5.1f Hz  时长=%.1fs' % (sid, p, len(a.samples)/a.sample_rate))

fem = sorted(results, key=lambda r: -r[1])[:3]
print('\n最像女声的三个: ' + ', '.join('sid=%d(%.0fHz)' % (s, p) for s, p, _ in fem))

out = os.path.join(dir_, 'cand')
os.makedirs(out, exist_ok=True)
for i, (sid, p, a) in enumerate(fem, 1):
    path = os.path.join(out, 'cand%d_sid%d.wav' % (i, sid))
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(a.sample_rate)
        w.writeframes((np.clip(np.asarray(a.samples), -1, 1) * 32767).astype(np.int16).tobytes())
    print('  写出', path)
