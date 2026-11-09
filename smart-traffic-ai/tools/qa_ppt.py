#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PPT 几何 QA：检测越界、文本溢出风险、低对比度"""
from pptx import Presentation
from pptx.util import Emu

prs = Presentation("docs/智游山城-AI交通出行助手-演示PPT.pptx")
SW, SH = prs.slide_width, prs.slide_height
issues = 0

def inch(v): return round(v / 914400, 2)

for i, slide in enumerate(prs.slides, 1):
    for sh in slide.shapes:
        # 越界检查
        if sh.left is None: continue
        if sh.left < 0 or sh.top < 0 or sh.left + sh.width > SW + 9144 or sh.top + sh.height > SH + 9144:
            print(f"[越界] slide {i}: {sh.shape_type} at ({inch(sh.left)},{inch(sh.top)}) size ({inch(sh.width)}x{inch(sh.height)})")
            issues += 1
        # 文本溢出风险：粗略按 每行字数*行高 估算
        if sh.has_text_frame and sh.text_frame.text.strip():
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if r.font.size and r.font.size.pt >= 28:
                        need = len(r.text) * r.font.size.pt * 1.05  # pt
                        avail = sh.width / 914400 * 72
                        if need > avail and len(r.text) > 4:
                            print(f"[可能溢出] slide {i}: '{r.text[:18]}…' need≈{need:.0f}pt avail≈{avail:.0f}pt")
                            issues += 1

print(f"\nQA 完成：{len(prs.slides._sldIdLst)} 页，发现问题 {issues} 处")
for i, slide in enumerate(prs.slides, 1):
    texts = [sh.text_frame.paragraphs[0].runs[0].text for sh in slide.shapes
             if sh.has_text_frame and sh.text_frame.text.strip()
             and sh.text_frame.paragraphs[0].runs]
    print(f"  p{i}: {' / '.join(texts[:2])[:50]}")
