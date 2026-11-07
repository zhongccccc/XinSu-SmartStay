"""阈值标定：给一批同人/异人对，算出分布、ROC 和推荐双阈值。

输入 CSV 两种格式任选：
    path_a,path_b,label        # label=1 同人，0 异人
或目录结构：
    pairs/same/*.jpg           # 每张图与 id/ 下同名图配成同人对
（推荐直接用 CSV，最不容易搞错。）

输出：TAR@FAR=1e-3 / 1e-2、EER、在当前 FAR 下的推荐 t_high / t_low。

用法：
    python scripts/calibrate.py --pairs pairs.csv --out calib.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from facekit.config import Config  # noqa: E402
from facekit.io_utils import imread_unicode  # noqa: E402
from facekit.matcher import cosine  # noqa: E402
from facekit.pipeline import FaceVerifier  # noqa: E402


def load_pairs(path: Path) -> list[tuple[str, str, int]]:
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        out.append((r["path_a"], r["path_b"], int(r["label"])))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--pairs", required=True, help="CSV: path_a,path_b,label")
    ap.add_argument("--out", default="calib_result.json")
    ap.add_argument("--far", type=float, default=1e-3, help="目标误接受率，默认 1e-3")
    ap.add_argument("--margin", type=float, default=0.05, help="灰区半宽，默认 0.05")
    args = ap.parse_args()

    cfg = Config.load(args.config)
    verifier = FaceVerifier(cfg)

    cache: dict[str, np.ndarray | None] = {}

    def emb_of(p: str) -> np.ndarray | None:
        if p not in cache:
            try:
                cache[p] = verifier.embed_id_photo(imread_unicode(p)).embedding
            except Exception as exc:  # noqa: BLE001 标定时跳过坏样本
                print(f"[skip] {p}: {exc}")
                cache[p] = None
        return cache[p]

    same: list[float] = []
    diff: list[float] = []
    for pa, pb, label in load_pairs(Path(args.pairs)):
        ea, eb = emb_of(pa), emb_of(pb)
        if ea is None or eb is None:
            continue
        s = cosine(ea, eb)
        (same if label == 1 else diff).append(s)

    if not same or not diff:
        print("样本不足：同人/异人两边都要有", file=sys.stderr)
        return 2

    same_a, diff_a = np.array(same), np.array(diff)
    thresholds = np.unique(np.round(np.concatenate([same_a, diff_a]), 4))
    tar = np.array([(same_a >= t).mean() for t in thresholds])
    far = np.array([(diff_a >= t).mean() for t in thresholds])

    idx = int(np.argmin(np.abs(far - args.far)))
    t_high = float(thresholds[idx])
    t_low = float(max(0.0, t_high - args.margin))

    # EER
    eer_idx = int(np.argmin(np.abs(tar - (1 - far))))
    eer = float((tar[eer_idx] + (1 - far[eer_idx])) / 2)

    def tar_at(far_target: float) -> float:
        i = int(np.argmin(np.abs(far - far_target)))
        return float(tar[i])

    result = {
        "n_same": len(same),
        "n_diff": len(diff),
        "same_mean": float(same_a.mean()),
        "same_p05": float(np.percentile(same_a, 5)),
        "same_p50": float(np.percentile(same_a, 50)),
        "diff_mean": float(diff_a.mean()),
        "diff_p95": float(np.percentile(diff_a, 95)),
        "diff_max": float(diff_a.max()),
        "eer": eer,
        "tar_at_far_1e-2": tar_at(1e-2),
        "tar_at_far_1e-3": tar_at(1e-3),
        "target_far": args.far,
        "recommended_t_high": t_high,
        "recommended_t_low": t_low,
        "margin": args.margin,
    }
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n把 t_high={t_high:.3f} / t_low={t_low:.3f} 写进 config.yaml 的 match 段。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
