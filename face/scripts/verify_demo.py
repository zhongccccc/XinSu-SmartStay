"""命令行核验：身份证照 vs 现场照（或摄像头）。

用法：
    python scripts/verify_demo.py --id samples/id_photo_sample.png --live samples/live.jpg
    python scripts/verify_demo.py --id samples/id_photo_sample.png --camera 0
    python scripts/verify_demo.py --id ... --live ... --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 允许从仓库根目录直接运行
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from facekit.camera import Camera  # noqa: E402
from facekit.config import Config  # noqa: E402
from facekit.io_utils import imread_unicode  # noqa: E402
from facekit.pipeline import FaceVerifier  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--id", required=True, help="身份证芯片照路径")
    ap.add_argument("--live", help="现场照路径（与 --camera 二选一）")
    ap.add_argument("--camera", type=int, help="摄像头设备号")
    ap.add_argument("--frames", type=int, default=None, help="抓拍帧数，默认取配置")
    ap.add_argument("--detector", choices=["yunet", "yolov5face"], help="临时切换检测器")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--save-aligned", help="把对齐后的图存到该目录，便于调阈值（含人脸数据，注意合规）")
    args = ap.parse_args()

    cfg = Config.load(args.config)
    if args.detector:
        cfg.models.detector = args.detector
    verifier = FaceVerifier(cfg)

    id_img = imread_unicode(args.id)

    if args.camera is not None:
        with Camera(
            index=args.camera,
            width=cfg.capture.width,
            height=cfg.capture.height,
            warmup_frames=cfg.capture.warmup_frames,
        ) as cam:
            print(f"摄像头实际分辨率: {cam.actual_size}")
            live_frames = cam.burst(
                args.frames or cfg.capture.burst, cfg.capture.burst_interval_ms
            )
    elif args.live:
        live_frames = [imread_unicode(args.live)]
        # 单张图没有多帧可聚合，放宽帧数要求，否则永远 retry
        cfg.match.min_valid_frames = 1
    else:
        print("需要 --live 或 --camera", file=sys.stderr)
        return 2

    result = verifier.verify(id_img, live_frames)

    if args.save_aligned:
        Path(args.save_aligned).mkdir(parents=True, exist_ok=True)
        ext = verifier.embed_id_photo(id_img)
        from facekit.io_utils import imwrite_unicode

        imwrite_unicode(str(Path(args.save_aligned) / "id_aligned.jpg"), ext.aligned)

    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"结论      : {result.decision}  ({result.reason})")
        print(f"相似度    : {result.score:.4f}")
        if result.detail:
            print(f"阈值      : high={result.detail.t_high} low={result.detail.t_low} "
                  f"过线帧占比={result.detail.agree_ratio:.0%}")
        for f in result.frames:
            if f.score is None:
                print(f"  frame {f.index}: 跳过 -> {f.error}")
            else:
                q = f.quality
                print(f"  frame {f.index}: score={f.score:.4f} "
                      f"blur={q.blur:.0f} bright={q.brightness:.0f} "
                      f"face={q.face_px:.0f}px align_err={q.align_err:.1f}")
        print("耗时(ms)  : " + ", ".join(f"{k}={v:.1f}" for k, v in result.latency_ms.items()))

    return 0 if result.decision == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
