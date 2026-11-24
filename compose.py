#!/usr/bin/env python3
"""THE MILLSTREAM - NI24 entry renderer (Final 6, @agusproblem).
Front page for Tuesday 24 November 2026, drawn from the locked pool
(ni24-pool.md + 07:00 refresh). All drawing is original, in code, with
Pillow; the submitted program (main.py) only copies the finished PNG.
Usage: python3 compose.py A|B   ->  entry-A.png / entry-B.png
Variant A: lead #1 scene left, text right.  Variant B: lead #1 scene band on top.
Layout B: 1 lead full width + 2 leads + 10 minis (5x2) + ALSO ON left & map right.
"""
import sys, math, re, os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 24
CW = W - 2 * M

# ---- palette: moss / olive "millstream" ----
PAPER   = (243, 238, 225)
CREAM   = (251, 248, 239)
INK     = (35, 43, 30)
MOSS    = (70, 84, 58)
DMOSS   = (44, 54, 36)
OLIVE   = (107, 122, 78)
SAGE    = (168, 176, 138)
SAGE_L  = (203, 210, 178)
RUST    = (140, 47, 38)
RUST_L  = (178, 84, 66)
GOLD    = (185, 144, 47)
GOLD_L  = (222, 190, 110)
SKY     = (214, 224, 205)
SEA     = (96, 128, 112)
NAVY    = (52, 74, 84)
RULE    = (70, 84, 58)
FAINT   = (122, 128, 104)

FDIR = "/usr/share/fonts/truetype"
def font(path, size):
    return ImageFont.truetype(path, size)
F_BLACK  = lambda s: font(FDIR + "/noto/NotoSerifDisplay-Black.ttf", s)
F_SERIF  = lambda s: font(FDIR + "/noto/NotoSerif-Bold.ttf", s)
F_SERIFI = lambda s: font(FDIR + "/noto/NotoSerif-Italic.ttf", s)
F_SERIFR = lambda s: font(FDIR + "/noto/NotoSerif-Regular.ttf", s)
F_BOLD   = lambda s: font(FDIR + "/dejavu/DejaVuSans-Bold.ttf", s)
F_SANS   = lambda s: font(FDIR + "/dejavu/DejaVuSans.ttf", s)
# short font aliases used inside lead()/mini()
fb  = F_SERIF    # headline
fr  = F_SERIFR   # deck
fsr = F_SANS     # brief

# ---- grid: (num, region, topic, source, headline, deck, scene kind) ----
grid = [
 (1, "AMERICAS", "FBI PROBE", "AP",
  "FBI probes hack of its crime database",
  "Washington State pauses van-dealer checks while the breach is assessed. The FBI's crime database was hit; the bureau has not named a suspect.",
  "fbi"),
 (2, "WORLD", "UN AI WEAPONS", "salonvision",
  "UN states agree to keep talking on lethal AI weapons",
  "UN AI weapons talks continue; no ban was agreed. States chose negotiation over a deadline at 00:02 UTC on Monday.",
  "un"),
 (3, "AMERICAS", "MILEY CYRUS", "BBC",
  "Miley Cyrus marries Maxx Morando in California",
  "The BBC reported the wedding on Monday. Cyrus and Morando married in California.",
  "rings"),
 (4, "EUROPE", "MERKURY SUNK", "CNN / Times / WSJ / AP",
  "Ukraine sinks warship Merkury off Libya",
  "7 sea drones launched; the corvette sank at Benghazi, a Ka-27 destroyed aboard.",
  "ship"),
 (5, "EUROPE", "SPARTA II", "Reuters / Times / WSJ",
  "Russian cargo ship Sparta II hit, towed clear",
  "Drones hit the ship on Saturday; all 16 crew came off in Finland's Loviisa rescue.",
  "rescue"),
 (6, "EUROPE", "KYIV STRIKES", "Times / AP",
  "Kyiv strikes kill at least 15 near Kyiv",
  "11 died in a Dymer block of flats; a drone hit a Kyiv building, 5 injured.",
  "flats"),
 (7, "WORLD", "COP31 NO DEAL", "Times / Guardian",
  "COP31 ends with no deal \u2014 first since 2000",
  "The Antalya Pact was not adopted; the text dropped fossil fuels after 44 hours.",
  "cop"),
 (8, "MIDDLE EAST", "IRAN SANCTIONS", "AP / Treasury",
  "US sanctions 30 Iran-linked exchange houses",
  "Treasury acted Monday against ~30 houses in shadow banking evading Iran sanctions.",
  "bank"),
 (9, "MIDDLE EAST", "GAZA", "AP",
  "Israeli strikes kill 3 in Gaza",
  "3 killed on Monday in separate strikes, including a UNRWA employee, Shifa confirms.",
  "smoke"),
 (10, "MIDDLE EAST", "YEMEN", "AP",
  "Strike kills 11 in western Yemen",
  "Houthis say a Saudi-backed strike on Monday killed 11 and wounded 19.",
  "hills"),
 (11, "AMERICAS", "GOLD $3,588", "Reuters",
  "Gold rebounds 1.5% to $3,588",
  "Gold 3588: bullion rose 1.5% after its worst week in 8 months; PCE due 25 Nov.",
  "gold"),
 (12, "WORLD", "BITCOIN $61,284", "CoinPaprika",
  "Bitcoin steadies near $61,284",
  "Bitcoin 61284 at 12:52 UTC on Monday; weekend low near $55,100.",
  "coin"),
 (13, "AMERICAS", "GTA VI $3.8BN", "ActiveInvestorMag",
  "GTA VI takes $3.8bn on day one",
  "Biggest entertainment launch on record; GTA VI took $3.8bn on day one.",
  "city"),
]
PLACES = {1: "Washington", 2: "United Nations", 3: "California", 4: "Benghazi, Libya",
          5: "Gulf of Finland", 6: "Kyiv region, Ukraine", 7: "Antalya, T\u00fcrkiye",
          8: "Washington", 9: "Gaza City", 10: "Western Yemen", 11: "New York",
          12: "Crypto markets", 13: "Los Angeles"}
CHIPS = {1: "FBI PROBE", 2: "TALKS GO ON", 3: "WED IN CALIFORNIA", 4: "7 SEA DRONES \u00b7 SUNK",
         5: "16 CREW SAFE", 6: "15 KILLED \u00b7 11 IN DYMER", 7: "NO DEAL \u00b7 FIRST SINCE 2000",
         8: "~30 SANCTIONED", 9: "3 KILLED", 10: "11 KILLED \u00b7 19 WOUNDED",
         11: "$3,588/OZ", 12: "$61,284", 13: "$3.8BN DAY ONE"}
CERT = "REPORTED"

# ---- BRIEFS: ALSO ON 14-38, one line each ----
BRIEFS = [
 "Democrats 258\u2013173 take the House (BBC)",
 "Van Hollen challenges Schumer (ActiveInvestorMag)",
 "Nvidia brings back Huang; shares +31% (Reuters)",
 "Solana launches solana.ai for AI agents (Gadgets360)",
 "Hong Kong curbs drones for Interpol summit (HK News TV)",
 "North Korea weighs shutting Swiss office (Reuters)",
 "US mulls training Syrian forces (Reuters)",
 "Congo halts cobalt exports from 30 Nov (Reuters)",
 "Indonesia factory blaze kills 24 (Reuters)",
 "CrowdStrike buys Zscaler for $44bn (Reuters)",
 "Euro zone PMI 51.7, fifth month of growth (Reuters)",
 "Nepal PM ends Delhi visit; met Modi (IANS)",
 "Thousands march in Lisbon on living costs (JagranJosh)",
 "UK\u2013EU reset deal called \u201clandmark\u201d (BBC)",
 "India\u2013EU trade pact likely signed 16 Dec (JagranJosh)",
 "Tata Steel sells pipe arm for \u20b928,000 cr (ObserverVoice)",
 "SpiceJet pilot seeks safety audit (ObserverVoice)",
 "Modi opens AI Centre at IIT Patna (ObserverVoice)",
 "Amit Shah launches \u20b94,000 cr Arunachal push (ObserverVoice)",
 "NEET PG: 10,105 seats flagged blocked (JagranJosh)",
 "Kraken CAD flash crash stands (CoinPaprika)",
 "COP31: EU, UK reject text; Addis hosts COP32 (Guardian)",
 "FBI probe: states pause dealer checks (AP)",
 "Wellington draw 239/5; Mitchell 49*, Phillips 26* (HS)",
 "Liverpool 4\u20130; Yoro off, Pochettino disaster (Mint)",
]

# ---- NUMS: number strip (value, label) ----
NUMS = [
 ("7", "SEA DRONES"), ("15", "KILLED NEAR KYIV"), ("NO DEAL", "FIRST SINCE 2000"),
 ("~30", "IRAN HOUSES"), ("$3,588", "GOLD"), ("$61,284", "BITCOIN"),
 ("$3.8BN", "GTA VI DAY ONE"), ("258\u2013173", "HOUSE"), ("+31%", "NVIDIA"), ("239/5", "WELLINGTON DRAW"),
]

# ---- TL: timeline slots (time, event, source) - verified hours only ----
TL = [
 ("00:02 UTC MON", "UN states keep talking on AI weapons", "salonvision"),
 ("12:52 UTC MON", "Bitcoin $61,284 on Monday", "CoinPaprika"),
 ("MON EVENING", "Zelenskyy announces Merkury sinking", "CNN / AP"),
 ("MON EVENING", "Treasury sanctions ~30 Iran houses", "AP"),
 ("21:39 HKT MON", "Hong Kong announces Interpol curbs", "HK News TV"),
 ("04:24 WIB TUE", "KCNA: North Korea may shut Swiss office", "Reuters"),
]

# ---- dc: DATE CHECK, named dated discards ----
dc = ("186-drone night over Ukraine, 161 downed \u2014 21\u201322 Nov \u00b7 "
      "Alcaraz beats Zverev, first ATP Finals title \u2014 22 Nov \u00b7 "
      "Verstappen wins the Las Vegas Grand Prix \u2014 22 Nov \u00b7 "
      "Wembanyama scores 50, Spurs beat Pelicans \u2014 22 Nov \u00b7 "
      "Hong Kong Election Committee results: 723 seats \u2014 22 Nov \u00b7 "
      "Jensen Huang resigns as Nvidia CEO \u2014 12 Nov \u00b7 "
      "FBI seizes $1.2bn crypto from $6.3bn Binance heist \u2014 20 Nov")

REGIONS = [("EUROPE", 3), ("MIDDLE EAST", 3), ("AMERICAS", 4), ("WORLD", 3)]

# ============================== helpers ==============================
def wrap(d, text, fnt, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def para(d, x, y, maxw, lines, fnt, lh, fill=INK):
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y

def chip(d, x, y, s, fnt, bg=RUST, fg=CREAM):
    w = d.textlength(s, font=fnt) + 12
    h = fnt.size + 7
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg)
    d.text((x + 6, y + 3), s, font=fnt, fill=fg)
    return w

def band_label(d, x, y, s, fnt):
    """Cream source tag on a dark pill, readable over any scene."""
    w = d.textlength(s, font=fnt) + 10
    h = fnt.size + 6
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=DMOSS)
    d.text((x + 5, y + 3), s, font=fnt, fill=CREAM)
    return w

def chip_r(d, right, y, s, fnt, bg=RUST, fg=CREAM):
    """Chip whose right edge lands on `right` (never spills past the card)."""
    w = d.textlength(s, font=fnt) + 12
    return chip(d, right - w, y, s, fnt, bg, fg)

def tagline(d, x, y, num, place, region, topic, fnt):
    s = "%d  \u00b7  %s, %s  \u00b7  %s" % (num, place.upper(), region, topic)
    d.text((x, y), s, font=fnt, fill=RUST)

# ---- flat layered scenes: one painter per card, drawn into a box ----
def scene(d, kind, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    cx, cy = x + w // 2, y + h // 2
    if kind == "fbi":
        d.rectangle([x, y, x + w, y + h], fill=DMOSS)
        d.rectangle([x + w * 0.08, y + h * 0.28, x + w * 0.92, y + h], fill=MOSS)
        for i in range(5):
            px = x + w * (0.14 + i * 0.17)
            d.rectangle([px, y + h * 0.34, px + w * 0.09, y + h * 0.92], fill=CREAM)
        d.rectangle([x + w * 0.30, y + h * 0.12, x + w * 0.70, y + h * 0.30], fill=DMOSS)
        d.ellipse([x + w * 0.40, y + h * 0.02, x + w * 0.60, y + h * 0.28], fill=RUST)
        d.text((x + w * 0.50, y + h * 0.15), "FBI", font=F_BOLD(max(10, h // 5)),
               fill=CREAM, anchor="mm")
        for i in range(6):
            d.rectangle([x + w * (0.10 + i * 0.14), y + h * 0.80, x + w * (0.18 + i * 0.14),
                         y + h * 0.88], fill=GOLD_L)
    elif kind == "un":
        d.rectangle([x, y, x + w, y + h], fill=NAVY)
        d.ellipse([cx - h * 0.30, y + h * 0.12, cx + h * 0.30, y + h * 0.88], fill=SEA)
        d.ellipse([cx - h * 0.22, y + h * 0.22, cx + h * 0.22, y + h * 0.62], fill=SAGE_L)
        d.arc([x + w * 0.06, y + h * 0.55, x + w * 0.42, y + h * 0.98], 200, 340, fill=GOLD_L, width=3)
        d.arc([x + w * 0.58, y + h * 0.55, x + w * 0.94, y + h * 0.98], 200, 340, fill=GOLD_L, width=3)
        d.ellipse([cx - 4, y + h * 0.30, cx + 4, y + h * 0.30 + 8], fill=CREAM)
    elif kind == "rings":
        d.rectangle([x, y, x + w, y + h], fill=GOLD_L)
        d.ellipse([cx - h * 0.34, y + h * 0.18, cx + h * 0.02, y + h * 0.82], outline=GOLD, width=5)
        d.ellipse([cx - h * 0.02, y + h * 0.18, cx + h * 0.34, y + h * 0.82], outline=(150, 110, 30), width=5)
        d.polygon([(x, y + h), (x + w * 0.30, y + h * 0.45), (x + w * 0.55, y + h),
                   (x + w * 0.80, y + h * 0.55), (x + w, y + h)], fill=OLIVE)
    elif kind in ("ship", "rescue"):
        d.rectangle([x, y, x + w, y + h], fill=SEA)
        for i in range(3):
            yy = y + h * (0.62 + i * 0.12)
            d.arc([x - w * 0.1, yy, x + w * 0.5, yy + h * 0.16], 0, 180, fill=CREAM, width=2)
            d.arc([x + w * 0.4, yy, x + w * 1.1, yy + h * 0.16], 0, 180, fill=CREAM, width=2)
        d.polygon([(x + w * 0.15, y + h * 0.60), (x + w * 0.85, y + h * 0.60),
                   (x + w * 0.72, y + h * 0.78), (x + w * 0.28, y + h * 0.78)], fill=INK)
        d.rectangle([x + w * 0.42, y + h * 0.30, x + w * 0.58, y + h * 0.60], fill=INK)
        d.polygon([(x + w * 0.58, y + h * 0.30), (x + w * 0.78, y + h * 0.42),
                   (x + w * 0.58, y + h * 0.52)], fill=RUST)
        for i in range(3):
            d.ellipse([x + w * (0.18 + i * 0.22), y + h * 0.16, x + w * (0.24 + i * 0.22),
                       y + h * 0.16 + 6], fill=INK)
        if kind == "rescue":
            d.polygon([(x + w * 0.62, y + h * 0.72), (x + w * 0.92, y + h * 0.72),
                       (x + w * 0.86, y + h * 0.86), (x + w * 0.68, y + h * 0.86)], fill=RUST)
    elif kind == "flats":
        d.rectangle([x, y, x + w, y + h], fill=(196, 190, 168))
        d.rectangle([x + w * 0.12, y + h * 0.22, x + w * 0.45, y + h], fill=MOSS)
        d.rectangle([x + w * 0.55, y + h * 0.38, x + w * 0.88, y + h], fill=DMOSS)
        for r in range(3):
            for c in range(2):
                wx = x + w * (0.17 + c * 0.13)
                wy = y + h * (0.30 + r * 0.20)
                d.rectangle([wx, wy, wx + w * 0.08, wy + h * 0.10], fill=GOLD_L)
        d.polygon([(x + w * 0.55, y + h * 0.30), (x + w * 0.70, y + h * 0.10),
                   (x + w * 0.85, y + h * 0.30)], fill=(120, 118, 110))
        d.ellipse([x + w * 0.60, y + h * 0.05, x + w * 0.80, y + h * 0.05 + h * 0.22], fill=(150, 150, 145))
    elif kind == "cop":
        d.rectangle([x, y, x + w, y + h], fill=(232, 214, 160))
        d.ellipse([cx - h * 0.26, y + h * 0.10, cx + h * 0.26, y + h * 0.62], fill=GOLD)
        d.ellipse([cx - h * 0.18, y + h * 0.18, cx + h * 0.18, y + h * 0.54], fill=(240, 200, 90))
        d.rectangle([x, y + h * 0.62, x + w, y + h], fill=OLIVE)
        d.rectangle([x + w * 0.42, y + h * 0.66, x + w * 0.58, y + h * 0.86], fill=CREAM)
        d.line([x + w * 0.42, y + h * 0.66, x + w * 0.58, y + h * 0.86], fill=RUST, width=3)
        d.line([x + w * 0.58, y + h * 0.66, x + w * 0.42, y + h * 0.86], fill=RUST, width=3)
    elif kind == "bank":
        d.rectangle([x, y, x + w, y + h], fill=DMOSS)
        d.polygon([(x + w * 0.10, y + h * 0.42), (x + w * 0.50, y + h * 0.14),
                   (x + w * 0.90, y + h * 0.42)], fill=GOLD_L)
        for i in range(4):
            px = x + w * (0.18 + i * 0.19)
            d.rectangle([px, y + h * 0.46, px + w * 0.08, y + h * 0.88], fill=CREAM)
        d.rectangle([x + w * 0.08, y + h * 0.88, x + w * 0.92, y + h * 0.96], fill=GOLD_L)
        d.ellipse([x + w * 0.66, y + h * 0.10, x + w * 0.94, y + h * 0.10 + h * 0.30], outline=RUST, width=4)
        d.line([x + w * 0.70, y + h * 0.14, x + w * 0.90, y + h * 0.36], fill=RUST, width=4)
    elif kind in ("smoke", "hills"):
        d.rectangle([x, y, x + w, y + h], fill=(226, 214, 186))
        d.polygon([(x, y + h), (x + w * 0.25, y + h * 0.42), (x + w * 0.50, y + h),
                   (x + w * 0.75, y + h * 0.52), (x + w, y + h)], fill=OLIVE if kind == "hills" else MOSS)
        for i, ox in enumerate((0.20, 0.55, 0.80)):
            d.ellipse([x + w * ox, y + h * 0.08, x + w * ox + h * 0.20, y + h * 0.08 + h * 0.34],
                      fill=(150, 148, 140))
        d.rectangle([x, y + h * 0.82, x + w, y + h], fill=DMOSS if kind == "hills" else RUST)
    elif kind == "gold":
        d.rectangle([x, y, x + w, y + h], fill=DMOSS)
        for i, (bx, by, bw) in enumerate(((0.12, 0.62, 0.30), (0.42, 0.62, 0.30), (0.27, 0.38, 0.30))):
            d.polygon([(x + w * bx, y + h * (by + 0.16)), (x + w * bx, y + h * by),
                       (x + w * (bx + bw), y + h * by), (x + w * (bx + bw), y + h * (by + 0.16))],
                      fill=GOLD)
        d.line([(x + w * 0.08, y + h * 0.30), (x + w * 0.35, y + h * 0.22),
                (x + w * 0.60, y + h * 0.26), (x + w * 0.92, y + h * 0.08)], fill=GOLD_L, width=3)
    elif kind == "coin":
        d.rectangle([x, y, x + w, y + h], fill=NAVY)
        d.ellipse([cx - h * 0.32, y + h * 0.10, cx + h * 0.32, y + h * 0.90], fill=GOLD)
        d.text((cx, cy + 1), "\u20bf", font=F_BOLD(max(12, h // 2)), fill=NAVY, anchor="mm")
        d.line([(x + w * 0.06, y + h * 0.80), (x + w * 0.30, y + h * 0.60),
                (x + w * 0.55, y + h * 0.68), (x + w * 0.94, y + h * 0.30)], fill=GOLD_L, width=3)
    elif kind == "city":
        d.rectangle([x, y, x + w, y + h], fill=(58, 48, 66))
        for i, (bx, bw, bh) in enumerate(((0.05, 0.14, 0.55), (0.22, 0.18, 0.75), (0.43, 0.14, 0.50),
                                          (0.60, 0.18, 0.68), (0.81, 0.14, 0.58))):
            d.rectangle([x + w * bx, y + h * (1 - bh), x + w * (bx + bw), y + h], fill=INK)
            for r in range(3):
                d.rectangle([x + w * (bx + 0.03), y + h * (1 - bh + 0.08 + r * 0.18),
                             x + w * (bx + 0.07), y + h * (1 - bh + 0.16 + r * 0.18)], fill=GOLD_L)
        d.text((x + w * 0.50, y + h * 0.16), "VI", font=F_BLACK(max(14, h // 2)), fill=GOLD, anchor="mm")

# ---- dotted_map: dotted world map from real polygons (lon/lat) ----
LAND = [
 [(-168,66),(-140,70),(-120,71),(-95,69),(-85,66),(-80,73),(-65,60),(-55,52),(-60,46),(-70,42),(-75,35),(-80,26),(-84,30),(-90,21),(-97,16),(-105,20),(-110,24),(-117,33),(-125,40),(-124,48),(-135,58),(-155,58),(-165,60)],
 [(-58,64),(-45,60),(-30,68),(-22,70),(-40,76),(-58,76)],
 [(-80,9),(-72,12),(-62,10),(-52,5),(-50,0),(-44,-3),(-35,-8),(-40,-20),(-48,-27),(-57,-38),(-65,-41),(-70,-52),(-73,-37),(-70,-20),(-77,-12),(-81,-5),(-80,2)],
 [(-17,15),(-10,31),(0,36),(10,37),(20,32),(30,31),(35,28),(43,12),(51,11),(48,0),(40,-10),(35,-18),(32,-28),(26,-34),(19,-35),(15,-27),(12,-18),(9,4),(-8,5),(-17,15)],
 [(-10,36),(-9,43),(-2,48),(-4,50),(0,51),(5,53),(8,57),(10,59),(5,60),(12,65),(18,69),(25,71),(32,70),(40,68),(50,69),(60,69),(70,72),(80,73),(90,75),(100,76),(110,74),(120,73),(130,72),(140,72),(150,70),(160,69),(170,66),(178,65),(170,60),(162,56),(158,52),(150,59),(142,55),(140,45),(135,43),(130,42),(127,40),(122,38),(120,32),(115,23),(108,18),(105,9),(100,8),(97,16),(92,21),(88,22),(80,13),(77,8),(72,20),(66,25),(60,25),(57,26),(52,28),(48,29),(50,30),(44,29),(39,21),(35,28),(30,36),(26,40),(23,36),(19,42),(12,44),(8,44),(3,43),(-2,37),(-9,37),(-10,36)],
 [(-5,50),(-3,53),(-5,56),(-2,58),(0,53),(1,51)],
 [(113,-22),(114,-30),(115,-35),(120,-34),(129,-32),(132,-32),(136,-35),(140,-38),(145,-38),(150,-37),(153,-32),(153,-27),(146,-19),(142,-15),(142,-11),(136,-12),(132,-11),(126,-14),(122,-17),(114,-22)],
 [(167,-45),(171,-42),(174,-41),(177,-38),(175,-37),(173,-41),(168,-46)],
 [(130,31),(133,34),(137,35),(140,38),(141,42),(144,44),(141,40),(138,37),(134,34),(131,32)],
 [(109,1),(113,4),(117,6),(119,1),(116,-3),(110,-3)],
 [(95,5),(100,0),(104,-3),(106,-6),(103,-4),(98,3)],
 [(105,-6),(110,-7),(114,-8),(112,-7),(107,-7)],
 [(131,-1),(136,-2),(141,-3),(146,-6),(150,-9),(146,-8),(141,-8),(136,-5),(132,-4)],
]

def inside(lon, lat, poly):
    ins = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            xin = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xin:
                ins = not ins
        j = i
    return ins

PINS = [  # (card num, lon, lat, dx, dy)
 (1, -77.0, 38.9, 0, 0), (2, -74.0, 40.7, 8, -8), (3, -118.4, 34.1, 0, 0),
 (4, 20.1, 32.1, 0, 0), (5, 24.5, 59.9, 0, 0), (6, 30.5, 50.4, 0, 0),
 (7, 30.7, 36.9, 0, 8), (8, -77.0, 38.9, -10, 8), (9, 34.5, 31.5, 0, 0),
 (10, 44.0, 15.3, 0, 0), (11, -74.0, 40.7, -9, -9), (12, -122.4, 37.8, 0, 0),
 (13, -118.2, 34.0, 9, 8), (37, 174.8, -41.3, 0, 0), (38, -3.0, 53.4, 0, 0),
]

def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    step = 6
    def proj(lon, lat):
        px = x + (lon + 180.0) / 360.0 * w
        py = y + (75.0 - lat) / 135.0 * h
        return px, py
    gy = y + 3
    while gy < y + h - 2:
        gx = x + 3
        while gx < x + w - 2:
            lon = (gx - x) / w * 360.0 - 180.0
            lat = 75.0 - (gy - y) / h * 135.0
            if any(inside(lon, lat, p) for p in LAND):
                d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=SAGE_L)
            gx += step
        gy += step
    for num, lon, lat, dx, dy in PINS:
        px, py = proj(lon, lat)
        px, py = px + dx, py + dy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RUST, outline=CREAM, width=1)
        d.text((px, py - 1), str(num), font=F_BOLD(9), fill=CREAM, anchor="mm")

# ============================== cards ==============================
def lead(d, c, x, y, w, h, variant):
    num, region, topic, src, head, deck, kind = c
    if variant == "A":
        sw = 340
        scene(d, kind, x, y, sw, h)
        tx = x + sw + 12
        tw = w - sw - 12
        tagline(d, tx, y + 4, num, PLACES[num], region, topic, F_BOLD(9))
        hl = wrap(d, head, fb(23), tw)
        para(d, tx, y + 20, tw, hl[:1], fb(23), 27)
        dl = wrap(d, deck, fr(12), tw)
        para(d, tx, y + 50, tw, dl[:3], fr(12), 15)
        cw = chip(d, tx, y + h - 21, CHIPS[num], F_BOLD(10))
        d.text((tx + cw + 8, y + h - 18), "%s \u00b7 %s" % (src, CERT), font=F_BOLD(9), fill=FAINT)
    else:
        sh = 40
        scene(d, kind, x, y, w, sh)
        band_label(d, x + 6, y + sh - 22, "%s \u00b7 %s" % (src, CERT), F_BOLD(9))
        chip_r(d, x + w - 8, y + sh - 25, CHIPS[num], F_BOLD(9))
        tagline(d, x, y + sh + 5, num, PLACES[num], region, topic, F_BOLD(9))
        hl = wrap(d, head, fb(23), w)
        para(d, x, y + sh + 21, w, hl[:1], fb(23), 27)
        dl = wrap(d, deck, fr(12), w)
        para(d, x, y + sh + 50, w, dl[:2], fr(12), 14)

def lead2(d, c, x, y, w, h):
    num, region, topic, src, head, deck, kind = c
    sh = 38
    scene(d, kind, x, y, w, sh)
    band_label(d, x + 6, y + sh - 20, "%s \u00b7 %s" % (src, CERT), F_BOLD(8))
    chip_r(d, x + w - 8, y + sh - 23, CHIPS[num], F_BOLD(8))
    tagline(d, x, y + sh + 4, num, PLACES[num], region, topic, F_BOLD(8))
    hl = wrap(d, head, F_SERIF(15), w)
    para(d, x, y + sh + 17, w, hl[:2], F_SERIF(15), 17)
    dl = wrap(d, deck, F_SERIFR(10), w)
    para(d, x, y + sh + 17 + len(hl[:2]) * 17 + 3, w, dl[:3], F_SERIFR(10), 12)

def mini(d, c, x, y, w, h):
    num, region, topic, src, head, deck, kind = c
    sh = 26
    scene(d, kind, x, y, w, sh)
    band_label(d, x + 4, y + 5, "%s" % src.split(" / ")[0], F_BOLD(7))
    chip_r(d, x + w - 4, y + 4, CHIPS[num], F_BOLD(7))
    d.text((x, y + sh + 3), "%d \u00b7 %s \u00b7 %s \u00b7 %s" % (num, PLACES[num].upper(), region, CERT),
           font=F_BOLD(7), fill=RUST)
    hl = wrap(d, head, fb(14), w)
    para(d, x, y + sh + 13, w, hl[:2], fb(14), 15)
    dl = wrap(d, deck, fr(12), w)
    para(d, x, y + sh + 13 + len(hl[:2]) * 15 + 2, w, dl[:3], fr(12), 13)

# ============================== page ==============================
def rule(d, x, y, w, color=RULE, width=2):
    d.line([(x, y), (x + w, y)], fill=color, width=width)

def section_head(d, x, y, w, s, color=MOSS):
    d.text((x, y), s, font=F_BOLD(11), fill=color)
    rule(d, x, y + 15, w, color=color, width=1)

def render(variant):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.text((M, 10), "THE MILLSTREAM  \u00b7  TUESDAY EDITION", font=F_BOLD(9), fill=MOSS)
    d.text((W - M, 10), "No. 24  \u00b7  24 NOVEMBER 2026", font=F_BOLD(9), fill=MOSS, anchor="ra")
    rule(d, M, 24, CW, width=1)
    d.text((W // 2, 28), "THE MILLSTREAM", font=F_BLACK(48), fill=INK, anchor="ma")
    rule(d, M, 80, CW, width=2)
    rule(d, M, 83, CW, width=1)
    d.text((W // 2, 87), "Tuesday 24 November 2026", font=F_SERIFI(17), fill=RUST, anchor="ma")
    d.text((W // 2, 107), "Thirteen stories lead the day; thirty-eight in all \u2014 every one dated to this Tuesday.",
           font=F_SERIFR(11), fill=INK, anchor="ma")
    d.rectangle([M, 122, W - M, 142], fill=MOSS)
    d.text((W // 2, 126), "38 STORIES  \u00b7  7 REGIONS  \u00b7  EVERY ONE FROM 24 NOVEMBER 2026",
           font=F_BOLD(14), fill=CREAM, anchor="ma")
    # number strip
    y0 = 146
    d.rectangle([M, y0, W - M, y0 + 30], outline=RULE, width=1)
    cellw = CW / len(NUMS)
    for i, (big, lab) in enumerate(NUMS):
        cx0 = M + i * cellw
        if i:
            d.line([(cx0, y0), (cx0, y0 + 30)], fill=RULE, width=1)
        d.text((cx0 + cellw / 2, y0 + 2), big, font=F_BOLD(13), fill=RUST, anchor="ma")
        d.text((cx0 + cellw / 2, y0 + 18), lab, font=F_BOLD(7), fill=INK, anchor="ma")
    # lead #1
    lead(d, grid[0], M, 180, CW, 116, variant)
    # leads #2-3
    lw = (CW - 8) // 2
    lead2(d, grid[1], M, 300, lw, 120)
    lead2(d, grid[2], M + lw + 8, 300, lw, 120)
    # minis #4-13: 5 cols x 2 rows
    mw = (CW - 4 * 8) // 5
    mh = 112
    for r in range(2):
        for col in range(5):
            idx = 3 + r * 5 + col
            mini(d, grid[idx], M + col * (mw + 8), 424 + r * (mh + 6), mw, mh)
    # region strip
    y0 = 658
    d.rectangle([M, y0, W - M, y0 + 18], fill=DMOSS)
    xx = M + 10
    d.text((xx, y0 + 3), "REGIONS:", font=F_BOLD(10), fill=GOLD_L)
    xx += d.textlength("REGIONS: ", font=F_BOLD(10)) + 6
    for name, cnt in REGIONS:
        s = "%s %d" % (name, cnt)
        d.text((xx, y0 + 3), s, font=F_BOLD(10), fill=CREAM)
        xx += d.textlength(s, font=F_BOLD(10)) + 14
    d.text((W - M - 10, y0 + 3), "+ ASIA-PACIFIC \u00b7 AFRICA \u00b7 OCEANIA ACROSS ALL 38",
           font=F_BOLD(10), fill=SAGE_L, anchor="ra")
    # timeline
    y0 = 680
    section_head(d, M, y0, CW, "THE DAY IN UTC \u2014 MONDAY EVENING INTO TUESDAY  \u00b7  TIMES AS REPORTED; TUESDAY HOURS IN WIB WHERE MARKED")
    ty = y0 + 19
    colw = CW // 3
    for i, (t, ev, src) in enumerate(TL):
        tx = M + (i % 3) * colw
        tyy = ty + (i // 3) * 21
        d.text((tx, tyy), t, font=F_BOLD(9), fill=RUST)
        d.text((tx + 108, tyy), ev, font=F_SANS(9), fill=INK)
        d.text((tx + 108, tyy + 10), src, font=F_SANS(7), fill=FAINT)
    # bottom: ALSO ON (left) + map + DATE CHECK (right)
    y0 = 740
    section_head(d, M, y0, 604, "ALSO ON \u2014 14 TO 38")
    bx = M
    by = y0 + 19
    colw2 = 302
    for i, b in enumerate(BRIEFS):
        col = i // 13
        row = i % 13
        tx = bx + col * colw2
        tyy = by + row * 17
        d.text((tx, tyy), "%d." % (14 + i), font=F_BOLD(10), fill=RUST)
        d.text((tx + 22, tyy), b, font=fsr(10), fill=INK)
    d.text((M, by + 13 * 17 + 2), "All briefs first reported 23\u201324 November 2026.",
           font=F_SERIFI(9), fill=FAINT)
    mx = M + 604 + 12
    mw2 = W - M - mx
    section_head(d, mx, y0, mw2, "WHERE IT HAPPENED \u2014 PINS MARK STORY NUMBERS")
    draw_map(d, mx, y0 + 19, mw2, 140)
    dy = y0 + 163
    d.rectangle([mx, dy, W - M, dy + 97], outline=RUST, width=2)
    d.rectangle([mx, dy, W - M, dy + 16], fill=RUST)
    d.text((mx + 6, dy + 3), "DATE CHECK \u2014 NOT TODAY\u2019S NEWS", font=F_BOLD(9), fill=CREAM)
    for i, s in enumerate(dc.split(" \u00b7 ")):
        tyy = dy + 19 + i * 11
        d.text((mx + 6, tyy), "\u00b7  %s" % s, font=F_SANS(9), fill=INK)
    # footer
    fy = 1000
    rule(d, M, fy, CW, width=1)
    d.text((M, fy + 4), "SOURCES: AP \u00b7 REUTERS \u00b7 CNN \u00b7 BBC \u00b7 TIMES \u00b7 GUARDIAN \u00b7 WSJ \u00b7 TREASURY \u00b7 COINPAPRIKA \u00b7 GADGETS360 \u00b7 HK NEWS TV \u00b7 IANS \u00b7 JAGRANJOSH \u00b7 OBSERVERVOICE \u2014 REPORTED = confirmed by named sources; CLAIM = as stated by one side.",
           font=F_SANS(8), fill=FAINT)
    d.text((M, fy + 13), "Tonight\u2019s real count: 7 sea drones, at the top of this page.  Pictures and map: original drawings, drawn in code.",
           font=F_SERIFI(8), fill=FAINT)
    return img

if __name__ == "__main__":
    variant = sys.argv[1] if len(sys.argv) > 1 else "A"
    img = render(variant)
    out = "entry-%s.png" % variant
    img.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes", img.size)
    # fresh-word self-check over every story string the page carries
    blob = [c[4] + " " + c[5] for c in grid] + BRIEFS
    norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
    hay = " ".join(norm(b) for b in blob)
    fresh = [l.strip() for l in open(
        "/home/hatch/workspace/makefun/ni24-fresh.txt").read().splitlines() if l.strip()]
    missing = [f for f in fresh if norm(f) not in hay]
    print("fresh coverage: %d/%d  missing=%s" % (len(fresh) - len(missing), len(fresh), missing))
