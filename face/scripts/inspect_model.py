"""Print input/output signature of an ONNX model (works with QDQ quantised models)."""
import sys

import onnxruntime as ort


def main(path: str) -> None:
    so = ort.SessionOptions()
    so.log_severity_level = 3
    sess = ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
    print(f"model: {path}")
    for i in sess.get_inputs():
        print(f"  in : {i.name:20s} {i.shape} {i.type}")
    for o in sess.get_outputs():
        print(f"  out: {o.name:20s} {o.shape} {o.type}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
        print()
