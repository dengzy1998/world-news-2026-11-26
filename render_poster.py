#!/usr/bin/env python3
"""Render the 26 November 2026 world-news poster (1024x1024 PNG).

52 stories from the sourced ledger stories.md: 3 illustrated leads, 12 grid
cards, 37 one-liners, a UTC timeline strip, a numbered schematic map, and a
DATE CHECK box listing older stories deliberately left out. Deterministic:
no network, no clock, no randomness. Writes entry.png beside this file.

Layout is drawn by small section builders over one shared canvas. Story
data lives in plain tuples at the top; the map continents are stored as
space-separated "lon,lat" strings and parsed at draw time.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

SIZE = (1024, 1024)
COLORS = {
    "paper": (248, 244, 232), "ink": (25, 25, 25), "muted": (90, 86, 76),
    "red": (166, 30, 30), "blue": (30, 78, 138), "navy": (16, 42, 84),
    "teal": (15, 107, 92), "gold": (154, 106, 0), "line": (201, 194, 176),
    "card": (255, 255, 255), "mapfill": (216, 210, 192),
    "mapline": (138, 132, 113), "white": (255, 255, 255),
}
FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


TITLE_F = load_font("DejaVuSans-Bold.ttf", 46)
DATE_F = load_font("DejaVuSans-Bold.ttf", 19)
SUB_F = load_font("DejaVuSans-Bold.ttf", 13)
SECTION_F = load_font("DejaVuSans-Bold.ttf", 12)
TAG_F = load_font("DejaVuSans-Bold.ttf", 11)
LEAD_HEAD_F = load_font("DejaVuSans-Bold.ttf", 16)
LEAD_SUM_F = load_font("DejaVuSans.ttf", 12)
GRID_HEAD_F = load_font("DejaVuSans-Bold.ttf", 12)
GRID_SUM_F = load_font("DejaVuSans.ttf", 11)
ONE_F = load_font("DejaVuSans.ttf", 10)
SMALL_F = load_font("DejaVuSans.ttf", 10)
SMALL_B_F = load_font("DejaVuSans-Bold.ttf", 10)
TINY_F = load_font("DejaVuSans.ttf", 9)
MAP_NUM_F = load_font("DejaVuSans-Bold.ttf", 10)

# --- story data: (number, region, headline, summary, source, accent, status) ---
LEADS = [
    (1, "WAR · MIDDLE EAST", "Houthis hit Saudi Arabia's biggest oil refinery",
     "Houthis say they struck the kingdom's largest refinery; oil jumps on supply fears.",
     "Reuters", "red", "CLAIM"),
    (2, "US · THANKSGIVING", "Macy's parade postponed — a first in 100 years",
     "The 100th parade moves to Saturday as a nor'easter bears down on New York.",
     "AP / Al Jazeera", "blue", "CONFIRMED"),
    (3, "ASIA", "Kim: North Korea should widen use of tactical nukes",
     "Kim inspects nuclear sites with his daughter and calls for diversified deployment.",
     "AP", "ink", "CONFIRMED"),
]

GRID = [
    (4, "DISASTER · CAIRO", "Cairo fuel tanker fire kills at least 30",
     "A fuel truck overturns on the ring road and bursts into flames; 25 hurt.",
     "SCMP", "red", "CONFIRMED"),
    (5, "JUSTICE · ISRAEL", "Judges urge dropping Netanyahu bribery case",
     "Judges say conviction unlikely; Netanyahu demands his trial end at once.",
     "AP", "blue", "CONFIRMED"),
    (6, "TECH · US", "US split over Alice Huang spying claims",
     "Officials divided on whether Huang was a Chinese spy; FBI finds no evidence.",
     "Reuters", "red", "CLAIM"),
    (7, "MARKETS · ASIA", "Asia shares bounce; Nikkei +1.6%, Kospi +1.9%",
     "Wall Street recoups most early losses; Nvidia ends -3.9% at $149.30.",
     "Reuters", "teal", "CONFIRMED"),
    (8, "ECONOMY · US", "US Q3 growth revised up to 4.3%",
     "Growth revised sharply higher; core inflation hits an uncomfortable 3.3%.",
     "Reuters", "gold", "CONFIRMED"),
    (9, "DISASTER · ASIA", "Indonesia mine search resumes; 13 dead, 13 trapped",
     "Rescuers return to an illegal gold mine in West Java after 13 deaths.",
     "Reuters", "red", "CONFIRMED"),
    (10, "US · LAW", "Second judge blocks Trump's birthright order",
     "Trump's newest order curtailing birthright citizenship is blocked again.",
     "Japan Times", "blue", "CONFIRMED"),
    (11, "EUROPE · UK", "UK to put EU deal to parliament for approval",
     "The British government will submit its EU deal for parliament's approval.",
     "AP", "blue", "CONFIRMED"),
    (12, "US · IOWA", "Iowa blast a 'tremendous success'; no airborne lead",
     "Army detonates 5 tons of lead azide; officials say zero airborne lead found.",
     "AP / ABC", "teal", "CONFIRMED"),
    (13, "SPACE · US", "SpaceX wins approval to launch space data centres",
     "US government approves SpaceX plan to put data centres in orbit.",
     "Japan Times", "ink", "CONFIRMED"),
    (14, "ASIA", "Hong Kong marks a year since the Tai Po fire",
     "A year on, Hong Kong remembers the 168 people killed in the fire.",
     "Japan Times", "gold", "CONFIRMED"),
    (15, "SPORT · EUROPE", "Champions League: Liverpool 3-0, Real Madrid 5-1",
     "Isak scores twice as Liverpool beat Brugge; Real hit five past PSV.",
     "BBC / Sky", "gold", "CONFIRMED"),
]

# one-liners: (number, region, text) — kept short to fit two lines per column
ONELINERS = [
    (16, "US", "US famine monitor to halt reporting as funding shortfall hits staff."),
    (17, "AF", "African insurgents take war to the skies with off-the-shelf drones."),
    (18, "EU", "Merz: 'Russia wants more than Ukraine' as he defends Kyiv aid."),
    (19, "AS", "Chinese firms pose growing competitive threat to Japanese firms, JETRO finds."),
    (20, "AS", "Uber names Rakesh Ranjan president for India and South Asia."),
    (21, "US", "Judge declines long-term ban on taxpayer-funded pro-Trump ads."),
    (22, "US", "US travellers face long airport lines, bad weather before Thanksgiving."),
    (23, "US", "King tides, high surf batter California coast."),
    (24, "US", "FedEx plane overruns Miami runway; airport briefly shut."),
    (25, "US", "Duran Duran guitarist Andy Taylor dies at 65."),
    (26, "AS", "Japan may designate secondary capitals in fall 2027."),
    (27, "US", "MLB sues players' union to block antitrust suit."),
    (28, "AS", "Mizuho extends banking push to India with Avendus deal."),
    (29, "AS", "JAXA unveils rover test model for India moon mission."),
    (30, "AS", "Japan's data centre boom faces revolt from residents."),
    (31, "US", "New US tariffs would likely lift US sugar prices."),
    (32, "AS", "Billions in data centre deals grind to halt after chip curbs."),
    (33, "US", "Vance's Thanksgiving F-bomb grabs attention online."),
    (34, "WORLD", "Gold eases to $3,566/oz, down ~8% in November."),
    (35, "WORLD", "OPEC+ to meet Nov 29 on 2027 output policy."),
    (36, "WORLD", "Brent $94.71, WTI $84.03 as oil rises on supply fears."),
    (37, "EU", "Denmark bans headscarves for prosecutors."),
    (38, "AS", "South Africa thrash Bangladesh by innings and 219 runs; Mulder 7/31."),
    (39, "AS", "India women's hockey climbs to world No.4 after beating Japan."),
    (40, "AS", "Nagaland United win Northeast derby, move second."),
    (41, "AS", "Rajasthan United crush Mohammedan SC 4-0."),
    (42, "AS", "Priyansh Arya shatters records in Syed Mushtaq Ali Trophy."),
    (43, "ME", "Gaza winter survival items out of reach for families in need."),
    (44, "EU", "UK to launch independent inquiry into nuclear testing impact on veterans."),
    (45, "AF", "Nigeria seizes $220M of meth, arrests 5 Mexican suspects."),
    (46, "AF", "Haftar makes first formal visit to Turkey."),
    (47, "AS", "Community cafeterias for kids in Japan hit record 13,800."),
    (48, "AS", "Japan to extend tax break for inherited home sales by four years."),
    (49, "ME", "Israel raids homes in south Syria, detains residents."),
    (50, "US", "New Jersey declares state of emergency ahead of storm."),
    (51, "WORLD", "S&P 500 futures +0.5%, Nasdaq +0.4% early Thursday."),
    (52, "WORLD", "Dollar index eases to 103.71; Swiss franc gains."),
]

# timeline: (hour_utc, label) — spaced so no two labels share a row nearby
TIMELINE = [
    (0.5, "Macy's postponed"), (2.0, "Oil jumps"),
    (3.5, "Cairo toll 30"), (5.5, "Asia bounce"),
    (7.5, "Kim sites"), (9.5, "UK EU deal"),
    (11.5, "Birthright blocked"), (13.5, "Iowa success"),
    (15.5, "SpaceX approval"), (18.0, "UCL 3-0"),
]

DATE_CHECK = [
    "Shenzhou 24 launches — 24 Nov (AP).",
    "Huawei guilty of trade-secret theft — 24 Nov (AP).",
    "Democrats clinch House majority of 259 — 25 Nov (AP).",
    "US announces tariffs on China, EU, 14 others — 25 Nov (AP).",
    "Samara refineries hit — 25 Nov (Kyiv Independent).",
    "EU unveils 50bn euro tech fund — 25 Nov (Reuters/FT).",
]

# map pins: (story number, lon, lat, badge_dx, badge_dy)
PINS = [(1, 50.1, 26.6, 0, -14), (2, -74, 40.7, -16, 12), (3, 127, 39, 0, -14),
        (4, 31.2, 30.0, 12, -12), (5, 35.2, 31.8, 14, 8), (6, -77, 38.9, 0, -14),
        (7, 139.7, 35.7, 0, 0), (8, -77, 38.9, 14, 10), (9, 107.6, -6.8, 0, 0),
        (10, -77, 38.9, -16, 8), (11, -0.1, 51.5, 0, -14), (12, -93.5, 41.6, 0, 0),
        (13, -80.6, 28.4, 0, 0), (14, 114.2, 22.3, 0, 0), (15, -3.0, 53.4, 0, -14)]

# Continents as "lon,lat" strings (one per landmass), parsed at draw time.
LAND = [
    "-168,66 -140,70 -125,72 -110,73 -95,80 -85,70 -75,62 -60,47 -70,42 "
    "-80,32 -85,25 -97,26 -105,20 -110,23 -125,40 -145,60 -165,60",
    "-80,10 -70,11 -60,5 -50,0 -40,-5 -35,-10 -40,-20 -48,-28 -58,-35 "
    "-65,-40 -70,-50 -73,-35 -75,-20 -80,-5",
    "-10,36 -5,43 0,50 5,58 10,57 18,56 23,60 30,70 35,68 40,60 30,50 "
    "28,45 20,40 12,44 3,42 -2,37 -9,38",
    "-17,15 -10,30 0,35 10,37 20,32 30,31 35,28 40,15 48,11 51,2 40,-5 "
    "35,-15 30,-25 20,-35 15,-30 12,-18 9,-1 8,4 -8,5 -15,11",
    "40,70 50,72 60,70 70,72 80,73 90,75 110,76 130,72 150,70 170,66 178,65 "
    "170,60 160,55 155,50 145,45 140,40 135,35 130,33 127,35 122,38 120,30 "
    "110,20 108,12 105,8 100,6 97,10 95,16 90,22 85,20 80,13 77,8 72,20 "
    "66,25 60,25 55,26 50,29 48,30 44,29 40,32 38,36 35,36 30,36 27,37 "
    "23,36 26,40 28,45 30,50 32,55 35,60 38,65",
    "113,-22 114,-30 115,-35 120,-34 129,-32 137,-35 140,-38 145,-38 150,-37 "
    "153,-32 153,-27 150,-22 146,-19 142,-11 137,-12 132,-12 126,-14 122,-17 "
    "118,-20",
]


def fit_text(draw, text, fnt, max_w):
    """Greedy word wrap to a pixel width; returns the lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def put_lines(draw, x, y, lines, fnt, fill, leading=None):
    step = leading if leading is not None else int(fnt.size * 1.25)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += step
    return y


def lead_artwork(draw, box, kind, accent_name):
    """Small programmatic illustration for a lead card."""
    accent = COLORS[accent_name]
    white = COLORS["white"]
    dark = COLORS["ink"]
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=accent)
    if kind == "refinery":
        # Oil refinery at night: distillation towers, flare stack, orange
        # flame burst over the plant.
        base = y1 - 12
        towers = [(x0 + 20, 30), (x0 + 58, 44), (x0 + 100, 34), (x0 + 142, 48),
                  (x0 + 186, 36), (x0 + 228, 42), (x0 + 268, 28)]
        for bx, bh in towers:
            draw.rectangle([bx, base - bh, bx + 26, base], fill=(52, 48, 44),
                           outline=dark, width=1)
            draw.rectangle([bx + 8, base - bh - 10, bx + 18, base - bh],
                           fill=(52, 48, 44), outline=dark, width=1)
            for wy in range(base - bh + 6, base - 4, 9):
                for wx in (bx + 5, bx + 15):
                    draw.rectangle([wx, wy, wx + 3, wy + 3], fill=(255, 200, 90))
        fx, fy = x0 + 292, y0 + 34
        for k in range(8):
            ang = k * 45 + 10
            ex = fx + int(26 * math.cos(math.radians(ang)))
            ey = fy + int(26 * math.sin(math.radians(ang)))
            draw.line([fx, fy, ex, ey], fill=(255, 190, 80), width=3)
        draw.ellipse([fx - 10, fy - 10, fx + 10, fy + 10], fill=(255, 210, 110),
                     outline=white, width=2)
        draw.line([x0, base, x1, base], fill=dark, width=2)
        draw.text((x0 + 10, y0 + 6), "RAS TANURA", font=TAG_F, fill=white)
        lab = "BRENT $94.71"
        tw = draw.textlength(lab, font=TAG_F)
        draw.text((x1 - 8 - tw, y1 - 20), lab, font=TAG_F, fill=white)
    elif kind == "balloon":
        # Thanksgiving parade balloon: a big round balloon on strings over
        # a crowd, against a storm-grey sky.
        cx = (x0 + x1) // 2
        sky = (70, 96, 130)
        draw.rectangle(box, fill=sky)
        draw.ellipse([cx - 52, y0 + 8, cx + 52, y0 + 62], fill=(255, 190, 60),
                     outline=white, width=2)
        draw.ellipse([cx - 40, y0 + 14, cx - 14, y0 + 32], fill=(255, 215, 120))
        for dx in (-30, -10, 10, 30):
            draw.line([cx + dx, y0 + 60, cx + dx // 2, y1 - 22],
                      fill=white, width=1)
        for i in range(9):
            px = x0 + 24 + i * 32
            draw.ellipse([px, y1 - 22, px + 10, y1 - 12], fill=(40, 44, 58))
        draw.text((x0 + 10, y0 + 6), "100TH PARADE", font=TAG_F, fill=white)
        lab = "TO SATURDAY"
        tw = draw.textlength(lab, font=TAG_F)
        draw.text((x1 - 8 - tw, y1 - 20), lab, font=TAG_F, fill=white)
    else:  # "missile": atom symbol — nucleus and three orbit rings
        cx = (x0 + x1) // 2 - 50
        cy = y0 + 48
        ring = (150, 170, 205)
        draw.ellipse([cx - 40, cy - 20, cx + 40, cy + 20], outline=ring, width=2)
        draw.ellipse([cx - 20, cy - 28, cx + 20, cy + 28], outline=ring, width=2)
        draw.line([cx - 34, cy + 24, cx + 34, cy - 24], fill=ring, width=2)
        draw.line([cx - 34, cy - 24, cx + 34, cy + 24], fill=ring, width=2)
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 90, 60),
                     outline=white, width=2)
        draw.text((x0 + 10, y0 + 6), "PYONGYANG", font=TAG_F, fill=white)
        lab = "TACTICAL NUKES"
        tw = draw.textlength(lab, font=TAG_F)
        draw.text((x1 - 8 - tw, y1 - 20), lab, font=TAG_F, fill=white)


def world_map(draw, x0, y0, x1, y1):
    red = COLORS["red"]
    white = COLORS["white"]

    def project(lon, lat):
        fx = (lon + 170.0) / 360.0
        fy = (85.0 - lat) / 145.0
        return (x0 + int(fx * (x1 - x0)), y0 + int(fy * (y1 - y0)))

    for landmass in LAND:
        pts = []
        for pair in landmass.split():
            lon, lat = pair.split(",")
            pts.append(project(float(lon), float(lat)))
        draw.polygon(pts, fill=COLORS["mapfill"], outline=COLORS["mapline"])
    for num, lon, lat, dx, dy in PINS:
        cx, cy = project(lon, lat)
        bx, by = cx + dx, cy + dy
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=red)
        if dx or dy:
            draw.line([cx, cy, bx, by], fill=red, width=1)
        draw.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=red,
                     outline=white, width=1)
        label = str(num)
        tw = draw.textlength(label, font=MAP_NUM_F)
        draw.text((bx - tw / 2, by - 7), label, font=MAP_NUM_F, fill=white)
    draw.text((x0, y1 - 12), "SCHEMATIC — NOT TO SCALE", font=TINY_F,
              fill=COLORS["muted"])


def masthead(d):
    ink = COLORS["ink"]
    red = COLORS["red"]
    muted = COLORS["muted"]
    d.rectangle([0, 0, SIZE[0], 6], fill=red)
    d.text((16, 14), "THE WORLD TODAY", font=TITLE_F, fill=ink)
    for i, line in enumerate(["THURSDAY", "26 NOVEMBER 2026"]):
        tw = d.textlength(line, font=DATE_F)
        d.text((SIZE[0] - 16 - tw, 16 + i * 24), line, font=DATE_F,
               fill=red if i == 0 else ink)
    d.text((16, 66), "52 STORIES  ·  5 REGIONS  ·  ONE PAGE  —  THURSDAY 26 NOVEMBER 2026",
           font=SUB_F, fill=muted)
    d.line([16, 88, SIZE[0] - 16, 88], fill=ink, width=2)


def lead_cards(d):
    kinds = ["refinery", "balloon", "missile"]
    top, height, width, gap = 96, 184, 322, 8
    card = COLORS["card"]
    line = COLORS["line"]
    ink = COLORS["ink"]
    muted = COLORS["muted"]
    for i, (num, region, head, summ, src, accent_name, status) in enumerate(LEADS):
        accent = COLORS[accent_name]
        x0 = 16 + i * (width + gap)
        x1 = x0 + width
        d.rectangle([x0, top, x1, top + height], fill=card, outline=line, width=1)
        lead_artwork(d, (x0 + 1, top + 1, x1 - 1, top + 80), kinds[i], accent_name)
        y = top + 86
        d.text((x0 + 10, y), f"{num} · {region}", font=TAG_F, fill=accent)
        y += 16
        y = put_lines(d, x0 + 10, y, fit_text(d, head, LEAD_HEAD_F, width - 20)[:2],
                      LEAD_HEAD_F, ink, leading=19)
        y += 3
        y = put_lines(d, x0 + 10, y, fit_text(d, summ, LEAD_SUM_F, width - 20)[:2],
                      LEAD_SUM_F, ink, leading=15)
        d.text((x0 + 10, y + 2), f"Source: {src} · {status}", font=TINY_F, fill=muted)


def grid_cards(d):
    top, height, width, gap = 288, 96, 242, 8
    card = COLORS["card"]
    line = COLORS["line"]
    ink = COLORS["ink"]
    white = COLORS["white"]
    for row in range(3):
        for col in range(4):
            num, region, head, summ, src, accent_name, status = GRID[row * 4 + col]
            accent = COLORS[accent_name]
            x0 = 16 + col * (width + gap)
            x1 = x0 + width
            y0 = top + row * (height + 6)
            d.rectangle([x0, y0, x1, y0 + height], fill=card, outline=line, width=1)
            d.ellipse([x0 + 8, y0 + 7, x0 + 26, y0 + 25], fill=accent)
            label = str(num)
            tw = d.textlength(label, font=SMALL_B_F)
            d.text((x0 + 17 - tw / 2, y0 + 10), label, font=SMALL_B_F, fill=white)
            d.text((x0 + 32, y0 + 9), region, font=TAG_F, fill=accent)
            y = put_lines(d, x0 + 8, y0 + 28,
                          fit_text(d, head, GRID_HEAD_F, width - 16)[:2],
                          GRID_HEAD_F, ink, leading=13)
            y = put_lines(d, x0 + 8, y + 2,
                          fit_text(d, summ, GRID_SUM_F, width - 16)[:2],
                          GRID_SUM_F, ink, leading=12)
            d.text((x0 + 8, y + 1), f"{src} · {status}", font=TINY_F,
                   fill=COLORS["muted"])


def timeline_strip(d):
    top, bottom = 596, 656
    ink = COLORS["ink"]
    red = COLORS["red"]
    muted = COLORS["muted"]
    d.rectangle([16, top, SIZE[0] - 16, bottom], fill=COLORS["card"],
                outline=COLORS["line"], width=1)
    base = top + 32
    d.line([24, base, SIZE[0] - 24, base], fill=ink, width=1)
    for h in range(0, 25, 4):
        x = 24 + int(h / 24.0 * (SIZE[0] - 48))
        d.line([x, base - 3, x, base + 3], fill=ink, width=1)
        lab = f"{h:02d}:00" + (" UTC" if h == 24 else "")
        tw = d.textlength(lab, font=TINY_F)
        lx = min(max(x - tw / 2, 24), SIZE[0] - 24 - tw)
        d.text((lx, base + 6), lab, font=TINY_F, fill=muted)
    levels = {"near": base - 13, "below": base + 18, "far": base - 25}
    order = ["near", "below", "far"]
    for i, (hour, lab) in enumerate(TIMELINE):
        x = 24 + int(hour / 24.0 * (SIZE[0] - 48))
        d.ellipse([x - 3, base - 3, x + 3, base + 3], fill=red)
        tw = d.textlength(lab, font=TINY_F)
        lx = min(max(x - tw / 2, 24), SIZE[0] - 24 - tw)
        d.text((lx, levels[order[i % 3]]), lab, font=TINY_F, fill=ink)


def oneliner_columns(d):
    top = 664
    ink = COLORS["ink"]
    d.text((16, top), "THE REST OF THE DAY — 37 MORE STORIES", font=SECTION_F, fill=ink)
    d.line([16, top + 17, 690, top + 17], fill=ink, width=1)
    col_w, col_gap = 219, 7
    groups = [ONELINERS[0:13], ONELINERS[13:25], ONELINERS[25:37]]
    for ci, group in enumerate(groups):
        cx = 16 + ci * (col_w + col_gap)
        y = top + 24
        for num, region, text in group:
            first = f"{num}. [{region}] " + text
            y = put_lines(d, cx, y, fit_text(d, first, ONE_F, col_w)[:2],
                          ONE_F, ink, leading=11)
            y += 2


def map_panel(d):
    mx0, my0, mx1, my1 = 698, 664, 1008, 836
    ink = COLORS["ink"]
    d.text((mx0, my0), "WHERE IT HAPPENED — STORIES 1–15", font=SECTION_F, fill=ink)
    d.rectangle([mx0, my0 + 20, mx1, my1], fill=COLORS["card"],
                outline=COLORS["line"], width=1)
    world_map(d, mx0 + 4, my0 + 24, mx1 - 4, my1 - 4)


def date_check_panel(d):
    mx0, mx1 = 698, 1008
    top = 846
    red = COLORS["red"]
    ink = COLORS["ink"]
    d.text((mx0, top), "DATE CHECK — OLDER STORIES WE LEFT OUT", font=SECTION_F, fill=red)
    d.line([mx0, top + 17, mx1, top + 17], fill=red, width=1)
    y = top + 24
    for item in DATE_CHECK:
        y = put_lines(d, mx0, y, fit_text(d, "· " + item, SMALL_F, mx1 - mx0),
                      SMALL_F, ink, leading=12)
        y += 3
    y += 4
    put_lines(d, mx0, y,
              fit_text(d, "Everything above is 26 November 2026 news.",
                       SMALL_F, mx1 - mx0),
              SMALL_F, ink, leading=12)


def footer(d):
    muted = COLORS["muted"]
    d.line([16, 1008, SIZE[0] - 16, 1008], fill=COLORS["line"], width=1)
    d.text((16, 1012),
           "CLAIM = an unverified claim, attributed to its source.  Sources: Reuters · AP · "
           "SCMP · Japan Times · Al Jazeera · Economic Times · BBC · Sky Sports.",
           font=TINY_F, fill=muted)


def build_poster():
    img = Image.new("RGB", SIZE, COLORS["paper"])
    d = ImageDraw.Draw(img)
    masthead(d)
    lead_cards(d)
    grid_cards(d)
    timeline_strip(d)
    oneliner_columns(d)
    map_panel(d)
    date_check_panel(d)
    footer(d)
    return img


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    build_poster().save(out, "PNG", optimize=True)
    print("wrote", out)
