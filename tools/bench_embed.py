"""在 K1 上对比：INT8 vs FP32 特征模型、不同线程数的耗时。"""
import time

import cv2
import numpy as np
import onnxruntime as ort

MODELS = {
    'MobileFaceNet-INT8': '/opt/zhikong/face/models/arcface_mobilefacenet_cut.q.onnx',
    'MobileFaceNet-FP32': '/opt/zhikong/face/models/arcface_mobilefacenet_cut.onnx',
    'R50-INT8': '/opt/zhikong/face/models/w600k_r50.q.onnx',
}
blob = np.random.rand(1, 3, 112, 112).astype(np.float32)

for threads in (4, 8):
    print('--- num_threads=%d ---' % threads)
    for name, path in MODELS.items():
        try:
            so = ort.SessionOptions()
            so.intra_op_num_threads = threads
            so.log_severity_level = 3
            t0 = time.time()
            sess = ort.InferenceSession(path, so, providers=['CPUExecutionProvider'])
            load = (time.time() - t0) * 1000
            inp = sess.get_inputs()[0].name
            sess.run(None, {inp: blob})          # 预热
            ts = []
            for _ in range(5):
                t = time.time()
                out = sess.run(None, {inp: blob})
                ts.append((time.time() - t) * 1000)
            dim = out[0].reshape(1, -1).shape[1]
            print('  %-20s 加载 %5.0fms  推理 平均 %6.1fms  最小 %6.1fms  维度 %d' % (
                name, load, sum(ts) / len(ts), min(ts), dim))
        except Exception as e:
            print('  %-20s 失败: %s' % (name, str(e)[:70]))
