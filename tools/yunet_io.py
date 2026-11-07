import numpy as np, onnxruntime as ort, os
p = '/opt/zhikong/face/models/face_detection_yunet_2023mar.onnx'
so = ort.SessionOptions(); so.intra_op_num_threads = 4
sess = ort.InferenceSession(p, so, providers=['CPUExecutionProvider'])
print('输入:')
for i in sess.get_inputs():
    print('  ', i.name, i.shape, i.type)
print('输出:')
for o in sess.get_outputs():
    print('  ', o.name, o.shape, o.type)
