"""多张照片两两比对：看相似度矩阵 + 拼一张对齐后的对比图。

诊断/验收用。比如怀疑某张照片是不是本人，把三张放一起看矩阵最直观：
同人之间通常 0.5~0.75，异人之间通常 <0.25；如果"异人"也跑到 0.5，
说明阈值必须往上抬。

    python scripts/compare_photos.py 原.png sf.jpg 抓拍.jpg
    python scripts/compare_photos.py a.jpg b.jpg --montage out/montage.jpg
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from facekit.align import align_face  # noqa: E402
from facekit.config import Config  # noqa: E402
from facekit.io_utils import imread_unicode, imwrite_unicode  # noqa: E402
from facekit.matcher import cosine  # noqa: E402
from facekit.pipeline import FaceVerifier  # noqa: E402


def label_of(path: str) -> str:
    return Path(path).stem[:10]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+", help="至少两张图")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--montage", default="out/compare_aligned.jpg", help="对齐图拼图输出路径")
    args = ap.parse_args()

    if len(args.images) < 2:
        print("至少给两张图", file=sys.stderr)
        return 2

    cfg = Config.load(args.config)
    verifier = FaceVerifier(cfg)

    embs: dict[str, np.ndarray] = {}
    crops: list[np.ndarray] = []
    for p in args.images:
        name = label_of(p)
        img = imread_unicode(p)
        faces = verifier.detector.detect(img)
        if not faces or faces[0].kps is None:
            print(f"[skip] {p}: 未检测到人脸")
            continue
        aligned, _, err = align_face(img, faces[0].kps, 112)
        embs[name] = verifier.embedder.embed(aligned)
        tile = aligned.copy()
        cv2.putText(tile, name, (2, 11), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (0, 255, 0), 1)
        crops.append(tile)
        f = faces[0]
        print(f"{name:12s} 框={np.round(f.box).astype(int).tolist()} 检测分={f.score:.3f} 对齐误差={err:.2f}")

    names = list(embs)
    if len(names) < 2:
        print("有效人脸不足两张", file=sys.stderr)
        return 1

    print("\n余弦相似度")
    width = max(12, *(len(n) + 2 for n in names))
    print(" " * width + "".join(f"{n:>{width}s}" for n in names))
    for a in names:
        print(f"{a:{width}s}" + "".join(f"{cosine(embs[a], embs[b]):>{width}.3f}" for b in names))

    if args.montage:
        Path(args.montage).parent.mkdir(parents=True, exist_ok=True)
        imwrite_unicode(args.montage, cv2.hconcat(crops))
        print(f"\n对齐图拼图: {args.montage}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
