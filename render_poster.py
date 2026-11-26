#!/usr/bin/env python3
"""Render THE WORLD TODAY — the 26 November 2026 world-news poster.

One 1024x1024 image: masthead, three illustrated lead stories, twelve
numbered grid cards, a UTC timeline strip, 37 one-line stories, a numbered
schematic world map, a DATE CHECK box and a footer. All story wording comes
from the day's ledger (stories.md); nothing is fetched from the network.
Pillow + DejaVu only. Output is deterministic: same input, same PNG bytes.
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

CREAM = (248, 244, 232)
INK = (20, 18, 16)
RED = (166, 30, 30)
BLUE = (47, 74, 107)
GOLD = (138, 109, 0)
GREEN = (46, 125, 50)
GRAY = (110, 100, 88)
CARD_BORDER = (185, 178, 164)
LAND = (216, 210, 192)
WHITE = (255, 255, 255)

SERIF_BOLD = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_BOLD = "DejaVuSans-Bold.ttf"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(text, fnt, width):
    """Greedy word wrap measured with the real font; returns a line list."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill, leading):
    """Draw lines top-to-bottom; returns the y just below the last line."""
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- data
LEADS = [
    {
        "tag": "1 \u00b7 WAR \u00b7 MIDDLE EAST",
        "color": RED,
        "headline": "Houthis hit Saudi Arabia's biggest oil refinery",
        "summary": ("Houthis say they struck the kingdom's largest refinery; "
                    "oil jumps as supply fears spread. Brent $94.71."),
        "source": "Source: Reuters \u00b7 CLAIM",
        "banner": "refinery",
        "corner_tl": "RAS TANURA",
        "corner_br": "BRENT $94.71",
    },
    {
        "tag": "2 \u00b7 US \u00b7 THANKSGIVING",
        "color": BLUE,
        "headline": "Macy's parade postponed \u2014 a first in 100 years",
        "summary": ("The 100th parade moves to Saturday as a nor'easter bears "
                    "down on New York; 80 million people travelling for the "
                    "holiday."),
        "source": "Source: AP / Al Jazeera / Malay Mail \u00b7 CONFIRMED",
        "banner": "parade",
        "corner_tl": "100TH PARADE",
        "corner_br": "TO SATURDAY",
    },
    {
        "tag": "3 \u00b7 ASIA",
        "color": INK,
        "headline": "Kim: North Korea should widen use of tactical nukes",
        "summary": ("Kim Jong Un inspects nuclear sites with his daughter and "
                    "calls for diversified deployment of tactical nuclear "
                    "weapons."),
        "source": "Source: AP / Manila Times \u00b7 CONFIRMED",
        "banner": "atom",
        "corner_tl": "PYONGYANG",
        "corner_br": "TACTICAL NUKES",
    },
]

CARDS = [
    {"n": 4, "tag": "DISASTER \u00b7 CAIRO", "color": RED,
     "headline": "Cairo fuel tanker fire kills at least 30",
     "summary": ("A fuel truck overturns on Cairo's ring road and bursts into "
                "flames; 27 vehicles charred, 25 hurt."),
     "source": "SCMP / Economic Times \u00b7 CONFIRMED"},
    {"n": 5, "tag": "JUSTICE \u00b7 ISRAEL", "color": BLUE,
     "headline": "Judges urge dropping Netanyahu bribery case",
     "summary": ("Israeli judges recommend prosecutors drop the most serious "
                "of three corruption cases; Netanyahu demands the trial end."),
     "source": "AP \u00b7 CONFIRMED"},
    {"n": 6, "tag": "TECH \u00b7 US", "color": RED,
     "headline": "US split over Alice Huang spying claims",
     "summary": ("Officials divided on whether Nvidia CEO's affair partner was "
                "a Chinese spy; FBI finds no evidence she was an asset."),
     "source": "Reuters \u00b7 CLAIM"},
    {"n": 7, "tag": "MARKETS \u00b7 ASIA", "color": BLUE,
     "headline": "Asia shares bounce; Nikkei +1.6%, Kospi +1.9%",
     "summary": ("Wall Street recoups most early losses; Nvidia ends -3.9% at "
                "$149.30, $2.3T below its October peak."),
     "source": "Reuters \u00b7 CONFIRMED"},
    {"n": 8, "tag": "ECONOMY \u00b7 US", "color": GOLD,
     "headline": "US Q3 growth revised up to 4.3%",
     "summary": ("US economic growth revised sharply higher; core inflation "
                "hits an uncomfortable 3.3%."),
     "source": "Reuters \u00b7 CONFIRMED"},
    {"n": 9, "tag": "DISASTER \u00b7 ASIA", "color": RED,
     "headline": "Indonesia mine search resumes; 13 dead, 13 trapped",
     "summary": ("Rescuers return to an illegal gold mine in West Java after 13 "
                "workers are confirmed dead."),
     "source": "Reuters \u00b7 CONFIRMED"},
    {"n": 10, "tag": "US \u00b7 LAW", "color": BLUE,
     "headline": "Second judge blocks Trump's birthright order",
     "summary": ("Trump's newest order curtailing birthright citizenship is "
                "blocked by a second judge."),
     "source": "Japan Times \u00b7 CONFIRMED"},
    {"n": 11, "tag": "EUROPE \u00b7 UK", "color": BLUE,
     "headline": "UK to put EU deal to parliament for approval",
     "summary": ("The British government will submit its EU deal for "
                "parliament's approval."),
     "source": "AP / Manila Times \u00b7 CONFIRMED"},
    {"n": 12, "tag": "US \u00b7 IOWA", "color": GREEN,
     "headline": "Iowa blast a 'tremendous success'; no airborne lead",
     "summary": ("Army detonates 5 tons of lead azide; federal officials say "
                "zero airborne lead detected."),
     "source": "AP / ABC \u00b7 CONFIRMED"},
    {"n": 13, "tag": "SPACE \u00b7 US", "color": INK,
     "headline": "SpaceX wins approval to launch space data centres",
     "summary": ("US government approves SpaceX plan to launch data centres "
                "in orbit."),
     "source": "Japan Times \u00b7 CONFIRMED"},
    {"n": 14, "tag": "ASIA", "color": GOLD,
     "headline": "Hong Kong marks a year since the Tai Po fire",
     "summary": ("A year on, Hong Kong remembers the 168 people killed in the "
                "housing complex fire."),
     "source": "Japan Times \u00b7 CONFIRMED"},
    {"n": 15, "tag": "SPORT \u00b7 EUROPE", "color": GOLD,
     "headline": "Champions League: Liverpool 3-0, Real Madrid 5-1",
     "summary": ("Isak scores twice as Liverpool beat Brugge; Real Madrid hit "
                "five past PSV; Man City 2-2 Napoli."),
     "source": "BBC / Sky Sports \u00b7 CONFIRMED"},
]

ONELINERS = [
    "16. [US] US famine monitor to halt reporting as funding shortfall hits staff.",
    "17. [AF] African insurgents take war to the skies with off-the-shelf drones.",
    "18. [EU] Merz: 'Russia wants more than Ukraine' as he defends Kyiv aid.",
    "19. [AS] Chinese firms pose growing competitive threat to Japanese firms, JETRO finds.",
    "20. [AS] Uber names Rakesh Ranjan president for India and South Asia.",
    "21. [US] Judge declines long-term ban on taxpayer-funded pro-Trump ads.",
    "22. [US] US travellers face long airport lines, bad weather before Thanksgiving.",
    "23. [US] King tides, high surf batter California coast.",
    "24. [US] FedEx plane overruns Miami runway; airport briefly shut.",
    "25. [US] Duran Duran guitarist Andy Taylor dies at 65.",
    "26. [AS] Japan may designate secondary capitals in fall 2027.",
    "27. [US] MLB sues players' union to block antitrust suit.",
    "28. [AS] Mizuho extends banking push to India with Avendus deal.",
    "29. [AS] JAXA unveils rover test model for India moon mission.",
    "30. [AS] Japan's data centre boom faces revolt from residents.",
    "31. [US] New US tariffs would likely lift US sugar prices.",
    "32. [AS] Billions in data centre deals grind to halt after chip curbs.",
    "33. [US] Vance's Thanksgiving F-bomb grabs attention online.",
    "34. [WORLD] Gold eases to $3,566/oz, down ~8% in November.",
    "35. [WORLD] OPEC+ to meet Nov 29 on 2027 output policy.",
    "36. [WORLD] Brent $94.71, WTI $84.03 as oil rises on supply fears.",
    "37. [EU] Denmark bans headscarves for prosecutors.",
    "38. [AS] South Africa thrash Bangladesh by innings and 219 runs; Mulder 7/31.",
    "39. [AS] India women's hockey climbs to world No.4 after beating Japan.",
    "40. [AS] Nagaland United win Northeast derby, move second.",
    "41. [AS] Rajasthan United crush Mohammedan SC 4-0.",
    "42. [AS] Priyansh Arya shatters records in Syed Mushtaq Ali Trophy.",
    "43. [ME] Gaza winter survival items out of reach for families in need.",
    "44. [EU] UK to launch independent inquiry into nuclear testing impact on veterans.",
    "45. [AF] Nigeria seizes $220M of meth, arrests 5 Mexican suspects.",
    "46. [AF] Haftar makes first formal visit to Turkey.",
    "47. [AS] Community cafeterias for kids in Japan hit record 13,800.",
    "48. [AS] Japan to extend tax break for inherited home sales by four years.",
    "49. [ME] Israel raids homes in south Syria, detains residents.",
    "50. [US] New Jersey declares state of emergency ahead of storm.",
    "51. [WORLD] S&P 500 futures +0.5%, Nasdaq +0.4% early Thursday.",
    "52. [WORLD] Dollar index eases to 103.71; Swiss franc gains.",
]

# (minutes after 00:00 UTC, label, label above the line?)
TIMELINE = [
    (30, "Macy's postponed", True),
    (97, "Oil jumps", False),
    (188, "Cairo toll 30", True),
    (240, "Asia bounce", False),
    (360, "Kim sites", True),
    (480, "UK EU deal", False),
    (600, "Birthright blocked", True),
    (720, "Iowa success", False),
    (840, "SpaceX approval", True),
    (960, "Travel chaos", False),
    (1080, "UCL 3-0", True),
]

DATECHECK = [
    "Shenzhou 24 launches \u2014 24 Nov (AP).",
    "Huawei guilty of trade-secret theft \u2014 24 Nov (AP).",
    "Solomon Islands names Australia top partner \u2014 24 Nov (AP).",
    "Unclassified CIA system breached \u2014 24 Nov (AP).",
    "Democrats clinch House majority of 259 \u2014 25 Nov (AP).",
    "US announces tariffs on China, EU, 14 others \u2014 25 Nov (AP).",
    "Samara refineries hit \u2014 25 Nov (Kyiv Independent).",
    "EU unveils 50bn euro tech fund \u2014 25 Nov (Reuters/FT).",
    "Poland asks NATO to down Russian missiles \u2014 25 Nov.",
    "Shein agrees $100M FTC settlement \u2014 25 Nov (AP).",
]

# Schematic continents, local coords inside the 332x90 map box.
CONTINENTS = [
    [(16, 20), (44, 10), (76, 14), (88, 24), (82, 36), (64, 42),
     (50, 52), (32, 48), (14, 36)],                       # N. America
    [(88, 8), (100, 6), (104, 14), (92, 16)],            # Greenland
    [(64, 52), (80, 50), (92, 60), (88, 78), (74, 84), (62, 66)],  # S. America
    [(158, 16), (176, 10), (192, 18), (188, 30), (172, 36), (156, 30)],  # Europe
    [(160, 42), (182, 40), (196, 52), (190, 72), (172, 82),
     (158, 66), (152, 52)],                               # Africa
    [(196, 14), (238, 8), (288, 12), (310, 22), (302, 38), (274, 46),
     (252, 42), (230, 52), (210, 40), (196, 28)],        # Asia
    [(256, 54), (266, 52), (268, 60), (258, 62)],        # SE Asia islands
    [(272, 56), (282, 54), (284, 62), (274, 64)],
    [(282, 66), (306, 64), (312, 74), (296, 80), (282, 76)],  # Australia
]
# Story number -> (x, y) on the schematic map.
MARKERS = {
    1: (224, 40), 2: (86, 26), 3: (292, 22), 4: (192, 46), 5: (206, 40),
    6: (22, 32), 7: (306, 34), 8: (68, 22), 9: (264, 60), 10: (94, 40),
    11: (168, 14), 12: (52, 38), 13: (40, 52), 14: (272, 44), 15: (156, 30),
}


# ---------------------------------------------------------------- banners
def draw_refinery(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(158, 27, 27))
    # Sun with rays, top right.
    cx, cy, r = x + w - 42, y + 22, 13
    for k in range(8):
        a = math.pi * k / 4
        x1 = cx + int((r + 2) * math.cos(a))
        y1 = cy + int((r + 2) * math.sin(a))
        x2 = cx + int((r + 8) * math.cos(a))
        y2 = cy + int((r + 8) * math.sin(a))
        draw.line([x1, y1, x2, y2], fill=(250, 204, 21), width=2)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 204, 21))
    # Refinery skyline: black towers with lit windows.
    base = y + h
    towers = [(0, 26, 34), (30, 20, 52), (54, 30, 44), (88, 18, 58),
              (110, 26, 38), (140, 22, 50), (166, 28, 42), (198, 20, 56),
              (222, 26, 40), (252, 22, 48), (278, 24, 36)]
    for tx, tw, th in towers:
        draw.rectangle([x + tx, base - th, x + tx + tw, base], fill=(24, 20, 18))
        for wy in range(base - th + 5, base - 4, 9):
            for wx in range(x + tx + 4, x + tx + tw - 3, 8):
                draw.rectangle([wx, wy, wx + 3, wy + 4], fill=(250, 204, 21))


def draw_parade(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=BLUE)
    # Big yellow parade balloon with a highlight.
    draw.ellipse([x + 78, y + 8, x + 250, y + 62], fill=(250, 204, 21))
    draw.ellipse([x + 100, y + 16, x + 170, y + 38], fill=(253, 224, 71))
    # Strings down to the handlers, drawn as small dark dots.
    for dx in range(0, 6):
        sx = x + 96 + dx * 26
        draw.line([sx, y + 60, sx - 6 + dx * 2, y + 74], fill=(20, 30, 45),
                  width=1)
        draw.ellipse([sx - 9, y + 71, sx - 3, y + 77], fill=(20, 30, 45))


def draw_atom(img, x, y, w, h):
    draw = ImageDraw.Draw(img)
    draw.rectangle([x, y, x + w, y + h], fill=(20, 20, 20))
    cx, cy = x + w // 2, y + h // 2
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.ellipse([w // 2 - 52, h // 2 - 16, w // 2 + 52, h // 2 + 16],
               outline=(170, 185, 205, 255), width=2)
    ld.ellipse([w // 2 - 13, h // 2 - 34, w // 2 + 13, h // 2 + 34],
               outline=(170, 185, 205, 255), width=2)
    diag = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dd = ImageDraw.Draw(diag)
    dd.ellipse([w // 2 - 52, h // 2 - 16, w // 2 + 52, h // 2 + 16],
               outline=(170, 185, 205, 255), width=2)
    diag = diag.rotate(45, resample=Image.BICUBIC, center=(w // 2, h // 2))
    layer = Image.alpha_composite(layer, diag)
    img.paste(layer, (x, y), layer)
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED)


# ---------------------------------------------------------------- sections
def draw_masthead(draw):
    draw.rectangle([0, 0, W, 6], fill=RED)
    draw.text((12, 8), "THE WORLD TODAY", font=font(SERIF_BOLD, 58), fill=INK)
    draw.text((1012, 12), "THURSDAY", font=font(SANS_BOLD, 19),
              fill=RED, anchor="ra")
    draw.text((1012, 36), "26 NOVEMBER 2026", font=font(SANS_BOLD, 19),
              fill=INK, anchor="ra")
    draw.text((12, 80), "52 STORIES \u00b7 5 REGIONS \u00b7 ONE PAGE \u2014 "
              "THURSDAY 26 NOVEMBER 2026", font=font(SANS_BOLD, 12),
              fill=GRAY)
    draw.rectangle([12, 92, 1012, 94], fill=INK)


def draw_leads(img, draw):
    xs = [12, 353, 694]
    w, y0 = 318, 100
    banner_h = 80
    for lead, x in zip(LEADS, xs):
        if lead["banner"] == "atom":
            draw_atom(img, x, y0, w, banner_h)
        elif lead["banner"] == "parade":
            draw_parade(draw, x, y0, w, banner_h)
        else:
            draw_refinery(draw, x, y0, w, banner_h)
        small = font(SANS_BOLD, 11)
        draw.text((x + 8, y0 + 6), lead["corner_tl"], font=small, fill=WHITE)
        # Bottom-right corner label on a dark chip so it stays readable
        # over the illustration (towers, balloon strings, atom orbits).
        br_w = small.getlength(lead["corner_br"])
        bx0, by0 = x + w - 8 - br_w - 6, y0 + banner_h - 19
        draw.rectangle([bx0, by0, x + w - 4, y0 + banner_h - 4],
                       fill=(20, 20, 20))
        draw.text((x + w - 8, y0 + banner_h - 18), lead["corner_br"],
                  font=small, fill=WHITE, anchor="ra")
        y = y0 + banner_h + 6
        draw.text((x, y), lead["tag"], font=font(SANS_BOLD, 12),
                  fill=lead["color"])
        y += 16
        y = text_block(draw, x, y,
                       wrap(lead["headline"], font(SANS_BOLD, 18), w),
                       font(SANS_BOLD, 18), INK, 22)
        y += 3
        y = text_block(draw, x, y, wrap(lead["summary"], font(SANS, 11), w),
                       font(SANS, 11), INK, 13)
        y += 4
        draw.text((x, y), lead["source"], font=font(SANS, 9), fill=GRAY)


def card_text_sizes():
    """Pick the largest headline/summary sizes whose cards all fit."""
    for hs, ss in [(13, 10), (12, 10), (12, 9)]:
        hf, sf = font(SANS_BOLD, hs), font(SANS, ss)
        ok = True
        for card in CARDS:
            hl = wrap(card["headline"], hf, 231)
            sl = wrap(card["summary"], sf, 231)
            used = 30 + len(hl) * (hs + 3) + 2 + len(sl) * (ss + 2) + 3 + 10
            if used > 106:
                ok = False
                break
        if ok:
            return hs, ss
    return 12, 9


def draw_grid(draw):
    hs, ss = card_text_sizes()
    hf, sf = font(SANS_BOLD, hs), font(SANS, ss)
    gx = [12, 264, 516, 768]
    gy = [302, 412, 522]
    cw, ch = 247, 108
    for row_i, y in enumerate(gy):
        for col_i, x in enumerate(gx):
            card = CARDS[row_i * 4 + col_i]
            draw.rectangle([x, y, x + cw, y + ch], fill=WHITE,
                           outline=CARD_BORDER, width=1)
            cx, cy = x + 17, y + 17
            draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=card["color"])
            draw.text((cx, cy), str(card["n"]), font=font(SANS_BOLD, 11),
                      fill=WHITE, anchor="mm")
            draw.text((x + 30, y + 9), card["tag"], font=font(SANS_BOLD, 11),
                      fill=card["color"])
            yy = text_block(draw, x + 8, y + 30,
                            wrap(card["headline"], hf, 231), hf, INK, hs + 3)
            yy += 2
            yy = text_block(draw, x + 8, yy, wrap(card["summary"], sf, 231),
                            sf, INK, ss + 2)
            draw.text((x + 8, yy + 3), card["source"], font=font(SANS, 9),
                      fill=GRAY)


def draw_timeline(draw):
    x0, x1, y0, y1 = 12, 1012, 638, 692
    draw.rectangle([x0, y0, x1, y1], fill=WHITE, outline=CARD_BORDER, width=1)
    axis_y = 664
    draw.line([x0 + 12, axis_y, x1 - 12, axis_y], fill=(120, 112, 96), width=1)
    hour_f = font(SANS, 9)
    for hr in range(0, 25, 4):
        tx = x0 + 12 + hr / 24 * (x1 - x0 - 24)
        draw.line([tx, axis_y - 3, tx, axis_y + 3], fill=(120, 112, 96), width=1)
        label = "24:00 UTC" if hr == 24 else "%02d:00" % hr
        draw.text((tx, 680), label, font=hour_f, fill=GRAY, anchor="ma")
    ev_f = font(SANS, 9)
    for minutes, label, above in TIMELINE:
        ex = x0 + 12 + minutes / 1440 * (x1 - x0 - 24)
        draw.ellipse([ex - 4, axis_y - 4, ex + 4, axis_y + 4], fill=RED)
        lx = min(max(ex, x0 + 52), x1 - 52)
        ly = 646 if above else 670
        draw.text((lx, ly), label, font=ev_f, fill=INK, anchor="ma")


def oneliner_size():
    """Largest one-liner font whose tallest column fits the bottom area."""
    cols = [ONELINERS[0:13], ONELINERS[13:25], ONELINERS[25:37]]
    for size in [10, 9.5, 9, 8.5, 8]:
        fnt = font(SANS, size)
        tallest = 0
        for col in cols:
            total = 0
            for item in col:
                total += len(wrap(item, fnt, 212)) * (size + 2) + 2
            tallest = max(tallest, total)
        if tallest <= 276:
            return size
    return 8


def draw_bottom(img, draw):
    draw.text((12, 700), "THE REST OF THE DAY \u2014 37 MORE STORIES",
              font=font(SANS_BOLD, 13), fill=INK)
    draw.text((680, 700), "WHERE IT HAPPENED \u2014 STORIES 1\u201315",
              font=font(SANS_BOLD, 13), fill=INK)
    draw.line([12, 716, 668, 716], fill=INK, width=1)
    draw.line([680, 716, 1012, 716], fill=INK, width=1)
    # One-liners: three columns on the left.
    size = oneliner_size()
    fnt = font(SANS, size)
    cols = [ONELINERS[0:13], ONELINERS[13:25], ONELINERS[25:37]]
    for col, x in zip(cols, [12, 234, 456]):
        y = 722
        for item in col:
            y = text_block(draw, x, y, wrap(item, fnt, 212), fnt, INK,
                           size + 2)
            y += 2
    # Schematic world map, right.
    mx, my = 680, 722
    draw.rectangle([mx, my, 1012, 812], fill=WHITE, outline=CARD_BORDER,
                   width=1)
    for poly in CONTINENTS:
        draw.polygon([(mx + px, my + py) for px, py in poly], fill=LAND)
    for n in range(1, 16):
        px, py = MARKERS[n]
        cx, cy = mx + px, my + py
        draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED)
        nf = font(SANS_BOLD, 8 if n >= 10 else 9)
        draw.text((cx, cy), str(n), font=nf, fill=WHITE, anchor="mm")
    draw.text((846, 816), "SCHEMATIC \u2014 NOT TO SCALE",
              font=font(SANS, 9), fill=GRAY, anchor="ma")
    # DATE CHECK box.
    draw.text((680, 836), "DATE CHECK \u2014 OLDER STORIES WE LEFT OUT",
              font=font(SANS_BOLD, 12), fill=RED)
    draw.line([680, 852, 1012, 852], fill=RED, width=1)
    y = 858
    df = font(SANS, 9)
    for item in DATECHECK:
        y = text_block(draw, 680, y, wrap("\u00b7 " + item, df, 332), df,
                       INK, 11)
    draw.text((680, y + 4), "Everything above is 26 November 2026 news.",
              font=font(SANS, 9), fill=GRAY)


def draw_footer(draw):
    draw.line([12, 1004, 1012, 1004], fill=INK, width=1)
    draw.text((12, 1009),
              "CLAIM = an unverified claim, attributed to its source.   "
              "Sources: Reuters \u00b7 AP \u00b7 SCMP \u00b7 Japan Times \u00b7 "
              "Al Jazeera \u00b7 Economic Times \u00b7 BBC \u00b7 Sky Sports.",
              font=font(SANS, 9), fill=GRAY)


def main():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_leads(img, draw)
    draw_grid(draw)
    draw_timeline(draw)
    draw_bottom(img, draw)
    draw_footer(draw)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG")
    data = open(out, "rb").read()
    print("entry.png sha256: %s (%d bytes)"
          % (hashlib.sha256(data).hexdigest(), len(data)))


if __name__ == "__main__":
    main()
