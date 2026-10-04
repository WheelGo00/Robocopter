"""生成《无人机硬件组成报告》里的整机硬件连接框图。

用法：python tools/make_block_diagram.py
输出：images/hardware-block-diagram.png
依赖：Pillow；中文字体使用 Windows 自带的微软雅黑。
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1800, 1200
DY = 40  # 标题与分组标签各占一行，图形整体下移
BG = "#FFFFFF"
TEXT = "#1F2328"
LABEL = "#57606A"

FONT_REG = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"


def font(path, size):
    return ImageFont.truetype(path, size)


# 每个方框：(x, y, w, h, 文字, 类别)
BOXES = [
    (60, 110, 320, 80, "全向 / 下视视觉系统", "sense"),
    (60, 210, 320, 80, "三维红外传感系统", "sense"),
    (60, 310, 320, 80, "GNSS 模块", "sense"),
    (60, 560, 320, 80, "智能飞行电池", "power"),
    (60, 700, 320, 80, "USB-C 充电 / 调参接口", "power"),
    (60, 840, 320, 80, "增强图传模块（4G，选配）", "power"),
    (520, 150, 320, 300, "飞控主控板", "fc"),
    (520, 700, 320, 80, "O4 图传模块 + 四天线", "comm"),
    (980, 110, 320, 80, "电调 ×4", "act"),
    (980, 210, 320, 80, "无刷电机 ×4", "act"),
    (980, 310, 320, 80, "折叠螺旋桨 ×4", "act"),
    (980, 460, 320, 80, "三轴云台", "act"),
    (980, 560, 320, 80, "相机 1/1.3 英寸 CMOS", "load"),
    (980, 660, 320, 80, "microSD 卡槽", "load"),
    (1400, 840, 300, 80, "遥控器 RC 2 / RC-N2", "comm"),
    (1400, 960, 300, 80, "移动设备 / DJI Fly", "comm"),
]

STYLE = {
    "sense": ("#EAF3FF", "#2F6FBF"),
    "fc": ("#FFF4E5", "#D98200"),
    "act": ("#EAF7EE", "#2E8B57"),
    "load": ("#EAF7EE", "#2E8B57"),
    "power": ("#F4EBFB", "#7B4FA8"),
    "comm": ("#FDECEF", "#C0392B"),
}

# 每条箭头：(起点, 终点, 标注, 是否虚线)
ARROWS = [
    ((380, 150), (520, 195), "图像", False),
    ((380, 250), (520, 285), "对地高度", False),
    ((380, 350), (520, 375), "位置与时间", False),
    ((380, 600), (520, 405), "供电与电池数据", False),
    ((840, 190), (980, 150), "转速指令", False),
    ((1140, 190), (1140, 210), "", False),
    ((1140, 290), (1140, 310), "", False),
    ((840, 330), (980, 495), "增稳指令", False),
    ((1140, 540), (1140, 560), "", False),
    ((1140, 640), (1140, 660), "", False),
    ((680, 450), (680, 700), "图传数据", False),
    ((840, 740), (1400, 885), "2.4 / 5.1 / 5.8 GHz 无线", False),
    ((1550, 920), (1550, 960), "转接线", False),
    ((220, 700), (220, 640), "充电", False),
    ((220, 780), (220, 840), "双头 USB-C", True),
    ((380, 880), (1400, 880), "4G 蜂窝链路", True),
]


def draw_box(draw, x, y, w, h, text, kind):
    fill, border = STYLE[kind]
    draw.rounded_rectangle((x, y, x + w, y + h), radius=14, fill=fill, outline=border, width=3)
    f = font(FONT_BOLD, 28) if kind == "fc" else font(FONT_REG, 24)
    lines = text.split("\n")
    heights = [draw.textbbox((0, 0), line, font=f)[3] for line in lines]
    total = sum(heights) + (len(lines) - 1) * 12
    cy = y + h / 2 - total / 2
    for line, lh in zip(lines, heights):
        tw = draw.textbbox((0, 0), line, font=f)[2]
        draw.text((x + w / 2 - tw / 2, cy), line, font=f, fill=TEXT)
        cy += lh + 12


def arrowhead(draw, p0, p1, color, size=14):
    import math

    angle = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    x, y = p1
    pts = [
        (x, y),
        (x - size * math.cos(angle - math.pi / 7), y - size * math.sin(angle - math.pi / 7)),
        (x - size * math.cos(angle + math.pi / 7), y - size * math.sin(angle + math.pi / 7)),
    ]
    draw.polygon(pts, fill=color)


def dashed_line(draw, p0, p1, color, width=3, dash=16, gap=10):
    import math

    total = math.dist(p0, p1)
    if total == 0:
        return
    ux, uy = (p1[0] - p0[0]) / total, (p1[1] - p0[1]) / total
    pos = 0.0
    while pos < total:
        end = min(pos + dash, total)
        draw.line(
            [(p0[0] + ux * pos, p0[1] + uy * pos), (p0[0] + ux * end, p0[1] + uy * end)],
            fill=color,
            width=width,
        )
        pos = end + gap


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    title_font = font(FONT_BOLD, 40)
    title = "DJI Mini 4 Pro 整机硬件连接框图"
    tw = draw.textbbox((0, 0), title, font=title_font)[2]
    draw.text((W / 2 - tw / 2, 30), title, font=title_font, fill=TEXT)

    # 分组标题
    area_font = font(FONT_BOLD, 24)
    draw.text((60, 98), "感知 · 决策 · 电源", font=area_font, fill=LABEL)
    draw.line([(60, 134), (300, 134)], fill="#D8DEE4", width=3)
    draw.text((980, 98), "执行 · 负载", font=area_font, fill=LABEL)
    draw.line([(980, 134), (1180, 134)], fill="#D8DEE4", width=3)

    for (x1, y1), (x2, y2), label, dashed in ARROWS:
        y1, y2 = y1 + DY, y2 + DY
        color = "#7B4FA8" if dashed else "#57606A"
        if dashed:
            dashed_line(draw, (x1, y1), (x2, y2), color)
        else:
            draw.line([(x1, y1), (x2, y2)], fill=color, width=3)
        arrowhead(draw, (x1, y1), (x2, y2), color)
        if label:
            mid = ((x1 + x2) / 2, (y1 + y2) / 2)
            f = font(FONT_REG, 20)
            lw = draw.textbbox((0, 0), label, font=f)[2]
            lh = draw.textbbox((0, 0), label, font=f)[3]
            draw.rectangle((mid[0] - lw / 2 - 6, mid[1] - lh / 2 - 4, mid[0] + lw / 2 + 6, mid[1] + lh / 2 + 6), fill=BG)
            draw.text((mid[0] - lw / 2, mid[1] - lh / 2), label, font=f, fill=LABEL)

    for x, y, w, h, text, kind in BOXES:
        draw_box(draw, x, y + DY, w, h, text, kind)

    legend_font = font(FONT_REG, 22)
    y0 = 1140
    draw.line([(60, y0), (140, y0)], fill="#57606A", width=3)
    draw.text((155, y0 - 14), "机内连接 / 直连", font=legend_font, fill=LABEL)
    dashed_line(draw, (480, y0), (560, y0), "#7B4FA8")
    draw.text((575, y0 - 14), "选配模块与蜂窝链路", font=legend_font, fill=LABEL)
    draw.text((900, y0 - 14), "依据：DJI Mini 4 Pro 技术参数与用户手册", font=legend_font, fill=LABEL)

    out = Path(__file__).resolve().parent.parent / "images" / "hardware-block-diagram.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print("saved", out)


if __name__ == "__main__":
    main()
