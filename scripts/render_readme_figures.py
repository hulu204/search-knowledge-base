"""生成 README 配图（assets/readme/*.png）。需要本机装有 Google Chrome。

用法：python3 scripts/render_readme_figures.py
文章数量变化后，先改下面 TOPICS / SOURCES 里的数字再运行。
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
OUT = REPO / "assets" / "readme"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONT = "PingFang SC, Helvetica Neue, Arial, sans-serif"
INK, GRAY = "#232F3E", "#5F6B7A"

STYLE = {
    "offline": ("#E07B00", "#FFF6EA"),
    "online": ("#1F6FD1", "#EEF5FF"),
    "store": ("#7B4BD6", "#F5F0FF"),
    "gpu": ("#4E9A1A", "#F0F8E8"),
    "mq": ("#5F6B7A", "#F4F6F8"),
    "ext": ("#8A94A3", "#FFFFFF"),
}
LINE = {"offline": "#E07B00", "online": "#1F6FD1", "ctrl": "#8A94A3"}


def text_width(s: str, size: float) -> float:
    return sum(size if ord(c) > 0x2E7F else size * 0.56 for c in s)


class Canvas:
    def __init__(self):
        self.parts: list[str] = []

    def add(self, s):
        self.parts.append(s)

    def box(self, x, y, w, h, title, lines=(), kind="online", dashed=False):
        stroke, fill = STYLE[kind]
        dash = ' stroke-dasharray="10 7"' if dashed else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="3"{dash}/>')
        self.add(f'<rect x="{x}" y="{y}" width="10" height="{h}" rx="5" fill="{stroke}"/>')
        total = 34 + len(lines) * 30
        ty = y + (h - total) / 2 + 28
        cx = x + w / 2 + 5
        self.add(f'<text x="{cx}" y="{ty}" font-size="28" font-weight="700" fill="{INK}" '
                 f'text-anchor="middle">{title}</text>')
        for i, line in enumerate(lines):
            self.add(f'<text x="{cx}" y="{ty + 38 + i * 30}" font-size="20" fill="{GRAY}" '
                     f'text-anchor="middle">{line}</text>')

    def frame(self, x, y, w, h, label, color, fill, tag):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{color}" stroke-width="3"/>')
        tw = text_width(tag, 24) + 36
        self.add(f'<rect x="{x}" y="{y}" width="{tw}" height="54" fill="{color}"/>')
        self.add(f'<text x="{x + tw / 2}" y="{y + 36}" font-size="24" font-weight="700" fill="#fff" '
                 f'text-anchor="middle">{tag}</text>')
        self.add(f'<text x="{x + tw + 20}" y="{y + 37}" font-size="28" font-weight="700" fill="{color}">{label}</text>')

    def label(self, x, y, s, color):
        w = text_width(s, 20) + 18
        self.add(f'<rect x="{x - w / 2}" y="{y - 17}" width="{w}" height="32" rx="6" fill="#fff" '
                 f'stroke="{color}" stroke-width="1.5"/>')
        self.add(f'<text x="{x}" y="{y + 7}" font-size="20" fill="{color}" text-anchor="middle">{s}</text>')

    def arrow(self, points, kind="online", text=None, at=None, both=False):
        color = LINE[kind]
        dash = ' stroke-dasharray="9 7"' if kind == "ctrl" else ""
        pts = " ".join(f"{px},{py}" for px, py in points)
        start = f' marker-start="url(#s-{kind})"' if both else ""
        self.add(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3"'
                 f'{dash} marker-end="url(#e-{kind})"{start}/>')
        if text:
            if at is None:
                (x1, y1), (x2, y2) = points[0], points[1]
                at = ((x1 + x2) / 2, (y1 + y2) / 2)
            self.label(at[0], at[1], text, color)

    def pill(self, x_right, y, s, color, fill):
        w = text_width(s, 30) + 56
        self.add(f'<rect x="{x_right - w}" y="{y - 34}" width="{w}" height="68" rx="34" fill="{fill}"/>')
        self.add(f'<text x="{x_right - w / 2}" y="{y + 11}" font-size="30" font-weight="600" fill="{color}" '
                 f'text-anchor="middle">{s}</text>')
        return x_right - w

    def header(self, kicker, title):
        self.add(f'<text x="80" y="70" font-size="30" font-weight="600" fill="{GRAY}">{kicker}</text>')
        self.add(f'<text x="80" y="150" font-size="64" font-weight="800" fill="{INK}">{title}</text>')

    def legend(self, y, lines, kinds):
        lx = 80
        for kind, name in lines:
            self.add(f'<line x1="{lx}" y1="{y}" x2="{lx + 70}" y2="{y}" stroke="{LINE[kind]}" stroke-width="3" '
                     f'marker-end="url(#e-{kind})"/>')
            self.add(f'<text x="{lx + 85}" y="{y + 8}" font-size="22" fill="{GRAY}">{name}</text>')
            lx += 300
        for kind, name in kinds:
            stroke, fill = STYLE[kind]
            self.add(f'<rect x="{lx}" y="{y - 14}" width="28" height="28" rx="6" fill="{fill}" '
                     f'stroke="{stroke}" stroke-width="3"/>')
            self.add(f'<text x="{lx + 40}" y="{y + 8}" font-size="22" fill="{GRAY}">{name}</text>')
            lx += 40 + text_width(name, 22) + 70

    def render(self, name, w, h):
        defs = ["<defs>"]
        for kind, color in LINE.items():
            defs.append(f'<marker id="e-{kind}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                        f'markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>')
            defs.append(f'<marker id="s-{kind}" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" '
                        f'markerHeight="7" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="{color}"/></marker>')
        defs.append("</defs>")
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
               f'font-family="{FONT}"><rect width="{w}" height="{h}" fill="#fff"/>{"".join(defs)}'
               f'{"".join(self.parts)}</svg>')
        html = OUT / f"_{name}.html"
        html.write_text(f'<html><body style="margin:0">{svg}</body></html>', encoding="utf-8")
        png = OUT / f"{name}.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={w},{h}", f"--screenshot={png}", html.as_uri()],
                       check=True, capture_output=True)
        html.unlink()
        print("ok", png)


# ================= 1. 工作原理 =================
c = Canvas()
W, H = 2760, 1400
c.header("01 · 工作原理", "一张图看全流程")
x = W - 80
x = c.pill(x, 115, "数据只在本机", "#1F6FD1", "#EEF5FF") - 24
x = c.pill(x, 115, "语义 + 关键词两路检索", "#4E9A1A", "#F0F8E8") - 24
c.pill(x, 115, "2421 篇公开技术文章", "#E07B00", "#FFF4E5")

# --- 入库 ---
c.frame(80, 210, 2260, 300, "入库：把文章变成可检索的文本块", "#E07B00", "#FFFCF7", "离线")
CY = 385
bx = [110 + i * 380 for i in range(6)]
c.box(bx[0], 300, 300, 170, "文章来源", ["公众号 · 微信读书", "RSS · 网页链接 · 网页存档"], "ext", dashed=True)
c.box(bx[1], 300, 300, 170, "抓取 + 解析", ["正文抽取 · 主题标签", "配图文字识别"], "offline")
c.box(bx[2], 300, 300, 170, "文章库", ["articles/ Markdown 正文", "2421 篇"], "store")
c.box(bx[3], 300, 300, 170, "切成文本块", ["按标题层级递归切分", "每块 ≤1800 token · 不重叠"], "offline")
c.box(bx[4], 300, 300, 170, "bge-m3 模型", ["语义向量 1024 维", "关键词权重"], "gpu")
c.box(bx[5], 300, 300, 170, "本地索引", ["kb.sqlite 原文和元数据", "dense.npy · sparse.npz"], "store")
for i in range(5):
    c.arrow([(bx[i] + 300, CY), (bx[i + 1], CY)], "offline")

# --- 在线演示 ---
c.box(2440, 760, 280, 170, "在线演示", ["GitHub Pages", "纯关键词检索"], "mq")
c.arrow([(2310, CY), (2580, CY), (2580, 760)], "offline", "只导出公开文章", at=(2580, 600))

# --- 查询 ---
c.frame(80, 680, 2260, 600, "查询：在本机检索，返回带出处的原文", "#1F6FD1", "#FFFFFF", "本机")
c.box(110, 760, 300, 170, "调用方", ["本地工作台 :3917", "AI 工具（MCP）"], "ext", dashed=True)
c.box(1630, 760, 680, 170, "检索服务 kb-server", ["语义和关键词两路各取 50 个候选", "融合排序后返回"], "online")
c.arrow([(410, 810), (1630, 810)], "online", "查询", at=(1020, 810))
c.arrow([(1630, 880), (410, 880)], "online", "返回：文本块原文 + 标题 · 来源 · 原文链接", at=(1020, 880))
c.arrow([(1780, 470), (1780, 760)], "online", "问题用同一模型编码", at=(1780, 625), both=True)
c.arrow([(2160, 470), (2160, 760)], "online", "读取向量和原文", at=(2160, 625), both=False)

# 一次查询的 5 步
px, py, pw, ph = 110, 990, 2200, 250
c.add(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="14" fill="#F7FAFF" '
      f'stroke="#1F6FD1" stroke-width="2" stroke-dasharray="8 6"/>')
c.add(f'<text x="{px + 28}" y="{py + 44}" font-size="24" font-weight="700" fill="#1F6FD1">一次查询的 5 步</text>')
steps = [
    ("① 编码问题", "语义向量 + 关键词权重"),
    ("② 两路打分", "语义相似度 · 关键词匹配"),
    ("③ 融合排序", "RRF 按名次合并，k=60"),
    ("④ 时间加权", "半衰期 2 年，最低 0.7 倍"),
    ("⑤ 每篇留 1 块", "默认返回前 6 条"),
]
gap, cw, ch, cy0 = 60, (pw - 56 - 4 * 60) / 5, 130, py + 80
for i, (t, s) in enumerate(steps):
    cx0 = px + 28 + i * (cw + gap)
    c.add(f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" rx="12" fill="#fff" stroke="#BCD3F2" stroke-width="2"/>')
    c.add(f'<text x="{cx0 + cw / 2}" y="{cy0 + 55}" font-size="26" font-weight="700" fill="{INK}" text-anchor="middle">{t}</text>')
    c.add(f'<text x="{cx0 + cw / 2}" y="{cy0 + 95}" font-size="20" fill="{GRAY}" text-anchor="middle">{s}</text>')
    if i < 4:
        c.arrow([(cx0 + cw + 8, cy0 + ch / 2), (cx0 + cw + gap - 8, cy0 + ch / 2)], "online")

c.legend(1340, [("offline", "入库数据流"), ("online", "查询请求")],
         [("offline", "处理步骤"), ("online", "检索服务"), ("store", "存储"), ("gpu", "模型"),
          ("mq", "在线演示"), ("ext", "外部")])
c.render("pipeline", W, H)


# ================= 2. 收录了什么 =================
TOPICS = [("搜索", 565), ("召回", 318), ("工程相关", 239), ("推荐", 172), ("问答/RAG", 139),
          ("索引构建", 136), ("排序", 127), ("搜索/RAG", 127), ("广告", 96), ("爬虫抓取", 93),
          ("其余 38 个标签", 409)]
SOURCES = [("DataFun", 234), ("Elastic", 221), ("Sease", 131), ("Marginalia", 121), ("eugeneyan", 121),
           ("百度", 102), ("LanceDB", 99), ("阿里妈妈", 96), ("阿里淘系", 96), ("Tunkelang", 93),
           ("其余 110 个来源", 1107)]
assert sum(v for _, v in TOPICS) == 2421 and sum(v for _, v in SOURCES) == 2421

c = Canvas()
W = 2760
c.header("02 · 收录了什么", "2421 篇文章的主题和来源")
x = W - 80
x = c.pill(x, 115, "120 个来源", "#1F6FD1", "#EEF5FF") - 24
c.pill(x, 115, "48 个主题标签", "#E07B00", "#FFF4E5")


def bars(fx, fy, fw, title, tag, color, fill, rows):
    top_rows, (rest_name, rest_v) = rows[:-1], rows[-1]
    fh = 100 + len(top_rows) * 74 + 90
    c.frame(fx, fy, fw, fh, title, color, fill, tag)
    lw, top = 230, fy + 100
    bw_max = fw - lw - 160
    vmax = max(v for _, v in top_rows)
    for i, (name, v) in enumerate(top_rows):
        y = top + i * 74
        c.add(f'<text x="{fx + lw}" y="{y + 32}" font-size="24" font-weight="600" '
              f'fill="{INK}" text-anchor="end">{name}</text>')
        bw = bw_max * v / vmax
        c.add(f'<rect x="{fx + lw + 24}" y="{y}" width="{bw}" height="46" rx="8" fill="{color}"/>')
        c.add(f'<text x="{fx + lw + 24 + bw + 14}" y="{y + 32}" font-size="24" font-weight="700" '
              f'fill="{color}">{v}</text>')
    y = top + len(top_rows) * 74 + 10
    c.add(f'<line x1="{fx + 30}" y1="{y - 22}" x2="{fx + fw - 30}" y2="{y - 22}" stroke="#E3E7EC" stroke-width="2"/>')
    c.add(f'<text x="{fx + lw + 24}" y="{y + 26}" font-size="24" fill="{GRAY}">{rest_name}，共 {rest_v} 篇</text>')
    return fy + fh


bottom = bars(80, 210, 1260, "按主题（篇）", "主题", "#E07B00", "#FFFCF7", TOPICS)
bars(1420, 210, 1260, "按来源（篇）", "来源", "#1F6FD1", "#FFFFFF", SOURCES)
H = bottom + 90
c.add(f'<text x="80" y="{bottom + 55}" font-size="22" fill="{GRAY}">主题和来源取自每篇文章的 tag / company 字段，'
      f'意思相近的标签没有合并。</text>')
c.render("corpus", W, H)
