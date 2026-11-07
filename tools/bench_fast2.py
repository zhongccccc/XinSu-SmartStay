import sys, time
import cv2
sys.path.insert(0, '/opt/zhikong/face')
from facekit.config import Config
from facekit.pipeline import FaceVerifier

v = FaceVerifier(Config.load('/opt/zhikong/face/config.yaml'))

idb = cv2.imread('/tmp/id_real.jpg')
h, w = idb.shape[:2]
if min(h, w) < 240:
    f = 400.0 / min(h, w)
    idb = cv2.resize(idb, (int(w * f), int(h * f)), interpolation=cv2.INTER_CUBIC)

live = cv2.imread('/tmp/live_pass.jpg')
frames = [live, live, live]

for name, fn in (('verify     ', v.verify), ('verify_fast', v.verify_fast)):
    t = time.time()
    r = fn(idb, frames)
    ms = (time.time() - t) * 1000
    lat = {k: round(val) for k, val in (r.latency_ms or {}).items()}
    print('  %s %5.0f ms | 结论=%s 分数=%.3f | 分项=%s' % (name, ms, r.decision, r.score, lat))
