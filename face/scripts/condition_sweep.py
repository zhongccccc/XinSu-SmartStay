"""条件扫描：同一张脸在不同拍摄条件下，相似度和质量门控怎么变。

这是"先摸边界"的工具——真机标定之前，用它确认质量门控的阈值选得合不合理。

    python scripts/condition_sweep.py --id samples/id_photo_sample.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from facekit.config import Config  # noqa: E402
from facekit.io_utils import imread_unicode  # noqa: E402
from facekit.pipeline import FaceVerifier  # noqa: E402
from facekit.simulate import make_capture  # noqa: E402

CASES = [
    ("理想", dict(yaw=0, brightness=1.0, blur=1.0, face_height=320)),
    ("轻微侧脸", dict(yaw=8, brightness=0.95, blur=1.5, face_height=300)),
    ("明显侧脸", dict(yaw=18, brightness=0.95, blur=1.5, face_height=300)),
    ("偏暗", dict(yaw=5, brightness=0.55, blur=2.0, face_height=300)),
    ("逆光过曝", dict(yaw=5, brightness=1.35, blur=2.0, face_height=300)),
    ("运动模糊", dict(yaw=5, brightness=0.9, blur=5.0, face_height=300)),
    ("距离偏远", dict(yaw=5, brightness=0.9, blur=1.5, face_height=150)),
    ("距离过近", dict(yaw=5, brightness=0.9, blur=1.5, face_height=520)),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--id", required=True)
    args = ap.parse_args()

    cfg = Config.load(args.config)
    cfg.match.min_valid_frames = 1
    verifier = FaceVerifier(cfg)
    id_img = imread_unicode(args.id)

    print(f"{'场景':<10}{'分数':>8}{'结论':>8}{'人脸px':>9}{'模糊':>8}{'亮度':>8}{'yaw':>7}{'pitch':>7}  备注")
    for name, kw in CASES:
        frame = make_capture(id_img, **kw)
        res = verifier.verify(id_img, [frame])
        f = res.frames[0]
        if f.score is None:
            print(f"{name:<10}{'--':>8}{res.decision:>8}{'--':>9}{'--':>8}{'--':>8}{'--':>7}{'--':>7}  {f.error}")
            continue
        q = f.quality
        print(
            f"{name:<10}{f.score:>8.3f}{res.decision:>8}{q.face_px:>9.0f}"
            f"{q.blur:>8.0f}{q.brightness:>8.0f}{q.yaw:>7.2f}{q.pitch:>7.2f}  {'、'.join(q.reasons) or 'ok'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
