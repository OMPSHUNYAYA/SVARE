#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2
import numpy as np
import hashlib
import math
import os

VERSION = "8.8"

WIDTH = 1600
HEIGHT = 900
OUTPUT_WIDTH = 1920
OUTPUT_HEIGHT = 1080
FPS = 24

OUT_VIDEO = "SVARE_Deterministic_Structural_Cinema_v8_8.mp4"
OUT_POSTER = "SVARE_Deterministic_Structural_Cinema_v8_8_Poster.png"
OUT_VERIFY = "SVARE_Deterministic_Structural_Cinema_v8_8_VERIFY.txt"
FAST_RENDER_MODE = True
STATIC_FRAME_ANIMATION = False
ENABLE_LIGHT_MOTION = False
ANIMATION_SAMPLES = 12

WHITE  = (248, 251, 255)
MUTED  = (205, 212, 224)
SOFT   = (160, 170, 185)
GOLD   = (255, 204, 35)
GREEN  = (110, 255, 64)
RED    = (255, 72, 60)
ORANGE = (255, 145, 35)
TEAL   = (255, 204, 35)
YELLOW = (255, 220, 45)
BLACK  = (2, 5, 12)
PANEL  = (7, 12, 24)
LINE   = (88, 102, 126)

SLIDE_DURATIONS = [
    5.4, 4.8, 5.0, 4.6, 5.0,
    5.0, 5.0, 4.8, 5.2, 5.2,
    5.0, 5.2, 5.0, 5.0, 5.2,
    5.2, 5.0, 5.4, 6.2,
]

TRANSITION_FRAMES = int(FPS * 0.36)
UI_LINE_Y = 820
TEXT_LIMIT_Y = 760

def load_font(size, bold=True):
    try:
        if os.name == "nt":
            path = r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
        else:
            path = (
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                if bold
                else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            )
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def text_size(draw, text, font):
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1]

def fit_font(draw, text, start, max_width, min_size=18, bold=True):
    size = start
    while size >= min_size:
        f = load_font(size, bold)
        if text_size(draw, text, f)[0] <= max_width:
            return f
        size -= 2
    return load_font(min_size, bold)

def draw_text(draw, xy, text, size, color=WHITE, bold=True,
              max_width=None, min_size=18):
    f = load_font(size, bold)
    if max_width is not None:
        f = fit_font(draw, text, size, max_width, min_size, bold)
    draw.text(xy, text, font=f, fill=color)
    return f

def center_text(draw, text, y, size, color=WHITE, bold=True,
                max_width=None, min_size=18):
    f = load_font(size, bold)
    if max_width is not None:
        f = fit_font(draw, text, size, max_width, min_size, bold)
    w, _ = text_size(draw, text, f)
    draw.text(((WIDTH - w) // 2, y), text, font=f, fill=color)
    return f

def center_in_box(draw, text, box, y, size, color=WHITE, bold=True, min_size=18):
    x1, _, x2, _ = box
    f = fit_font(draw, text, size, x2 - x1 - 40, min_size, bold)
    w, _ = text_size(draw, text, f)
    draw.text((x1 + (x2 - x1 - w) // 2, y), text, font=f, fill=color)
    return f

def panel(draw, box, fill=PANEL, outline=LINE, width=3, radius=24):
    draw.rounded_rectangle(box, radius=radius, fill=fill,
                           outline=outline, width=width)

def gradient_bg(seed=1, primary=GREEN, secondary=GOLD, energy=0.42):
    y = np.linspace(0.0, 1.0, HEIGHT, dtype=np.float32)[:, None]
    x = np.linspace(0.0, 1.0, WIDTH,  dtype=np.float32)[None, :]
    base = 6 + 12*(1-y) + 7*np.sin((x*2.0 + y*1.4 + seed)*math.pi)*energy
    r = base + primary[0]*0.035*(1-y) + secondary[0]*0.025*x
    g = base + primary[1]*0.055*(1-y) + secondary[1]*0.025*x
    b = base + primary[2]*0.035*(1-y) + secondary[2]*0.020*x
    arr = np.dstack([r, g, b]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def add_vignette(img, strength=110):
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(26):
        alpha = int(strength * (i / 25) ** 2)
        draw.rectangle(
            (i*14, i*10, WIDTH-i*14, HEIGHT-i*10),
            outline=(0, 0, 0, alpha), width=22)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def cinematic_bg(seed=1, primary=GREEN, secondary=GOLD,
                 streaks=130, storm=False):
    img = gradient_bg(seed, primary, secondary, 0.36)
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    rng = np.random.default_rng(seed)
    cx = int(rng.integers(250, WIDTH - 250))
    cy = int(rng.integers(150, 540))
    for _ in range(streaks):
        a      = int(rng.integers(14, 70))
        length = int(rng.integers(80, 360))
        x      = int(rng.integers(-120, WIDTH + 120))
        y      = int(rng.integers(40, 780))
        ang    = math.atan2(y - cy, x - cx) + float(rng.normal(0, 0.12))
        x2     = int(x + math.cos(ang) * length)
        y2     = int(y + math.sin(ang) * length)
        col    = primary if rng.random() > 0.38 else secondary
        draw.line((x, y, x2, y2),
                  fill=(col[0], col[1], col[2], a),
                  width=int(rng.integers(1, 4)))
    if storm:
        for _ in range(12):
            x   = int(rng.integers(800, 1500))
            y   = int(rng.integers(80, 520))
            pts = [(x, y)]
            for _ in range(5):
                x += int(rng.integers(-60, 60))
                y += int(rng.integers(28, 68))
                pts.append((x, y))
            draw.line(pts, fill=(primary[0], primary[1], primary[2], 115), width=4)
            draw.line(pts, fill=(255, 255, 255, 50), width=1)
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return add_vignette(img, 120)

def glow_shape(base, draw_func, color, blur=18, repeat=2):
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_func(d, (*color, 170))
    for _ in range(repeat):
        blurred = layer.filter(ImageFilter.GaussianBlur(blur))
        base = Image.alpha_composite(base.convert("RGBA"), blurred).convert("RGB")
    layer2 = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(layer2)
    draw_func(d2, (*color, 255))
    return Image.alpha_composite(base.convert("RGBA"), layer2).convert("RGB")

def draw_number(draw, n, total=19):
    box = (28, 30, 76, 78)
    draw.rounded_rectangle(box, radius=7, fill=GOLD)
    f = load_font(26, True)
    w, h = text_size(draw, str(n), f)
    draw.text(
        (box[0]+(box[2]-box[0]-w)//2, box[1]+(box[3]-box[1]-h)//2-2),
        str(n), font=f, fill=(10, 10, 12))

def draw_calculator_body(draw, cx, cy, scale=1.0, color=GOLD):
    w = int(250*scale); h = int(320*scale)
    x1 = cx - w//2;  y1 = cy - h//2
    x2 = cx + w//2;  y2 = cy + h//2
    draw.rounded_rectangle((x1, y1, x2, y2),
        radius=int(22*scale), outline=color, width=max(3, int(7*scale)))
    draw.rounded_rectangle(
        (x1+int(28*scale), y1+int(28*scale), x2-int(28*scale), y1+int(105*scale)),
        radius=int(10*scale), outline=color, width=max(2, int(4*scale)))
    kw = int(34*scale); kh = int(28*scale)
    gx = int(20*scale); gy = int(18*scale)
    sx = x1+int(34*scale); sy = y1+int(135*scale)
    for r in range(4):
        for c in range(4):
            kx = sx + c*(kw+gx); ky = sy + r*(kh+gy)
            draw.rounded_rectangle((kx, ky, kx+kw, ky+kh),
                radius=int(6*scale), outline=color, width=max(2, int(3*scale)))

def draw_ui(draw, progress=0.2, duration="1:38"):
    y = UI_LINE_Y
    draw.line((34, y, WIDTH-48, y), fill=(160, 166, 180), width=2)
    draw.line((34, y, 34+int((WIDTH-82)*progress), y), fill=RED, width=5)
    kx = 34+int((WIDTH-82)*progress)
    draw.ellipse((kx-8, y-8, kx+8, y+8), fill=RED)
    f = load_font(22, True)
    draw.polygon([(42,858),(42,828),(69,843)], fill=WHITE)
    draw.polygon([(112,858),(112,828),(135,843)], fill=WHITE)
    draw.rectangle((137,828,144,858), fill=WHITE)
    draw.arc((196,831,232,867), -35, 35, fill=WHITE, width=4)
    draw.polygon([(165,840),(182,828),(182,858)], fill=WHITE)
    draw.text((260, 832), duration, font=f, fill=WHITE)
    for i, x in enumerate([1370, 1450, 1530]):
        if i == 0:
            draw.ellipse((x-12,830,x+12,854), outline=WHITE, width=4)
            draw.line((x-18,842,x+18,842), fill=WHITE, width=4)
            draw.line((x,824,x,860), fill=WHITE, width=4)
        elif i == 1:
            draw.rectangle((x-22,826,x+22,858), outline=WHITE, width=4)
        else:
            draw.line((x-24,826,x-5,826), fill=WHITE, width=4)
            draw.line((x+5,826,x+24,826), fill=WHITE, width=4)
            draw.line((x-24,826,x-24,845), fill=WHITE, width=4)
            draw.line((x+24,826,x+24,845), fill=WHITE, width=4)
            draw.line((x-24,858,x-5,858), fill=WHITE, width=4)
            draw.line((x+5,858,x+24,858), fill=WHITE, width=4)
            draw.line((x-24,858,x-24,839), fill=WHITE, width=4)
            draw.line((x+24,858,x+24,839), fill=WHITE, width=4)

def draw_check(draw, x, y, color=GREEN):
    draw.ellipse((x, y+5, x+28, y+33), outline=color, width=4)
    draw.line((x+7, y+20, x+13, y+28, x+23, y+10), fill=color, width=4)

def draw_cross(draw, x, y, color=RED):
    draw.ellipse((x, y+5, x+28, y+33), outline=color, width=4)
    draw.line((x+8, y+13, x+21, y+26), fill=color, width=4)
    draw.line((x+21, y+13, x+8, y+26), fill=color, width=4)

def bullet(draw, x, y, text, color=GREEN, size=30, check=True):
    if check:
        draw_check(draw, x, y, color)
    else:
        draw_cross(draw, x, y, color)
    draw_text(draw, (x+48, y), text, size, WHITE, True,
              max_width=760, min_size=22)

def simple_glow_icon(img, center, kind, color):
    cx, cy = center
    def f(d, rgba):
        if kind == "calculator":
            d.rounded_rectangle((cx-95,cy-120,cx+95,cy+120), radius=14, outline=rgba, width=6)
            d.rounded_rectangle((cx-72,cy-96,cx+72,cy-35), radius=8, outline=rgba, width=4)
            for r in range(4):
                for c in range(4):
                    x = cx-65+c*43; y = cy-5+r*35
                    d.rounded_rectangle((x,y,x+26,y+22), radius=5, outline=rgba, width=3)
        elif kind == "monitor":
            d.rounded_rectangle((cx-90,cy-70,cx+90,cy+50), radius=10, outline=rgba, width=6)
            d.line((cx-35,cy+72,cx+35,cy+72), fill=rgba, width=5)
            d.line((cx,cy+50,cx,cy+72), fill=rgba, width=5)
        elif kind == "structure":
            pts = [(cx,cy-95),(cx-100,cy-20),(cx-60,cy+95),(cx+60,cy+95),(cx+100,cy-20)]
            d.line(pts+[pts[0]], fill=rgba, width=5)
            for px,py in pts:
                d.ellipse((px-10,py-10,px+10,py+10), fill=rgba)
            d.line((cx,cy-95,cx+60,cy+95), fill=rgba, width=4)
            d.line((cx-100,cy-20,cx+100,cy-20), fill=rgba, width=4)
        elif kind == "stack":
            for i in range(6):
                y = cy+86-i*34
                d.line((cx-120,y,cx+120,y), fill=rgba, width=3)
                d.line((cx-120,y,cx-70,y-28), fill=rgba, width=3)
                d.line((cx+120,y,cx+70,y-28), fill=rgba, width=3)
        elif kind == "shield":
            pts = [(cx,cy-105),(cx+100,cy-45),(cx+70,cy+72),(cx,cy+120),(cx-70,cy+72),(cx-100,cy-45)]
            d.line(pts+[pts[0]], fill=rgba, width=8, joint="curve")
            d.line((cx-42,cy+6,cx-10,cy+42,cx+52,cy-42), fill=rgba, width=10)
        elif kind == "code":
            d.rounded_rectangle((cx-105,cy-70,cx+105,cy+70), radius=18, outline=rgba, width=6)
            d.line((cx-58,cy-18,cx-100,cy+8,cx-58,cy+36), fill=rgba, width=6)
            d.line((cx+58,cy-18,cx+100,cy+8,cx+58,cy+36), fill=rgba, width=6)
            d.line((cx-14,cy+44,cx+28,cy-44), fill=rgba, width=6)
        elif kind == "infinity":
            d.arc((cx-120, cy-54, cx, cy+54), -40, 320, fill=rgba, width=6)
            d.arc((cx, cy-54, cx+120, cy+54), 140, 500, fill=rgba, width=6)
    return glow_shape(img, f, color, 16, 2)

def formula_box(draw, box, lines, outline=GOLD, font_size=30):
    panel(draw, box, fill=(5,10,22), outline=outline, width=3, radius=12)
    x1,y1,x2,y2 = box
    px, py = 30, 20
    usable_w = x2-x1-px*2
    usable_h = y2-y1-py*2
    if not lines:
        return
    size = min(font_size, max(18, int(usable_h/(len(lines)*1.28))))
    fonts = [fit_font(draw, ln, size, usable_w, 20, True) for ln in lines]
    lhs   = [max(24, int(text_size(draw,"0123456789AZ",f)[1]*1.45)) for f in fonts]
    total = sum(lhs)
    y = y1 + max(py, (y2-y1-total)//2)
    for ln, f, lh in zip(lines, fonts, lhs):
        draw.text((x1+px, y), ln, font=f, fill=WHITE)
        y += lh

def slide1():
    img = cinematic_bg(101, GREEN, GOLD, 170)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 1)

    draw_text(draw, (118, 58),  "TRY THIS",       74, GOLD,  True)
    draw_text(draw, (122, 144), "IN CALCULATOR",  42, WHITE, True)

    formula_box(draw, (115, 245, 740, 390),
        ["1.0000000000000001", "- 1.0000000000000000"],
        outline=GOLD, font_size=34)

    draw_calculator_body(draw, 420, 515, 0.72, GOLD)
    draw_text(draw, (765, 298), "?",              158, RED,   True)
    draw_text(draw, (600, 505), "What should",    40,  WHITE, True)
    draw_text(draw, (600, 555), "the answer be?", 40,  WHITE, True)

    panel(draw, (930, 250, 1465, 570), fill=(5,10,22), outline=GREEN, width=3, radius=18)
    draw_text(draw, (975, 292), "Tiny residual.",        44, GREEN, True)
    draw_text(draw, (975, 360), "Easy to lose.",         44, WHITE, True)
    draw_text(draw, (975, 455), "Structure will decide.",36, MUTED, True)

    draw_ui(draw, 0.05)
    return img

def slide2():
    img = cinematic_bg(102, RED, ORANGE, 130)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 2)

    draw_text(draw, (145, 58),  "FLOATING-POINT",  62, ORANGE, True)
    draw_text(draw, (150, 132), "CALCULATORS SHOW", 40, WHITE,  True)

    draw_calculator_body(draw, 1095, 345, 1.05, RED)
    formula_box(draw, (145, 225, 745, 475),
        ["0", "or", "1e-16"],
        outline=RED, font_size=66)

    draw_text(draw, (150, 535), "Same expression.",    42, WHITE, True)
    draw_text(draw, (150, 595), "Different surfaces.", 42, MUTED, True)

    panel(draw, (820, 595, 1480, 710), fill=(7,12,24), outline=ORANGE, width=3, radius=16)
    center_in_box(draw,
        "The residual can silently disappear in floating-point.",
        (820, 595, 1480, 710), 635, 30, WHITE, True, 22)

    draw_ui(draw, 0.10)
    return img

def slide3():
    img = cinematic_bg(103, GREEN, GOLD, 150)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 3)

    draw_text(draw, (150, 60),  "SVARE OUTPUT",         68, GREEN, True)
    draw_text(draw, (150, 142), "exact engine result",  44, WHITE, True)

    formula_box(draw, (155, 245, 870, 475),
        [
            "value   : 0.0000000000000001",
            "state   : RESOLVED",
            "depth   : 16",
            "direction: +",
        ],
        outline=GREEN, font_size=32)

    img = simple_glow_icon(img, (1240, 360), "structure", GREEN)
    draw = ImageDraw.Draw(img)

    draw_text(draw, (160, 545), "Same structure.",  44, WHITE, True)
    draw_text(draw, (160, 604), "Same value.",      44, GREEN, True)

    draw_ui(draw, 0.15)
    return img

def slide4():
    img = cinematic_bg(104, WHITE, GOLD, 125)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 4)

    draw_text(draw, (150, 70), "WHAT HAPPENED?", 66, GOLD, True)

    draw_text(draw, (160, 200), "Floating-point",       42, WHITE, True)
    draw_text(draw, (160, 258), "collapsed the surface.", 42, WHITE, True)
    draw_text(draw, (160, 316), "The digit was lost.",   42, MUTED, True)

    for i in range(80):
        x = 820 + int(360*math.cos(i*0.24)*(i/80))
        y = 355 + int(250*math.sin(i*0.35)*(i/80))
        draw.ellipse((x-2,y-2,x+2,y+2), fill=(WHITE[0],WHITE[1],WHITE[2]))

    panel(draw, (930, 245, 1420, 520), fill=(5,10,22), outline=ORANGE, width=3, radius=18)
    draw_text(draw, (970, 285), "The float surface",   38, WHITE, True, max_width=420)
    draw_text(draw, (970, 355), "collapsed.",           38, WHITE, True, max_width=420)
    draw_text(draw, (970, 415), "SVARE's structure",   38, GOLD,  True, max_width=420)
    draw_text(draw, (970, 465), "did not.",             38, GOLD,  True, max_width=420)

    draw_ui(draw, 0.20)
    return img

def slide5():
    img = cinematic_bg(105, GREEN, TEAL, 150)
    img = simple_glow_icon(img, (1220, 360), "stack", GREEN)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 5)

    draw_text(draw, (150, 62),  "SVARE REVEALS",    66, GREEN, True)
    draw_text(draw, (150, 142), "not just value",   42, WHITE, True)
    draw_text(draw, (150, 194), "but structure",    42, WHITE, True)

    bullet(draw, 170, 300, "Depth  — how many layers are visible",      GREEN, 34)
    bullet(draw, 170, 374, "Direction  — sign as a structural field",   GREEN, 34)
    bullet(draw, 170, 448, "Certificate  — SHA-256 of the resolution",  GREEN, 34)

    panel(draw, (155, 560, 780, 665), fill=(5,10,22), outline=GREEN, width=3, radius=14)
    draw_text(draw, (185, 588), "Value is the surface.", 32, WHITE, True)
    draw_text(draw, (185, 628), "Structure is the proof.", 32, GREEN, True)

    draw_ui(draw, 0.25)
    return img

def slide6():
    img = cinematic_bg(106, GOLD, GREEN, 130)
    img = simple_glow_icon(img, (1210, 375), "calculator", GOLD)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 6)

    draw_text(draw, (150, 60),  "EXAMPLE 2",  56, GOLD, True)
    draw_text(draw, (150, 135), "2 / 3",      72, GOLD, True)

    draw_text(draw, (160, 275), "A float calculator may show:", 34, WHITE, True)
    formula_box(draw, (160, 335, 780, 430),
        ["0.666666666666666666"],
        outline=GOLD, font_size=32)

    draw_text(draw, (160, 490), "Silently bounded.",       38, WHITE, True)
    draw_text(draw, (160, 545), "No residual signal.",     38, MUTED, True)
    draw_text(draw, (160, 600), "No declared depth.",      38, MUTED, True)

    draw_ui(draw, 0.30)
    return img

def slide7():
    img = cinematic_bg(107, GREEN, TEAL, 155)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 7)

    draw_text(draw, (145, 58),  "SVARE OUTPUT",          60, GREEN, True)
    draw_text(draw, (145, 132), "2 / 3   depth 8",       44, GOLD,  True)

    formula_box(draw, (155, 225, 820, 505),
        [
            "value   : 0.66666666",
            "state   : RESOLVED",
            "depth   : 8",
            "residual: continues",
        ],
        outline=GREEN, font_size=40)

    img = simple_glow_icon(img, (1210, 360), "stack", GREEN)
    draw = ImageDraw.Draw(img)

    draw_text(draw, (160, 560), "Depth is declared.",        40, WHITE, True)
    draw_text(draw, (160, 615), "Residual is explicit.",     40, GREEN, True)

    draw_ui(draw, 0.35)
    return img

def slide8():
    img = cinematic_bg(108, GREEN, GOLD, 140)
    img = simple_glow_icon(img, (1140, 385), "stack", GREEN)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 8)

    draw_text(draw, (150, 58),  "STRUCTURAL DEPTH",      58, ORANGE, True)
    draw_text(draw, (150, 132), "declared, not guessed.", 40, WHITE,  True)

    y = 270
    for label in ["6th digit", "5th digit", "4th digit",
                  "3rd digit", "2nd digit", "1st digit"]:
        bullet(draw, 170, y, label, GREEN, 32)
        y += 58

    panel(draw, (740, 610, 1460, 700), fill=(5,10,22), outline=GREEN, width=2, radius=12)
    draw_text(draw, (770, 635),
        "Each layer reveals one digit. Residual is always declared.",
        28, WHITE, True, max_width=660)

    draw_ui(draw, 0.40)
    return img

def slide9():
    img = cinematic_bg(109, ORANGE, GOLD, 125)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 9)

    center_text(draw, "CORE PRINCIPLE", 70, 64, ORANGE, True)

    formula_box(draw, (240, 200, 1360, 430),
        [
            "value_visible  iff  structure_uniquely_resolves",
             "",
            "structure_uniquely_resolves =",
            "  complete  AND  consistent",
        ],
        outline=ORANGE, font_size=38)

    panel(draw, (240, 460, 1360, 560), fill=(5,10,22), outline=GREEN, width=3, radius=14)
    center_in_box(draw,
        "This is the Structural Admissibility principle.",
        (240, 460, 1360, 560), 495, 34, WHITE, True)

    panel(draw, (240, 578, 1360, 650), fill=(4,8,18), outline=LINE, width=2, radius=12)
    center_in_box(draw,
        "SVARE Phase I implements this for single binary operations.",
        (240, 578, 1360, 650), 606, 27, MUTED, False)

    draw_ui(draw, 0.45)
    return img

def slide10():
    img = cinematic_bg(110, RED, GOLD, 120)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 10)

    center_text(draw, "RESOLUTION STATES", 68, 60, GREEN, True)

    panel(draw, (80, 175, 530, 420), fill=(8,14,26), outline=RED, width=4, radius=18)
    draw_text(draw, (118, 210), "FORBIDDEN",         42, RED,    True)
    draw_text(draw, (118, 278), "e.g.  9 / 0",      28, MUTED,  True)
    draw_text(draw, (118, 325), "Unsafe structure.", 30, WHITE,  True)
    draw_text(draw, (118, 368), "Value: undefined.", 30, WHITE,  True)

    panel(draw, (555, 175, 1045, 420), fill=(8,14,26), outline=YELLOW, width=4, radius=18)
    draw_text(draw, (593, 210), "INDETERMINATE",     36, YELLOW, True)
    draw_text(draw, (593, 270), "e.g.  0 / 0",      28, MUTED,  True)
    draw_text(draw, (593, 318), "No unique value.",  30, WHITE,  True)
    draw_text(draw, (593, 360), "Remains absent.",   30, WHITE,  True)

    panel(draw, (1070, 175, 1520, 420), fill=(8,14,26), outline=GREEN, width=4, radius=18)
    draw_text(draw, (1108, 210), "RESOLVED",          42, GREEN,  True)
    draw_text(draw, (1108, 278), "e.g.  5 + 2 = 7",  28, MUTED,  True)
    draw_text(draw, (1108, 325), "Complete + consistent.", 28, WHITE, True)
    draw_text(draw, (1108, 368), "Value visible.",    30, GREEN,  True)

    panel(draw, (200, 490, 1400, 580), fill=(5,10,22), outline=GREEN, width=3, radius=14)
    center_in_box(draw,
        "Absence is structural truth.  Silence is valid output.",
        (200, 490, 1400, 580), 527, 34, GREEN, True)

    panel(draw, (200, 598, 1400, 660), fill=(4,8,18), outline=LINE, width=2, radius=12)
    center_in_box(draw,
        "States shown are Phase I engine states (v8.1).",
        (200, 598, 1400, 660), 622, 26, MUTED, False)

    draw_ui(draw, 0.50)
    return img

def slide11():
    img = cinematic_bg(111, GREEN, GOLD, 140)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 11)

    draw_text(draw, (130, 60), "THE SHIFT", 64, GOLD, True)

    panel(draw, (120, 210, 640, 570), fill=(5,10,22), outline=ORANGE, width=3, radius=18)
    draw_text(draw, (165, 245), "Float calculator asks:", 32, WHITE,  True)
    draw_text(draw, (165, 310), '"Can this be',          38, WHITE,  True)
    draw_text(draw, (165, 360), 'computed?"',            38, WHITE,  True)
    draw_text(draw, (165, 430), "→ gives a number",      30, MUTED,  True)
    draw_text(draw, (165, 474), "→ no residual signal",  30, MUTED,  True)

    panel(draw, (960, 210, 1480, 570), fill=(5,10,22), outline=GREEN, width=3, radius=18)
    draw_text(draw, (1005, 245), "SVARE asks:",             32, GREEN,  True)
    draw_text(draw, (1005, 310), '"Should this value',      38, WHITE,  True)
    draw_text(draw, (1005, 360), 'be visible?"',            38, WHITE,  True)
    draw_text(draw, (1005, 430), "→ depth declared",        30, GREEN,  True)
    draw_text(draw, (1005, 474), "→ residual explicit",     30, GREEN,  True)

    draw.line((700, 390, 900, 390), fill=WHITE, width=6)
    draw.polygon([(900,390),(860,368),(860,412)], fill=WHITE)

    panel(draw, (200, 610, 1400, 690), fill=(5,10,22), outline=GOLD, width=2, radius=14)
    center_in_box(draw,
        "From floating-point computation  →  structural admissibility",
        (200, 610, 1400, 690), 643, 30, GOLD, True)

    draw_ui(draw, 0.55)
    return img

def slide12():
    img = cinematic_bg(112, GREEN, GOLD, 155)
    img = simple_glow_icon(img, (820, 305), "structure", GREEN)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 12)

    center_text(draw, "BEYOND NUMBERS",                         62, 62, GREEN, True)
    center_text(draw, "a structural foundation for value governance", 138, 32, WHITE, True)

    panel(draw, (180, 430, 1420, 530), fill=(5,10,22), outline=GOLD, width=3, radius=14)
    center_in_box(draw,
        "Float execution shows a surface.  Structure preserves the proof.",
        (180, 430, 1420, 530), 468, 34, WHITE, True)

    panel(draw, (180, 555, 1420, 640), fill=(5,10,22), outline=GREEN, width=3, radius=14)
    center_in_box(draw,
        "Phase I is a minimal reference kernel.  The principle scales.",
        (180, 555, 1420, 640), 589, 30, GREEN, True)

    panel(draw, (180, 658, 1420, 720), fill=(4,8,18), outline=LINE, width=2, radius=12)
    center_in_box(draw,
        "Research artifact — not yet production-ready.",
        (180, 658, 1420, 720), 683, 26, MUTED, False)

    draw_ui(draw, 0.60)
    return img

def slide13():
    img = cinematic_bg(113, GOLD, GREEN, 120)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 13)

    draw_text(draw, (140, 60),  "STRUCTURAL FOUNDATION",  52, ORANGE, True)
    draw_text(draw, (140, 132), "for real-world problems", 36, MUTED,  True)

    items = [
        ("Finance",      "float rounding silently changes values"),
        ("Science",      "reproducibility gaps from hidden precision"),
        ("Engineering",  "boundary failures from silent approximation"),
        ("AI systems",   "outputs with no structural grounding"),
    ]

    y = 220
    for domain, issue in items:
        bullet(draw, 170, y, f"{domain}  —  {issue}", GOLD, 30)
        y += 86

    panel(draw, (170, 590, 1380, 670), fill=(5,10,22), outline=GREEN, width=3, radius=14)
    draw_text(draw, (205, 618),
        "SVARE addresses the structural root.  Phase I — research stage.",
        30, WHITE, True, max_width=1140)

    draw_ui(draw, 0.65)
    return img

def slide14():
    img = cinematic_bg(115, GOLD, GREEN, 120)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 14)

    center_text(draw, "CORRECTNESS PRESERVATION", 56, 60, GOLD, True)

    draw_text(draw, (320, 175), "Classical truth is never modified.", 38, WHITE, True)
    draw_text(draw, (320, 230), "The structural layer is additive.",  36, MUTED, True)

    formula_box(draw, (330, 320, 1270, 450),
        ["phi((m, a, s)) = m"],
        outline=GOLD, font_size=52)

    center_text(draw, "Structure adds visibility.  Value remains exact.", 490, 36, GREEN, True)
    center_text(draw, "No approximation is introduced.", 550, 30, MUTED, True)

    panel(draw, (330, 598, 1270, 668), fill=(4,8,18), outline=LINE, width=2, radius=12)
    center_in_box(draw,
        "Phase I reference kernel  —  single binary operations  —  research artifact",
        (330, 598, 1270, 668), 626, 25, MUTED, False)

    draw_ui(draw, 0.75)
    return img

def slide15():
    img = cinematic_bg(116, GREEN, GOLD, 125)
    img = simple_glow_icon(img, (1220, 405), "shield", GREEN)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 15)

    draw_text(draw, (130, 58), "DEPENDENCY ELIMINATION", 50, GREEN, True)

    items = [
        "No floating-point approximation dependency",
        "No evaluation-order dependency",
        "No silent rounding",
        "No hidden precision loss",
        "No forced value from incomplete structure",
    ]

    y = 170
    for item in items:
        bullet(draw, 160, y, item, GREEN, 30)
        y += 70

    panel(draw, (160, 590, 980, 680), fill=(5,10,22), outline=GREEN, width=3, radius=14)
    draw_text(draw, (190, 618),
        "Correctness without floating-point dependency.",
        30, WHITE, True, max_width=780)

    draw_ui(draw, 0.80)
    return img

def slide16():
    img = cinematic_bg(117, GOLD, GREEN, 125)
    img = simple_glow_icon(img, (1210, 405), "shield", GOLD)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 16)

    draw_text(draw, (130, 58), "DETERMINISTIC REPRODUCIBILITY", 44, ORANGE, True)

    items = [
        "Same structure",
        "Same visible value",
        "Same resolution state",
        "Same certificate (SHA-256)",
        "Same depth and direction",
    ]

    y = 170
    for item in items:
        bullet(draw, 160, y, item, GOLD, 32)
        y += 72

    panel(draw, (160, 620, 1060, 706), fill=(5,10,22), outline=GOLD, width=3, radius=14)
    draw_text(draw, (190, 648),
        "Verified: run the engine twice — identical output.",
        30, WHITE, True, max_width=840)

    draw_ui(draw, 0.85)
    return img

def slide17():
    img = cinematic_bg(118, (255,145,35), GREEN, 140)
    img = simple_glow_icon(img, (1135, 370), "code", ORANGE)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 17)

    draw_text(draw, (130, 64),  "TINY ENGINE.",         58, GREEN, True)
    draw_text(draw, (130, 134), "REAL POWER.",          58, GOLD,  True)

    draw_text(draw, (145, 275), "This video was not edited.",       38, WHITE, True)
    draw_text(draw, (145, 330), "It was generated by a script —",   38, WHITE, True)
    draw_text(draw, (145, 385), "deterministically, from structure.", 38, GREEN, True)

    draw_text(draw, (145, 490), "Run the script again:",            34, MUTED, True)
    draw_text(draw, (145, 540), "identical frames,",                36, WHITE, True)
    draw_text(draw, (145, 590), "identical certificate.",           36, GOLD,  True)

    panel(draw, (130, 650, 900, 720), fill=(5,10,22), outline=GREEN, width=2, radius=12)
    draw_text(draw, (160, 675),
        "This is STRUMER — video from structure.",
        28, GREEN, True, max_width=720)

    draw_ui(draw, 0.90)
    return img

def slide18():
    img = cinematic_bg(119, GOLD, GREEN, 150, True)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 18)

    draw_text(draw, (140, 60),  "THE DESIGN DIRECTION", 54, ORANGE, True)

    items = [
        "Structure-first",
        "Float-free arithmetic",
        "Transparent depth",
        "Deterministic certificates",
        "Explicit residual signals",
    ]

    y = 165
    for item in items:
        draw_check(draw, 175, y-2, GREEN)
        draw_text(draw, (225, y), item, 34, WHITE, True)
        y += 66

    panel(draw, (170, 600, 1200, 680), fill=(5,10,22), outline=GREEN, width=3, radius=14)
    draw_text(draw, (205, 628),
        "A structural approach — where value follows from admissibility.",
        30, GREEN, True, max_width=970)

    draw_ui(draw, 0.95)
    return img

def slide19():
    img = cinematic_bg(120, GREEN, GOLD, 160)
    img = simple_glow_icon(img, (1220, 360), "infinity", GREEN)
    draw = ImageDraw.Draw(img)
    draw_number(draw, 19)

    draw_text(draw, (120, 86), "JOIN THE", 62, WHITE, True)
    draw_text(draw, (120, 190), "STRUCTURAL REVOLUTION", 60, GOLD, True, max_width=820, min_size=48)

    panel(draw, (120, 390, 900, 500), fill=(5, 10, 22), outline=GREEN, width=3, radius=14)
    center_in_box(draw,
        "Value becomes visible when structure resolves.",
        (120, 390, 900, 500), 428, 30, WHITE, True, 22)

    panel(draw, (120, 530, 900, 625), fill=(4, 8, 18), outline=LINE, width=2, radius=12)
    center_in_box(draw,
        "Research artifact — Phase I — not for safety-critical deployment.",
        (120, 530, 900, 625), 562, 24, MUTED, False, 18)

    draw_text(draw, (120, 675), "github.com/OMPSHUNYAYA", 30, MUTED, False)

    draw_text(draw, (1148, 500), "THIS IS", 34, WHITE, True)
    draw_text(draw, (1148, 548), "SVARE", 52, GREEN, True)

    draw_ui(draw, 1.00)
    return img

SLIDE_BUILDERS = [
    slide1, slide2, slide3, slide4, slide5,
    slide6, slide7, slide8, slide9, slide10,
    slide11, slide12, slide13, slide14, slide15,
    slide16, slide17, slide18, slide19,
]

SLIDE_NAMES = [
    "Try This In Calculator",
    "Floating-Point Calculators Show",
    "SVARE Exact Engine Output",
    "What Happened",
    "SVARE Reveals Structure",
    "Example Two Thirds",
    "SVARE Declared Depth",
    "Structural Depth Declared",
    "Core Principle",
    "Resolution States",
    "The Shift",
    "Beyond Numbers Structural Foundation",
    "Structural Foundation For Real-World Problems",
    "Correctness Preservation",
    "Dependency Elimination",
    "Deterministic Reproducibility",
    "Tiny Engine Real Power",
    "The Design Direction",
    "Join The Structural Revolution",
]

def animate_slide(slide, index, t):
    img = slide.convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    pulse = (math.sin(t*math.pi*2.0)+1)/2

    sweep_slides  = [2, 4, 8, 15, 18]
    sweep_colors  = [GREEN, GREEN, ORANGE, GOLD, GREEN]
    if index in sweep_slides:
        col = sweep_colors[sweep_slides.index(index)]
        x = int(-260+(WIDTH+520)*((t*0.65)%1.0))
        for i in range(70):
            a = max(0, 24-i//3)
            draw.line((x+i*7,0,x-290+i*7,760),
                      fill=(col[0],col[1],col[2],a), width=2)

    particle_slides = [0, 1, 3, 5, 6, 10, 12, 16, 17]
    if index in particle_slides:
        rng = np.random.default_rng(1000+index)
        for _ in range(22):
            px = int(rng.integers(90, WIDTH-90))
            py = int(rng.integers(80, 720))
            r  = int(rng.integers(1, 4))
            a  = int(30+pulse*44)
            col = GREEN if index%2==0 else GOLD
            draw.ellipse((px-r,py-r,px+r,py+r),
                         fill=(col[0],col[1],col[2],a))

    if index == 9:
        alpha = int(40+60*pulse)
        draw.rounded_rectangle((80, 175, 530, 420),
            radius=18, outline=(255,72,60,alpha), width=4)
        draw.rounded_rectangle((555, 175, 1045, 420),
            radius=18, outline=(255,220,45,alpha), width=4)
        draw.rounded_rectangle((1070, 175, 1520, 420),
            radius=18, outline=(110,255,64,alpha), width=4)

    final = Image.alpha_composite(img, overlay).convert("RGB")
    zoom  = 1.0 + (0.014 if index in [0,2,17,18] else 0.010)*math.sin(t*math.pi)
    if abs(zoom-1.0) > 0.001:
        nw, nh = int(WIDTH*zoom), int(HEIGHT*zoom)
        resized = final.resize((nw,nh), Image.Resampling.BICUBIC)
        ox, oy  = (nw-WIDTH)//2, (nh-HEIGHT)//2
        final   = resized.crop((ox,oy,ox+WIDTH,oy+HEIGHT))
    return final

def transition(a, b, t):
    ease = t*t*(3-2*t)
    return Image.blend(a.convert("RGB"), b.convert("RGB"), ease)

def scale_for_output(img):
    if WIDTH == OUTPUT_WIDTH and HEIGHT == OUTPUT_HEIGHT:
        return img
    return img.resize((OUTPUT_WIDTH, OUTPUT_HEIGHT), Image.Resampling.LANCZOS)

def frame_to_bgr(img):
    out = scale_for_output(img.convert("RGB"))
    return cv2.cvtColor(np.array(out), cv2.COLOR_RGB2BGR)

def canonical_text(value):
    if isinstance(value, dict):
        return "{" + "|".join(str(k)+"="+canonical_text(value[k])
                               for k in sorted(value)) + "}"
    if isinstance(value, list):
        return "[" + "|".join(canonical_text(x) for x in value) + "]"
    if isinstance(value, float):
        return format(value, ".12g")
    return str(value)

def sha256_hex(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def structure_payload():
    return {
        "project": "SVARE",
        "title": "SVARE Deterministic Structural Cinema",
        "version": VERSION,
        "output_video": OUT_VIDEO,
        "width": WIDTH, "height": HEIGHT,
        "output_width": OUTPUT_WIDTH, "output_height": OUTPUT_HEIGHT,
        "fps": FPS,
        "slides": SLIDE_NAMES,
        "principle":   "value_correctness = resolve(structure)",
        "visibility":  "value_visible iff structure_uniquely_resolves",
        "condition":   "structure_uniquely_resolves = complete AND consistent",
        "states":      ["RESOLVED", "FORBIDDEN", "INDETERMINATE_ZERO"],
        "phase":       "Phase I — single binary operations — research artifact",
        "certificate_note":
            "certificate identity depends on structural encoding",
    }

def structure_signature():
    return sha256_hex(canonical_text(structure_payload()))

def structure_certificate():
    return structure_signature()[:16]

def write_verify():
    lines = [
        "SVARE Deterministic Structural Cinema",
        f"version: {VERSION}",
        f"video: {OUT_VIDEO}",
        f"poster: {OUT_POSTER}",
        "principle: value_correctness = resolve(structure)",
        "law: same structure -> same value",
        f"slides: {len(SLIDE_BUILDERS)}",
        f"fps: {FPS}",
        f"resolution: {OUTPUT_WIDTH}x{OUTPUT_HEIGHT}",
        f"structure_signature: {structure_signature()}",
        f"certificate: {structure_certificate()}",
        "engine_states (Phase I v8.1):",
        "  RESOLVED:           structure complete + consistent -> value visible",
        "  FORBIDDEN:          structurally unsafe -> value undefined",
        "  INDETERMINATE_ZERO: 0/0 -> value indeterminate",
        "phase: Phase I — single binary operations",
        "scope: research artifact — not production-ready",
        "release_note: external reference video artifact",
    ]
    with open(OUT_VERIFY, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def write_video_stream():
    print(f"  Building {len(SLIDE_BUILDERS)} slides...")
    slides = [builder() for builder in SLIDE_BUILDERS]

    scale_for_output(slides[0]).save(OUT_POSTER)
    print(f"  Poster saved: {OUT_POSTER}")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(OUT_VIDEO, fourcc, FPS, (OUTPUT_WIDTH, OUTPUT_HEIGHT))
    if not writer.isOpened():
        raise RuntimeError("Video writer could not be opened.")

    bgr_slides = [frame_to_bgr(s) for s in slides]

    for index, slide in enumerate(slides):
        frame_count = int(round(SLIDE_DURATIONS[index] * FPS))

        if FAST_RENDER_MODE and STATIC_FRAME_ANIMATION:
            for _ in range(frame_count):
                writer.write(bgr_slides[index])
        elif FAST_RENDER_MODE and ENABLE_LIGHT_MOTION:
            cached = []
            sc = max(2, ANIMATION_SAMPLES)
            for k in range(sc):
                frame = animate_slide(slide, index, k/max(1,sc-1))
                cached.append(frame_to_bgr(frame))
            for i in range(frame_count):
                slot = int((i/max(1,frame_count-1))*(sc-1))
                writer.write(cached[slot])
        else:
            for i in range(frame_count):
                frame = animate_slide(slide, index, i/max(1,frame_count-1))
                writer.write(frame_to_bgr(frame))

        if index < len(slides)-1:
            ns = slides[index+1]
            for j in range(TRANSITION_FRAMES):
                frame = transition(slide, ns, j/max(1,TRANSITION_FRAMES-1))
                writer.write(frame_to_bgr(frame))

        print(f"  Slide {index+1}/{len(slides)} rendered ({frame_count} frames)")

    writer.release()

def main():
    print("=" * 64)
    print(f"SVARE Deterministic Structural Cinema  v{VERSION}")
    print("=" * 64)
    print("Principle:    value_correctness = resolve(structure)")
    print("Law:          same structure -> same value")
    print("Engine:       SVARE v8.1 — float-free, deterministic")
    print("Phase:        Phase I — single binary operations")
    print("Scope:        research artifact")
    print(f"Slides:       {len(SLIDE_BUILDERS)}")
    print()

    write_video_stream()
    write_verify()

    print()
    print(f"  Created: {OUT_VIDEO}")
    print(f"  Created: {OUT_POSTER}")
    print(f"  Created: {OUT_VERIFY}")
    print()
    print(f"  structure_signature : {structure_signature()}")
    print(f"  certificate         : {structure_certificate()}")
    print()
    print("  RESOLVED:           structure complete + consistent -> value visible")
    print("  FORBIDDEN:          structurally unsafe             -> value undefined")
    print("  INDETERMINATE_ZERO: 0/0                             -> indeterminate")
    print()
    print("  same structure -> same value -> same structural proof")
    print("=" * 64)

if __name__ == "__main__":
    main()
