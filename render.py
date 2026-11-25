#!/usr/bin/env python3
"""Render news-image-20261125 entry.png with PIL.

Dense cream-serif newspaper front page (ATM recipe): 46 stories,
13 pictured (3 leads + 10 cards), UTC timeline, day-in-numbers
strip, pinned world map, 33 one-line briefs, DATE CHECK box and a
verification footer. All illustrations are flat vector shapes
drawn from scratch with PIL primitives. All stories are real,
dated Wednesday 25 November 2026 (or first reported that day),
sourced from live news search (Reuters, AP, Al Jazeera, UN, ...).

Drawn at 2048x2048 (master), then downscaled to 1024x1024 for
the submitted entry.png (must stay under 1 MiB).
"""
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 2048
PAPER = (247, 243, 233)
INK = (26, 26, 26)
NAVY = (31, 58, 95)
BRICK = (179, 64, 42)
TEAL = (42, 127, 111)
OCHRE = (200, 147, 42)
MUTED = (107, 98, 87)
RULE = (201, 192, 171)
CARD_BG = (252, 249, 240)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIFB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

MX = 40
CW = W - 2 * MX


def wrap(text, font, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text(x, y, s, font, fill=INK, anchor="la"):
    d.text((x, y), s, font=font, fill=fill, anchor=anchor)


def hline(y, x0=MX, x1=W - MX, fill=RULE, width=2):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- kicker
fk = F(SANSB, 22)
text(MX, 28, "ONE DAY OF WORLD NEWS, ONE PICTURE", fk, NAVY)
text(W - MX, 28, "46 STORIES  ·  7 REGIONS  ·  EVERY ONE FROM THIS WEDNESDAY",
     fk, NAVY, anchor="ra")
hline(64)

# ---------------------------------------------------------------- masthead
fm = F(SERIFB, 92)
text(W // 2, 80, "Wednesday 25 November 2026", fm, INK, anchor="ma")
hline(176, width=4)
fsub = F(SANSB, 20)
text(W // 2, 188,
     "ASIA 9  ·  MIDDLE EAST 10  ·  EUROPE 14  ·  AMERICAS 7  ·  AFRICA 2  ·  OCEANIA 1  ·  GLOBAL 3",
     fsub, MUTED, anchor="ma")
hline(224)

# ---------------------------------------------------------------- timeline
ft_t = F(SANSB, 18)
ft_h = F(SANS, 18)
timeline = [
    ("OVERNIGHT", "Russian strike kills\ntwo in Odesa"),
    ("00:18 UTC", "Shenzhou-24 lifts off\nwith Pakistani aboard"),
    ("01:00 UTC", "Asian stocks tumble\non tariff threats"),
    ("ASIA DAY", "Nvidia suppliers cheer\nHuang's return"),
    ("EUROPE DAY", "Sarkozy case sent\nto trial in Paris"),
    ("EVENING", "Trump honours Giuliani,\npardons two turkeys"),
]
ty, th = 236, 100
text(MX, ty - 4, "THE DAY IN UTC", F(SANSB, 18), BRICK)
tw = (CW - 5 * 8) // 6
for i, (t, htxt) in enumerate(timeline):
    x = MX + i * (tw + 8)
    d.rectangle([x, ty + 24, x + tw, ty + 24 + th - 24], outline=RULE)
    text(x + 12, ty + 30, t, ft_t, NAVY)
    for j, ln in enumerate(htxt.split("\n")):
        text(x + 12, ty + 56 + j * 22, ln, ft_h, INK)
hline(ty + 24 + th + 8)

# ---------------------------------------------------------------- numbers
ny = 356
text(MX, ny, "THE DAY IN NUMBERS", F(SANSB, 18), BRICK)
nums = [
    ("1st", "Pakistani in orbit;\nfirst foreigner on Tiangong"),
    ("-5.3%", "Kospi's fall at\nits worst point"),
    ("$3.8bn", "US military aid to\nIsrael now in doubt"),
    ("25", "hostages held in a\nCartagena supermarket"),
    ("53%", "of Germans now oppose\nUkraine military aid"),
    ("60 km", "Houthis from Aden,\nthe temporary capital"),
]
nw = (CW - 5 * 8) // 6
for i, (n, cap) in enumerate(nums):
    x = MX + i * (nw + 8)
    text(x + 8, ny + 26, n, F(SERIFB, 42), NAVY)
    for j, ln in enumerate(cap.split("\n")):
        text(x + 8, ny + 76 + j * 20, ln, F(SANS, 16), MUTED)
hline(ny + 120)

# ---------------------------------------------------------------- pictures
def illu_box(x, y, w, h, tint):
    d.rectangle([x, y, x + w, y + h], fill=tint, outline=RULE)


def flame(cx, cy, s, col=BRICK):
    d.polygon([(cx, cy - 32 * s), (cx + 18 * s, cy + 4 * s), (cx + 8 * s, cy + 16 * s),
               (cx - 8 * s, cy + 16 * s), (cx - 18 * s, cy + 4 * s)], fill=col)
    d.polygon([(cx, cy - 12 * s), (cx + 8 * s, cy + 12 * s), (cx - 8 * s, cy + 12 * s)],
              fill=OCHRE)


def ship(cx, cy, s, hull, sail):
    d.polygon([(cx - 68 * s, cy), (cx + 68 * s, cy), (cx + 52 * s, cy + 24 * s),
               (cx - 52 * s, cy + 24 * s)], fill=hull)
    d.rectangle([cx + 28 * s, cy - 28 * s, cx + 56 * s, cy], fill=hull)
    d.rectangle([cx - 56 * s, cy - 16 * s, cx - 16 * s, cy], fill=sail)
    for k in range(3):
        d.arc([cx - 80 * s + k * 52 * s, cy + 32 * s, cx - 32 * s + k * 52 * s,
               cy + 52 * s], 0, 180, fill=NAVY, width=3)


def building(cx, cy, s, col=NAVY):
    d.rectangle([cx - 32 * s, cy - 44 * s, cx + 32 * s, cy + 28 * s], fill=col)
    for r in range(3):
        for c in range(3):
            d.rectangle([cx - 24 * s + c * 18 * s, cy - 36 * s + r * 20 * s,
                         cx - 12 * s + c * 18 * s, cy - 24 * s + r * 20 * s],
                        fill=OCHRE)
    d.polygon([(cx - 36 * s, cy - 44 * s), (cx, cy - 60 * s), (cx + 36 * s, cy - 44 * s)],
              fill=BRICK)


def scales(cx, cy, s, col=NAVY):
    d.line([cx, cy - 32 * s, cx, cy + 28 * s], fill=col, width=6)
    d.line([cx - 32 * s, cy - 24 * s, cx + 32 * s, cy - 24 * s], fill=col, width=4)
    d.line([cx - 32 * s, cy - 24 * s, cx - 32 * s, cy + 4 * s], fill=col, width=4)
    d.line([cx + 32 * s, cy - 24 * s, cx + 32 * s, cy + 4 * s], fill=col, width=4)
    d.polygon([(cx - 44 * s, cy + 4 * s), (cx - 20 * s, cy + 4 * s), (cx - 32 * s, cy + 20 * s)],
              fill=col)
    d.polygon([(cx + 20 * s, cy + 4 * s), (cx + 44 * s, cy + 4 * s), (cx + 32 * s, cy + 20 * s)],
              fill=col)
    d.rectangle([cx - 24 * s, cy + 28 * s, cx + 24 * s, cy + 34 * s], fill=col)


def chart(cx, cy, s, down=True, col=BRICK):
    pts = [(cx - 60 * s, cy + 8 * s), (cx - 30 * s, cy - 4 * s), (cx, cy + 4 * s),
           (cx + 30 * s, cy - 20 * s), (cx + 60 * s, cy - 32 * s)] if not down else \
          [(cx - 60 * s, cy - 28 * s), (cx - 30 * s, cy - 12 * s), (cx, cy - 20 * s),
           (cx + 30 * s, cy + 4 * s), (cx + 60 * s, cy + 24 * s)]
    d.line(pts, fill=col, width=6)
    d.polygon([(cx + 60 * s, cy + 24 * s), (cx + 44 * s, cy + 24 * s),
               (cx + 60 * s, cy + 8 * s)], fill=col)


def draw_illu(kind, x, y, w, h):
    cx, cy = x + w // 2, y + h // 2
    s = min(w, h) / 128.0
    if kind == "rocket":
        illu_box(x, y, w, h, (222, 228, 240))
        d.polygon([(cx - 22, cy - 44), (cx - 22, cy + 20), (cx + 22, cy + 20),
                   (cx + 22, cy - 44)], fill=PAPER, outline=NAVY, width=3)
        d.polygon([(cx - 22, cy - 44), (cx, cy - 66), (cx + 22, cy - 44)], fill=BRICK)
        d.ellipse([cx - 10, cy - 28, cx + 10, cy - 8], fill=TEAL, outline=NAVY, width=2)
        d.polygon([(cx - 22, cy + 8), (cx - 40, cy + 34), (cx - 22, cy + 20)], fill=BRICK)
        d.polygon([(cx + 22, cy + 8), (cx + 40, cy + 34), (cx + 22, cy + 20)], fill=BRICK)
        flame(cx, cy + 44, s * 1.1)
        for sx, sy in [(-52, -52), (54, -44), (-58, 20), (58, 30), (40, -58)]:
            d.ellipse([cx + sx - 3, cy + sy - 3, cx + sx + 3, cy + sy + 3], fill=NAVY)
    elif kind == "ship":
        illu_box(x, y, w, h, (214, 226, 238))
        ship(cx, cy - 8, s * 0.9, NAVY, BRICK)
        flame(cx + 52, cy - 44, s * 0.8)
        d.ellipse([cx + 36, cy - 60, cx + 44, cy - 52], fill=(160, 160, 158))
        d.ellipse([cx + 48, cy - 68, cx + 58, cy - 58], fill=(178, 178, 176))
    elif kind == "chart":
        illu_box(x, y, w, h, (240, 226, 222))
        for i, hh in enumerate((28, 40, 20, 48)):
            d.rectangle([cx - 56 + i * 30, cy + 24 - hh, cx - 36 + i * 30, cy + 24],
                        fill=TEAL if i % 2 == 0 else BRICK)
        chart(cx, cy - 12, s * 0.55)
    elif kind == "medal":
        illu_box(x, y, w, h, (238, 228, 210))
        d.polygon([(cx - 24, cy - 58), (cx - 8, cy - 58), (cx - 2, cy - 16),
                   (cx - 30, cy - 16)], fill=BRICK)
        d.polygon([(cx + 8, cy - 58), (cx + 24, cy - 58), (cx + 30, cy - 16),
                   (cx + 2, cy - 16)], fill=NAVY)
        d.ellipse([cx - 34, cy - 24, cx + 34, cy + 44], fill=OCHRE, outline=BRICK, width=3)
        d.polygon([(cx, cy - 12), (cx + 8, cy + 4), (cx + 24, cy + 4), (cx + 12, cy + 14),
                   (cx + 16, cy + 30), (cx, cy + 20), (cx - 16, cy + 30),
                   (cx - 12, cy + 14), (cx - 24, cy + 4), (cx - 8, cy + 4)],
                  fill=PAPER)
    elif kind == "plane":
        illu_box(x, y, w, h, (222, 230, 238))
        d.polygon([(cx - 64, cy - 4), (cx + 52, cy - 4), (cx + 68, cy + 4),
                   (cx + 52, cy + 12), (cx - 64, cy + 12)], fill=NAVY)
        d.polygon([(cx - 16, cy - 32), (cx + 4, cy - 32), (cx + 4, cy + 20),
                   (cx - 16, cy + 20)], fill=NAVY)
        d.polygon([(cx - 52, cy + 12), (cx - 32, cy + 12), (cx - 44, cy + 32),
                   (cx - 60, cy + 32)], fill=NAVY)
        for wx in (-40, -20, 0, 20):
            d.ellipse([cx + wx, cy - 2, cx + wx + 8, cy + 6], fill=OCHRE)
    elif kind == "scales":
        illu_box(x, y, w, h, (232, 228, 222))
        scales(cx, cy, s * 0.9)
    elif kind == "flag":
        illu_box(x, y, w, h, (222, 235, 225))
        d.polygon([(cx - 64, cy + 36), (cx - 28, cy - 24), (cx + 8, cy + 36)], fill=(120, 140, 110))
        d.polygon([(cx - 12, cy + 36), (cx + 24, cy - 24), (cx + 64, cy + 36)], fill=(100, 120, 95))
        d.line([cx + 52, cy - 58, cx + 52, cy + 36], fill=INK, width=4)
        d.polygon([(cx + 52, cy - 58), (cx + 96, cy - 44), (cx + 52, cy - 30)], fill=BRICK)
    elif kind == "radar":
        illu_box(x, y, w, h, (232, 230, 238))
        d.rectangle([cx - 10, cy - 10, cx + 10, cy + 44], fill=NAVY)
        d.polygon([(cx - 34, cy - 44), (cx + 34, cy - 44), (cx + 10, cy - 10),
                   (cx - 10, cy - 10)], fill=PAPER, outline=NAVY, width=3)
        for r in (52, 70):
            d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=TEAL, width=3)
        d.line([cx, cy - 44, cx, cy - 66], fill=NAVY, width=3)
        d.ellipse([cx - 5, cy - 71, cx + 5, cy - 61], fill=BRICK)
    elif kind == "runway":
        illu_box(x, y, w, h, (238, 226, 214))
        d.polygon([(cx - 70, cy + 44), (cx - 14, cy - 44), (cx + 14, cy - 44),
                   (cx + 70, cy + 44)], fill=(90, 90, 96))
        for k in range(4):
            yy = cy - 32 + k * 20
            ww = 4 + k * 3
            d.rectangle([cx - ww, yy, cx + ww, yy + 8], fill=PAPER)
        d.ellipse([cx + 40, cy - 58, cx + 56, cy - 42], fill=(160, 160, 158))
        d.ellipse([cx + 52, cy - 66, cx + 66, cy - 52], fill=(178, 178, 176))
    elif kind == "blast":
        illu_box(x, y, w, h, (228, 224, 220))
        building(cx - 12, cy + 8, s * 0.9)
        flame(cx + 44, cy - 12, s * 0.7)
        d.ellipse([cx + 36, cy - 60, cx + 60, cy - 36], fill=(160, 160, 158))
        d.ellipse([cx + 48, cy - 68, cx + 68, cy - 48], fill=(178, 178, 176))
    elif kind == "chip":
        illu_box(x, y, w, h, (222, 236, 222))
        d.rectangle([cx - 40, cy - 32, cx + 24, cy + 32], fill=NAVY)
        for k in range(4):
            d.line([cx - 52, cy - 24 + k * 16, cx - 40, cy - 24 + k * 16], fill=NAVY, width=4)
            d.line([cx + 24, cy - 24 + k * 16, cx + 36, cy - 24 + k * 16], fill=NAVY, width=4)
        d.rectangle([cx - 24, cy - 16, cx + 8, cy + 16], fill=TEAL)
        chart(cx + 48, cy - 4, s * 0.5, down=False, col=TEAL)
    elif kind == "santa":
        illu_box(x, y, w, h, (238, 228, 200))
        d.rectangle([cx - 70, cy + 24, cx + 70, cy + 44], fill=(214, 196, 150))
        d.polygon([(cx - 46, cy + 24), (cx - 46, cy - 30), (cx + 10, cy - 30),
                   (cx + 10, cy + 24)], fill=BRICK)
        d.polygon([(cx - 46, cy - 30), (cx - 18, cy - 52), (cx + 10, cy - 30)], fill=BRICK)
        d.ellipse([cx - 46, cy - 34, cx - 18, cy - 6], fill=PAPER)
        d.ellipse([cx + 30, cy - 44, cx + 62, cy - 12], fill=PAPER)
        d.ellipse([cx + 38, cy - 38, cx + 54, cy - 22], fill=NAVY)
    elif kind == "handshake":
        illu_box(x, y, w, h, (222, 228, 238))
        d.line([cx - 52, cy - 58, cx - 52, cy + 36], fill=INK, width=4)
        d.line([cx + 52, cy - 58, cx + 52, cy + 36], fill=INK, width=4)
        d.polygon([(cx - 52, cy - 58), (cx - 8, cy - 44), (cx - 52, cy - 30)], fill=TEAL)
        d.polygon([(cx + 52, cy - 58), (cx + 8, cy - 44), (cx + 52, cy - 30)], fill=BRICK)
        d.polygon([(cx, cy - 58), (cx + 6, cy - 44), (cx + 18, cy - 44), (cx + 8, cy - 34),
                   (cx + 12, cy - 20), (cx, cy - 28), (cx - 12, cy - 20),
                   (cx - 8, cy - 34), (cx - 18, cy - 44), (cx - 6, cy - 44)],
                  fill=OCHRE)
        d.rectangle([cx - 40, cy + 36, cx + 40, cy + 44], fill=NAVY)


# ---------------------------------------------------------------- stories
# (num, kind, region, topic, status, headline, deck)
LEADS = [
    (1, "rocket", "GLOBAL", "SPACE", "CONFIRMED – REUTERS",
     "Shenzhou-24 lifts off with first Pakistani in orbit",
     "Zeeshan Ali, 40, joins two Chinese crew on Tiangong; first foreign astronaut aboard the station."),
    (2, "ship", "EUROPE", "WAR", "CONFIRMED – REUTERS",
     "Zelenskiy confirms Ukraine hit Russian ship in Baltic",
     "Kyiv owns Saturday's drone strike on a cargo ship in the Gulf of Finland; Norway urges caution."),
    (3, "chart", "ASIA", "MARKETS", "CONFIRMED – REUTERS",
     "Asian stocks tumble as US tariff threats hit sentiment",
     "Kospi falls 5.3%, Taiwan 5.1%, Nikkei 2.9%; Nvidia gives back 5.9% after Monday's surge."),
]
CARDS = [
    (4, "medal", "AMERICAS", "POLITICS", "CONFIRMED – AP",
     "Trump awards Giuliani the Medal of Freedom",
     "Ex-New York mayor, 82, honoured at White House; led city through 9/11."),
    (5, "plane", "AMERICAS", "IMMIGRATION", "CONFIRMED – AP",
     "Abrego Garcia to self-deport to Spain, AP reports",
     "Salvadoran migrant to fly to Europe on a commercial flight to avoid deportation."),
    (6, "scales", "EUROPE", "JUSTICE", "CONFIRMED – REUTERS",
     "Sarkozy corruption case sent to trial in Paris",
     "Ex-president and wife Carla Bruni face trial; first hearing set for 1 April 2027."),
    (7, "flag", "MIDDLE EAST", "WAR", "CONFIRMED – REUTERS",
     "Houthis will not seize Aden, Yemeni army says",
     "Fighters pushed to 60 km of the temporary capital; 'not as dire as reported'."),
    (8, "radar", "AMERICAS", "TRAVEL", "CONFIRMED – FAA",
     "Radar outage delays flights at Chicago O'Hare",
     "FAA holds some arrivals as technicians repair ground radar at holiday peak."),
    (9, "runway", "MIDDLE EAST", "WAR", "REPORTED – AL JAZEERA",
     "Strikes reported on Houthi-run Hodeidah airport",
     "Fire and smoke seen over the Red Sea port city; no casualty toll yet given."),
    (10, "blast", "EUROPE", "WAR", "CONFIRMED – REUTERS",
     "Russian strike kills two in Ukraine's Odesa region",
     "Cars and homes hit; drones attack Kyiv late on Tuesday, injuring two."),
    (11, "chip", "ASIA", "TECH", "CONFIRMED – REUTERS",
     "Huawei convicted in US trial over Iran business",
     "Jury finds firm deceived banks and stole trade secrets; case began in 2018."),
    (12, "santa", "EUROPE", "LIGHT", "CONFIRMED – REUTERS",
     "Santas wash up on a Bulgarian beach in a container",
     "Life-size figures and a polar bear found near Burgas; vessel hit by drones."),
    (13, "handshake", "MIDDLE EAST", "POLITICS", "CONFIRMED – REUTERS",
     "Eisenkot clinches first coalition pact in Israel",
     "Ex-army chief's Yashar party signs deal with Lieberman's party after election."),
]

fnum = F(SERIFB, 30)
flab = F(SANSB, 16)
fstat = F(SANSB, 16)
fhl = F(SERIFB, 28)
fdk = F(SERIF, 18)

ly, lh = 488, 296
lw = (CW - 2 * 24) // 3
for i, (num, kind, region, topic, status, hl, dk) in enumerate(LEADS):
    x = MX + i * (lw + 24)
    d.rectangle([x, ly, x + lw, ly + lh], fill=CARD_BG, outline=RULE)
    draw_illu(kind, x + 2, ly + 2, lw - 4, 108)
    d.ellipse([x + 16, ly + 116, x + 60, ly + 160], fill=NAVY)
    text(x + 38, ly + 120, str(num), F(SERIFB, 26), PAPER, anchor="ma")
    text(x + 72, ly + 120, f"{region} · {topic}", flab, BRICK)
    text(x + 72, ly + 142, status, fstat, TEAL)
    lines = wrap(hl, fhl, lw - 32)
    yy = ly + 168
    for ln in lines[:2]:
        text(x + 16, yy, ln, fhl, INK)
        yy += 30
    dlines = wrap(dk, fdk, lw - 32)
    for ln in dlines[:3]:
        text(x + 16, yy, ln, fdk, INK)
        yy += 22

fhl2 = F(SERIFB, 22)
fdk2 = F(SERIF, 18)
cy0, chh = 796, 256
cw2 = (CW - 4 * 16) // 5
for r in range(2):
    for c in range(5):
        st = CARDS[r * 5 + c]
        num, kind, region, topic, status, hl, dk = st
        x = MX + c * (cw2 + 16)
        y = cy0 + r * (chh + 16)
        d.rectangle([x, y, x + cw2, y + chh], fill=CARD_BG, outline=RULE)
        draw_illu(kind, x + 2, y + 2, cw2 - 4, 92)
        d.ellipse([x + 12, y + 100, x + 44, y + 132], fill=NAVY)
        text(x + 28, y + 102, str(num), F(SERIFB, 20), PAPER, anchor="ma")
        text(x + 52, y + 102, f"{region} · {topic}", F(SANSB, 14), BRICK)
        text(x + 52, y + 120, status, F(SANSB, 14), TEAL)
        lines = wrap(hl, fhl2, cw2 - 24)
        yy = y + 142
        for ln in lines[:2]:
            text(x + 12, yy, ln, fhl2, INK)
            yy += 24
        dlines = wrap(dk, fdk2, cw2 - 24)
        for ln in dlines[:2]:
            text(x + 12, yy, ln, fdk2, INK)
            yy += 22

# ---------------------------------------------------------------- bottom
by = 1328
hline(by)
# --- map panel
mapx, mapw = MX, 784
text(mapx, by + 16, "WHERE IT HAPPENED", F(SANSB, 20), BRICK)
text(mapx, by + 44, "Pins 1–13 match the pictured stories above.", F(SANS, 16), MUTED)
map_top, map_bot = by + 76, by + 392
map_l, map_r = mapx, mapx + mapw - 16
d.rectangle([map_l, map_top, map_r, map_bot], fill=(233, 226, 205), outline=RULE)


def proj(lon, lat):
    px = map_l + (lon + 180) * (map_r - map_l) / 360.0
    py = map_top + (85 - lat) * (map_bot - map_top) / 145.0
    return px, py


CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80), (-75, 73),
     (-65, 60), (-55, 52), (-60, 46), (-70, 42), (-75, 35), (-80, 26), (-85, 30),
     (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-140, 60),
     (-155, 58), (-168, 66)],
    [(-80, 10), (-75, 11), (-70, 12), (-62, 10), (-52, 5), (-50, 0), (-35, -8),
     (-40, -20), (-48, -28), (-58, -35), (-65, -41), (-70, -54), (-73, -37),
     (-70, -20), (-80, -5), (-80, 10)],
    [(-17, 15), (-10, 31), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -18), (28, -33), (20, -35),
     (12, -18), (9, 4), (-8, 4), (-17, 15)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59), (18, 56),
     (21, 55), (24, 58), (30, 60), (30, 70), (40, 68), (55, 69), (70, 72), (90, 75),
     (110, 76), (130, 72), (150, 70), (170, 66), (178, 65), (170, 60), (162, 56),
     (158, 52), (142, 50), (140, 40), (135, 35), (130, 32), (122, 30), (120, 22),
     (110, 20), (105, 10), (100, 8), (98, 12), (92, 16), (88, 22), (80, 15),
     (77, 8), (72, 20), (66, 25), (60, 25), (57, 26), (52, 28), (48, 30), (44, 29),
     (40, 36), (36, 36), (30, 36), (26, 38), (23, 36), (19, 40), (15, 44), (12, 44),
     (8, 44), (3, 43), (-2, 37), (-6, 36), (-10, 36)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35),
     (140, -38), (147, -39), (150, -37), (153, -27), (146, -19), (142, -11),
     (135, -12), (132, -11), (126, -14), (122, -17), (114, -22)],
    [(-45, 60), (-30, 68), (-20, 70), (-25, 76), (-40, 80), (-58, 76), (-55, 70),
     (-45, 60)],
]
for poly in CONTINENTS:
    d.polygon([proj(lo, la) for lo, la in poly], fill=(232, 220, 194),
              outline=(185, 172, 141))
for lo, la, r in [(130, 32, 6), (137, 36, 6), (141, 40, 6), (95, 5, 6), (105, -2, 6),
                  (115, -8, 6), (125, -5, 6), (135, -4, 6), (167, -16, 4), (174, -41, 4),
                  (18, -34, 4), (-3, 54, 4)]:
    px, py = proj(lo, la)
    d.ellipse([px - r, py - r, px + r, py + r], fill=(232, 220, 194),
              outline=(185, 172, 141))

PINS = [(100, 40, 1), (24, 59, 2), (139, 35, 3), (-77, 39, 4), (-89, 13, 5),
        (2, 49, 6), (45, 13, 7), (-88, 42, 8), (43, 15, 9), (31, 46, 10),
        (-74, 41, 11), (27, 42, 12), (35, 32, 13)]
OFFSETS = {7: (32, 32), 9: (-36, -28), 10: (0, -32), 12: (0, 32), 13: (28, 20)}
fpin = F(SERIFB, 18)
for lon, lat, num in PINS:
    px, py = proj(lon, lat)
    ox, oy = OFFSETS.get(num, (0, 0))
    qx, qy = px + ox, py + oy
    if (ox, oy) != (0, 0):
        d.line([px, py, qx, qy], fill=BRICK, width=2)
    d.ellipse([qx - 16, qy - 16, qx + 16, qy + 16], fill=NAVY, outline=PAPER, width=2)
    text(qx, qy - 14, str(num), fpin, PAPER, anchor="ma")

text(mapx, map_bot + 12,
     "ASIA 9 · MIDDLE EAST 10 · EUROPE 14 · AMERICAS 7 · AFRICA 2 · OCEANIA 1 · GLOBAL 3",
     F(SANSB, 16), MUTED)

# --- briefs panel
bx = mapx + mapw + 24
bw = W - MX - bx
text(bx, by + 16, "ALSO ON WEDNESDAY — STORIES 14–46", F(SANSB, 20), BRICK)
BRIEFS = [
    (14, "US: Trump pardons turkeys Freedom, Feathers (Reuters)"),
    (15, "US: Fort Hood gunman seeks stay of execution (Reuters)"),
    (16, "US: Huckabee doubts Israel aid ends this year (Reuters)"),
    (17, "US: Thomas Markle indicted over abuse images (Reuters)"),
    (18, "Sweden: Vote due on Kristersson staying as PM (Reuters)"),
    (19, "Germany: Berlin Left expels antisemitism-row MP (Reuters)"),
    (20, "Germany: 53% now oppose Ukraine military aid (Reuters)"),
    (21, "Yemen: Houthis hit Riyadh tower; 11 wounded (Reuters)"),
    (22, "Russia: Putin vows reply as Kyiv hits oil plants (Reuters)"),
    (23, "Colombia: 25 held hostage in Cartagena shop (Reuters)"),
    (24, "WHO: US urged to lift Cuba fuel blockade (Reuters)"),
    (25, "Spain: Govt challenges Madrid unborn law (Reuters)"),
    (26, "Latvia: President sees Ukraine 'tipping point' (Reuters)"),
    (27, "Belarus: Lukashenko offers to fly with Zelenskiy (Reuters)"),
    (28, "UK: Prisoner admits killing child killer Huntley (Reuters)"),
    (29, "Turkey: AK Party veteran quits amid fund probe (Reuters)"),
    (30, "Libya: Frozen conflict risks fresh instability (Reuters)"),
    (31, "UN: Gaza remains raise war-crimes concern (UN)"),
    (32, "Iran: Security chief hails 'new world order' (Al Jazeera)"),
    (33, "India: BJP, Akali Dal open seat-sharing talks (Alfaaz)"),
    (34, "India: Nayi Chetna 5.0 gender drive launched (Govt)"),
    (35, "Cricket: South Africa lead Bangladesh by 403 runs (AAP)"),
    (36, "Tennis: Czechia beat Canada in Davis Cup QF (Davis Cup)"),
    (37, "Cricket: England beat Australia by 8 wickets (AAP)"),
    (38, "Cricket: Mumbai stay unbeaten in Indian T20 (Sporting Ave)"),
    (39, "India: Rahul Gandhi backs strong Israel ties (Al Jazeera)"),
    (40, "Gaza: Mass funeral for 70 found in rubble (Al Jazeera)"),
    (41, "Iran: Tehran threatens reply to any attack (Al Jazeera)"),
    (42, "West Bank: Army zones become settler land (Al Jazeera)"),
    (43, "NATO: Early-warning jets planned for Poland (NATO)"),
    (44, "Cricket: India–NZ Test: Prasidh strikes, Nicholls out (Rediff)"),
    (45, "Cricket: Sooryavanshi, 15, hits 204 off 53 balls (AAP)"),
    (46, "Asia: Nvidia suppliers cheer Huang's return (Reuters)"),
]
fb = F(SANS, 16)
fbn = F(SANSB, 16)
colw = (bw - 20) // 2
half = (len(BRIEFS) + 1) // 2
overflow = []
for i, (num, txt) in enumerate(BRIEFS):
    col = 0 if i < half else 1
    row = i if col == 0 else i - half
    x = bx + col * (colw + 20)
    y = by + 52 + row * 23
    text(x, y, f"{num}.", fbn, NAVY)
    text(x + 40, y, txt, fb, INK)
    if d.textlength(txt, font=fb) > colw - 40:
        overflow.append((num, txt))
if overflow:
    print("BRIEF OVERFLOW (too wide for column):")
    for n, t in overflow:
        print(" ", n, t)

# ---------------------------------------------------------------- date check
dy = 1836
d.rectangle([MX, dy, W - MX, dy + 96], fill=(238, 230, 208), outline=RULE)
text(MX + 16, dy + 10, "DATE CHECK", F(SANSB, 18), BRICK)
dc = ("Left out on purpose — broke before Wednesday: COP31 collapse (23 Nov) · Russia's 'terrorism' warning "
      "(23 Nov) · Gaza toll 74,746 update (23 Nov) · Democrats' 259 House seats (24 Nov).  "
      "Not yet: US Thanksgiving (Thu) · Iowa lead-azide blast (Wed morning) · Macy's 100th parade (Thu).")
for j, ln in enumerate(wrap(dc, F(SANS, 18), CW - 32)):
    text(MX + 16, dy + 36 + j * 22, ln, F(SANS, 18), INK)

# ---------------------------------------------------------------- footer
fy = 1944
hline(fy)
foot = ("Every story here happened or was first reported on Wednesday 25 November 2026. "
        "CLAIM = one side's account, not yet verified. Sources: Reuters, AP, Al Jazeera, UN, "
        "The West Australian, AAP, Rediff, Alfaaz Time, Govt of India. Original drawings.")
for j, ln in enumerate(wrap(foot, F(SANS, 16), CW)):
    text(W // 2, fy + 12 + j * 20, ln, F(SANS, 16), MUTED, anchor="ma")

OUT = os.path.dirname(os.path.abspath(__file__))
img.save(os.path.join(OUT, "master2048.png"))
small = img.resize((1024, 1024), Image.LANCZOS)
small.save(os.path.join(OUT, "entry.png"), optimize=True)
print("saved master", img.size, "entry", small.size)
print("master bytes:", os.path.getsize(os.path.join(OUT, "master2048.png")))
print("entry bytes:", os.path.getsize(os.path.join(OUT, "entry.png")))
