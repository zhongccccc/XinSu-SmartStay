# 酒店入住一体机 · 身份证照 vs 现场抓拍 1:1 人脸比对

面向 **进迭时空 K1（MUSE Pi Pro）+ IMX219** 的可运行实现：读卡器取身份证芯片照，
IMX219 只拍现场人脸，本机完成检测 → 对齐 → 特征 → 判定。

```text
身份证芯片照 (358x441)                 IMX219 抓拍 (720p, 3~5 帧)
        │                                      │
        ├─ 检测 (YuNet / YOLOv5-face) ─────────┤
        │                                      │
        ├─ 5 点相似变换 → 112x112 ─────────────┤   ← 官方 ArcFace 模板
        │                                      │
        ├─ ArcFace MobileFaceNet (INT8, 128 维)┤
        │                                      │
        └──── 余弦相似度 × 3~5 帧 → 中位数 ─────┘
                              │
                    双阈值：pass / review / retry
```

---

## 1. 快速开始

```bash
# 1) 依赖
pip install -r requirements.txt

# 2) 模型（YuNet 232 KB + buffalo R50 43 MB）
python scripts/fetch_models.py

# 3) 用仓库自带的样图跑一次
python scripts/verify_demo.py --id samples/id_photo_sample.png --live samples/live_sim.jpg

# 4) 接摄像头
python scripts/verify_demo.py --id samples/id_photo_sample.png --camera 0
```

输出示例（x86 开发机，非 K1）：

```text
结论      : pass  (比对通过)
相似度    : 0.8894
阈值      : high=0.45 low=0.32 过线帧占比=100%
  frame 0: score=0.8894 blur=265 bright=113 face=198px align_err=1.7
耗时(ms)  : id_ms=11.8, detect_ms_avg=3.3, embed_ms_avg=7.1, total_ms=31.3
```

---

## 2. 目录

```
facekit/
  detector.py   YuNet 检测器 + YOLOv5-face 检测器（含官方 INT8 解码）
  align.py      5 点相似变换对齐（官方 ArcFace 模板，闭式解）
  embedder.py   ArcFace 特征（默认 R50 512 维）+ L2 归一化
  quality.py    质量门控：人脸尺寸/清晰度/亮度/侧脸/抬头
  matcher.py    余弦 + 双阈值 + 多帧中位数
  pipeline.py   端到端 FaceVerifier
  camera.py     V4L2 采集 + 连拍 + AE 预热
  idcard.py     读卡器抽象（厂商 SDK 只需实现 read()）
  store.py      特征缓存（加盐哈希）+ 审计日志，不落人脸图
  simulate.py   合成"现场抓拍"，仅供无真机时跑通链路
scripts/
  verify_demo.py      单次核验（图片/摄像头）
  calibrate.py        用真实同人/异人对标定阈值
  condition_sweep.py  摸条件边界（光照/角度/距离/模糊）
  fetch_models.py     下载模型
  inspect_model.py    查看 ONNX 输入输出
tests/test_core.py    不依赖 pytest 的自检
```

---

## 3. 几个关键决策（都是实测出来的，不是照搬文档）

### ① 关键点交给 YuNet，YOLOv5-face 只出框

官方 `yolov5n-face_320_cut.q.onnx` 的框是准的（样图置信度 0.87，框与人工标注吻合），
但这个「cut」导出的关键点通道按官方 C++ 的两种公式都解不出合理人脸：5 个点会挤在框中心
（瞳距只有 36px，实际应约 70px，肉眼可辨）。官方的人脸应用本身也是用 SCRFD 出 5 点，
没有用 YOLOv5-face 的关键点。

所以默认 `detector: yunet`（232 KB，框 + 5 点都稳）；想要 YOLOv5-face 的速度时设
`detector: yolov5face`，此时它的框 + YuNet 在局部放大图上的关键点组合使用。

### ② 比对帧不能用 320p

检测流缩到 320 没问题，但比对必须回到原图裁剪：人脸宽 ≥160 px 再对齐到 112×112。
在 320 宽画面里人脸只有 60~100 px，等于放大插值，细节全丢。

### ③ 识别模型：默认 MobileFaceNet，判别力不够时换 R50

默认 `arcface_mobilefacenet_cut.q.onnx`（1.2 MB，128 维，快）。它在光照正常、
正脸的抓拍上够用；但实测在**暗光/逆光**的低质量抓拍上判别力会崩：

| 模型 | 同人（kjw 照 vs 抓拍） | 异人最高（男性照 vs 抓拍） | 间隔 |
|---|---|---|---|
| MobileFaceNet 128 维 | 0.442 | **0.536** | **−0.09（不可用）** |
| buffalo R50 512 维 | 0.320 | 0.056 | +0.27 |

如果现场光照不可控，把 `models.arcface` 换成 `models/w600k_r50.q.onnx`
（官方人脸应用实际用的就是它），同时把阈值改成 ~0.30/0.20。代价是模型 43 MB、
单次特征提取从 6 ms 涨到 22 ms（x86）。

模型本身是健康的：同图翻转 0.947、调光 ±10% 0.99、轻微模糊 0.99，
说明差距出在弱模型对低质量输入的编码能力，不是预处理或对齐。

### ④ 阈值随模型变，不能跨模型沿用

R50 的分值整体比 MobileFaceNet 低一档，换模型必须重标阈值。

### ⑤ 姿态不能用「对齐残差」判断

相似变换只有 4 个自由度，侧脸 20° 也能把 5 点拟合到 1.8 px 残差。改用
「鼻尖相对眼-嘴中线的偏移」当 yaw/pitch 代理（见 `quality.pose_metrics`），实测侧脸时明显变化。

---

## 4. 调参与标定（上线前必做）

`config.yaml` 里所有阈值都是**占位值**，必须用真机样本重标：

```bash
# pairs.csv 三列：path_a,path_b,label（1=同人，0=异人）
python scripts/calibrate.py --pairs pairs.csv --far 1e-3
```

输出里会给出 `recommended_t_high` / `recommended_t_low`，抄回 `config.yaml` 的 `match` 段。

样本要求：

| 项 | 要求 |
|---|---|
| 数量 | ≥300 对（150 同人 / 150 异人） |
| 覆盖 | 年龄 18-30/30-50/50+、戴眼镜、化妆、逆光、暗光、口罩 |
| 采集 | **必须用这台一体机在这个点位拍**，不能用网图 |
| 指标 | TAR@FAR=1e-3 为主，配合一次通过率、失败原因分布 |

先用 `condition_sweep.py` 摸清边界，能提前发现"距离偏远"这类结构性问题：

```bash
python scripts/condition_sweep.py --id samples/id_photo_sample.png
```

---

## 5. K1 板上部署

```bash
sudo apt-get install -y spacemit-onnxruntime libopencv-dev \
    python3-spacemit-ort python3-opencv
```

`config.yaml`：

```yaml
runtime:
  providers: [SpaceMITExecutionProvider, CPUExecutionProvider]
  num_threads: 4
```

检测器/模型路径不变。确认 EP 真的生效：

```bash
python scripts/inspect_model.py models/arcface_mobilefacenet_cut.q.onnx
# 或在代码里打印 ort.get_available_providers() 与实际 session providers
```

摄像头：IMX219 经 ISP 后是 `/dev/video*`，`camera.py` 默认 `CAP_V4L2`，打不开会自动退回默认后端。
先用 `v4l2-ctl --list-formats-ext -d /dev/video0` 确认支持的分辨率，再对齐 `capture.width/height`。

**先验证成像，再调模型**：在目标距离（30~50 cm）拍一张身份证或一张 A4 纸，
看文字边缘是否锐利。IMX219 模组多为固定焦距（约 1 m 外合焦），近距离虚焦
对相似度的伤害比任何模型选择都大。模糊就把镜头旋到工作距离（有胶的话先松开），
或换同接口的可调焦模组。

---

## 6. 已知限制（写进产品说明，别让销售乱承诺）

| 限制 | 说明 |
|---|---|
| 活体 | 单目 RGB 只能做被动活体，挡不住"举着手机/打印照片"。要么加红外模组，要么定位成**辅助核验 + 人工兜底** |
| 逆光 | IMX219 无 HDR，玻璃门逆光会让人脸变成剪影。加正面柔光最有效 |
| 儿童/老人 | 与证件照年龄差大，通过率明显偏低，必须有人工通道 |
| 合规 | 人脸属敏感个人信息：单独告知同意、最小必要、可拒绝、只存特征不存图、约定留存期 |
| 资质 | 若要作为住宿登记的"人证核验终端"对外宣称，公安侧有检测认证要求；自研板卡方案通常拿不到，定位"辅助核验"更现实 |

---

## 7. 读卡器接入

`facekit/idcard.py` 只约定一件事：`read() -> IdCardData`，其中 `photo` 是芯片里的
BGR 图（二代证 358×441 JPEG）。厂商 SDK（华视 CVR-100、新中新、精伦等）包一层子类即可，
主流程不用改。开发阶段可以用 `JsonIdCardReader` / `StaticIdCardReader` 顶替。

建议把证件照特征按身份证号加盐哈希缓存（`store.EmbeddingStore`），
同一客人再次入住可以省掉一次证件照推理。

---

## 8. 与「官方 demo 直跑」的差异

| 项 | 官方 demo | 本项目 | 原因 |
|---|---|---|---|
| 预处理 | 整图 letterbox 到 112 | 5 点相似变换对齐 | 不对齐同人相似度会掉 0.15~0.25 |
| 检测 | YOLOv5-face（含关键点） | YuNet 出关键点 | 该导出的关键点不可用 |
| 分辨率 | 单流 | 检测流 320 + 比对流原图 | 小脸放大等于丢细节 |
| 判定 | 单阈值 | 双阈值 + 多帧中位数 | 降低"一次误判就拒客" |
| 质量 | 无 | 尺寸/清晰度/亮度/姿态 | 拍不清的脸不该进模型 |
| 存储 | 无 | 特征缓存 + 审计日志，不存图 | 合规 |

---

## 9. 文档

`docs/` 目录下是本项目的成套文档，可直接发给甲方或评审：

| 文件 | 内容 |
|---|---|
| `技术方案_酒店人脸比对.docx` / `.pdf` | 19 页技术方案：需求、架构、算法、工程实现、性能、标定、部署、合规、风险、验收 |
| `会话记录_酒店人脸比对.html` / `.md` | 本项目全部对话记录（12 轮），含实测过程与结论 |
| `assets/` | 文档引用的对比图 |

文档由 `docs/build_tech_doc.py` 生成，改完脚本重新跑一次即可更新 DOCX。
