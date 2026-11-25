#!/usr/bin/env python3
"""Build the front page for the news-image-20261125 make.fun entry.

The concept is a broadsheet front page squeezed into one square
image: 46 dated stories from Wednesday 25 November 2026, with five
late items from Tuesday 24 November that are flagged TUE wherever
they show up. The 13 biggest stories each get a small flat picture
drawn from Pillow primitives. Around them sit a UTC timeline of
the day, a strip of key figures, a world map whose numbered pins
point back to the pictured stories, 33 one-line briefs, a DATE
CHECK panel that owns up to what was left out and why, and a
sourcing footer.

Rendering happens on a 2048x2048 canvas (kept as master2048.png);
the file that ships, entry.png, is a 1024x1024 downscale that has
to stay under 1 MiB.
"""

import os

from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------
# Canvas geometry and the ink/paper palette shared by every section.
# ------------------------------------------------------------------
CANVAS = 2048
MARGIN = 40
PAGE_W = CANVAS - 2 * MARGIN

CREAM = (247, 243, 233)
INK = (26, 26, 26)
NAVY = (31, 58, 95)
BRICK = (179, 64, 42)
TEAL = (42, 127, 111)
OCHRE = (200, 147, 42)
MUTED = (107, 98, 87)
RULE_GREY = (201, 192, 171)
CARD_CREAM = (252, 249, 240)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load_font(path, size):
    return ImageFont.truetype(path, size)


class FrontPage:
    """The page itself plus the three helpers every section reuses."""

    def __init__(self):
        self.image = Image.new("RGB", (CANVAS, CANVAS), CREAM)
        self.draw = ImageDraw.Draw(self.image)

    def write(self, x, y, string, font, colour=INK, anchor="la"):
        self.draw.text((x, y), string, font=font, fill=colour, anchor=anchor)

    def rule(self, y, colour=RULE_GREY, width=2):
        self.draw.line([(MARGIN, y), (CANVAS - MARGIN, y)], fill=colour, width=width)

    def wrapped(self, string, font, width):
        """Greedy word wrap, measured with the real font metrics."""
        lines = []
        current = ""
        for word in string.split():
            trial = word if current == "" else current + " " + word
            if self.draw.textlength(trial, font=font) <= width:
                current = trial
            else:
                if current != "":
                    lines.append(current)
                current = word
        if current != "":
            lines.append(current)
        return lines


# ------------------------------------------------------------------
# Small reusable motifs that several pictures are assembled from.
# ------------------------------------------------------------------
def motif_flame(pen, cx, cy, s, colour=BRICK):
    pen.polygon([(cx, cy - 32 * s), (cx + 18 * s, cy + 4 * s),
                 (cx + 8 * s, cy + 16 * s), (cx - 8 * s, cy + 16 * s),
                 (cx - 18 * s, cy + 4 * s)], fill=colour)
    pen.polygon([(cx, cy - 12 * s), (cx + 8 * s, cy + 12 * s),
                 (cx - 8 * s, cy + 12 * s)], fill=OCHRE)


def motif_boat(pen, cx, cy, s, hull_colour, sail_colour):
    pen.polygon([(cx - 68 * s, cy), (cx + 68 * s, cy),
                 (cx + 52 * s, cy + 24 * s), (cx - 52 * s, cy + 24 * s)],
                fill=hull_colour)
    pen.rectangle([cx + 28 * s, cy - 28 * s, cx + 56 * s, cy], fill=hull_colour)
    pen.rectangle([cx - 56 * s, cy - 16 * s, cx - 16 * s, cy], fill=sail_colour)
    for k in range(3):
        pen.arc([cx - 80 * s + k * 52 * s, cy + 32 * s,
                 cx - 32 * s + k * 52 * s, cy + 52 * s], 0, 180,
                fill=NAVY, width=3)


def motif_tower(pen, cx, cy, s, colour=NAVY):
    pen.rectangle([cx - 32 * s, cy - 44 * s, cx + 32 * s, cy + 28 * s], fill=colour)
    for row in range(3):
        for col in range(3):
            pen.rectangle([cx - 24 * s + col * 18 * s, cy - 36 * s + row * 20 * s,
                           cx - 12 * s + col * 18 * s, cy - 24 * s + row * 20 * s],
                          fill=OCHRE)
    pen.polygon([(cx - 36 * s, cy - 44 * s), (cx, cy - 60 * s),
                 (cx + 36 * s, cy - 44 * s)], fill=BRICK)


def motif_balance(pen, cx, cy, s, colour=NAVY):
    pen.line([(cx, cy - 32 * s), (cx, cy + 28 * s)], fill=colour, width=6)
    pen.line([(cx - 32 * s, cy - 24 * s), (cx + 32 * s, cy - 24 * s)],
             fill=colour, width=4)
    pen.line([(cx - 32 * s, cy - 24 * s), (cx - 32 * s, cy + 4 * s)],
             fill=colour, width=4)
    pen.line([(cx + 32 * s, cy - 24 * s), (cx + 32 * s, cy + 4 * s)],
             fill=colour, width=4)
    pen.polygon([(cx - 44 * s, cy + 4 * s), (cx - 20 * s, cy + 4 * s),
                 (cx - 32 * s, cy + 20 * s)], fill=colour)
    pen.polygon([(cx + 20 * s, cy + 4 * s), (cx + 44 * s, cy + 4 * s),
                 (cx + 32 * s, cy + 20 * s)], fill=colour)
    pen.rectangle([cx - 24 * s, cy + 28 * s, cx + 24 * s, cy + 34 * s], fill=colour)


def motif_trend(pen, cx, cy, s, falling=True, colour=BRICK):
    if falling:
        points = [(cx - 60 * s, cy - 28 * s), (cx - 30 * s, cy - 12 * s),
                  (cx, cy - 20 * s), (cx + 30 * s, cy + 4 * s),
                  (cx + 60 * s, cy + 24 * s)]
    else:
        points = [(cx - 60 * s, cy + 8 * s), (cx - 30 * s, cy - 4 * s),
                  (cx, cy + 4 * s), (cx + 30 * s, cy - 20 * s),
                  (cx + 60 * s, cy - 32 * s)]
    pen.line(points, fill=colour, width=6)
    pen.polygon([(cx + 60 * s, cy + 24 * s), (cx + 44 * s, cy + 24 * s),
                 (cx + 60 * s, cy + 8 * s)], fill=colour)


# ------------------------------------------------------------------
# The thirteen pictures. Each paints its own tinted panel first,
# then draws inside it around the panel centre.
# ------------------------------------------------------------------
def _panel(pen, x, y, w, h, tint):
    pen.rectangle([x, y, x + w, y + h], fill=tint, outline=RULE_GREY)


def _centre(x, y, w, h):
    return x + w // 2, y + h // 2, min(w, h) / 128.0


def art_rocket(page, x, y, w, h):
    pen = page.draw
    _panel(pen, x, y, w, h, (222, 228, 240))
    cx, cy, s = _centre(x, y, w, h)
    pen.polygon([(cx - 22, cy - 44), (cx - 22, cy + 20),
                 (cx + 22, cy + 20), (cx + 22, cy - 44)],
                fill=CREAM, outline=NAVY, width=3)
    pen.polygon([(cx - 22, cy - 44), (cx, cy - 66), (cx + 22, cy - 44)], fill=BRICK)
    pen.ellipse([cx - 10, cy - 28, cx + 10, cy - 8], fill=TEAL, outline=NAVY, width=2)
    pen.polygon([(cx - 22, cy + 8), (cx - 40, cy + 34), (cx - 22, cy + 20)], fill=BRICK)
    pen.polygon([(cx + 22, cy + 8), (cx + 40, cy + 34), (cx + 22, cy + 20)], fill=BRICK)
    motif_flame(pen, cx, cy + 44, s * 1.1)
    for sx, sy in [(-52, -52), (54, -44), (-58, 20), (58, 30), (40, -58)]:
        pen.ellipse([cx + sx - 3, cy + sy - 3, cx + sx + 3, cy + sy + 3], fill=NAVY)


def art_boat(page, x, y, w, h):
    pen = page.draw
    _panel(pen, x, y, w, h, (214, 226, 238))
    cx, cy, s = _centre(x, y, w, h)
    motif_boat(pen, cx, cy - 8, s * 0.9, NAVY, BRICK)
    motif_flame(pen, cx + 52, cy - 44, s * 0.8)
    pen.ellipse([cx + 36, cy - 60, cx + 44, cy - 52], fill=(160, 160, 158))
    pen.ellipse([cx + 48, cy - 68, cx + 58, cy - 58], fill=(178, 178, 176))


def art_bars(page, x, y, w, h):
    pen = page.draw
    _panel(pen, x, y, w, h, (240, 226, 222))
    cx, cy, s = _centre(x, y, w, h)
    for i, bar_h in enumerate((28, 40, 20, 48)):
        pen.rectangle([cx - 56 + i * 30, cy + 24 - bar_h,
                       cx - 36 + i * 30, cy + 24],
                      fill=TEAL if i % 2 == 0 else BRICK)
    motif_trend(pen, cx, cy - 12, s * 0.55)


def art_medal(page, x, y, w, h):
    pen = page.draw
    _panel(pen, x, y, w, h, (238, 228, 210))
    cx, cy, s = _centre(x, y, w, h)
    pen.polygon([(cx - 24, cy - 58), (cx - 8, cy - 58), (cx - 2, cy - 16),
                 (cx - 30, cy - 16)], fill=BRICK)
    pen.polygon([(cx + 8, cy - 58), (cx + 24, cy - 58), (cx + 30, cy - 16),
                 (cx + 2, cy - 16)], fill=NAVY)
    pen.ellipse([cx - 34, cy - 24, cx + 34, cy + 44],
                fill=OCHRE, outline=BRICK, width=3)
    pen.polygon([(cx, cy - 12), (cx + 8, cy + 4), (cx + 24, cy + 4),
                 (cx + 12, cy + 14), (cx + 16, cy + 30), (cx, cy + 20),
                 (cx - 16, cy + 30), (cx - 12, cy + 14), (cx - 24, cy + 4),
                 (cx - 8, cy + 4)], fill=CREAM)


def art_plane(page, x, y, w, h):
    pen = page.draw
    _panel(pen, x, y, w, h, (222, 230, 238))
    cx, cy, s = _centre(x, y, w, h)
    pen.polygon([(cx - 64, cy - 4), (cx + 52, cy - 4), (cx + 68, cy + 4),
                 (cx + 52, cy + 12), (cx - 64, cy + 12)], fill=NAVY)
    pen.polygon([(cx - 16, cy - 32), (cx + 4, cy - 32), (cx + 4, cy + 20),
                 (cx - 16, cy + 20)], fill=NAVY)
    pen.polygon([(cx - 52, cy + 12), (cx - 32, cy + 12), (cx - 44, cy + 32),
                 (cx - 60, cy + 32)], fill=NAVY)
    for wx in (-40, -20, 0, 20):
        pen.ellipse([cx + wx, cy - 2, cx + wx + 8, cy + 6], fill=OCHRE)


def art_balance(page, x, y, w, h):
    pen = page.draw
    _panel(pen, x, y, w, h, (232, 228, 222))
    cx, cy, s = _centre(x, y, w, h)
    motif_balance(pen, cx, cy, s * 0.9)


def art_flag(page, x, y, w, h):
    pen = page.draw
    _panel(pen, x, y, w, h, (222, 235, 225))
    cx, cy, s = _centre(x, y, w, h)
    pen.polygon([(cx - 64, cy + 36), (cx - 28, cy - 24), (cx + 8, cy + 36)],
                fill=(120, 140, 110))
    pen.polygon([(cx - 12, cy + 36), (cx + 24, cy - 24), (cx + 64, cy + 36)],
                fill=(100, 120, 95))
    pen.line([(cx + 52, cy - 58), (cx + 52, cy + 36)], fill=INK, width=4)
    pen.polygon([(cx + 52, cy - 58), (cx + 96, cy - 44), (cx + 52, cy - 30)],
                fill=BRICK)


def art_radar(page, x, y, w, h):
    pen = page.draw
    _panel(pen, x, y, w, h, (232, 230, 238))
    cx, cy, s = _centre(x, y, w, h)
    pen.rectangle([cx - 10, cy - 10, cx + 10, cy + 44], fill=NAVY)
    pen.polygon([(cx - 34, cy - 44), (cx + 34, cy - 44), (cx + 10, cy - 10),
                 (cx - 10, cy - 10)], fill=CREAM, outline=NAVY, width=3)
    for r in (52, 70):
        pen.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=TEAL, width=3)
    pen.line([(cx, cy - 44), (cx, cy - 66)], fill=NAVY, width=3)
    pen.ellipse([cx - 5, cy - 71, cx + 5, cy - 61], fill=BRICK)


def art_runway(page, x, y, w, h):
    pen = page.draw
    _panel(pen, x, y, w, h, (238, 226, 214))
    cx, cy, s = _centre(x, y, w, h)
    pen.polygon([(cx - 70, cy + 44), (cx - 14, cy - 44), (cx + 14, cy - 44),
                 (cx + 70, cy + 44)], fill=(90, 90, 96))
    for k in range(4):
        dash_y = cy - 32 + k * 20
        dash_w = 4 + k * 3
        pen.rectangle([cx - dash_w, dash_y, cx + dash_w, dash_y + 8], fill=CREAM)
    pen.ellipse([cx + 40, cy - 58, cx + 56, cy - 42], fill=(160, 160, 158))
    pen.ellipse([cx + 52, cy - 66, cx + 66, cy - 52], fill=(178, 178, 176))


def art_blast(page, x, y, w, h):
    pen = page.draw
    _panel(pen, x, y, w, h, (228, 224, 220))
    cx, cy, s = _centre(x, y, w, h)
    motif_tower(pen, cx - 12, cy + 8, s * 0.9)
    motif_flame(pen, cx + 44, cy - 12, s * 0.7)
    pen.ellipse([cx + 36, cy - 60, cx + 60, cy - 36], fill=(160, 160, 158))
    pen.ellipse([cx + 48, cy - 68, cx + 68, cy - 48], fill=(178, 178, 176))


def art_chip(page, x, y, w, h):
    pen = page.draw
    _panel(pen, x, y, w, h, (222, 236, 222))
    cx, cy, s = _centre(x, y, w, h)
    pen.rectangle([cx - 40, cy - 32, cx + 24, cy + 32], fill=NAVY)
    for k in range(4):
        pin_y = cy - 24 + k * 16
        pen.line([(cx - 52, pin_y), (cx - 40, pin_y)], fill=NAVY, width=4)
        pen.line([(cx + 24, pin_y), (cx + 36, pin_y)], fill=NAVY, width=4)
    pen.rectangle([cx - 24, cy - 16, cx + 8, cy + 16], fill=TEAL)
    motif_trend(pen, cx + 48, cy - 4, s * 0.5, falling=False, colour=TEAL)


def art_santa(page, x, y, w, h):
    pen = page.draw
    _panel(pen, x, y, w, h, (238, 228, 200))
    cx, cy, s = _centre(x, y, w, h)
    pen.rectangle([cx - 70, cy + 24, cx + 70, cy + 44], fill=(214, 196, 150))
    pen.polygon([(cx - 46, cy + 24), (cx - 46, cy - 30), (cx + 10, cy - 30),
                 (cx + 10, cy + 24)], fill=BRICK)
    pen.polygon([(cx - 46, cy - 30), (cx - 18, cy - 52), (cx + 10, cy - 30)],
                fill=BRICK)
    pen.ellipse([cx - 46, cy - 34, cx - 18, cy - 6], fill=CREAM)
    pen.ellipse([cx + 30, cy - 44, cx + 62, cy - 12], fill=CREAM)
    pen.ellipse([cx + 38, cy - 38, cx + 54, cy - 22], fill=NAVY)


def art_emblem(page, x, y, w, h):
    pen = page.draw
    _panel(pen, x, y, w, h, (222, 228, 238))
    cx, cy, s = _centre(x, y, w, h)
    pen.line([(cx - 52, cy - 58), (cx - 52, cy + 36)], fill=INK, width=4)
    pen.line([(cx + 52, cy - 58), (cx + 52, cy + 36)], fill=INK, width=4)
    pen.polygon([(cx - 52, cy - 58), (cx - 8, cy - 44), (cx - 52, cy - 30)],
                fill=TEAL)
    pen.polygon([(cx + 52, cy - 58), (cx + 8, cy - 44), (cx + 52, cy - 30)],
                fill=BRICK)
    pen.polygon([(cx, cy - 58), (cx + 6, cy - 44), (cx + 18, cy - 44),
                 (cx + 8, cy - 34), (cx + 12, cy - 20), (cx, cy - 28),
                 (cx - 12, cy - 20), (cx - 8, cy - 34), (cx - 18, cy - 44),
                 (cx - 6, cy - 44)], fill=OCHRE)
    pen.rectangle([cx - 40, cy + 36, cx + 40, cy + 44], fill=NAVY)


ARTWORK = {
    "rocket": art_rocket,
    "ship": art_boat,
    "chart": art_bars,
    "medal": art_medal,
    "plane": art_plane,
    "scales": art_balance,
    "flag": art_flag,
    "radar": art_radar,
    "runway": art_runway,
    "blast": art_blast,
    "chip": art_chip,
    "santa": art_santa,
    "handshake": art_emblem,
}


def paint_art(page, kind, x, y, w, h):
    ARTWORK[kind](page, x, y, w, h)


# ------------------------------------------------------------------
# Story data. The five Tuesday items say so in their status line.
# ------------------------------------------------------------------
LEAD_STORIES = [
    {"no": 1, "art": "rocket", "region": "GLOBAL", "topic": "SPACE",
     "status": "CONFIRMED – REUTERS",
     "headline": "Shenzhou-24 lifts off with first Pakistani in orbit",
     "deck": "Zeeshan Ali, 40, joins two Chinese crew on Tiangong; "
             "first foreign astronaut aboard the station."},
    {"no": 2, "art": "ship", "region": "EUROPE", "topic": "WAR",
     "status": "CONFIRMED TUE – REUTERS",
     "headline": "Zelenskiy confirms Ukraine hit Russian ship in Baltic",
     "deck": "Kyiv owns Saturday's drone strike on a cargo ship in the "
             "Gulf of Finland; Norway urges caution."},
    {"no": 3, "art": "chart", "region": "ASIA", "topic": "MARKETS",
     "status": "CONFIRMED – REUTERS",
     "headline": "Asian stocks tumble as US tariff threats hit sentiment",
     "deck": "Kospi drops 5.7% at its worst, Taiwan 8.2%, Nikkei 3.2%; "
             "Nvidia gives back 5.9% after Monday's surge."},
]

CARD_STORIES = [
    {"no": 4, "art": "medal", "region": "AMERICAS", "topic": "POLITICS",
     "status": "CONFIRMED TUE – AP",
     "headline": "Trump awards Giuliani the Medal of Freedom",
     "deck": "Ex-New York mayor, 82, honoured at White House; led city through 9/11."},
    {"no": 5, "art": "plane", "region": "AMERICAS", "topic": "IMMIGRATION",
     "status": "CONFIRMED – AP",
     "headline": "Abrego Garcia to self-deport to Spain, AP reports",
     "deck": "Salvadoran migrant to fly to Europe on a commercial flight to avoid deportation."},
    {"no": 6, "art": "scales", "region": "EUROPE", "topic": "JUSTICE",
     "status": "CONFIRMED TUE – REUTERS",
     "headline": "Sarkozy corruption case sent to trial in Paris",
     "deck": "Ex-president and wife Carla Bruni face trial; first hearing set for 1 April 2027."},
    {"no": 7, "art": "flag", "region": "MIDDLE EAST", "topic": "WAR",
     "status": "CONFIRMED – REUTERS",
     "headline": "Houthis will not seize Aden, Yemeni army says",
     "deck": "Fighters pushed to 60 km of the temporary capital; 'not as dire as reported'."},
    {"no": 8, "art": "radar", "region": "AMERICAS", "topic": "TRAVEL",
     "status": "CONFIRMED – FAA",
     "headline": "Radar outage delays flights at Chicago O'Hare",
     "deck": "FAA holds some arrivals as technicians repair ground radar at holiday peak."},
    {"no": 9, "art": "runway", "region": "MIDDLE EAST", "topic": "WAR",
     "status": "REPORTED – AL JAZEERA",
     "headline": "Strikes reported on Houthi-run Hodeidah airport",
     "deck": "Fire and smoke seen over the Red Sea port city; no casualty toll yet given."},
    {"no": 10, "art": "blast", "region": "EUROPE", "topic": "WAR",
     "status": "CONFIRMED – REUTERS",
     "headline": "Russian strike kills two in Ukraine's Odesa region",
     "deck": "Cars and homes hit; drones attack Kyiv late on Tuesday, injuring two."},
    {"no": 11, "art": "chip", "region": "ASIA", "topic": "TECH",
     "status": "CONFIRMED TUE – REUTERS",
     "headline": "Huawei convicted in US trial over Iran business",
     "deck": "Jury finds firm deceived banks and stole trade secrets; case began in 2018."},
    {"no": 12, "art": "santa", "region": "EUROPE", "topic": "LIGHT",
     "status": "CONFIRMED – REUTERS",
     "headline": "Santas wash up on a Bulgarian beach in a container",
     "deck": "Life-size figures and a polar bear found near Burgas; vessel hit by drones."},
    {"no": 13, "art": "handshake", "region": "MIDDLE EAST", "topic": "POLITICS",
     "status": "CONFIRMED – REUTERS",
     "headline": "Eisenkot clinches first coalition pact in Israel",
     "deck": "Ex-army chief's Yashar party signs deal with Lieberman's party after election."},
]

TIMELINE = [
    ("OVERNIGHT", "Russian strike kills\ntwo in Odesa"),
    ("00:18 UTC", "Shenzhou-24 lifts off\nwith Pakistani aboard"),
    ("01:00 UTC", "Asian stocks tumble\non tariff threats"),
    ("ASIA DAY", "Nvidia suppliers cheer\nHuang's return"),
    ("EUROPE DAY", "Sarkozy case sent\nto trial in Paris"),
    ("TUE EVENING", "Trump honours Giuliani,\npardons two turkeys"),
]

FIGURES = [
    ("1st", "Pakistani in orbit;\nfirst foreigner on Tiangong"),
    ("-5.7%", "Kospi's fall at\nits worst point"),
    ("$3.8bn", "US military aid to\nIsrael now in doubt"),
    ("25", "hostages held in a\nCartagena supermarket"),
    ("53%", "of Germans now oppose\nUkraine military aid"),
    ("60 km", "Houthis from Aden,\nthe temporary capital"),
]

# Stories 14-46, one line each; the number is the position + 14.
BRIEF_LINES = [
    "US: Trump pardons turkeys Freedom, Feathers (Reuters, Tue)",
    "US: Fort Hood gunman seeks stay of execution (Reuters)",
    "US: Huckabee doubts Israel aid ends this year (Reuters)",
    "US: Thomas Markle indicted over abuse images (Reuters)",
    "Sweden: Vote due on Kristersson staying as PM (Reuters)",
    "Germany: Berlin Left expels antisemitism-row MP (Reuters)",
    "Germany: 53% now oppose Ukraine military aid (Reuters)",
    "Yemen: Houthis hit Riyadh tower; 11 wounded (Reuters)",
    "Russia: Putin vows reply as Kyiv hits oil plants (Reuters)",
    "Colombia: 25 held hostage in Cartagena shop (Reuters)",
    "WHO: US urged to lift Cuba fuel blockade (Reuters)",
    "Spain: Govt challenges Madrid unborn law (Reuters)",
    "Latvia: President sees Ukraine 'tipping point' (Reuters)",
    "Belarus: Lukashenko offers to fly with Zelenskiy (Reuters)",
    "UK: Prisoner admits killing child killer Huntley (Reuters)",
    "Turkey: AK Party veteran quits amid fund probe (Reuters)",
    "Libya: Frozen conflict risks fresh instability (Reuters)",
    "UN: Gaza remains raise war-crimes concern (UN)",
    "Iran: Security chief hails 'new world order' (Al Jazeera)",
    "India: BJP, Akali Dal open seat-sharing talks (Alfaaz)",
    "India: Nayi Chetna 5.0 gender drive launched (Govt)",
    "Cricket: South Africa lead Bangladesh by 403 runs (AAP)",
    "Tennis: Czechia beat Canada in Davis Cup QF (Davis Cup)",
    "Cricket: England beat Australia by 8 wickets (AAP)",
    "Cricket: Mumbai stay unbeaten in Indian T20 (Sporting Ave)",
    "India: Rahul Gandhi backs strong Israel ties (Al Jazeera)",
    "Gaza: Mass funeral for 70 found in rubble (Al Jazeera)",
    "Iran: Tehran threatens reply to any attack (Al Jazeera)",
    "West Bank: Army zones become settler land (Al Jazeera)",
    "NATO: Early-warning jets planned for Poland (NATO)",
    "Cricket: India–NZ Test: Prasidh strikes, Nicholls out (Rediff)",
    "Cricket: Sooryavanshi, 15, hits 204 off 53 balls (AAP)",
    "Asia: Nvidia suppliers cheer Huang's return (Reuters)",
]


# ------------------------------------------------------------------
# Page sections, painted top to bottom in reading order.
# ------------------------------------------------------------------
def draw_header(page):
    strap = load_font(SANS_BOLD, 22)
    page.write(MARGIN, 28, "ONE DAY OF WORLD NEWS, ONE PICTURE", strap, NAVY)
    page.write(CANVAS - MARGIN, 28,
               "46 STORIES  ·  7 REGIONS  ·  FIVE FROM TUESDAY, MARKED TUE",
               strap, NAVY, anchor="ra")
    page.rule(64)
    page.write(CANVAS // 2, 80, "Wednesday 25 November 2026",
               load_font(SERIF_BOLD, 92), INK, anchor="ma")
    page.rule(176, width=4)
    page.write(CANVAS // 2, 188,
               "ASIA 9  ·  MIDDLE EAST 9  ·  EUROPE 14  ·  AMERICAS 8  ·  "
               "AFRICA 2  ·  OCEANIA 1  ·  GLOBAL 3",
               load_font(SANS_BOLD, 20), MUTED, anchor="ma")
    page.rule(224)


def draw_timeline(page):
    top, height = 236, 100
    page.write(MARGIN, top - 4, "THE DAY IN UTC", load_font(SANS_BOLD, 18), BRICK)
    stamp_font = load_font(SANS_BOLD, 18)
    head_font = load_font(SANS, 18)
    cell_w = (PAGE_W - 5 * 8) // 6
    for i, (stamp, headline) in enumerate(TIMELINE):
        x = MARGIN + i * (cell_w + 8)
        page.draw.rectangle([x, top + 24, x + cell_w, top + 24 + height - 24],
                            outline=RULE_GREY)
        page.write(x + 12, top + 30, stamp, stamp_font, NAVY)
        for j, line in enumerate(headline.split("\n")):
            page.write(x + 12, top + 56 + j * 22, line, head_font, INK)
    page.rule(top + 24 + height + 8)


def draw_figures(page):
    top = 356
    page.write(MARGIN, top, "THE DAY IN NUMBERS", load_font(SANS_BOLD, 18), BRICK)
    figure_font = load_font(SERIF_BOLD, 42)
    caption_font = load_font(SANS, 16)
    cell_w = (PAGE_W - 5 * 8) // 6
    for i, (figure, caption) in enumerate(FIGURES):
        x = MARGIN + i * (cell_w + 8)
        page.write(x + 8, top + 26, figure, figure_font, NAVY)
        for j, line in enumerate(caption.split("\n")):
            page.write(x + 8, top + 76 + j * 20, line, caption_font, MUTED)
    page.rule(top + 120)


def _headline_and_deck(page, story, text_x, start_y, wrap_width,
                       headline_font, deck_font, headline_step, deck_step,
                       headline_max, deck_max):
    y = start_y
    for line in page.wrapped(story["headline"], headline_font, wrap_width)[:headline_max]:
        page.write(text_x, y, line, headline_font, INK)
        y += headline_step
    for line in page.wrapped(story["deck"], deck_font, wrap_width)[:deck_max]:
        page.write(text_x, y, line, deck_font, INK)
        y += deck_step


def draw_leads(page):
    top, height = 488, 296
    width = (PAGE_W - 2 * 24) // 3
    label_font = load_font(SANS_BOLD, 16)
    status_font = load_font(SANS_BOLD, 16)
    headline_font = load_font(SERIF_BOLD, 28)
    deck_font = load_font(SERIF, 18)
    number_font = load_font(SERIF_BOLD, 26)
    for i, story in enumerate(LEAD_STORIES):
        x = MARGIN + i * (width + 24)
        page.draw.rectangle([x, top, x + width, top + height],
                            fill=CARD_CREAM, outline=RULE_GREY)
        paint_art(page, story["art"], x + 2, top + 2, width - 4, 108)
        page.draw.ellipse([x + 16, top + 116, x + 60, top + 160], fill=NAVY)
        page.write(x + 38, top + 120, str(story["no"]), number_font, CREAM,
                   anchor="ma")
        page.write(x + 72, top + 120,
                   story["region"] + " · " + story["topic"], label_font, BRICK)
        page.write(x + 72, top + 142, story["status"], status_font, TEAL)
        _headline_and_deck(page, story, x + 16, top + 168, width - 32,
                           headline_font, deck_font, 30, 22, 2, 3)


def draw_cards(page):
    top, height = 796, 256
    width = (PAGE_W - 4 * 16) // 5
    headline_font = load_font(SERIF_BOLD, 22)
    deck_font = load_font(SERIF, 18)
    number_font = load_font(SERIF_BOLD, 20)
    label_font = load_font(SANS_BOLD, 14)
    status_font = load_font(SANS_BOLD, 14)
    for i, story in enumerate(CARD_STORIES):
        row, col = divmod(i, 5)
        x = MARGIN + col * (width + 16)
        y = top + row * (height + 16)
        page.draw.rectangle([x, y, x + width, y + height],
                            fill=CARD_CREAM, outline=RULE_GREY)
        paint_art(page, story["art"], x + 2, y + 2, width - 4, 92)
        page.draw.ellipse([x + 12, y + 100, x + 44, y + 132], fill=NAVY)
        page.write(x + 28, y + 102, str(story["no"]), number_font, CREAM,
                   anchor="ma")
        page.write(x + 52, y + 102,
                   story["region"] + " · " + story["topic"], label_font, BRICK)
        page.write(x + 52, y + 120, story["status"], status_font, TEAL)
        _headline_and_deck(page, story, x + 12, y + 142, width - 24,
                           headline_font, deck_font, 24, 22, 2, 2)


# ------------------------------------------------------------------
# Bottom third: the pinned map on the left, the briefs on the right.
# ------------------------------------------------------------------
MAP_LEFT = MARGIN
MAP_WIDTH = 784
MAP_TOP = 1328 + 76
MAP_BOTTOM = 1328 + 392
MAP_RIGHT = MAP_LEFT + MAP_WIDTH - 16
LAND_FILL = (232, 220, 194)
LAND_EDGE = (185, 172, 141)

CONTINENT_OUTLINES = [
    [[-168, 66], [-140, 70], [-125, 72], [-110, 73], [-95, 80], [-85, 80],
     [-75, 73], [-65, 60], [-55, 52], [-60, 46], [-70, 42], [-75, 35],
     [-80, 26], [-85, 30], [-90, 21], [-97, 16], [-105, 20], [-115, 28],
     [-125, 40], [-125, 49], [-140, 60], [-155, 58], [-168, 66]],
    [[-80, 10], [-75, 11], [-70, 12], [-62, 10], [-52, 5], [-50, 0],
     [-35, -8], [-40, -20], [-48, -28], [-58, -35], [-65, -41], [-70, -54],
     [-73, -37], [-70, -20], [-80, -5], [-80, 10]],
    [[-17, 15], [-10, 31], [0, 36], [10, 37], [20, 32], [32, 31], [35, 28],
     [43, 12], [51, 11], [48, 0], [40, -10], [35, -18], [28, -33], [20, -35],
     [12, -18], [9, 4], [-8, 4], [-17, 15]],
    [[-10, 36], [-9, 43], [-2, 48], [0, 51], [5, 53], [8, 57], [10, 59],
     [18, 56], [21, 55], [24, 58], [30, 60], [30, 70], [40, 68], [55, 69],
     [70, 72], [90, 75], [110, 76], [130, 72], [150, 70], [170, 66],
     [178, 65], [170, 60], [162, 56], [158, 52], [142, 50], [140, 40],
     [135, 35], [130, 32], [122, 30], [120, 22], [110, 20], [105, 10],
     [100, 8], [98, 12], [92, 16], [88, 22], [80, 15], [77, 8], [72, 20],
     [66, 25], [60, 25], [57, 26], [52, 28], [48, 30], [44, 29], [40, 36],
     [36, 36], [30, 36], [26, 38], [23, 36], [19, 40], [15, 44], [12, 44],
     [8, 44], [3, 43], [-2, 37], [-6, 36], [-10, 36]],
    [[113, -22], [114, -30], [115, -35], [124, -33], [130, -32], [137, -35],
     [140, -38], [147, -39], [150, -37], [153, -27], [146, -19], [142, -11],
     [135, -12], [132, -11], [126, -14], [122, -17], [114, -22]],
    [[-45, 60], [-30, 68], [-20, 70], [-25, 76], [-40, 80], [-58, 76],
     [-55, 70], [-45, 60]],
]

ISLANDS = [(130, 32, 6), (137, 36, 6), (141, 40, 6), (95, 5, 6), (105, -2, 6),
           (115, -8, 6), (125, -5, 6), (135, -4, 6), (167, -16, 4),
           (174, -41, 4), (18, -34, 4), (-3, 54, 4)]

MAP_PINS = [(100, 40, 1), (24, 59, 2), (139, 35, 3), (-77, 39, 4),
            (-89, 13, 5), (2, 49, 6), (45, 13, 7), (-88, 42, 8), (43, 15, 9),
            (31, 46, 10), (-74, 41, 11), (27, 42, 12), (35, 32, 13)]
PIN_NUDGES = {7: (32, 32), 9: (-36, -28), 10: (0, -32), 12: (0, 32), 13: (28, 20)}


def _project(lon, lat):
    px = MAP_LEFT + (lon + 180) * (MAP_RIGHT - MAP_LEFT) / 360.0
    py = MAP_TOP + (85 - lat) * (MAP_BOTTOM - MAP_TOP) / 145.0
    return px, py


def draw_map(page):
    section_y = 1328
    page.write(MAP_LEFT, section_y + 16, "WHERE IT HAPPENED",
               load_font(SANS_BOLD, 20), BRICK)
    page.write(MAP_LEFT, section_y + 44,
               "Pins 1–13 match the pictured stories above.",
               load_font(SANS, 16), MUTED)
    page.draw.rectangle([MAP_LEFT, MAP_TOP, MAP_RIGHT, MAP_BOTTOM],
                        fill=(233, 226, 205), outline=RULE_GREY)
    for outline in CONTINENT_OUTLINES:
        page.draw.polygon([_project(lon, lat) for lon, lat in outline],
                          fill=LAND_FILL, outline=LAND_EDGE)
    for lon, lat, r in ISLANDS:
        px, py = _project(lon, lat)
        page.draw.ellipse([px - r, py - r, px + r, py + r],
                          fill=LAND_FILL, outline=LAND_EDGE)
    pin_font = load_font(SERIF_BOLD, 18)
    for lon, lat, num in MAP_PINS:
        px, py = _project(lon, lat)
        ox, oy = PIN_NUDGES.get(num, (0, 0))
        qx, qy = px + ox, py + oy
        if (ox, oy) != (0, 0):
            page.draw.line([(px, py), (qx, qy)], fill=BRICK, width=2)
        page.draw.ellipse([qx - 16, qy - 16, qx + 16, qy + 16],
                          fill=NAVY, outline=CREAM, width=2)
        page.write(qx, qy - 14, str(num), pin_font, CREAM, anchor="ma")
    page.write(MAP_LEFT, MAP_BOTTOM + 12,
               "ASIA 9 · MIDDLE EAST 9 · EUROPE 14 · AMERICAS 8 · AFRICA 2 · "
               "OCEANIA 1 · GLOBAL 3",
               load_font(SANS_BOLD, 16), MUTED)


def draw_briefs(page):
    section_y = 1328
    left = MAP_LEFT + MAP_WIDTH + 24
    width = CANVAS - MARGIN - left
    page.write(left, section_y + 16, "ALSO REPORTED — STORIES 14–46",
               load_font(SANS_BOLD, 20), BRICK)
    body_font = load_font(SANS, 16)
    number_font = load_font(SANS_BOLD, 16)
    column_w = (width - 20) // 2
    split = (len(BRIEF_LINES) + 1) // 2
    too_wide = []
    for i, line in enumerate(BRIEF_LINES):
        if i < split:
            column, row = 0, i
        else:
            column, row = 1, i - split
        x = left + column * (column_w + 20)
        y = section_y + 52 + row * 23
        page.write(x, y, str(i + 14) + ".", number_font, NAVY)
        page.write(x + 40, y, line, body_font, INK)
        if page.draw.textlength(line, font=body_font) > column_w - 40:
            too_wide.append((i + 14, line))
    if too_wide:
        print("BRIEF OVERFLOW (too wide for column):")
        for num, line in too_wide:
            print(" ", num, line)


def draw_date_check(page):
    top = 1836
    page.draw.rectangle([MARGIN, top, CANVAS - MARGIN, top + 96],
                        fill=(238, 230, 208), outline=RULE_GREY)
    page.write(MARGIN + 16, top + 10, "DATE CHECK", load_font(SANS_BOLD, 18),
               BRICK)
    body = ("Left out on purpose — broke before Wednesday: COP31 collapse "
            "(23 Nov) · Russia's 'terrorism' warning (23 Nov) · Gaza toll "
            "74,746 update (23 Nov) · Democrats' 259 House seats (24 Nov).  "
            "Not yet: US Thanksgiving (Thu) · Macy's 100th parade (Thu).")
    body_font = load_font(SANS, 18)
    for j, line in enumerate(page.wrapped(body, body_font, PAGE_W - 32)):
        page.write(MARGIN + 16, top + 36 + j * 22, line, body_font, INK)


def draw_footer(page):
    top = 1944
    page.rule(top)
    body = ("Stories here happened or were first reported on Wednesday "
            "25 November 2026, except five late stories from Tuesday "
            "24 November, marked TUE. CLAIM = one side's account, not yet "
            "verified. Sources: Reuters, AP, Al Jazeera, UN, "
            "The West Australian, AAP, Rediff, Alfaaz Time, Govt of India. "
            "Original drawings.")
    body_font = load_font(SANS, 16)
    for j, line in enumerate(page.wrapped(body, body_font, PAGE_W)):
        page.write(CANVAS // 2, top + 12 + j * 20, line, body_font, MUTED,
                   anchor="ma")


def build():
    page = FrontPage()
    draw_header(page)
    draw_timeline(page)
    draw_figures(page)
    draw_leads(page)
    draw_cards(page)
    page.rule(1328)
    draw_map(page)
    draw_briefs(page)
    draw_date_check(page)
    draw_footer(page)

    here = os.path.dirname(os.path.abspath(__file__))
    master_path = os.path.join(here, "master2048.png")
    entry_path = os.path.join(here, "entry.png")
    page.image.save(master_path)
    shrunk = page.image.resize((1024, 1024), Image.LANCZOS)
    shrunk.save(entry_path, optimize=True)
    print("saved master", page.image.size, "entry", shrunk.size)
    print("master bytes:", os.path.getsize(master_path))
    print("entry bytes:", os.path.getsize(entry_path))


if __name__ == "__main__":
    build()
