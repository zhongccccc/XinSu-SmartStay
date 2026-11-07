# -*- coding: utf-8 -*-
"""Dump all readable content of a .pptx to a UTF-8 markdown file."""
import sys, os, json
from pptx import Presentation
from pptx.util import Emu

src = sys.argv[1]
out = sys.argv[2]

prs = Presentation(src)
lines = []
lines.append("# PPTX dump: %s" % os.path.basename(src))
lines.append("")
lines.append("- slide size: %.2f x %.2f in (%d slides)" % (
    prs.slide_width / 914400, prs.slide_height / 914400, len(prs.slides)))
lines.append("")

def walk(shapes, depth=0):
    for sh in shapes:
        pad = "  " * depth
        t = sh.shape_type
        name = sh.name
        info = "%s- [%s] %s" % (pad, t, name)
        if sh.has_text_frame:
            txt = " / ".join(p.text for p in sh.text_frame.paragraphs if p.text.strip())
            if txt.strip():
                info += "\n%s  TEXT: %s" % (pad, txt)
        if getattr(sh, "has_table", False) and sh.has_table:
            for r, row in enumerate(sh.table.rows):
                cells = [c.text.replace("\n", " ") for c in row.cells]
                info += "\n%s  ROW%d: %s" % (pad, r, " | ".join(cells))
        if getattr(sh, "has_chart", False) and sh.has_chart:
            ch = sh.chart
            try:
                cats = list(ch.plots[0].categories)
                info += "\n%s  CHART cats: %s" % (pad, cats)
                for s in ch.series:
                    info += "\n%s  CHART series %s: %s" % (pad, s.name, list(s.values))
            except Exception as e:
                info += "\n%s  CHART <unreadable: %s>" % (pad, e)
        if sh.shape_type == 6 or sh.__class__.__name__ == "GroupShape":
            try:
                walk(sh.shapes, depth + 1)
                continue
            except Exception:
                pass
        lines.append(info)
        # pictures: capture image size
        try:
            if sh.shape_type == 13:
                lines.append("%s  IMG: %s bytes=%.0fx%.0f" % (
                    pad, sh.image.filename, sh.width / 914400, sh.height / 914400))
        except Exception:
            pass

for i, slide in enumerate(prs.slides, 1):
    lines.append("")
    lines.append("## Slide %d" % i)
    try:
        layout = slide.slide_layout.name
        lines.append("(layout: %s)" % layout)
    except Exception:
        pass
    walk(slide.shapes)
    if slide.has_notes_slide:
        nt = slide.notes_slide.notes_text_frame.text
        if nt.strip():
            lines.append("  NOTES: %s" % nt.replace("\n", " / "))

with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("wrote", out, len(lines), "lines")
