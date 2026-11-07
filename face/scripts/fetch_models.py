"""下载所需模型。

    python scripts/fetch_models.py            # 下载推荐组合（YuNet + ArcFace INT8）
    python scripts/fetch_models.py --all      # 外加 YOLOv5-face 与 FP32 版本

模型来源：
  * SpacemiT Model Zoo  https://archive.spacemit.com/spacemit-ai/BRDK/Model_Zoo/CV/
  * OpenCV Zoo (YuNet)  https://github.com/opencv/opencv_zoo

如果板端访问 GitHub 慢，YuNet 也可以手动拷进 models/。
"""

from __future__ import annotations

import argparse
import os
import urllib.request

SPACEMIT = "https://archive.spacemit.com/spacemit-ai/BRDK/Model_Zoo/CV"
SPACEMIT_NEW = "https://archive.spacemit.com/spacemit-ai/model_zoo/vision"
OPENCV_ZOO = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_detection_yunet/face_detection_yunet_2023mar.onnx"
)

CORE = [
    (OPENCV_ZOO, "face_detection_yunet_2023mar.onnx"),
    # buffalo_l 的识别模型：官方人脸应用实际用的就是这个
    (f"{SPACEMIT_NEW}/buffalo_l/w600k_r50.q.onnx", "w600k_r50.q.onnx"),
]
EXTRA = [
    (f"{SPACEMIT}/ArcFace/arcface_mobilefacenet_cut.q.onnx", "arcface_mobilefacenet_cut.q.onnx"),
    (f"{SPACEMIT}/YOLOv5-face/yolov5n-face_320_cut.q.onnx", "yolov5n-face_320_cut.q.onnx"),
    (f"{SPACEMIT}/YOLOv5-face/yolov5n-face_320_cut.onnx", "yolov5n-face_320_cut.onnx"),
    (f"{SPACEMIT}/ArcFace/arcface_mobilefacenet_cut.onnx", "arcface_mobilefacenet_cut.onnx"),
]


def fetch(url: str, dst: str) -> None:
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        print(f"skip  {os.path.basename(dst)}")
        return
    try:
        urllib.request.urlretrieve(url, dst)
        print(f"ok    {os.path.basename(dst):40s} {os.path.getsize(dst):>10,} B")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL  {os.path.basename(dst)}: {exc}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "models"))
    args = ap.parse_args()

    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    for url, name in CORE + (EXTRA if args.all else []):
        fetch(url, os.path.join(out, name))


if __name__ == "__main__":
    main()
