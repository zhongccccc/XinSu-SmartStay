import sys, time
import cv2
sys.path.insert(0, '/opt/zhikong/face')
from facekit.config import Config
from facekit.pipeline import FaceVerifier

v = FaceVerifier(Config.load('/opt/zhikong/face/config.yaml'))
idb = cv2.imread('/tmp/id_real.jpg')
h, w = idb.shape[:2]
f = 400.0 / min(h, w)
idb = cv2.resize(idb, (int(w*f), int(h*f)), interpolation=cv2.INTER_CUBIC)
live = cv2.imread('/tmp/live_pass.jpg')

t = time.time(); ext = v.embed_id_photo(idb); id_ms = (time.time()-t)*1000
print('证件照特征（只算一次）: %.0f ms' % id_ms)

for n in (2, 3):
    frames = [live]*n
    t = time.time(); r = v.verify_fast(idb, frames, id_embedding=ext.embedding)
    ms = (time.time()-t)*1000
    print('  缓存证件照后 %d 帧: %.0f ms  结论=%s 分数=%.3f' % (n, ms, r.decision, r.score))
