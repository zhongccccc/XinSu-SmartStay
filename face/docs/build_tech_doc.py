"""生成《酒店入住一体机·人证合一比对人脸系统 技术方案》DOCX。

    python docs/build_tech_doc.py
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

DOCS = Path(__file__).resolve().parent
OUT = DOCS / "技术方案_酒店人脸比对.docx"

BODY_FONT = "宋体"
HEAD_FONT = "微软雅黑"
CODE_FONT = "Consolas"
ACCENT = RGBColor(0x0B, 0x5C, 0xAD)

doc = Document()


# --------------------------------------------------------------------------
# 基础样式
# --------------------------------------------------------------------------
def set_cn(run, font: str, size: float | None = None, bold: bool | None = None,
           color: RGBColor | None = None) -> None:
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color


def setup() -> None:
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.6)
    sec.top_margin = Cm(2.4)
    sec.bottom_margin = Cm(2.2)

    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(4)

    for name, size in (("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 11.5)):
        st = doc.styles[name]
        st.font.name = HEAD_FONT
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = ACCENT if name == "Heading 1" else RGBColor(0x1F, 0x23, 0x28)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), HEAD_FONT)
        st.paragraph_format.space_before = Pt(14 if name == "Heading 1" else 10)
        st.paragraph_format.space_after = Pt(6)


def h1(text: str) -> None:
    doc.add_paragraph(text, style="Heading 1")


def h2(text: str) -> None:
    doc.add_paragraph(text, style="Heading 2")


def h3(text: str) -> None:
    doc.add_paragraph(text, style="Heading 3")


def p(text: str = "", bold: bool = False, size: float = 10.5, space_after: int = 4) -> None:
    para = doc.add_paragraph()
    para.paragraph_format.space_after = Pt(space_after)
    run = para.add_run(text)
    set_cn(run, BODY_FONT, size, bold)
    return para


def lead(label: str, text: str) -> None:
    para = doc.add_paragraph()
    para.paragraph_format.space_after = Pt(4)
    r1 = para.add_run(label)
    set_cn(r1, BODY_FONT, 10.5, True)
    r2 = para.add_run(text)
    set_cn(r2, BODY_FONT, 10.5)


def bullets(items: list[str], numbered: bool = False) -> None:
    for i, item in enumerate(items, 1):
        para = doc.add_paragraph()
        para.paragraph_format.left_indent = Cm(0.6)
        para.paragraph_format.first_line_indent = Cm(-0.45)
        para.paragraph_format.space_after = Pt(2)
        prefix = f"{i}. " if numbered else "· "
        run = para.add_run(prefix + item)
        set_cn(run, BODY_FONT, 10.5)


def shade(cell, hex_fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tc_pr.append(shd)


def table(headers: list[str], rows: list[list[str]], widths: list[float] | None = None,
          font_size: float = 9.5) -> None:
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        set_cn(run, HEAD_FONT, font_size, True, RGBColor(0xFF, 0xFF, 0xFF))
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        shade(cell, "0B5CAD")
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(str(val))
            set_cn(run, BODY_FONT, font_size)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def code(text: str) -> None:
    para = doc.add_paragraph()
    para.paragraph_format.left_indent = Cm(0.4)
    para.paragraph_format.space_before = Pt(4)
    para.paragraph_format.space_after = Pt(6)
    para.paragraph_format.line_spacing = 1.1
    para.paragraph_format.keep_together = True
    p_pr = para._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), "F3F4F6")
    p_pr.append(shd)
    run = para.add_run(text)
    run.font.name = CODE_FONT
    run.font.size = Pt(9)


def figure(path: Path, caption: str, width: float = 14.0) -> None:
    if not path.exists():
        return
    doc.add_picture(str(path), width=Cm(width))
    last = doc.paragraphs[-1]
    last.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(caption)
    set_cn(run, BODY_FONT, 9, False, RGBColor(0x57, 0x60, 0x6A))


def note(text: str) -> None:
    para = doc.add_paragraph()
    para.paragraph_format.left_indent = Cm(0.3)
    para.paragraph_format.space_before = Pt(2)
    p_pr = para._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "18")
    left.set(qn("w:color"), "D29922")
    left.set(qn("w:space"), "6")
    borders.append(left)
    p_pr.append(borders)
    run = para.add_run(text)
    set_cn(run, BODY_FONT, 9.5, False, RGBColor(0x57, 0x60, 0x6A))


setup()


def add_footer() -> None:
    para = doc.sections[0].footer.paragraphs[0]
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = para.add_run("第 ")
    set_cn(r, BODY_FONT, 9)
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    r2 = para.add_run()
    r2._r.append(begin)
    r2._r.append(instr)
    r2._r.append(sep)
    r2._r.append(end)
    set_cn(r2, BODY_FONT, 9)
    r3 = para.add_run(" 页")
    set_cn(r3, BODY_FONT, 9)


add_footer()

# --------------------------------------------------------------------------
# 封面
# --------------------------------------------------------------------------
for _ in range(4):
    doc.add_paragraph()

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("酒店入住一体机")
set_cn(run, HEAD_FONT, 30, True, ACCENT)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = sub.add_run("人证合一比对人脸系统")
set_cn(run, HEAD_FONT, 24, True, ACCENT)

sub2 = doc.add_paragraph()
sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = sub2.add_run("技 术 方 案")
set_cn(run, HEAD_FONT, 16, False, RGBColor(0x57, 0x60, 0x6A))

doc.add_paragraph()
line = doc.add_paragraph()
line.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = line.add_run("进迭时空 K1（MUSE Pi Pro） + IMX219 + 二代证读卡器")
set_cn(run, BODY_FONT, 11, False, RGBColor(0x57, 0x60, 0x6A))

for _ in range(8):
    doc.add_paragraph()

info = [
    ("文档版本", "v1.0"),
    ("适用硬件", "MUSE Pi Pro（K1，8 核 RISC-V）/ IMX219 / 二代证读卡器"),
    ("软件栈", "Bianbu OS + SpacemiT ONNXRuntime + OpenCV"),
    ("编制日期", "2026-11-06"),
]
t = doc.add_table(rows=0, cols=2)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
for k, v in info:
    cells = t.add_row().cells
    r1 = cells[0].paragraphs[0].add_run(k)
    set_cn(r1, HEAD_FONT, 10, True)
    r2 = cells[1].paragraphs[0].add_run(v)
    set_cn(r2, BODY_FONT, 10)
    cells[0].width, cells[1].width = Cm(3.2), Cm(11.0)

doc.add_page_break()

# --------------------------------------------------------------------------
# 目录（手工，便于无域更新）
# --------------------------------------------------------------------------
h1("目录")
toc = [
    ("1  概述", "1.1 背景　1.2 目标　1.3 范围　1.4 术语"),
    ("2  需求与约束", "2.1 功能需求　2.2 非功能需求　2.3 硬件与环境约束"),
    ("3  总体方案", "3.1 架构分层　3.2 核验时序　3.3 部署形态　3.4 方案取舍"),
    ("4  算法设计", "4.1 检测　4.2 对齐　4.3 特征　4.4 判定　4.5 质量门控　4.6 参数"),
    ("5  工程实现", "5.1 代码结构　5.2 核心接口　5.3 关键细节　5.4 数据与存储　5.5 降级"),
    ("6  性能", "6.1 实测　6.2 K1 预估　6.3 优化手段"),
    ("7  精度评估与标定", "7.1 指标　7.2 标定流程　7.3 实测结论　7.4 失败模式"),
    ("8  部署与运维", "8.1 环境　8.2 模型　8.3 服务化　8.4 外设　8.5 升级　8.6 监控"),
    ("9  合规与安全", "9.1 个人信息　9.2 留存　9.3 活体　9.4 资质"),
    ("10  风险与对策", ""),
    ("11  验收标准", "11.1 功能　11.2 性能　11.3 精度"),
    ("12  附录", "A 模型清单　B 命令速查　C 实测数据"),
]
for name, sub in toc:
    para = doc.add_paragraph()
    para.paragraph_format.space_after = Pt(6)
    r = para.add_run(name)
    set_cn(r, HEAD_FONT, 11, True)
    if sub:
        r2 = para.add_run("　　" + sub)
        set_cn(r2, BODY_FONT, 9, False, RGBColor(0x57, 0x60, 0x6A))

doc.add_page_break()

# --------------------------------------------------------------------------
# 1 概述
# --------------------------------------------------------------------------
h1("1  概述")

h2("1.1 背景")
p("酒店前台正在部署自助入住一体机，客人刷身份证后需要核验“持证人就是证件本人”。"
  "传统做法依赖前台人员目视比对，效率低、易漏判，夜间和客流高峰尤其明显。"
  "本方案在一体机本地完成 1:1 人脸比对：读卡器取出身份证芯片照片，摄像头拍摄现场人脸，"
  "本机计算相似度并给出结论。")

h2("1.2 目标")
bullets([
    "本地闭环：人脸图像不出设备，断网可用。",
    "一次核验端到端 ≤ 1 s（抓拍 3~5 帧 + 比对判定）。",
    "真实场景一次通过率 ≥ 90%，误接受率控制在业务可接受范围。",
    "单人次核验可解释：输出分数、质量指标与失败原因，便于人工复核。",
])

h2("1.3 范围")
p("本文覆盖算法链路、工程实现、部署运维与验收方法。不包含：一体机 UI 与业务流程编排、"
  "公安旅馆业系统的数据上报接口、支付与房态系统对接。")

h2("1.4 术语")
table(["术语", "含义"], [
    ["1:1 比对", "把现场人脸与指定的一张证件照比对，判断是否同一人"],
    ["Embedding", "人脸经神经网络编码得到的定长特征向量"],
    ["FAR / FRR", "误接受率（把异人判成同人）/ 误拒绝率（把同人判成异人）"],
    ["TAR@FAR", "在给定误接受率下的通过率，衡量模型判别力的核心指标"],
    ["灰区", "分数落在两个阈值之间，既不能自动通过也不宜直接拒绝，转人工"],
    ["对齐", "按五官关键点做相似变换，把人脸摆正到统一模板"],
], widths=[3.6, 12.0])

# --------------------------------------------------------------------------
# 2 需求与约束
# --------------------------------------------------------------------------
h1("2  需求与约束")

h2("2.1 功能需求")
table(["编号", "需求", "说明"], [
    ["FR-01", "读取身份证芯片照", "通过公安部认证的二代证读卡器获取文字信息与证件照（358×441 JPEG）"],
    ["FR-02", "现场人脸采集", "IMX219 采集 720p 画面，连续抓拍多帧"],
    ["FR-03", "1:1 比对", "计算现场人脸与证件照的相似度并给出结论"],
    ["FR-04", "质量门控", "人脸过小、模糊、过暗/过曝、侧脸、抬头低头时拒绝比对并提示重拍"],
    ["FR-05", "三态判定", "通过 / 灰区转人工 / 重拍"],
    ["FR-06", "结果留痕", "记录分数、质量指标、时间戳，不保存人脸图像"],
], widths=[2.2, 4.2, 9.2])

h2("2.2 非功能需求")
table(["类别", "指标", "目标值"], [
    ["性能", "单次核验耗时（P95）", "≤ 1.0 s（K1 目标）"],
    ["性能", "连续核验稳定性", "500 次无崩溃、无内存增长"],
    ["精度", "TAR@FAR=1e-3", "≥ 97%（真实场景样本，待标定验证）"],
    ["精度", "一次通过率", "≥ 90%"],
    ["可用性", "离线运行", "完全本地，无网络依赖"],
    ["可维护", "参数可配置", "阈值、质量门限全部集中在 config.yaml"],
    ["合规", "数据最小化", "仅存特征与分数，不存人脸图"],
], widths=[2.4, 6.4, 6.8])

h2("2.3 硬件与环境约束")
p("硬件已定型，方案必须在这个边界内工作：")
table(["部件", "规格", "对方案的影响"], [
    ["主控", "进迭时空 K1，8 核 RISC-V（X60），RVV 1.0 256-bit，标称 2.0 TOPS INT8，无独立 NPU", "算力靠 CPU 向量扩展，模型必须量化且不能太大"],
    ["系统", "Bianbu OS（Debian 系），SpacemiT ONNXRuntime + SpaceMITExecutionProvider", "推理统一走 ONNX Runtime，C++/Python 均可"],
    ["摄像头", "IMX219，800 万像素，MIPI-CSI，卷帘快门，模组多为定焦", "无 HDR、近距易虚焦，需先验证成像"],
    ["证件源", "二代证读卡器（芯片照 358×441）", "证件照为标准正脸、平光，质量稳定"],
    ["交互", "触摸屏 + 语音/文字提示", "决定重拍提示与重试次数"],
], widths=[2.2, 7.6, 5.8])
note("约束说明：K1 的 2.0 TOPS 是 CPU 同构算力，实际可用算力取决于向量指令利用率与散热，"
     "所有性能结论必须以真机实测为准，不可直接套用官方标称值。")

# --------------------------------------------------------------------------
# 3 总体方案
# --------------------------------------------------------------------------
h1("3  总体方案")

h2("3.1 架构分层")
p("系统分为四层，全部运行在一体机本地：")
table(["层次", "职责", "关键实现"], [
    ["采集层", "摄像头取流、连拍、证件照获取", "camera.py（V4L2/OpenCV）、idcard.py（读卡器抽象）"],
    ["算法层", "检测、对齐、特征、比对", "detector.py / align.py / embedder.py / matcher.py"],
    ["业务层", "质量门控、三态判定、重试策略、审计", "quality.py / pipeline.py / store.py"],
    ["接口层", "供 UI 调用的核验接口", "FaceVerifier.verify()，返回结构化结果"],
], widths=[2.2, 6.2, 7.2])

h2("3.2 核验时序")
code(
    "客人刷证              摄像头预热（丢 8 帧等 AE/AWB 收敛）\n"
    "   │                        │\n"
    "   ▼                        ▼\n"
    "读卡器读芯片照 ──► 检测最大人脸 ──► 5 点对齐 112×112 ──► 特征向量 A\n"
    "                                                    │\n"
    "                    连拍 3~5 帧 ──► 逐帧检测/质量门控/对齐/特征 ──► 向量 Bi\n"
    "                                                    │\n"
    "                              score_i = cos(A, Bi) ──► 取中位数\n"
    "                                                    │\n"
    "                        score ≥ t_high ──► 通过\n"
    "                        score <  t_low  ──► 重拍\n"
    "                        否则            ──► 转人工复核"
)

h2("3.3 部署形态")
bullets([
    "单进程常驻服务，开机自启（systemd），通过本地 HTTP / Unix Socket 向 UI 提供核验接口。",
    "模型文件随程序发布，放在 models/ 目录，启动时一次性加载，常驻内存。",
    "无外部依赖：不调用云端 API，不需要网络。",
    "日志与特征缓存落在本地 SQLite 与 JSONL，按天滚动。",
])

h2("3.4 方案取舍")
table(["决策点", "选择", "理由"], [
    ["本地 vs 云端", "本地", "延迟可控、断网可用、人脸数据不出设备（合规刚性要求）"],
    ["1:1 vs 1:N", "1:1", "业务只需核验“这张证是不是本人”，1:N 会引入误挂他档的风险"],
    ["活体", "被动活体（规划中）", "硬件只有单目 RGB，强活体需加红外；当前定位辅助核验 + 人工兜底"],
    ["特征存储", "只存 128/512 维向量", "不可逆、体积小（约 0.5~2 KB），比存图合规"],
], widths=[2.8, 4.0, 9.0])

doc.add_page_break()

# --------------------------------------------------------------------------
# 4 算法设计
# --------------------------------------------------------------------------
h1("4  算法设计")

h2("4.1 人脸检测")
h3("4.1.1 候选与实测")
p("候选三个：OpenCV 内置 YuNet、SpacemiT Model Zoo 的 YOLOv5-face（INT8）、insightface 的 SCRFD。"
  "对同一张 2432×1728 证件照实测：")
table(["模型", "输入", "输出", "检测结果", "结论"], [
    ["YuNet", "320×320", "框 + 5 关键点", "置信度 0.94，框与五官吻合", "采用"],
    ["YOLOv5-face (INT8)", "320×320", "3 层特征图 ×16", "置信度 0.87，框正确", "可选出框"],
    ["SCRFD det_10g", "640×640", "框 + 5 关键点", "官方人脸应用使用", "备选，算力开销大"],
], widths=[3.4, 2.6, 3.4, 4.6, 2.4])

h3("4.1.2 关键发现：YOLOv5-face 的关键点不可用")
p("Model Zoo 提供的 yolov5n-face_320_cut.q.onnx 是“cut”导出（后处理被裁掉），"
  "按官方 C++ 的两种解码方式还原关键点后，5 个点全部挤在框中心：实测瞳距 36 px，"
  "而同一张脸的真实瞳距约 70 px，目视即可判定错误。官方的人脸应用本身也是用 SCRFD 出 5 点，"
  "并未使用 YOLOv5-face 的关键点。")
p("因此本项目把“检测框”和“关键点”拆开：默认由 YuNet 同时提供两者；"
  "若启用 YOLOv5-face 出框，则在小图上用 YuNet 二次定位关键点（LandmarkRefiner）。")

h2("4.2 人脸对齐")
h3("4.2.1 为什么必须对齐")
p("ArcFace 类模型在训练时所有人脸都被摆到固定的 5 点模板上。推理时若直接把检测框裁出来，"
  "人脸的角度、尺度、位置都与训练分布不一致，同一人的相似度会明显下降。"
  "官方 demo 的预处理只是整图 letterbox 到 112×112，没有对齐，不能直接用于线上。")

h3("4.2.2 相似变换闭式解")
p("5 个点恰好确定一个相似变换（4 自由度：缩放、旋转、平移）。用最小二乘闭式解，"
  "比 RANSAC 稳定，且没有随机性：")
code(
    "src 中心 μs，dst 中心 μd\n"
    "a = Σ (d_i-μd)·(s_i-μs) / Σ |s_i-μs|²\n"
    "b = Σ [(d_iy-μdy)(s_ix-μsx) - (d_ix-μdx)(s_iy-μsy)] / Σ |s_i-μs|²\n"
    "M = [ a  -b  μdx - a·μsx + b·μsy ]\n"
    "    [ b   a  μdy - b·μsx - a·μsy ]"
)

h3("4.2.3 标准模板")
p("采用与 SpacemiT 官方 align_face.cpp 一致的 ArcFace 112×112 模板（与 buffalo_l 同源）：")
table(["序号", "部位", "x", "y"], [
    ["1", "左眼中心", "38.2946", "51.6963"],
    ["2", "右眼中心", "73.5318", "51.5014"],
    ["3", "鼻尖", "56.0252", "71.7366"],
    ["4", "左嘴角", "41.5493", "92.3655"],
    ["5", "右嘴角", "70.7299", "92.2041"],
], widths=[1.8, 3.6, 3.6, 3.6])

h3("4.2.4 对齐质量指标")
p("对齐后计算 5 点重投影误差（变换后的关键点与模板的平均距离）。正脸通常 < 2 px，"
  "明显侧脸或低头会到 3~5 px。该指标只作为参考记录，不作为姿态判据（原因见 4.5.1）。")

h2("4.3 特征提取")
h3("4.3.1 模型")
table(["模型", "体积", "输入", "输出维度", "定位"], [
    ["MobileFaceNet（官方 INT8）", "1.2 MB", "112×112", "128", "默认，追求速度"],
    ["buffalo_l R50（INT8）", "43.8 MB", "112×112", "512", "高精度，暗光/低质量抓拍时启用"],
], widths=[4.6, 2.4, 2.4, 2.6, 5.0])

h3("4.3.2 预处理")
p("BGR→RGB，HWC→CHW，归一化 (x/255 − 0.5)/0.5（等价于 (x − 127.5)/127.5），输入 float32。"
  "这一顺序与官方 arcface_process.py 一致，实测 RGB 明显优于 BGR（同人分 0.44 vs 0.39）。")

h3("4.3.3 必须做 L2 归一化")
p("官方 MobileFaceNet 输出未归一化（实测范数 2.96），直接算内积会受模长影响，"
  "必须先做 L2 归一化再取余弦。")

h3("4.3.4 量化影响")
p("对同一组人像，FP32 与 INT8 的相似度差异在 0.01 量级（如 0.442 vs 0.430），"
  "说明这套 QDQ 量化没有破坏判别力；模型本身的判别力问题（见 7.3）与量化无关。")

h2("4.4 比对判定")
h3("4.4.1 余弦相似度")
p("两个 L2 归一化向量的点积即余弦，取值 [-1,1]，越大越像。")
code("cos(A, B) = (A · B) / (|A| · |B|) = A · B   （A、B 已归一化）")

h3("4.4.2 双阈值与灰区")
table(["条件", "结论", "动作"], [
    ["中位数 ≥ t_high 且过线帧占比 ≥ 50%", "pass", "放行，进入入住流程"],
    ["中位数 < t_low", "retry", "提示调整光线/距离后重拍"],
    ["其余", "review", "转前台人工复核，不直接拒绝"],
], widths=[7.2, 2.4, 6.4])
p("双阈值而不是单阈值，是为了把“模型不确定”的情况交给人工，避免把客人卡在机器前，"
  "也避免为了降低误拒而放宽阈值、抬高误接受。")

h3("4.4.3 多帧聚合")
p("现场连拍 3~5 帧，逐帧算分，取中位数。中位数比均值抗单帧异常，比取最大值保守。"
  "同时统计“过线帧占比”，用于识别“分数勉强但抖动大”的情况。")

h2("4.5 质量门控")
p("通过率的第一瓶颈是成像，不是模型。门控不通过的帧直接不参与打分，并给出具体原因。")
table(["指标", "算法", "默认阈值", "说明"], [
    ["人脸宽度", "检测框宽（原图像素）", "≥ 160 px", "720p 下脸宽应 ≥ 160，1080p 建议 200"],
    ["清晰度", "对齐后 112×112 灰度图的拉普拉斯方差", "≥ 35", "在统一尺度上比较，公允"],
    ["亮度", "对齐后灰度均值", "60 ~ 200", "过暗/过曝都拒"],
    ["左右偏转 yaw", "(鼻尖x − 双眼中点x) / 瞳距", "|yaw| ≤ 0.15", "正脸约 0，±0.15 已可见侧脸"],
    ["俯仰 pitch", "(鼻尖y − 眼线y) / (嘴线y − 眼线y)", "0.30 ~ 0.70", "正脸约 0.55"],
], widths=[2.6, 7.0, 3.0, 3.4])

h3("4.5.1 为什么不用对齐残差判断姿态")
p("相似变换只有 4 个自由度，5 个点几乎总能拟合得很贴——实测侧脸 20° 时残差仍只有 1.8 px。"
  "残差反映的是“五官是否非刚性变形”，不是姿态。因此改用关键点几何关系构造 yaw/pitch 代理量，"
  "实测侧脸时 yaw 从 0.02 变到 0.15，能有效触发门控。")

h2("4.6 参数总表")
p("全部参数集中在 config.yaml，现场可调，无需改代码：")
table(["分组", "参数", "默认值", "作用"], [
    ["models", "detector", "yunet", "检测器选择"],
    ["models", "arcface", "arcface_mobilefacenet_cut.q.onnx", "识别模型"],
    ["detector", "conf_threshold", "0.6", "检测置信度"],
    ["quality", "min_face_px", "160", "人脸尺寸下限"],
    ["quality", "blur_min", "35", "清晰度下限"],
    ["quality", "yaw_max", "0.15", "侧脸上限"],
    ["match", "t_high / t_low", "0.45 / 0.32", "双阈值"],
    ["match", "aggregate", "median", "多帧聚合方式"],
    ["capture", "burst / interval", "4 帧 / 120 ms", "连拍策略"],
], widths=[2.2, 4.6, 6.4, 3.8])

doc.add_page_break()

# --------------------------------------------------------------------------
# 5 工程实现
# --------------------------------------------------------------------------
h1("5  工程实现")

h2("5.1 代码结构")
code(
    "face_verify_k1/\n"
    "├── facekit/                核心库\n"
    "│   ├── detector.py         YuNet / YOLOv5-face 检测器（含 INT8 解码）\n"
    "│   ├── align.py            5 点相似变换对齐\n"
    "│   ├── embedder.py         ArcFace 特征 + L2 归一化\n"
    "│   ├── quality.py          质量门控与姿态代理\n"
    "│   ├── matcher.py          余弦 / 双阈值 / 多帧聚合\n"
    "│   ├── pipeline.py         FaceVerifier 端到端\n"
    "│   ├── camera.py           V4L2 采集、预热、连拍\n"
    "│   ├── idcard.py           读卡器抽象\n"
    "│   └── store.py            特征缓存 + 审计日志\n"
    "├── scripts/                CLI 工具（核验/标定/压测/对比）\n"
    "├── config.yaml             全部参数\n"
    "├── models/                 ONNX 模型\n"
    "└── tests/                  不依赖 pytest 的自检"
)

h2("5.2 核心接口")
code(
    "verifier = FaceVerifier(Config.load(\"config.yaml\"))\n"
    "result = verifier.verify(id_photo_bgr, live_frames)\n"
    "\n"
    "# result.decision  : pass | review | retry\n"
    "# result.score     : 中位数相似度\n"
    "# result.frames[*] : 每帧分数 / 质量指标 / 失败原因\n"
    "# result.latency_ms: 分阶段耗时"
)
p("verify() 只依赖 numpy 数组，不关心图像来自摄像头、文件还是浏览器，便于集成与测试。")

h2("5.3 关键实现细节")
h3("5.3.1 中文路径")
p("Windows 下 cv2.imread 走 ANSI 接口，中文路径会读失败（本项目实测 E:\\人脸配对\\原.png 读不到）。"
  "统一改用 np.fromfile + cv2.imdecode / cv2.imencode + tofile。")

h3("5.3.2 letterbox 坐标映射")
p("检测在 320×320 的等比缩放画面上进行，框坐标必须映射回原图。缩放比与填充偏移封装在 "
  "LetterboxInfo 中，点与框分别提供 to_original / to_original_boxes，避免把 (N,4) 的框当作点处理。")

h3("5.3.3 推理会话")
code(
    "so = ort.SessionOptions()\n"
    "so.intra_op_num_threads = 4\n"
    "sess = ort.InferenceSession(model, so, providers=[\"SpaceMITExecutionProvider\",\n"
    "                                                  \"CPUExecutionProvider\"])"
)
p("provider 列表按优先级给出，缺失时自动回退到 CPU。上线必须打印真实生效的 provider，"
  "不能只看配置——配置写了不代表插件已加载。")

h3("5.3.4 摄像头采集")
bullets([
    "打开后先丢弃若干帧，等自动曝光与白平衡收敛（IMX219 尤其明显）。",
    "连拍时每帧间隔 120 ms，给 AE 留出调整时间，也让表情/姿态略有变化便于筛选。",
    "K1 上优先 CAP_V4L2；Windows 开发机自动回退。",
])

h3("5.3.5 读卡器抽象")
code(
    "class IdCardReader(Protocol):\n"
    "    def read(self) -> IdCardData: ...   # 含 name/id_number/photo(BGR)"
)
p("各厂商 SDK（华视、新中新、精伦等）只需实现一个子类，主流程不感知厂商差异。")

h2("5.4 数据与存储")
table(["数据", "存储方式", "留存", "说明"], [
    ["证件照特征", "SQLite（id_hash + 512B 向量）", "长期", "按身份证号加盐哈希索引，同一客人复用"],
    ["核验记录", "JSONL 审计日志", "按合规要求", "时间、哈希、分数、质量、结论；不含图像"],
    ["人脸图像", "不落盘", "—", "仅在内存中处理，进程结束即释放"],
], widths=[3.2, 6.2, 3.0, 5.2])

h2("5.5 错误处理与降级")
table(["异常", "处理", "用户可见行为"], [
    ["检测不到人脸", "该帧跳过", "提示“请正对摄像头”"],
    ["质量不合格", "该帧跳过并记录原因", "提示具体原因（太暗/太远/侧脸）"],
    ["有效帧不足", "整体判 retry", "提示重试，2 次后转人工"],
    ["模型加载失败", "启动即失败，不进入服务", "设备报障，避免带病运行"],
    ["读卡器异常", "返回明确错误码", "引导人工核验"],
], widths=[4.0, 6.4, 6.0])

# --------------------------------------------------------------------------
# 6 性能
# --------------------------------------------------------------------------
h1("6  性能")

h2("6.1 实测（x86 开发机，仅作参考）")
table(["阶段", "MobileFaceNet 方案", "R50 方案"], [
    ["检测（YuNet, 720p→320）", "2.5 ~ 3.4 ms", "2.5 ~ 3.4 ms"],
    ["对齐（112×112）", "< 1 ms", "< 1 ms"],
    ["特征提取", "6.4 ms", "21.7 ms"],
    ["单次核验（1 帧）", "28 ~ 35 ms", "63 ~ 75 ms"],
    ["单次核验（4 帧）", "约 60 ms", "约 120 ms"],
], widths=[6.4, 5.0, 5.0])
p("说明：以上是普通 x86 CPU 单线程推理的数据，不含摄像头曝光等待与 UI 渲染。")

h2("6.2 K1 上的预估")
p("K1 依靠 RVV 向量扩展做 INT8 推理，官方 Model Zoo 给出的同类模型实测约为："
  "YOLOv8n 320×320 约 26 FPS、MobileFaceNet 112×112 约 110 FPS。"
  "据此估算本项目单帧流水线在 100~300 ms 量级，R50 方案约 300~800 ms。"
  "以上为估算，必须以真机实测替换。")

h2("6.3 优化手段")
bullets([
    "降低检测频率：预览阶段 2~3 次/秒跑检测，命中后再触发特征提取，避免每帧全量推理。",
    "检测与比对分辨率分离：检测用 320，比对从原图裁剪，兼顾速度与精度。",
    "模型分级：默认 MobileFaceNet；仅当质量指标偏低（暗光、模糊）时切换到 R50 复算。",
    "线程绑定：intra_op_num_threads 设为 4，与 K1 的簇结构匹配，避免跨簇调度开销。",
    "会话常驻：模型在进程启动时加载一次，避免每次核验重复初始化。",
])

doc.add_page_break()

# --------------------------------------------------------------------------
# 7 精度
# --------------------------------------------------------------------------
h1("7  精度评估与标定")

h2("7.1 指标")
p("以 TAR@FAR=1e-3 为主指标，辅以 EER 与一次通过率。1:1 场景下误接受（把别人放进来）"
  "是安全与合规风险，误拒绝只是体验问题，因此标定优先控制 FAR。")

h2("7.2 标定流程")
code(
    "# pairs.csv 三列：path_a,path_b,label（1=同人，0=异人）\n"
    "python scripts/calibrate.py --pairs pairs.csv --far 1e-3 --out calib.json\n"
    "# 输出：同人/异人分布、EER、TAR@FAR、推荐 t_high / t_low"
)
p("样本要求：≥ 300 对（150 同人 / 150 异人），覆盖 18-30/30-50/50+ 年龄段、"
  "戴眼镜、化妆、逆光、暗光、口罩等条件，且必须用这台一体机在真实点位采集。")

h2("7.3 实测结论（小样本，仅用于说明方法）")
table(["关系", "MobileFaceNet", "buffalo R50"], [
    ["同人（kjw 证件照 vs 现场抓拍）", "0.442", "0.320"],
    ["同人（kjw 两张证件照）", "0.770", "0.596"],
    ["同人（sf 证件照 vs 现场抓拍）", "0.671", "—"],
    ["异人（sf 证件照 vs kjw 抓拍）", "0.536", "0.056"],
    ["异人（kjw 证件照 vs sf 抓拍）", "0.144", "—"],
], widths=[8.4, 4.4, 4.0])
note("关键结论：MobileFaceNet 在暗光逆光抓拍上出现“同人 0.442 < 异人 0.536”的倒挂，"
     "判别力失效；R50 在同一组图上同人 0.32、异人 0.056，间隔 0.26，可用。"
     "因此正式部署建议使用 R50，或强制改善现场光照后再评估 MobileFaceNet。")

figure(DOCS / "assets" / "three_way.jpg", "图 1　对齐后的人脸（sf / kjw / 现场抓拍）", 12)

h2("7.4 已知失败模式")
table(["场景", "表现", "对策"], [
    ["逆光/暗光", "人脸欠曝，特征退化，同人分骤降", "正面补光；提高亮度门限；必要时切 R50"],
    ["明显侧脸/低头", "五官错位，对齐失真", "yaw/pitch 门控 + UI 引导"],
    ["口罩/墨镜/刘海遮挡", "关键点偏移", "依赖质量门控 + 人工复核"],
    ["儿童、老人", "与证件照年龄差大", "接受较低通过率，保留人工通道"],
    ["照片/屏幕翻拍", "单目无法区分", "规划被动活体；对外定位辅助核验"],
], widths=[3.6, 6.4, 6.2])

h2("7.5 上线策略")
p("建议灰度：先作为辅助核验（人工确认），积累 1~2 个月真实分布与误判样本，"
  "再依据实测 ROC 调整阈值并逐步放开自动放行比例。所有核验分数进入审计日志，供回流标定。")

# --------------------------------------------------------------------------
# 8 部署
# --------------------------------------------------------------------------
h1("8  部署与运维")

h2("8.1 环境准备")
code(
    "sudo apt-get update\n"
    "sudo apt-get install -y spacemit-onnxruntime libopencv-dev \\\n"
    "    python3-spacemit-ort python3-opencv\n"
    "pip install -r requirements.txt   # numpy / pyyaml 等"
)

h2("8.2 模型部署")
code(
    "python scripts/fetch_models.py            # YuNet + R50\n"
    "python scripts/fetch_models.py --all      # 另含 YOLOv5-face 与 MobileFaceNet"
)
p("模型目录随程序发布；升级模型只替换 models/ 下的文件并重启服务。")

h2("8.3 服务化（systemd）")
code(
    "[Unit]\n"
    "Description=FaceVerify Kiosk Service\n"
    "After=multi-user.target\n"
    "\n"
    "[Service]\n"
    "WorkingDirectory=/opt/face_verify_k1\n"
    "ExecStart=/usr/bin/python3 scripts/service.py --config config.yaml\n"
    "Restart=always\n"
    "RestartSec=3\n"
    "\n"
    "[Install]\n"
    "WantedBy=multi-user.target"
)

h2("8.4 外设接入")
bullets([
    "摄像头：确认 /dev/video* 节点与支持的分辨率（v4l2-ctl --list-formats-ext），在 config 中对齐。",
    "读卡器：按厂商 SDK 实现 IdCardReader，注意 USB 供电与断线重连。",
    "补光：镜头两侧 4000K 柔光，照度 ≥ 300 lux 打在脸上，是提升通过率性价比最高的改动。",
])

h2("8.5 升级与回滚")
p("版本化发布：程序目录 + 模型目录分别打版本号；升级前备份 config.yaml 与数据库；"
  "保留上一版本目录，异常时秒级回滚。")

h2("8.6 监控")
table(["指标", "采集方式", "告警阈值"], [
    ["核验成功率", "审计日志按小时聚合", "连续 1 小时 < 80%"],
    ["平均耗时", "pipeline 内计时", "P95 > 2 s"],
    ["重拍率", "decision=retry 占比", "> 15%"],
    ["服务存活", "systemd + 心跳", "进程退出立即重启并上报"],
], widths=[3.6, 6.4, 6.0])

doc.add_page_break()

# --------------------------------------------------------------------------
# 9 合规
# --------------------------------------------------------------------------
h1("9  合规与安全")

h2("9.1 个人信息保护")
bullets([
    "人脸信息属于敏感个人信息，须单独告知并取得同意，不得以“拒绝入住”变相强制。",
    "遵循最小必要：只采集核验所需的一帧画面，核验结束即释放。",
    "提供替代通道：拒绝人脸核验的客人可走人工登记。",
    "处理者需做个人信息保护影响评估（PIA），明确目的、方式、范围与保存期限。",
])

h2("9.2 数据留存")
p("仅保留特征向量、分数与时间戳，不保存人脸图像；日志按最小化原则脱敏（身份证号只存加盐哈希）。"
  "留存期限与删除机制写入运维制度，到期自动清理。")

h2("9.3 活体")
p("当前硬件为单目 RGB，只能做被动活体（纹理、摩尔纹、屏幕反光），无法可靠防御照片/视频攻击。"
  "产品定位为“辅助核验 + 人工兜底”，不得对外宣称具备强活体能力。"
  "如需强活体，需增加红外模组或结构光。")

h2("9.4 资质")
p("若作为住宿登记的“人证核验终端”对外宣称，公安侧通常有相应检测与认证要求；"
  "自研板卡方案一般不具备该资质。建议定位为酒店内部辅助工具，正式核验仍由前台人员完成。")

# --------------------------------------------------------------------------
# 10 风险
# --------------------------------------------------------------------------
h1("10  风险与对策")
table(["编号", "风险", "影响", "对策"], [
    ["R1", "现场光照不可控（逆光/暗光）", "通过率骤降、误判上升", "补光改造；提高亮度门限；R50 复算"],
    ["R2", "IMX219 定焦，近距虚焦", "人脸细节丢失", "调整镜头焦距或换可调焦模组；先做成像验收"],
    ["R3", "K1 实际算力不足", "延迟超标", "模型分级；降低检测频率；实测后再定模型"],
    ["R4", "模型判别力不足（如 MobileFaceNet 暗光倒挂）", "误接受", "换 R50；阈值按 FAR 标定"],
    ["R5", "无活体", "照片攻击", "被动活体 + 人工兜底；规划红外"],
    ["R6", "读卡器兼容性", "无法取证件照", "选型阶段做 SDK 联调；可用拍照 OCR 兜底"],
    ["R7", "合规资质缺失", "不能作为官方核验设备", "定位辅助工具；不做对外宣称"],
], widths=[1.4, 5.4, 3.8, 6.0])

# --------------------------------------------------------------------------
# 11 验收
# --------------------------------------------------------------------------
h1("11  验收标准")

h2("11.1 功能用例")
table(["编号", "用例", "预期"], [
    ["TC-01", "本人持本人证件", "pass，分数 ≥ t_high"],
    ["TC-02", "他人持他人证件", "pass"],
    ["TC-03", "他人持本人证件（冒用）", "retry/review，不得 pass"],
    ["TC-04", "人脸过小（>1 m）", "retry，提示靠近"],
    ["TC-05", "逆光站立", "retry 或 review，提示调整"],
    ["TC-06", "连续 3 次失败", "转人工，不锁死设备"],
    ["TC-07", "拔网线", "功能不受影响"],
], widths=[2.2, 6.6, 6.8])

h2("11.2 性能")
bullets([
    "单次核验 P95 ≤ 1.0 s（K1）。",
    "连续 500 次核验无崩溃、内存增长 < 50 MB。",
    "冷启动到可服务 ≤ 30 s。",
])

h2("11.3 精度")
p("用真实场景 300 对样本标定后：TAR@FAR=1e-3 ≥ 97%，一次通过率 ≥ 90%，"
  "灰区占比 ≤ 10%。未达标则按 7.4 的失败模式逐项整改后复测。")

# --------------------------------------------------------------------------
# 12 附录
# --------------------------------------------------------------------------
doc.add_page_break()
h1("12  附录")

h2("A  模型清单")
table(["文件", "用途", "大小", "来源"], [
    ["face_detection_yunet_2023mar.onnx", "人脸检测 + 5 点", "232 KB", "OpenCV Zoo"],
    ["w600k_r50.q.onnx", "特征提取（512 维）", "43.8 MB", "buffalo_l / SpacemiT"],
    ["arcface_mobilefacenet_cut.q.onnx", "特征提取（128 维，轻量）", "1.2 MB", "SpacemiT Model Zoo"],
    ["yolov5n-face_320_cut.q.onnx", "备选检测（只出框）", "2.1 MB", "SpacemiT Model Zoo"],
], widths=[7.0, 5.0, 2.4, 4.0])

h2("B  命令速查")
code(
    "python scripts/verify_demo.py --id 证件照.jpg --live 现场照.jpg\n"
    "python scripts/verify_demo.py --id 证件照.jpg --camera 0\n"
    "python scripts/compare_photos.py a.jpg b.jpg c.jpg\n"
    "python scripts/condition_sweep.py --id 证件照.jpg\n"
    "python scripts/calibrate.py --pairs pairs.csv --far 1e-3\n"
    "python scripts/webcam_server.py --id 证件照.jpg --port 8777   # 浏览器抓图核验"
)

h2("C  实测数据明细")
table(["项目", "数值", "条件"], [
    ["检测置信度（YuNet）", "0.94", "2432×1728 证件照"],
    ["检测置信度（YOLOv5-face）", "0.87", "同上"],
    ["YOLOv5-face 关键点瞳距", "36 px", "真实约 70 px，判定不可用"],
    ["对齐重投影误差", "1.3 ~ 3.3 px", "正脸 ~ 1.9 px"],
    ["同人相似度（R50）", "0.32", "暗光抓拍，亮度 79"],
    ["异人相似度（R50）", "0.056", "同上"],
    ["单帧耗时（x86）", "28 ~ 75 ms", "含检测/对齐/特征"],
], widths=[7.0, 4.2, 6.4])

p("")
p("—— 文档结束 ——", size=9)

doc.core_properties.title = "酒店入住一体机 人证合一比对人脸系统 技术方案"
doc.core_properties.subject = "K1 / IMX219 人脸比对"
doc.core_properties.author = "技术方案"

OUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(str(OUT))
print("saved", OUT, f"{OUT.stat().st_size:,} bytes")
