#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成参赛演示 PPT：智游山城 · AI 交通出行助手"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# 视觉系统：与网页一致 —— 暖纸底 / 墨蓝 / 火锅红
PAPER = RGBColor(0xF4, 0xEE, 0xE2)
INK = RGBColor(0x23, 0x2F, 0x3B)
SOFT = RGBColor(0x5C, 0x6A, 0x78)
ACCENT = RGBColor(0xC8, 0x45, 0x2E)
TEAL = RGBColor(0x2E, 0x6F, 0x6B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = prs.slide_width, prs.slide_height


def bg(slide, color=PAPER):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def rect(slide, x, y, w, h, color, line=None):
    from pptx.enum.shapes import MSO_SHAPE
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    sp.fill.solid()
    sp.fill.fore_color.rgb = color
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
    sp.shadow.inherit = False
    return sp


def text(slide, x, y, w, h, runs, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT,
         font="Microsoft YaHei", spacing=1.25, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, line in enumerate(runs if isinstance(runs, list) else [runs]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        if isinstance(line, tuple):
            content, opts = line
        else:
            content, opts = line, {}
        r = p.add_run()
        r.text = content
        f = r.font
        f.size = Pt(opts.get("size", size))
        f.bold = opts.get("bold", bold)
        f.color.rgb = opts.get("color", color)
        f.name = font
    return tb


def header(slide, no, title, sub=""):
    """内页统一页眉：竖排序号方块 + 标题"""
    bg(slide)
    rect(slide, 0, 0, Inches(0.22), SH, ACCENT)
    rect(slide, Inches(0.75), Inches(0.62), Inches(0.62), Inches(0.62), ACCENT)
    text(slide, Inches(0.75), Inches(0.62), Inches(0.62), Inches(0.62), no,
         size=22, color=WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(slide, Inches(1.62), Inches(0.58), Inches(10.6), Inches(0.75), title,
         size=30, bold=True)
    if sub:
        text(slide, Inches(1.62), Inches(1.28), Inches(10.6), Inches(0.45), sub,
             size=14, color=SOFT)
    rect(slide, Inches(1.62), Inches(1.82), Inches(2.4), Pt(2.6), ACCENT)


def bullets(slide, x, y, w, items, size=17, gap=1.55):
    """items: [(小标题, 说明), ...]"""
    cy = y
    for head, body in items:
        rect(slide, x, cy + Inches(0.09), Inches(0.16), Inches(0.16), ACCENT)
        text(slide, x + Inches(0.34), cy - Inches(0.05), w, Inches(0.45), head,
             size=size + 2, bold=True)
        tb = text(slide, x + Inches(0.34), cy + Inches(0.38), w, Inches(0.8), body,
                  size=size - 2, color=SOFT, spacing=1.3)
        cy += Inches(gap)
    return cy


# ─────────────────────────── 1. 封面 ───────────────────────────
s = prs.slides.add_slide(BLANK)
bg(s, INK)
rect(s, 0, Inches(6.9), SW, Inches(0.6), ACCENT)
rect(s, Inches(0.9), Inches(1.15), Inches(1.5), Inches(1.5), ACCENT)
text(s, Inches(0.9), Inches(1.15), Inches(1.5), Inches(1.5), "渝",
     size=64, color=WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
text(s, Inches(2.75), Inches(1.2), Inches(9.8), Inches(1.1), "智游山城",
     size=58, color=WHITE, bold=True)
text(s, Inches(2.78), Inches(2.28), Inches(9.8), Inches(0.6),
     "AI 交通出行助手 —— 让游客在拥堵城市里聪明出行",
     size=22, color=RGBColor(0xD8, 0xCC, 0xB2))
rect(s, Inches(1.0), Inches(3.4), Inches(2.2), Pt(3), ACCENT)
text(s, Inches(1.0), Inches(3.85), Inches(11.4), Inches(1.6),
     [("2026 川渝大学生“数智”作品设计应用技能大赛", {"size": 22, "bold": True, "color": WHITE}),
      ("人工智能+应用组 · 参赛作品", {"size": 18, "color": RGBColor(0xB9, 0xC4, 0xCE)})])
text(s, Inches(1.0), Inches(5.55), Inches(11.4), Inches(1.2),
     [("参赛团队：____________     指导教师：____________", {"size": 15, "color": RGBColor(0x8E, 0x9B, 0xA8)}),
      ("赛道方向：大模型应用 × 智慧文旅交通", {"size": 15, "color": RGBColor(0x8E, 0x9B, 0xA8)})])

# ─────────────────────────── 2. 痛点 ───────────────────────────
s = prs.slides.add_slide(BLANK)
header(s, "壹", "为什么做这件事", "节假日旅游城市的出行困境")
bullets(s, Inches(1.0), Inches(2.35), Inches(11.2), [
    ("游客“三不知”", "不知道什么时候去不堵 · 不知道怎么走最优 · 不知道去哪错峰。信息差直接转化为排队 2 小时、走错山路、错过夜景。"),
    ("城市“潮汐式”拥堵", "节假日渝中半岛车流集中爆发：洪崖洞—解放碑—索道一带 19:00–22:00 人流巅峰，路段通行时间可达平峰 3 倍。"),
    ("现有导航的不足", "通用地图导航只回答“怎么走最快”，不回答“怎么玩最好”：缺少游览顺序、停留时长、错峰时机的一体化建议。"),
], size=18, gap=1.62)
rect(s, Inches(1.0), Inches(6.55), Inches(11.3), Inches(0.62), RGBColor(0xFD, 0xF3, 0xE7))
text(s, Inches(1.25), Inches(6.62), Inches(11.0), Inches(0.5),
     "我们的命题：把「拥堵预测 + 智能规划 + 大模型问答」装进一个页面，让游客 30 秒拿到可执行的出行方案。",
     size=14.5, color=RGBColor(0x9C, 0x2F, 0x1D), bold=True)

# ─────────────────────────── 3. 方案总览 ───────────────────────────
s = prs.slides.add_slide(BLANK)
header(s, "贰", "作品总览：四个 AI 能力协同", "Web 应用 · 前后端一体 · 开箱即演示")
bullets(s, Inches(1.0), Inches(2.35), Inches(11.2), [
    ("🗺️ 实时路况热力地图", "两江四岸交互地图：拖动时间轴（06:00–23:00）+ 切换晴/雨/雾，全城 17 条路段拥堵态势实时重绘。"),
    ("🧭 AI 路线规划引擎", "出发点 + 多景点 + 出发时间 → 自动排游览顺序，输出每段交通方式、到达/离开时刻、错峰建议。"),
    ("📈 轻量拥堵预测模型", "时段双峰曲线 × 节假日系数 × 天气系数，纯 CPU 秒级出结果，可解释、可复现、可换城市。"),
    ("💬 AI 出行顾问（RAG）", "自然语言问答，知识库检索 + 大模型增强双层架构，断网无 Key 自动降级，演示永不翻车。"),
], size=17, gap=1.28)

# ─────────────────────────── 4. 路线规划 ───────────────────────────
s = prs.slides.add_slide(BLANK)
header(s, "叁", "核心功能：AI 路线规划", "时间依赖最短路 + 贪心行程编排")
bullets(s, Inches(1.0), Inches(2.35), Inches(6.6), [
    ("算法", "Dijkstra（时间依赖版）：边权 = 当前时刻的预测行程时间，出发时间不同 → 路线不同。"),
    ("编排", "贪心选择“到达最早”的下一景点，自然规避拥堵；全程停留时长参与时间推进。"),
    ("输出", "游览顺序 · 每段交通方式（轨道/打车/步行）· 到达离开时刻 · 逐段拥堵等级 · 错峰建议。"),
], size=16, gap=1.5)
rect(s, Inches(8.1), Inches(2.35), Inches(4.3), Inches(4.3), WHITE)
text(s, Inches(8.4), Inches(2.6), Inches(3.8), Inches(0.5), "演示用例", size=16, bold=True, color=ACCENT)
text(s, Inches(8.4), Inches(3.15), Inches(3.8), Inches(3.3),
     [("出发：重庆北站 09:00", {"size": 13.5, "bold": True}),
      ("想去：洪崖洞 / 磁器口 / 长江索道", {"size": 13, "color": SOFT}),
      ("", {"size": 6}),
      ("系统输出（真实计算）：", {"size": 13.5, "bold": True}),
      ("① 磁器口 09:58 到 → 11:58 走", {"size": 12.5, "color": SOFT}),
      ("② 洪崖洞 13:2x 到 → …", {"size": 12.5, "color": SOFT}),
      ("③ 长江索道 …", {"size": 12.5, "color": SOFT}),
      ("", {"size": 6}),
      ("总在途 58.4+ 分钟，含逐段拥堵提示", {"size": 12.5, "color": ACCENT})])

# ─────────────────────────── 5. 拥堵预测 ───────────────────────────
s = prs.slides.add_slide(BLANK)
header(s, "肆", "核心功能：拥堵预测模型", "可解释 · 轻量 · 确定性可复现")
text(s, Inches(1.0), Inches(2.3), Inches(11.2), Inches(0.7),
     "路段行程时间 = 自由流时间 × congestion_ratio(路段, 时刻, 天气)",
     size=19, bold=True, color=TEAL)
bullets(s, Inches(1.0), Inches(2.9), Inches(11.2), [
    ("时段基线", "工作日双峰曲线（08:00 / 18:00 通勤峰）、节假日出游单峰（10:00–17:00），两条 24 小时曲线驱动。"),
    ("多因子叠加", "路段两端景点热度 × 节假日放大（+35%）；天气系数：晴 1.00 / 雨 1.18 / 雾 1.12（重庆多雾）；确定性扰动模拟偶发状况。"),
    ("工程特性", "同一输入必得同一输出（CRC32 播种）→ 答辩现场可复现任意结果；纯 Python 零依赖，CPU 秒级响应。"),
    ("可升级", "接口与真实数据训练兼容：接入高德/百度交通态势开放数据后可替换为回归模型，上层 API 不变。"),
], size=16, gap=1.05)

# ─────────────────────────── 6. AI 问答 ───────────────────────────
s = prs.slides.add_slide(BLANK)
header(s, "伍", "核心功能：AI 出行顾问", "RAG 检索 + 大模型增强，双层降级设计")
bullets(s, Inches(1.0), Inches(2.35), Inches(11.2), [
    ("检索层（始终可用）", "14 条出行知识库（洪崖洞限流、索道排队、北站广场、错峰原则…），2-gram 关键词检索，离线可跑。"),
    ("大模型层（可插拔）", "配置 LLM_API_KEY 后自动启用：知识库内容 + 实时路况摘要作为上下文注入，回答具体、不编造数据。"),
    ("降级策略", "断网 / 无 Key / 接口超时 → 自动回退检索式回答，标注数据来源。答辩现场的“保险丝”。"),
    ("交互细节", "快捷问题一键提问，回答标注〔大模型增强〕/〔知识库检索〕来源，可解释、可追问。"),
], size=16, gap=1.12)

# ─────────────────────────── 7. 系统架构 ───────────────────────────
s = prs.slides.add_slide(BLANK)
header(s, "陆", "系统架构与技术栈", "前后端一体 · 部署简单 · 易移植")
bullets(s, Inches(1.0), Inches(2.35), Inches(11.2), [
    ("前端", "原生 HTML/CSS/JS 单页应用：SVG 交互地图、时间轴拖拽、行程卡片、对话面板。无构建工具，零依赖。"),
    ("后端", "Python + FastAPI：4 组 RESTful API（景点 / 路况 / 规划 / 问答），静态资源一体托管，一条命令启动。"),
    ("算法层", "时间依赖 Dijkstra + 贪心行程编排 + 多因子拥堵预测 + RAG 检索问答，模块解耦、接口标准化。"),
    ("扩展性", "换一份 data/*.json 路网数据即可移植到成都、西安等任意旅游城市；易接入小程序 / 公众号 / 大屏。"),
], size=16, gap=1.12)

# ─────────────────────────── 8. 演示脚本 ───────────────────────────
s = prs.slides.add_slide(BLANK)
header(s, "柒", "现场演示脚本（约 3 分钟）", "照着走即可，全程真实计算")
items = [
    ("0:00–0:30", "拖动时间轴 06→23 点，展示全城路段从畅通到“严重拥堵”的实时变化；切“雨天”看系数跳升。"),
    ("0:30–1:30", "点选景点（洪崖洞/磁器口/索道）→ 生成行程：展示自动排序、逐段交通方式、错峰建议。"),
    ("1:30–2:15", "AI 顾问提问：“洪崖洞什么时候去不堵？”“下雨天推荐去哪？”展示自然语言问答。"),
    ("2:15–3:00", "拔网线/不配 Key 再问一次 → 降级到知识库回答，强调“演示永不翻车”的工程设计。"),
]
cy = Inches(2.35)
for t, d in items:
    rect(s, Inches(1.0), cy, Inches(1.55), Inches(0.52), INK)
    text(s, Inches(1.0), cy, Inches(1.55), Inches(0.52), t,
         size=13, color=WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, Inches(2.8), cy - Inches(0.02), Inches(9.6), Inches(0.9), d, size=14.5, spacing=1.25)
    cy += Inches(1.12)

# ─────────────────────────── 9. 创新点 ───────────────────────────
s = prs.slides.add_slide(BLANK)
header(s, "捌", "创新点与赛道契合", "人工智能+应用组")
bullets(s, Inches(1.0), Inches(2.35), Inches(11.2), [
    ("四类 AI 能力协同", "预测模型 + 智能规划 + RAG 检索 + 大模型生成，不是单点 API 调用，而是完整决策闭环。"),
    ("“规划即对话”场景创新", "从‘导航怎么走’升级为‘行程怎么排’：把交通工程的时间依赖最短路翻译成游客能直接用的语言。"),
    ("面向真实痛点", "节假日错峰、索道排队、北站走错广场——知识库来自真实重庆出行避坑经验，可直接服务游客。"),
    ("稳健工程设计", "大模型可插拔降级、确定性可复现、零依赖部署——为答辩与真实使用场景各上了一道保险。"),
], size=17, gap=1.28)

# ─────────────────────────── 10. 结尾 ───────────────────────────
s = prs.slides.add_slide(BLANK)
bg(s, INK)
rect(s, 0, Inches(6.9), SW, Inches(0.6), ACCENT)
text(s, Inches(1.1), Inches(2.5), Inches(11.2), Inches(1.2), "谢谢观看",
     size=52, color=WHITE, bold=True)
text(s, Inches(1.12), Inches(3.85), Inches(11.2), Inches(0.6),
     "智游山城 · AI 交通出行助手 —— 让每一条路都走得明白",
     size=20, color=RGBColor(0xD8, 0xCC, 0xB2))
rect(s, Inches(1.15), Inches(4.75), Inches(2.2), Pt(3), ACCENT)
text(s, Inches(1.12), Inches(5.2), Inches(11.2), Inches(0.9),
     [("代码开源：github.com/<your-username>/smart-traffic-ai", {"size": 15, "color": RGBColor(0x8E, 0x9B, 0xA8)}),
      ("2026 川渝大学生“数智”作品设计应用技能大赛 · 人工智能+应用组", {"size": 15, "color": RGBColor(0x8E, 0x9B, 0xA8)})])

prs.save("docs/智游山城-AI交通出行助手-演示PPT.pptx")
print("saved:", len(prs.slides.__iter__.__self__._sldIdLst), "slides")
