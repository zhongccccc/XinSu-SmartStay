"""抓一帧摄像头画面存盘，用于确认设备和构图。

    python scripts/capture_once.py --probe          # 列出可用设备号
    python scripts/capture_once.py --camera 0 --out samples/cap.jpg
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from facekit.io_utils import imwrite_unicode  # noqa: E402


def open_cam(index: int, width: int, height: int):
    for backend in (cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY):
        cap = cv2.VideoCapture(index, backend)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            ok, frame = cap.read()
            if ok and frame is not None:
                return cap, frame
            cap.release()
    return None, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--out", default="samples/webcam_capture.jpg")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--probe", action="store_true")
    args = ap.parse_args()

    if args.probe:
        for i in range(4):
            cap, frame = open_cam(i, args.width, args.height)
            if cap is None:
                print(f"camera {i}: 无")
            else:
                print(f"camera {i}: {frame.shape[1]}x{frame.shape[0]}")
                cap.release()
        return 0

    cap, frame = open_cam(args.camera, args.width, args.height)
    if cap is None:
        print(f"打不开摄像头 {args.camera}", file=sys.stderr)
        return 1

    best = frame
    for _ in range(8):  # 等 AE/AWB 收敛，顺便挑最清晰的一帧
        ok, f = cap.read()
        if not ok or f is None:
            continue
        if cv2.Laplacian(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var() > cv2.Laplacian(
            cv2.cvtColor(best, cv2.COLOR_BGR2GRAY), cv2.CV_64F
        ).var():
            best = f
    cap.release()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    imwrite_unicode(args.out, best)
    print(f"saved {args.out}  {best.shape[1]}x{best.shape[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
