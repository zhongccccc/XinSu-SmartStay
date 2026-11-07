"""把一张证件照"拍成"一体机现场效果（命令行封装）。

用法：
    python scripts/simulate_capture.py --src samples/id_photo_sample.png \
        --out samples/live_sim.jpg --face-height 280 --yaw 6 --brightness 0.85
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from facekit.io_utils import imread_unicode, imwrite_unicode  # noqa: E402
from facekit.simulate import make_capture  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--face-height", type=float, default=280)
    ap.add_argument("--yaw", type=float, default=5.0)
    ap.add_argument("--brightness", type=float, default=0.85)
    ap.add_argument("--blur", type=float, default=2.0)
    ap.add_argument("--noise", type=float, default=6.0)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    img = make_capture(
        imread_unicode(args.src),
        width=args.width,
        height=args.height,
        face_height=args.face_height,
        yaw=args.yaw,
        brightness=args.brightness,
        blur=args.blur,
        noise=args.noise,
        seed=args.seed,
    )
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    imwrite_unicode(args.out, img)
    print(f"saved {args.out}  {img.shape[1]}x{img.shape[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
