#!/usr/bin/env python3
"""
Figment Brochure Generator
Creates 5 PDF brochures: SAT, GRE, GMAT, IELTS, ACS
Design matches figment.global — dark backgrounds, gold accents, Playfair/Cormorant/Inter typography
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import math

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR   = "/Users/praveenkumarmohan/Desktop/Figment Website"
FONTS_DIR  = "/Users/praveenkumarmohan/Library/Fonts"
EXPERTS    = f"{BASE_DIR}/experts"
OUT_DIR    = os.path.expanduser("~/Desktop/Figment Brochures")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Fonts ──────────────────────────────────────────────────────────────────
pdfmetrics.registerFont(TTFont('Playfair',         f'{FONTS_DIR}/PlayfairDisplay-VariableFont_wght.ttf'))
pdfmetrics.registerFont(TTFont('Playfair-Italic',  f'{FONTS_DIR}/PlayfairDisplay-Italic-VariableFont_wght.ttf'))
pdfmetrics.registerFont(TTFont('Cormorant-Italic', f'{FONTS_DIR}/CormorantGaramond-Italic-VariableFont_wght.ttf'))
pdfmetrics.registerFont(TTFont('Cormorant',        f'{FONTS_DIR}/CormorantGaramond-VariableFont_wght.ttf'))
pdfmetrics.registerFont(TTFont('Inter-Light',      f'{FONTS_DIR}/Inter_24pt-Light.ttf'))
pdfmetrics.registerFont(TTFont('Inter',            f'{FONTS_DIR}/Inter_24pt-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Inter-Medium',     f'{FONTS_DIR}/Inter_24pt-Medium.ttf'))
pdfmetrics.registerFont(TTFont('Inter-Bold',       f'{FONTS_DIR}/Inter_24pt-Bold.ttf'))

# ── Color palette ──────────────────────────────────────────────────────────
BLACK    = HexColor('#000000')
NAVY     = HexColor('#0B2C4A')
IVORY    = HexColor('#F4F1EC')
GOLD     = HexColor('#C6A75E')
GOLD_L   = HexColor('#d9bc80')
CHARCOAL = HexColor('#1C1C1C')
GREY     = HexColor('#8A8F96')
WHITE_10 = Color(1, 1, 1, 0.10)
WHITE_06 = Color(1, 1, 1, 0.06)
WHITE_05 = Color(1, 1, 1, 0.05)
IVORY_65 = Color(0.957, 0.945, 0.925, 0.65)
IVORY_40 = Color(0.957, 0.945, 0.925, 0.40)
GOLD_30  = Color(0.776, 0.655, 0.369, 0.30)

# ── Page dimensions (A4) ───────────────────────────────────────────────────
W, H = A4   # 595.27 x 841.89 pt
MAR_L = 18 * mm
MAR_R = 18 * mm
CONTENT_W = W - MAR_L - MAR_R

# ── Low-level drawing helpers ──────────────────────────────────────────────

def set_fill(c, col):
    c.setFillColor(col)

def set_stroke(c, col):
    c.setStrokeColor(col)

def bg(c, col=BLACK):
    """Fill entire page background."""
    c.setFillColor(col)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def label(c, text, x, y, size=6, font='Inter-Medium', col=GOLD, tracking=0.5):
    c.setFillColor(col)
    c.setFont(font, size)
    # letter-spacing simulation: draw char by char
    cx = x
    for ch in text.upper():
        c.drawString(cx, y, ch)
        cx += c.stringWidth(ch, font, size) + tracking
    return cx

def heading(c, text, x, y, size=26, font='Playfair', col=IVORY, max_width=None, leading=None):
    if leading is None:
        leading = size * 1.05
    c.setFillColor(col)
    c.setFont(font, size)
    if max_width is None:
        c.drawString(x, y, text)
        return y - leading
    # word-wrap
    words = text.split()
    line = ''
    cy = y
    for w in words:
        test = (line + ' ' + w).strip()
        if c.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            if line:
                c.drawString(x, cy, line)
                cy -= leading
            line = w
    if line:
        c.drawString(x, cy, line)
        cy -= leading
    return cy

def body_text(c, text, x, y, size=8, font='Inter-Light', col=IVORY_65,
              max_width=None, leading=None):
    if leading is None:
        leading = size * 1.6
    c.setFillColor(col)
    c.setFont(font, size)
    if max_width is None:
        c.drawString(x, y, text)
        return y - leading
    words = text.split()
    line = ''
    cy = y
    for w in words:
        test = (line + ' ' + w).strip()
        if c.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            if line:
                c.drawString(x, cy, line)
                cy -= leading
            line = w
    if line:
        c.drawString(x, cy, line)
        cy -= leading
    return cy

def gold_rule(c, x, y, w=10*mm):
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.75)
    c.line(x, y, x + w, y)

def horiz_rule(c, x, y, w=CONTENT_W, col=WHITE_06):
    c.setStrokeColor(col)
    c.setLineWidth(0.5)
    c.line(x, y, x + w, y)

def stat_block(c, x, y, val, lbl, val_size=22, lbl_size=6):
    """Draw a stat: big gold value + small grey label below."""
    c.setFillColor(GOLD)
    c.setFont('Playfair', val_size)
    c.drawCentredString(x, y, val)
    c.setFillColor(GREY)
    c.setFont('Inter', lbl_size)
    cx = x
    for ch in lbl.upper():
        cx_step = c.stringWidth(ch, 'Inter', lbl_size) + 0.25
        c.drawString(cx - c.stringWidth(lbl.upper(), 'Inter', lbl_size)/2 +
                     c.stringWidth(lbl.upper()[:lbl.upper().index(ch)], 'Inter', lbl_size)
                     if False else cx, y - val_size * 1.2, ch)
        break
    # simpler:
    c.setFillColor(GREY)
    c.setFont('Inter', lbl_size)
    c.drawCentredString(x, y - val_size * 1.15, lbl.upper())

def nav_brand(c):
    """Draw Figment wordmark top-left."""
    c.setFillColor(IVORY)
    c.setFont('Playfair', 12)
    c.drawString(MAR_L, H - 14*mm, 'Figment')
    c.setFillColor(GOLD)
    c.setFont('Inter', 5)
    c.drawString(MAR_L, H - 17.5*mm, 'ADMISSIONS CONSULTING')

def footer_bar(c, page_num=None):
    """Draw footer with Figment branding."""
    c.setFillColor(Color(0, 0, 0, 0.6))
    c.rect(0, 0, W, 8*mm, fill=1, stroke=0)
    c.setFillColor(GREY)
    c.setFont('Inter', 6)
    c.drawString(MAR_L, 2.5*mm, 'figment.global  ·  info@figment.global  ·  +91 74487 55866')
    if page_num:
        c.drawRightString(W - MAR_R, 2.5*mm, str(page_num))

def section_header(c, tag, title, x=None, y=None, title_size=22, max_w=None):
    """Standardised section start: LABEL tag + heading + gold rule."""
    if x is None: x = MAR_L
    if y is None: y = H - 30*mm
    if max_w is None: max_w = CONTENT_W
    label(c, tag, x, y, size=6)
    y -= 5*mm
    ny = heading(c, title, x, y, size=title_size, max_width=max_w)
    gold_rule(c, x, ny - 2*mm)
    return ny - 7*mm   # return next y position

def circle_photo(c, path, cx, cy, r):
    """Draw circular photo using clipping."""
    try:
        from reportlab.lib.utils import ImageReader
        img = ImageReader(path)
        iw, ih = img.getSize()
        # clip to circle
        p = c.beginPath()
        p.circle(cx, cy, r)
        c.clipPath(p, stroke=0, fill=0)
        # draw image square-fitted inside circle
        side = r * 2
        c.drawImage(path, cx - r, cy - r, side, side,
                    mask='auto', preserveAspectRatio=True)
        c.restoreState()
        c.saveState()
        # gold ring
        c.setStrokeColor(GOLD_30)
        c.setLineWidth(1.5)
        c.circle(cx, cy, r, stroke=1, fill=0)
    except Exception:
        # fallback: gold circle placeholder
        c.setFillColor(NAVY)
        c.circle(cx, cy, r, fill=1, stroke=0)
        c.setStrokeColor(GOLD_30)
        c.setLineWidth(1.5)
        c.circle(cx, cy, r, stroke=1, fill=0)

def circle_initials(c, cx, cy, r, initials):
    """Draw circular placeholder with initials."""
    # gradient-ish: navy circle
    c.setFillColor(NAVY)
    c.circle(cx, cy, r, fill=1, stroke=0)
    c.setStrokeColor(GOLD_30)
    c.setLineWidth(1.5)
    c.circle(cx, cy, r, stroke=1, fill=0)
    c.setFillColor(GOLD)
    c.setFont('Playfair', r * 0.7)
    c.drawCentredString(cx, cy - r * 0.25, initials)

def prog_card(c, x, y, w, h, title, subtitle, stats, features, price,
              bg_col=None, accent=True):
    """Draw a program card box."""
    if bg_col is None:
        bg_col = Color(0, 0, 0, 0.35)
    # background
    c.setFillColor(bg_col)
    c.rect(x, y - h, w, h, fill=1, stroke=0)
    if accent:
        c.setFillColor(GOLD)
        c.rect(x, y, w, 2, fill=1, stroke=0)
    # badge/title
    cy = y - 6*mm
    c.setFillColor(GOLD)
    c.setFont('Inter-Medium', 6)
    lx = x + 5*mm
    for ch in title.upper():
        c.drawString(lx, cy, ch)
        lx += c.stringWidth(ch, 'Inter-Medium', 6) + 0.3
    cy -= 5*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 13)
    c.drawString(x + 5*mm, cy, subtitle)
    cy -= 4.5*mm
    # divider
    c.setStrokeColor(WHITE_06)
    c.setLineWidth(0.5)
    c.line(x + 5*mm, cy, x + w - 5*mm, cy)
    cy -= 5*mm
    # stats row
    stat_w = (w - 10*mm) / len(stats)
    for i, (sv, sl) in enumerate(stats):
        sx = x + 5*mm + i * stat_w + stat_w / 2
        c.setFillColor(GOLD)
        c.setFont('Playfair', 16)
        c.drawCentredString(sx, cy, sv)
        c.setFillColor(GREY)
        c.setFont('Inter', 5.5)
        c.drawCentredString(sx, cy - 5*mm, sl.upper())
    cy -= 11*mm
    # features
    for feat in features:
        horiz_rule(c, x + 5*mm, cy + 1*mm, w - 10*mm)
        c.setFillColor(IVORY_65)
        c.setFont('Inter-Light', 7)
        # wrap feature text
        words = feat.split()
        line = ''
        fx = x + 5*mm
        for word in words:
            test = (line + ' ' + word).strip()
            if c.stringWidth(test, 'Inter-Light', 7) <= w - 12*mm:
                line = test
            else:
                c.drawString(fx, cy - 2.5*mm, line)
                cy -= 4.5*mm
                line = word
        if line:
            c.drawString(fx, cy - 2.5*mm, line)
        cy -= 7.5*mm
    # price
    cy -= 1*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 18)
    c.drawString(x + 5*mm, cy, price)

# ══════════════════════════════════════════════════════════════════════════════
#  SHARED TEAM PAGE
# ══════════════════════════════════════════════════════════════════════════════

TEAM_MEMBERS = [
    {
        'name': 'Praveen Kumar',
        'role': 'Founder & Lead Counsellor',
        'cred': 'IIM Ahmedabad · Anna University',
        'photo': f'{EXPERTS}/Praveen Kumar.jpeg',
        'bio': 'IIM Ahmedabad alumnus with a track record of placing students in Ivy League universities. Master storyteller — builds student narratives that consistently wow admissions committees worldwide.'
    },
    {
        'name': 'Vinodh Kumar',
        'role': 'Senior Counsellor — MBA & Professional',
        'cred': 'IIM Mumbai · PSG Tech (M.Tech) · Anna Univ',
        'photo': f'{EXPERTS}/Vinodh Kumar.jpeg',
        'bio': 'Combines engineering depth with IIM Mumbai management acumen and industry experience to guide working professionals into top MBA and graduate programmes globally.'
    },
    {
        'name': 'Brindha Devi Rajkumar',
        'role': 'Counsellor — Technology & CS Applications',
        'cred': 'Anna University · Former Software Engineer',
        'photo': f'{EXPERTS}/Brindha.png',
        'bio': 'Former software engineer turned counsellor. Guided dozens of students into top CS, AI, and Data Science programmes at leading universities across the US and Europe.'
    },
    {
        'name': 'Dr Muniraj Vignesh N',
        'role': 'Academic Counsellor — STEM & Research',
        'cred': 'PhD Candidate · Madurai Kamaraj University',
        'photo': f'{EXPERTS}/Muniraj.png',
        'bio': 'Practising PhD scholar guiding students across STEM undergraduate, postgraduate, and doctoral admissions at Tier 1 global institutions.'
    },
    {
        'name': 'Karthick N',
        'role': 'Senior Faculty & Admissions Expert',
        'cred': 'M.Sc. Mathematics · Central University Kerala',
        'photo': None,
        'initials': 'KN',
        'bio': 'Combines elite SAT, GRE, and GMAT coaching with admissions expertise. Unique dual mastery of test prep and profile strategy guides students to their target universities.'
    },
]

INSTITUTIONS = 'IIM Ahmedabad  ·  IIM Mumbai  ·  Anna University  ·  PSG Tech  ·  Central University Kerala'

def draw_team_page(c):
    """Draw the full team page — used as last page of every brochure."""
    c.showPage()
    bg(c, CHARCOAL)
    nav_brand(c)

    # header
    y = H - 22*mm
    label(c, 'Our Admissions Experts', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 28)
    c.drawString(MAR_L, y, 'The people behind')
    y -= 30*mm * 0.95
    c.setFillColor(GOLD)
    c.setFont('Cormorant-Italic', 32)
    c.drawString(MAR_L, y, 'every offer letter.')
    y -= 6*mm
    gold_rule(c, MAR_L, y)
    y -= 5*mm

    # institution strip
    c.setFillColor(Color(0.957, 0.945, 0.925, 0.25))
    c.setFont('Inter', 6)
    iw = c.stringWidth(INSTITUTIONS, 'Inter', 6)
    c.drawCentredString(W/2, y, INSTITUTIONS)
    y -= 7*mm

    # — team grid: 3 + 2 layout —
    PHOTO_R = 14*mm
    CARD_H   = 58*mm
    GAP      = 4*mm

    # Row 1: 3 cards
    card_w = (CONTENT_W - 2*GAP) / 3
    row1_y = y
    for i, m in enumerate(TEAM_MEMBERS[:3]):
        cx = MAR_L + i * (card_w + GAP)
        # card bg
        c.setFillColor(WHITE_05)
        c.rect(cx, row1_y - CARD_H, card_w, CARD_H, fill=1, stroke=0)
        # photo
        px = cx + card_w/2
        py = row1_y - PHOTO_R - 5*mm
        c.saveState()
        if m.get('photo') and os.path.exists(m['photo']):
            circle_photo(c, m['photo'], px, py, PHOTO_R)
        else:
            circle_initials(c, px, py, PHOTO_R, m.get('initials', '?'))
        c.restoreState()
        # text
        ty = py - PHOTO_R - 3*mm
        c.setFillColor(IVORY)
        c.setFont('Playfair', 9)
        c.drawCentredString(px, ty, m['name'])
        ty -= 3.5*mm
        c.setFillColor(GOLD)
        c.setFont('Cormorant-Italic', 7.5)
        # wrap role
        role_lines = []
        words = m['role'].split()
        line = ''
        for w in words:
            t = (line + ' ' + w).strip()
            if c.stringWidth(t, 'Cormorant-Italic', 7.5) <= card_w - 6*mm:
                line = t
            else:
                role_lines.append(line)
                line = w
        role_lines.append(line)
        for rl in role_lines:
            c.drawCentredString(px, ty, rl)
            ty -= 3.5*mm
        ty -= 1*mm
        c.setFillColor(GREY)
        c.setFont('Inter', 5.5)
        c.drawCentredString(px, ty, m['cred'])
        ty -= 3.5*mm
        # bio
        c.setFillColor(IVORY_40)
        c.setFont('Inter-Light', 6)
        words = m['bio'].split()
        line = ''
        for w in words:
            t = (line + ' ' + w).strip()
            if c.stringWidth(t, 'Inter-Light', 6) <= card_w - 6*mm:
                line = t
            else:
                if ty > row1_y - CARD_H + 2*mm:
                    c.drawCentredString(px, ty, line)
                    ty -= 3.5*mm
                line = w
        if line and ty > row1_y - CARD_H + 2*mm:
            c.drawCentredString(px, ty, line)

    y = row1_y - CARD_H - GAP

    # Row 2: 2 cards centred
    card_w2 = (CONTENT_W - GAP) / 2
    row2_offset = (CONTENT_W - (2*card_w2 + GAP)) / 2   # = 0 since it fills full width
    for i, m in enumerate(TEAM_MEMBERS[3:]):
        cx = MAR_L + row2_offset + i * (card_w2 + GAP)
        c.setFillColor(WHITE_05)
        c.rect(cx, y - CARD_H, card_w2, CARD_H, fill=1, stroke=0)
        px = cx + card_w2/2
        py = y - PHOTO_R - 5*mm
        c.saveState()
        if m.get('photo') and os.path.exists(m['photo']):
            circle_photo(c, m['photo'], px, py, PHOTO_R)
        else:
            circle_initials(c, px, py, PHOTO_R, m.get('initials', '?'))
        c.restoreState()
        ty = py - PHOTO_R - 3*mm
        c.setFillColor(IVORY)
        c.setFont('Playfair', 9)
        c.drawCentredString(px, ty, m['name'])
        ty -= 3.5*mm
        c.setFillColor(GOLD)
        c.setFont('Cormorant-Italic', 7.5)
        role_lines = []
        words = m['role'].split()
        line = ''
        for w in words:
            t = (line + ' ' + w).strip()
            if c.stringWidth(t, 'Cormorant-Italic', 7.5) <= card_w2 - 8*mm:
                line = t
            else:
                role_lines.append(line)
                line = w
        role_lines.append(line)
        for rl in role_lines:
            c.drawCentredString(px, ty, rl)
            ty -= 3.5*mm
        ty -= 1*mm
        c.setFillColor(GREY)
        c.setFont('Inter', 5.5)
        c.drawCentredString(px, ty, m['cred'])
        ty -= 3.5*mm
        c.setFillColor(IVORY_40)
        c.setFont('Inter-Light', 6)
        words = m['bio'].split()
        line = ''
        for w in words:
            t = (line + ' ' + w).strip()
            if c.stringWidth(t, 'Inter-Light', 6) <= card_w2 - 8*mm:
                line = t
            else:
                if ty > y - CARD_H + 2*mm:
                    c.drawCentredString(px, ty, line)
                    ty -= 3.5*mm
                line = w
        if line and ty > y - CARD_H + 2*mm:
            c.drawCentredString(px, ty, line)

    y = y - CARD_H - 5*mm

    # contact gold band
    band_h = 14*mm
    c.setFillColor(GOLD)
    c.rect(0, y - band_h, W, band_h, fill=1, stroke=0)
    c.setFillColor(BLACK)
    c.setFont('Inter', 5.5)
    label_str = 'GET IN TOUCH'
    for i, ch in enumerate(label_str):
        pass
    c.drawString(MAR_L, y - 4.5*mm, 'GET IN TOUCH')
    c.setFont('Playfair', 11)
    c.drawString(MAR_L, y - 9*mm, 'info@figment.global  ·  +91 74487 55866  ·  figment.global')

    footer_bar(c)


# ══════════════════════════════════════════════════════════════════════════════
#  SAT BROCHURE
# ══════════════════════════════════════════════════════════════════════════════

def make_sat():
    path = f'{OUT_DIR}/Figment_SAT_Brochure.pdf'
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle('Figment — SAT Programme Brochure')

    # ── Page 1: Cover ────────────────────────────────────────────────────────
    bg(c, BLACK)
    # navy side panel
    c.setFillColor(NAVY)
    c.rect(W * 0.62, 0, W * 0.38, H, fill=1, stroke=0)
    # subtle diagonal lines on navy panel
    c.setStrokeColor(Color(1,1,1,0.03))
    c.setLineWidth(0.5)
    for i in range(0, int(W*0.38 + H), 18):
        c.line(W*0.62, H - i, min(W, W*0.62 + i), H)

    nav_brand(c)

    # hero text — bottom third of page
    y = H * 0.52
    label(c, 'SAT Preparation Programme', MAR_L, y, size=6.5)
    y -= 8*mm

    c.setFillColor(IVORY)
    c.setFont('Playfair', 62)
    c.drawString(MAR_L, y, 'Crack')
    y -= 58*mm * 0.88
    c.setFillColor(GOLD)
    c.setFont('Cormorant-Italic', 68)
    c.drawString(MAR_L, y, 'the SAT.')
    y -= 12*mm

    gold_rule(c, MAR_L, y, 15*mm)
    y -= 7*mm

    c.setFillColor(IVORY_65)
    c.setFont('Cormorant-Italic', 12)
    desc = 'Structured coaching. Adaptive strategy. Real exam simulation.'
    c.drawString(MAR_L, y, desc)
    y -= 10*mm

    # stats row
    stats = [('1600', 'Max Score'), ('26', 'Sessions (Batch)'), ('5', 'Mock Tests'), ('₹55K', 'Starting From')]
    sw = CONTENT_W * 0.58 / len(stats)
    for i, (sv, sl) in enumerate(stats):
        sx = MAR_L + i * sw + sw/2
        c.setFillColor(GOLD)
        c.setFont('Playfair', 20)
        c.drawCentredString(sx, y, sv)
        c.setFillColor(GREY)
        c.setFont('Inter', 5.5)
        c.drawCentredString(sx, y - 5.5*mm, sl.upper())

    footer_bar(c, 1)
    c.showPage()

    # ── Page 2: About the SAT + Program Cards ───────────────────────────────
    bg(c, CHARCOAL)
    nav_brand(c)

    y = H - 22*mm
    label(c, 'About the SAT', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 24)
    c.drawString(MAR_L, y, 'Know your exam.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 7*mm

    # SAT quick facts in 4 boxes
    facts = [
        ('1600', 'Max Score', '800 each section'),
        ('2h 14m', 'Exam Duration', 'No calculator needed'),
        ('2 Sections', 'R&W + Math', 'Digital Adaptive'),
        ('4x/year', 'Test Dates', 'India — Aug to May'),
    ]
    box_w = CONTENT_W / 4 - 2*mm
    box_h = 22*mm
    for i, (val, lbl, sub) in enumerate(facts):
        bx = MAR_L + i * (box_w + 2.67*mm)
        c.setFillColor(WHITE_05)
        c.rect(bx, y - box_h, box_w, box_h, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont('Playfair', 16)
        c.drawCentredString(bx + box_w/2, y - 7*mm, val)
        c.setFillColor(IVORY)
        c.setFont('Inter-Medium', 6.5)
        c.drawCentredString(bx + box_w/2, y - 12*mm, lbl)
        c.setFillColor(GREY)
        c.setFont('Inter-Light', 5.5)
        c.drawCentredString(bx + box_w/2, y - 15.5*mm, sub)
    y -= box_h + 8*mm

    # Section description
    c.setFillColor(GOLD)
    c.setFont('Cormorant-Italic', 10)
    c.drawString(MAR_L, y, 'Digital SAT · Adaptive · 2 Modules per Section')
    y -= 4*mm
    y = body_text(c, 'The SAT tests critical thinking across Reading & Writing and Math. The digital format is adaptive — module 2 difficulty adjusts based on your module 1 performance. Figment\'s programme trains you to master both the content and the adaptive strategy.', MAR_L, y, size=8, max_width=CONTENT_W, col=IVORY_65)
    y -= 5*mm

    horiz_rule(c, MAR_L, y)
    y -= 7*mm

    # Programme Cards heading
    label(c, 'Choose Your Programme', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawString(MAR_L, y, 'Two paths to your target score.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 8*mm

    # Two programme cards side by side
    card_w = CONTENT_W / 2 - 3*mm
    card_h = 105*mm

    # Batch card
    bx = MAR_L
    c.setFillColor(Color(0,0,0,0.4))
    c.rect(bx, y - card_h, card_w, card_h, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(bx, y, card_w, 2, fill=1, stroke=0)

    cy = y - 6*mm
    label(c, 'Batch Programme', bx + 5*mm, cy)
    cy -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 14)
    c.drawString(bx + 5*mm, cy, 'SAT Batch Coaching')
    cy -= 4*mm
    c.setFillColor(GREY)
    c.setFont('Cormorant-Italic', 8)
    c.drawString(bx + 5*mm, cy, 'Online · Small Group · Focused')
    cy -= 5*mm
    horiz_rule(c, bx + 5*mm, cy, card_w - 10*mm)
    cy -= 5*mm

    # stats
    bstats = [('26', 'Sessions'), ('52 hrs', 'Content'), ('5', 'Mocks')]
    sw2 = (card_w - 10*mm) / 3
    for i, (sv, sl) in enumerate(bstats):
        sx = bx + 5*mm + i*sw2 + sw2/2
        c.setFillColor(GOLD)
        c.setFont('Playfair', 16)
        c.drawCentredString(sx, cy, sv)
        c.setFillColor(GREY)
        c.setFont('Inter', 5.5)
        c.drawCentredString(sx, cy - 5*mm, sl.upper())
    cy -= 12*mm

    batch_features = [
        '26 structured sessions across 8 SAT domains',
        '52 hours of content — R&W + Math in depth',
        '5 full-length mock tests (official College Board format)',
        'Score tracker & personalised error log',
        'WhatsApp doubt support between sessions',
        'Access to 3,000+ practice questions',
    ]
    for feat in batch_features:
        horiz_rule(c, bx + 5*mm, cy + 1*mm, card_w - 10*mm)
        cy -= 2.5*mm
        c.setFillColor(IVORY_65)
        c.setFont('Inter-Light', 7)
        c.drawString(bx + 5*mm, cy, feat)
        cy -= 5*mm
    cy -= 1*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawString(bx + 5*mm, cy, '₹55,000')
    c.setFillColor(GREY)
    c.setFont('Inter-Light', 6)
    c.drawString(bx + 5*mm, cy - 4.5*mm, 'inclusive of all study materials')

    # Private card
    px2 = MAR_L + card_w + 6*mm
    c.setFillColor(NAVY)
    c.rect(px2, y - card_h, card_w, card_h, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(px2, y, card_w, 2, fill=1, stroke=0)

    cy = y - 6*mm
    label(c, 'Private Coaching', px2 + 5*mm, cy)
    cy -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 14)
    c.drawString(px2 + 5*mm, cy, 'SAT Private Coaching')
    cy -= 4*mm
    c.setFillColor(GREY)
    c.setFont('Cormorant-Italic', 8)
    c.drawString(px2 + 5*mm, cy, 'One-on-One · Personalised · Accelerated')
    cy -= 5*mm
    horiz_rule(c, px2 + 5*mm, cy, card_w - 10*mm)
    cy -= 5*mm

    pstats = [('15', 'Sessions'), ('30 hrs', 'Content'), ('5', 'Mocks')]
    for i, (sv, sl) in enumerate(pstats):
        sx = px2 + 5*mm + i*sw2 + sw2/2
        c.setFillColor(GOLD)
        c.setFont('Playfair', 16)
        c.drawCentredString(sx, cy, sv)
        c.setFillColor(GREY)
        c.setFont('Inter', 5.5)
        c.drawCentredString(sx, cy - 5*mm, sl.upper())
    cy -= 12*mm

    private_features = [
        '15 personalised 1:1 sessions with your coach',
        '30 hours of focussed, targeted instruction',
        '5 full-length mocks + detailed score analysis',
        'Custom study plan built around your weak areas',
        'Priority doubt-clearing — same-day response',
        'Flexible scheduling to suit school/board exams',
    ]
    for feat in private_features:
        horiz_rule(c, px2 + 5*mm, cy + 1*mm, card_w - 10*mm)
        cy -= 2.5*mm
        c.setFillColor(IVORY_65)
        c.setFont('Inter-Light', 7)
        c.drawString(px2 + 5*mm, cy, feat)
        cy -= 5*mm
    cy -= 1*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawString(px2 + 5*mm, cy, '₹85,000')
    c.setFillColor(GREY)
    c.setFont('Inter-Light', 6)
    c.drawString(px2 + 5*mm, cy - 4.5*mm, 'inclusive of all study materials')

    footer_bar(c, 2)
    c.showPage()

    # ── Page 3: Curriculum + How We Teach ───────────────────────────────────
    bg(c, BLACK)
    nav_brand(c)

    y = H - 22*mm
    label(c, 'Curriculum', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 24)
    c.drawString(MAR_L, y, 'What we cover.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 7*mm

    # Two curriculum columns: R&W and Math
    col_w = CONTENT_W / 2 - 3*mm
    rw_domains = [
        ('Craft & Structure',          '28%', 'Words in Context · Text Structure · Cross-text Connections'),
        ('Information & Ideas',        '26%', 'Main Idea · Details · Quantitative Evidence · Inferences'),
        ('Standard English Conventions','26%', 'Grammar · Sentence Boundaries · Punctuation · Form/Structure'),
        ('Expression of Ideas',        '20%', 'Rhetorical Synthesis · Transitions · Organization'),
    ]
    math_domains = [
        ('Algebra',                    '35%', 'Linear Equations · Functions · Systems of Equations'),
        ('Advanced Math',              '35%', 'Quadratics · Polynomials · Rational Expressions · Radicals'),
        ('Problem-Solving & Data',     '15%', 'Ratios · Rates · Statistics · Probability'),
        ('Geometry & Trigonometry',    '15%', 'Area · Volume · Circles · Trigonometry'),
    ]

    for col_i, (col_title, col_pct, domains) in enumerate([
        ('Reading & Writing', '800 pts', rw_domains),
        ('Math', '800 pts', math_domains),
    ]):
        cx = MAR_L + col_i * (col_w + 6*mm)
        # column bg
        c.setFillColor(Color(11/255, 44/255, 74/255, 0.35))
        col_h = 4 * 20*mm + 20*mm
        c.rect(cx, y - col_h, col_w, col_h, fill=1, stroke=0)
        # column header
        c.setFillColor(NAVY)
        c.rect(cx, y - 12*mm, col_w, 12*mm, fill=1, stroke=0)
        c.setFillColor(IVORY)
        c.setFont('Playfair', 12)
        c.drawString(cx + 4*mm, y - 7.5*mm, col_title)
        c.setFillColor(GOLD)
        c.setFont('Inter', 6)
        c.drawRightString(cx + col_w - 4*mm, y - 7.5*mm, col_pct)

        dy = y - 16*mm
        for dname, dpct, dtopics in domains:
            horiz_rule(c, cx + 4*mm, dy + 1*mm, col_w - 8*mm)
            dy -= 3*mm
            c.setFillColor(IVORY)
            c.setFont('Inter-Medium', 7.5)
            c.drawString(cx + 4*mm, dy, dname)
            c.setFillColor(GOLD)
            c.setFont('Playfair', 7.5)
            c.drawRightString(cx + col_w - 4*mm, dy, dpct)
            dy -= 4*mm
            c.setFillColor(IVORY_40)
            c.setFont('Inter-Light', 6)
            # wrap topics
            words = dtopics.split()
            line = ''
            for w in words:
                t = (line + ' ' + w).strip()
                if c.stringWidth(t, 'Inter-Light', 6) <= col_w - 8*mm:
                    line = t
                else:
                    c.drawString(cx + 4*mm, dy, line)
                    dy -= 3.5*mm
                    line = w
            if line:
                c.drawString(cx + 4*mm, dy, line)
            dy -= 6*mm

    y -= col_h + 8*mm

    # How We Teach
    label(c, 'Methodology', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawString(MAR_L, y, 'The Figment Method.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 7*mm

    steps = [
        ('01', 'Diagnostic Assessment',
         'Every student begins with a full-length mock test. We identify your exact starting score, domain strengths, and weak zones before a single session begins.'),
        ('02', 'Personalised Learning Map',
         'Based on the diagnostic, we build a prioritised study plan — allocating more time to high-value, high-error domains for maximum score gains.'),
        ('03', 'Structured Coaching Sessions',
         '26 sessions (Batch) or 15 private sessions covering all 8 SAT domains with exam-level practice, timed drills, and strategy walkthroughs.'),
        ('04', 'Mock Tests & Score Tracking',
         '5 full-length official-format mocks throughout the programme. Each mock is reviewed question-by-question to close error patterns before exam day.'),
    ]
    step_h = 15*mm
    for snum, stitle, sbody in steps:
        c.setFillColor(WHITE_05)
        c.rect(MAR_L, y - step_h, CONTENT_W, step_h, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont('Cormorant-Italic', 16)
        c.drawString(MAR_L + 4*mm, y - 9*mm, snum)
        c.setFillColor(IVORY)
        c.setFont('Playfair', 10)
        c.drawString(MAR_L + 18*mm, y - 5.5*mm, stitle)
        body_text(c, sbody, MAR_L + 18*mm, y - 10*mm, size=7, col=GREY,
                  max_width=CONTENT_W - 22*mm)
        y -= step_h + 1.5*mm

    footer_bar(c, 3)
    c.showPage()

    # ── Page 4: Crash Course + Why Figment ──────────────────────────────────
    bg(c, CHARCOAL)
    nav_brand(c)

    y = H - 22*mm
    label(c, 'Also Available', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 22)
    c.drawString(MAR_L, y, 'SAT Crash Course')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 8*mm

    # Crash course box
    c.setFillColor(NAVY)
    c.rect(MAR_L, y - 40*mm, CONTENT_W, 40*mm, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(MAR_L, y, CONTENT_W, 2, fill=1, stroke=0)

    c.setFillColor(IVORY)
    c.setFont('Playfair', 14)
    c.drawString(MAR_L + 6*mm, y - 8*mm, 'Quick Prep — 2 Weeks Before Exam')
    c.setFillColor(IVORY_65)
    c.setFont('Inter-Light', 7.5)
    crash_text = '8 high-intensity sessions · Rapid error analysis · 2 full-length mocks · Last-mile strategy · Designed for students who have already done some prep and need a final push.'
    body_text(c, crash_text, MAR_L + 6*mm, y - 14*mm, size=7.5, col=IVORY_65,
              max_width=CONTENT_W * 0.65)
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawRightString(MAR_L + CONTENT_W - 6*mm, y - 14*mm, '₹18,000')
    c.setFillColor(GREY)
    c.setFont('Inter-Light', 6)
    c.drawRightString(MAR_L + CONTENT_W - 6*mm, y - 19*mm, '8 sessions · 2 mocks')

    y -= 50*mm

    # Compare table
    label(c, 'Programme Comparison', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawString(MAR_L, y, 'Find your right fit.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 7*mm

    headers = ['', 'Batch', 'Private', 'Crash Course']
    col_widths = [50*mm, 40*mm, 40*mm, 40*mm]
    rows = [
        ('Sessions',    '26',       '15',           '8'),
        ('Duration',    '52 hours', '30 hours',     '16 hours'),
        ('Mock Tests',  '5',        '5',            '2'),
        ('Format',      'Group',    '1-on-1',       'Group'),
        ('Best for',    'Steady prep','Flexible/fast','Last-minute'),
        ('Price',       '₹55,000',  '₹85,000',      '₹18,000'),
    ]
    row_h = 7*mm
    # header row
    c.setFillColor(NAVY)
    c.rect(MAR_L, y - row_h, CONTENT_W, row_h, fill=1, stroke=0)
    cx = MAR_L
    for hi, hdr in enumerate(headers):
        cw = col_widths[hi]
        c.setFillColor(GOLD if hi > 0 else GREY)
        c.setFont('Inter-Medium', 7)
        if hi == 0:
            c.drawString(cx + 3*mm, y - 4.5*mm, hdr)
        else:
            c.drawCentredString(cx + cw/2, y - 4.5*mm, hdr)
        cx += cw
    y -= row_h

    for ri, row in enumerate(rows):
        bg_c = WHITE_05 if ri % 2 == 0 else Color(0,0,0,0)
        c.setFillColor(bg_c)
        c.rect(MAR_L, y - row_h, CONTENT_W, row_h, fill=1, stroke=0)
        cx = MAR_L
        for ci, cell in enumerate(row):
            cw = col_widths[ci]
            if ci == 0:
                c.setFillColor(GREY)
                c.setFont('Inter-Medium', 7)
                c.drawString(cx + 3*mm, y - 4.5*mm, cell)
            else:
                is_price = row[0] == 'Price'
                c.setFillColor(GOLD if is_price else IVORY_65)
                c.setFont('Playfair' if is_price else 'Inter-Light', 8 if is_price else 7)
                c.drawCentredString(cx + cw/2, y - 4.5*mm, cell)
            cx += cw
        y -= row_h

    y -= 10*mm

    # Why Figment
    label(c, 'Why Figment', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawString(MAR_L, y, 'The Figment difference.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 7*mm

    why = [
        ('Expert faculty', 'IIM and top-university alumni who combine subject mastery with real admissions insight.'),
        ('Adaptive coaching', 'Every lesson adjusts to your score trajectory — not a fixed syllabus regardless of performance.'),
        ('Official-format mocks', '5 full-length tests mirroring the exact digital SAT interface for zero exam-day surprises.'),
        ('Proven results', 'Students consistently hit target scores with an average improvement of 120+ points.'),
    ]
    why_w = CONTENT_W / 2 - 3*mm
    why_h = 22*mm
    for i, (wt, wb) in enumerate(why):
        wx = MAR_L + (i % 2) * (why_w + 6*mm)
        wy = y - (i // 2) * (why_h + 3*mm)
        c.setFillColor(WHITE_05)
        c.rect(wx, wy - why_h, why_w, why_h, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(wx, wy - why_h, 2, why_h, fill=1, stroke=0)
        c.setFillColor(IVORY)
        c.setFont('Playfair', 10)
        c.drawString(wx + 5*mm, wy - 7*mm, wt)
        body_text(c, wb, wx + 5*mm, wy - 12*mm, size=7, col=GREY,
                  max_width=why_w - 8*mm)

    footer_bar(c, 4)

    # Team page
    draw_team_page(c)

    c.save()
    print(f'✓  SAT brochure saved → {path}')
    return path


# ══════════════════════════════════════════════════════════════════════════════
#  GRE BROCHURE
# ══════════════════════════════════════════════════════════════════════════════

def make_gre():
    path = f'{OUT_DIR}/Figment_GRE_Brochure.pdf'
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle('Figment — GRE Programme Brochure')

    # ── Page 1: Cover ────────────────────────────────────────────────────────
    bg(c, BLACK)
    c.setFillColor(NAVY)
    c.rect(0, 0, W * 0.38, H, fill=1, stroke=0)
    c.setStrokeColor(Color(1,1,1,0.03))
    c.setLineWidth(0.5)
    for i in range(0, int(W*0.38 + H), 18):
        c.line(0, H - i, min(W*0.38, i), H)

    nav_brand(c)

    y = H * 0.52
    label(c, 'GRE Preparation Programme', MAR_L, y, size=6.5)
    y -= 8*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 55)
    c.drawString(MAR_L, y, 'Your Score.')
    y -= 52*mm * 0.88
    c.setFillColor(GOLD)
    c.setFont('Cormorant-Italic', 60)
    c.drawString(MAR_L, y, 'Unlocked.')
    y -= 12*mm

    gold_rule(c, MAR_L, y, 15*mm)
    y -= 7*mm

    c.setFillColor(IVORY_65)
    c.setFont('Cormorant-Italic', 12)
    c.drawString(MAR_L, y, 'Verbal Precision. Quant Mastery. Essay Excellence.')
    y -= 10*mm

    stats = [('340', 'Max Score'), ('50', 'Sessions'), ('75 hrs', 'Content'), ('10', 'Mock Tests')]
    sw = CONTENT_W * 0.65 / len(stats)
    for i, (sv, sl) in enumerate(stats):
        sx = MAR_L + i*sw + sw/2
        c.setFillColor(GOLD)
        c.setFont('Playfair', 20)
        c.drawCentredString(sx, y, sv)
        c.setFillColor(GREY)
        c.setFont('Inter', 5.5)
        c.drawCentredString(sx, y - 5.5*mm, sl.upper())

    footer_bar(c, 1)
    c.showPage()

    # ── Page 2: Test Overview + Programme ───────────────────────────────────
    bg(c, CHARCOAL)
    nav_brand(c)

    y = H - 22*mm
    label(c, 'About the GRE', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 24)
    c.drawString(MAR_L, y, 'Know your exam.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 7*mm

    facts = [
        ('260–340', 'Score Range', 'Verbal + Quant'),
        ('~2h', 'Duration', 'Adaptive sections'),
        ('3 Sections', 'V + Q + AWA', '2 tasks + 2+2 modules'),
        ('ETS', 'Test Maker', 'Accepted worldwide'),
    ]
    box_w = CONTENT_W / 4 - 2*mm
    box_h = 22*mm
    for i, (val, lbl, sub) in enumerate(facts):
        bx = MAR_L + i * (box_w + 2.67*mm)
        c.setFillColor(WHITE_05)
        c.rect(bx, y - box_h, box_w, box_h, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont('Playfair', 14)
        c.drawCentredString(bx + box_w/2, y - 7*mm, val)
        c.setFillColor(IVORY)
        c.setFont('Inter-Medium', 6.5)
        c.drawCentredString(bx + box_w/2, y - 12*mm, lbl)
        c.setFillColor(GREY)
        c.setFont('Inter-Light', 5.5)
        c.drawCentredString(bx + box_w/2, y - 15.5*mm, sub)
    y -= box_h + 8*mm

    body_text(c, 'The GRE General Test is accepted by thousands of graduate and business schools worldwide, including top MBA programmes. Its Verbal Reasoning, Quantitative Reasoning, and Analytical Writing sections test the high-level cognitive skills required for graduate study. Figment\'s GRE programme is designed to maximise your score across all three in the shortest possible time.', MAR_L, y, size=8, max_width=CONTENT_W, col=IVORY_65)
    y -= 32*mm

    horiz_rule(c, MAR_L, y)
    y -= 7*mm

    # Programme card
    label(c, 'Programme Details', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawString(MAR_L, y, 'Online Batch Programme.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 8*mm

    # Single programme box
    box_h2 = 80*mm
    c.setFillColor(NAVY)
    c.rect(MAR_L, y - box_h2, CONTENT_W, box_h2, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(MAR_L, y, CONTENT_W, 2, fill=1, stroke=0)

    cy = y - 7*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 16)
    c.drawString(MAR_L + 6*mm, cy, 'GRE Batch Coaching — Online')
    cy -= 4.5*mm
    c.setFillColor(GREY)
    c.setFont('Cormorant-Italic', 9)
    c.drawString(MAR_L + 6*mm, cy, 'Small-batch · Live sessions · Comprehensive coverage')
    cy -= 6*mm

    pstats = [('50', 'Sessions'), ('75 hrs', 'Content'), ('10', 'Mock Tests'), ('3+', 'Batch Timings')]
    sw3 = CONTENT_W / len(pstats)
    for i, (sv, sl) in enumerate(pstats):
        sx = MAR_L + i*sw3 + sw3/2
        c.setFillColor(GOLD)
        c.setFont('Playfair', 18)
        c.drawCentredString(sx, cy, sv)
        c.setFillColor(GREY)
        c.setFont('Inter', 5.5)
        c.drawCentredString(sx, cy - 5*mm, sl.upper())
    cy -= 12*mm

    horiz_rule(c, MAR_L + 6*mm, cy, CONTENT_W - 12*mm)
    cy -= 4*mm

    feats = [
        '50 structured sessions covering all GRE sections',
        'Verbal: 1,000+ vocabulary building, RC strategies, SE/TC',
        'Quant: Arithmetic, Algebra, Geometry, Data Analysis',
        'AWA: Issue + Argument essay templates, scoring rubric',
        '10 full-length mock tests with performance analytics',
        'Multiple batch timings: morning, evening, weekend',
    ]
    col2 = len(feats) // 2
    for i, feat in enumerate(feats):
        fx = MAR_L + 6*mm + (i // col2) * CONTENT_W/2
        c.setFillColor(IVORY_65)
        c.setFont('Inter-Light', 7)
        c.drawString(fx, cy - (i % col2) * 6*mm, '· ' + feat)
    cy -= (col2 + 1) * 6*mm
    cy = y - box_h2 + 10*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 16)
    c.drawString(MAR_L + 6*mm, cy, 'Contact us for current pricing')
    c.setFillColor(GREY)
    c.setFont('Inter-Light', 6)
    c.drawString(MAR_L + 6*mm, cy - 4.5*mm, 'info@figment.global  ·  +91 74487 55866')

    y -= box_h2 + 8*mm

    footer_bar(c, 2)
    c.showPage()

    # ── Page 3: Curriculum + Why Figment ────────────────────────────────────
    bg(c, BLACK)
    nav_brand(c)

    y = H - 22*mm
    label(c, 'Curriculum', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 24)
    c.drawString(MAR_L, y, 'Every section. In depth.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 8*mm

    sections = [
        ('Verbal Reasoning', '170 pts', [
            ('Text Completion',       'Fill 1–3 blanks; context-based vocabulary'),
            ('Sentence Equivalence',  'Choose 2 words that give the same meaning'),
            ('Reading Comprehension', 'Passage-based: main idea, inference, detail'),
            ('Vocabulary Strategy',   '1,000+ high-frequency GRE word list'),
        ]),
        ('Quantitative Reasoning', '170 pts', [
            ('Arithmetic',            'Number properties, fractions, percentages, ratios'),
            ('Algebra',               'Equations, inequalities, functions, coordinate geometry'),
            ('Geometry',              'Lines, angles, polygons, circles, 3D figures'),
            ('Data Analysis',         'Statistics, probability, data interpretation sets'),
        ]),
        ('Analytical Writing', '6 pts', [
            ('Analyse an Issue',      'Build a structured argument; 30-minute essay'),
            ('Analyse an Argument',   'Evaluate a flawed argument; 30-minute essay'),
            ('Template Strategy',     'Proven templates for 5+ scored essays'),
            ('Scoring Rubric',        'Understand exactly what graders look for'),
        ]),
    ]
    sec_w = CONTENT_W / 3 - 3*mm
    for si, (stitle, smax, srows) in enumerate(sections):
        sx = MAR_L + si * (sec_w + 4.5*mm)
        sec_h = len(srows) * 16*mm + 20*mm
        c.setFillColor(Color(11/255, 44/255, 74/255, 0.3))
        c.rect(sx, y - sec_h, sec_w, sec_h, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.rect(sx, y - 13*mm, sec_w, 13*mm, fill=1, stroke=0)
        c.setFillColor(IVORY)
        c.setFont('Playfair', 10)
        # wrap title
        c.drawString(sx + 3*mm, y - 7*mm, stitle)
        c.setFillColor(GOLD)
        c.setFont('Inter', 6)
        c.drawRightString(sx + sec_w - 3*mm, y - 7*mm, smax)
        dy = y - 17*mm
        for rname, rdesc in srows:
            horiz_rule(c, sx + 3*mm, dy + 1*mm, sec_w - 6*mm)
            dy -= 3*mm
            c.setFillColor(IVORY)
            c.setFont('Inter-Medium', 7)
            c.drawString(sx + 3*mm, dy, rname)
            dy -= 3.5*mm
            c.setFillColor(IVORY_40)
            c.setFont('Inter-Light', 6)
            words = rdesc.split()
            line = ''
            for w in words:
                t = (line + ' ' + w).strip()
                if c.stringWidth(t, 'Inter-Light', 6) <= sec_w - 6*mm:
                    line = t
                else:
                    c.drawString(sx + 3*mm, dy, line)
                    dy -= 3.5*mm
                    line = w
            if line:
                c.drawString(sx + 3*mm, dy, line)
            dy -= 5.5*mm

    y -= max(len(s[2]) for s in sections) * 16*mm + 28*mm

    # Why Figment
    label(c, 'Why Figment', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawString(MAR_L, y, 'The Figment difference.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 7*mm

    why = [
        ('Targeted vocabulary system', 'Spaced repetition + context-learning for 1,000+ words that actually appear on the GRE.'),
        ('Data-driven progress tracking', '10 full mocks with section-by-section performance analytics and score projection.'),
        ('Expert AWA coaching', 'Live essay reviews with scored feedback — not just templates but actual grader perspective.'),
        ('Flexible scheduling', 'Morning, evening, and weekend batch options to fit around your work or college calendar.'),
    ]
    why_w = CONTENT_W / 2 - 3*mm
    why_h = 20*mm
    for i, (wt, wb) in enumerate(why):
        wx = MAR_L + (i % 2) * (why_w + 6*mm)
        wy = y - (i // 2) * (why_h + 3*mm)
        c.setFillColor(WHITE_05)
        c.rect(wx, wy - why_h, why_w, why_h, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(wx, wy - why_h, 2, why_h, fill=1, stroke=0)
        c.setFillColor(IVORY)
        c.setFont('Playfair', 10)
        c.drawString(wx + 5*mm, wy - 7*mm, wt)
        body_text(c, wb, wx + 5*mm, wy - 12*mm, size=7, col=GREY,
                  max_width=why_w - 8*mm)

    footer_bar(c, 3)

    draw_team_page(c)
    c.save()
    print(f'✓  GRE brochure saved → {path}')
    return path


# ══════════════════════════════════════════════════════════════════════════════
#  GMAT BROCHURE
# ══════════════════════════════════════════════════════════════════════════════

def make_gmat():
    path = f'{OUT_DIR}/Figment_GMAT_Brochure.pdf'
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle('Figment — GMAT Focus Programme Brochure')

    # Cover
    bg(c, BLACK)
    c.setFillColor(Color(11/255, 44/255, 74/255, 0.7))
    c.rect(0, H * 0.65, W, H * 0.35, fill=1, stroke=0)
    nav_brand(c)

    y = H * 0.52
    label(c, 'GMAT Focus Edition Programme', MAR_L, y, size=6.5)
    y -= 8*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 55)
    c.drawString(MAR_L, y, 'Master')
    y -= 52*mm * 0.88
    c.setFillColor(GOLD)
    c.setFont('Cormorant-Italic', 60)
    c.drawString(MAR_L, y, 'the GMAT.')
    y -= 12*mm
    gold_rule(c, MAR_L, y, 15*mm)
    y -= 7*mm
    c.setFillColor(IVORY_65)
    c.setFont('Cormorant-Italic', 12)
    c.drawString(MAR_L, y, 'Quant. Verbal. Data Insights. Admission-ready scores.')
    y -= 10*mm

    stats = [('805', 'Max Score'), ('40', 'Classes'), ('60 hrs', 'Content'), ('8', 'Mock Tests'), ('₹48K', 'Investment')]
    sw = CONTENT_W * 0.78 / len(stats)
    for i, (sv, sl) in enumerate(stats):
        sx = MAR_L + i*sw + sw/2
        c.setFillColor(GOLD)
        c.setFont('Playfair', 18)
        c.drawCentredString(sx, y, sv)
        c.setFillColor(GREY)
        c.setFont('Inter', 5.5)
        c.drawCentredString(sx, y - 5.5*mm, sl.upper())

    footer_bar(c, 1)
    c.showPage()

    # Page 2: Test overview + programme
    bg(c, CHARCOAL)
    nav_brand(c)
    y = H - 22*mm
    label(c, 'About the GMAT', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 24)
    c.drawString(MAR_L, y, 'GMAT Focus Edition — what\'s changed.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 7*mm

    facts = [
        ('205–805', 'Score Range', 'New scoring scale'),
        ('2h 15m', 'Duration', 'Focus Edition'),
        ('3 Sections', 'Q + V + DI', '64 questions total'),
        ('GMAC', 'Test Maker', 'Top B-schools globally'),
    ]
    box_w = CONTENT_W / 4 - 2*mm
    box_h = 22*mm
    for i, (val, lbl, sub) in enumerate(facts):
        bx = MAR_L + i * (box_w + 2.67*mm)
        c.setFillColor(WHITE_05)
        c.rect(bx, y - box_h, box_w, box_h, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont('Playfair', 13)
        c.drawCentredString(bx + box_w/2, y - 7*mm, val)
        c.setFillColor(IVORY)
        c.setFont('Inter-Medium', 6.5)
        c.drawCentredString(bx + box_w/2, y - 12*mm, lbl)
        c.setFillColor(GREY)
        c.setFont('Inter-Light', 5.5)
        c.drawCentredString(bx + box_w/2, y - 15.5*mm, sub)
    y -= box_h + 8*mm

    body_text(c, 'The GMAT Focus Edition is the new standard for MBA admissions. Gone is the AWA section — replaced by Data Insights which tests data literacy, the skill set most in demand at top B-schools. Figment\'s GMAT programme is specifically built for the Focus Edition, covering all three sections with the depth and speed required for 700+ scores.', MAR_L, y, size=8, max_width=CONTENT_W, col=IVORY_65)
    y -= 34*mm

    horiz_rule(c, MAR_L, y)
    y -= 7*mm

    label(c, 'Programme Details', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawString(MAR_L, y, 'Batch Coaching Programme.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 8*mm

    box_h2 = 75*mm
    c.setFillColor(NAVY)
    c.rect(MAR_L, y - box_h2, CONTENT_W, box_h2, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(MAR_L, y, CONTENT_W, 2, fill=1, stroke=0)

    cy = y - 7*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 14)
    c.drawString(MAR_L + 6*mm, cy, 'GMAT Focus Batch Coaching — Online')
    cy -= 5*mm
    c.setFillColor(GREY)
    c.setFont('Cormorant-Italic', 9)
    c.drawString(MAR_L + 6*mm, cy, 'Live sessions · Structured curriculum · GMAC official materials')
    cy -= 7*mm

    gmat_stats = [('40', 'Classes'), ('60 hrs', 'Content'), ('8', 'Mock Tests'), ('700+', 'Target Score')]
    sw3 = CONTENT_W / len(gmat_stats)
    for i, (sv, sl) in enumerate(gmat_stats):
        sx = MAR_L + i*sw3 + sw3/2
        c.setFillColor(GOLD)
        c.setFont('Playfair', 18)
        c.drawCentredString(sx, cy, sv)
        c.setFillColor(GREY)
        c.setFont('Inter', 5.5)
        c.drawCentredString(sx, cy - 5*mm, sl.upper())
    cy -= 12*mm

    horiz_rule(c, MAR_L + 6*mm, cy, CONTENT_W - 12*mm)
    cy -= 4*mm

    feats = [
        'Quant (21 Q, 45 min): Algebra, Arithmetic, Geometry',
        'Verbal (23 Q, 45 min): Critical Reasoning, Reading Comp.',
        'Data Insights (20 Q, 45 min): DS, MSR, TA, TPA, GI',
        '8 full-length Focus Edition mock tests',
        'Error tracking + score projection worksheets',
        'GMAC Official Practice problems integrated',
    ]
    for i, feat in enumerate(feats):
        c.setFillColor(IVORY_65)
        c.setFont('Inter-Light', 7)
        fx = MAR_L + 6*mm + (i % 2) * CONTENT_W/2
        c.drawString(fx, cy - (i // 2) * 6*mm, '· ' + feat)

    cy = y - box_h2 + 10*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawString(MAR_L + 6*mm, cy, '₹48,000')
    c.setFillColor(GREY)
    c.setFont('Inter-Light', 6)
    c.drawString(MAR_L + 6*mm, cy - 4.5*mm, 'inclusive of all study materials')

    footer_bar(c, 2)
    c.showPage()

    # Page 3: Curriculum + Why Figment
    bg(c, BLACK)
    nav_brand(c)
    y = H - 22*mm
    label(c, 'Curriculum', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 24)
    c.drawString(MAR_L, y, 'Three sections. Total mastery.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 8*mm

    gmat_sections = [
        ('Quantitative Reasoning', '21 Qs · 45 min', [
            ('Problem Solving',      'Standard multiple-choice quant problems'),
            ('Arithmetic',           'Number theory, fractions, percentages, ratios'),
            ('Algebra',              'Equations, functions, coordinate geometry'),
            ('Geometry',             'Lines, triangles, circles, coordinate geometry'),
        ]),
        ('Verbal Reasoning', '23 Qs · 45 min', [
            ('Critical Reasoning',   'Strengthen/weaken, assumption, inference, flaw'),
            ('Reading Comprehension','Long & short passages: main point, detail, inference'),
            ('Argument Analysis',    'Evaluate argument logic and identify assumptions'),
            ('Pacing Strategy',      'Time management across 23 questions in 45 minutes'),
        ]),
        ('Data Insights', '20 Qs · 45 min', [
            ('Data Sufficiency',     'Classic DS: two-statement sufficiency analysis'),
            ('Multi-Source Reasoning','Interpret tables, graphs, and passages together'),
            ('Table Analysis',       'Sort and analyse tabular data to answer questions'),
            ('Graphics Interpretation','Scatter plots, bar charts — fill-in-blank format'),
        ]),
    ]
    sec_w = CONTENT_W / 3 - 3*mm
    for si, (stitle, smax, srows) in enumerate(gmat_sections):
        sx = MAR_L + si * (sec_w + 4.5*mm)
        sec_h = len(srows) * 16*mm + 22*mm
        c.setFillColor(Color(11/255, 44/255, 74/255, 0.3))
        c.rect(sx, y - sec_h, sec_w, sec_h, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.rect(sx, y - 15*mm, sec_w, 15*mm, fill=1, stroke=0)
        c.setFillColor(IVORY)
        c.setFont('Playfair', 10)
        c.drawString(sx + 3*mm, y - 7*mm, stitle)
        c.setFillColor(GOLD)
        c.setFont('Inter', 6)
        c.drawString(sx + 3*mm, y - 11*mm, smax)
        dy = y - 19*mm
        for rname, rdesc in srows:
            horiz_rule(c, sx + 3*mm, dy + 1*mm, sec_w - 6*mm)
            dy -= 3*mm
            c.setFillColor(IVORY)
            c.setFont('Inter-Medium', 7)
            c.drawString(sx + 3*mm, dy, rname)
            dy -= 3.5*mm
            c.setFillColor(IVORY_40)
            c.setFont('Inter-Light', 6)
            words = rdesc.split()
            line = ''
            for w in words:
                t = (line + ' ' + w).strip()
                if c.stringWidth(t, 'Inter-Light', 6) <= sec_w - 6*mm:
                    line = t
                else:
                    c.drawString(sx + 3*mm, dy, line)
                    dy -= 3.5*mm
                    line = w
            if line:
                c.drawString(sx + 3*mm, dy, line)
            dy -= 5.5*mm

    y -= sec_h + 10*mm

    label(c, 'Why Figment', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawString(MAR_L, y, 'The Figment difference.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 7*mm

    why = [
        ('Focus Edition specialists', 'Curriculum fully aligned to the new GMAT Focus — no outdated AWA content, full Data Insights coverage.'),
        ('Data Insights edge', 'Most students struggle with DI. Our dedicated DI module closes this gap and often unlocks 40–50 extra points.'),
        ('700+ track record', 'Average student improvement of 80–100 points. Multiple 750+ scorers every cycle.'),
        ('Expert MBA faculty', 'Taught by IIM alumni who have been through the GMAT process and understand exactly what B-schools want.'),
    ]
    why_w = CONTENT_W / 2 - 3*mm
    why_h = 22*mm
    for i, (wt, wb) in enumerate(why):
        wx = MAR_L + (i % 2) * (why_w + 6*mm)
        wy = y - (i // 2) * (why_h + 3*mm)
        c.setFillColor(WHITE_05)
        c.rect(wx, wy - why_h, why_w, why_h, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(wx, wy - why_h, 2, why_h, fill=1, stroke=0)
        c.setFillColor(IVORY)
        c.setFont('Playfair', 10)
        c.drawString(wx + 5*mm, wy - 7*mm, wt)
        body_text(c, wb, wx + 5*mm, wy - 12*mm, size=7, col=GREY,
                  max_width=why_w - 8*mm)

    footer_bar(c, 3)
    draw_team_page(c)
    c.save()
    print(f'✓  GMAT brochure saved → {path}')
    return path


# ══════════════════════════════════════════════════════════════════════════════
#  IELTS BROCHURE
# ══════════════════════════════════════════════════════════════════════════════

def make_ielts():
    path = f'{OUT_DIR}/Figment_IELTS_Brochure.pdf'
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle('Figment — IELTS Programme Brochure')

    # Cover
    bg(c, BLACK)
    c.setFillColor(NAVY)
    c.rect(W * 0.58, 0, W * 0.42, H, fill=1, stroke=0)
    nav_brand(c)

    y = H * 0.52
    label(c, 'IELTS Preparation Programme', MAR_L, y, size=6.5)
    y -= 8*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 55)
    c.drawString(MAR_L, y, 'Your Band.')
    y -= 52*mm * 0.88
    c.setFillColor(GOLD)
    c.setFont('Cormorant-Italic', 62)
    c.drawString(MAR_L, y, 'Achieved.')
    y -= 12*mm
    gold_rule(c, MAR_L, y, 15*mm)
    y -= 7*mm
    c.setFillColor(IVORY_65)
    c.setFont('Cormorant-Italic', 12)
    c.drawString(MAR_L, y, 'Listening. Reading. Writing. Speaking.')
    y -= 10*mm

    stats = [('9.0', 'Max Band'), ('4', 'Modules'), ('7+', 'Avg Target'), ('2+', 'Mock Tests')]
    sw = CONTENT_W * 0.6 / len(stats)
    for i, (sv, sl) in enumerate(stats):
        sx = MAR_L + i*sw + sw/2
        c.setFillColor(GOLD)
        c.setFont('Playfair', 20)
        c.drawCentredString(sx, y, sv)
        c.setFillColor(GREY)
        c.setFont('Inter', 5.5)
        c.drawCentredString(sx, y - 5.5*mm, sl.upper())

    footer_bar(c, 1)
    c.showPage()

    # Page 2: Test overview + 4 programmes
    bg(c, CHARCOAL)
    nav_brand(c)
    y = H - 22*mm
    label(c, 'About IELTS', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 24)
    c.drawString(MAR_L, y, 'Know your exam.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 7*mm

    facts = [
        ('0–9', 'Band Score', 'In 0.5 increments'),
        ('2h 45m', 'Duration', 'All 4 modules'),
        ('Academic / GT', 'Test Type', 'Univ / Migration'),
        ('IDP / BC', 'Test Makers', 'Centres worldwide'),
    ]
    box_w = CONTENT_W / 4 - 2*mm
    box_h = 22*mm
    for i, (val, lbl, sub) in enumerate(facts):
        bx = MAR_L + i * (box_w + 2.67*mm)
        c.setFillColor(WHITE_05)
        c.rect(bx, y - box_h, box_w, box_h, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont('Playfair', 14)
        c.drawCentredString(bx + box_w/2, y - 7*mm, val)
        c.setFillColor(IVORY)
        c.setFont('Inter-Medium', 6.5)
        c.drawCentredString(bx + box_w/2, y - 12*mm, lbl)
        c.setFillColor(GREY)
        c.setFont('Inter-Light', 5.5)
        c.drawCentredString(bx + box_w/2, y - 15.5*mm, sub)
    y -= box_h + 8*mm

    body_text(c, 'IELTS is the world\'s most popular English proficiency test — required for university admissions in the UK, Australia, Canada, and increasingly the USA. Figment\'s IELTS programme covers all four modules with targeted strategies that work for both Academic and General Training formats.', MAR_L, y, size=8, max_width=CONTENT_W, col=IVORY_65)
    y -= 26*mm

    horiz_rule(c, MAR_L, y)
    y -= 7*mm

    label(c, 'Choose Your Programme', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawString(MAR_L, y, 'Four ways to your target band.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 7*mm

    programmes = [
        ('Online Batch', 'Live · Small Group', [('25', 'Sessions'), ('37.5 hrs', 'Content'), ('2', 'Mocks')],
         ['Live sessions via Zoom', 'All 4 modules', 'Band prediction reports'],
         'Most Popular', True),
        ('Classroom Batch', 'In-person · Madurai', [('15', 'Sessions'), ('30 hrs', 'Content'), ('2', 'Mocks')],
         ['Centre-based coaching', 'Face-to-face feedback', 'Speaking practice circles'],
         None, False),
        ('One-on-One', 'Private · Flexible', [('10', 'Sessions'), ('20 hrs', 'Content'), ('1:1', 'Support')],
         ['1:1 sessions', 'Custom study plan', 'Flexible scheduling'],
         None, False),
        ('Enrichment Add-on', 'With Praveen Kumar', [('5 hrs', 'Content'), ('1:1', 'With Founder'), ('IIM', 'Faculty')],
         ['High-band writing coaching', 'Speaking interview prep', 'Praveen\'s personal toolkit'],
         None, False),
    ]

    prog_w = CONTENT_W / 4 - 2.25*mm
    prog_h = 75*mm
    for pi, (ptitle, psub, pstats, pfeats, pbadge, pfeatured) in enumerate(programmes):
        px2 = MAR_L + pi * (prog_w + 3*mm)
        bg_col = NAVY if pfeatured else Color(0,0,0,0.3)
        c.setFillColor(bg_col)
        c.rect(px2, y - prog_h, prog_w, prog_h, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(px2, y, prog_w, 2, fill=1, stroke=0)

        if pbadge:
            c.setFillColor(GOLD)
            c.setFont('Inter-Medium', 5.5)
            badge_text = pbadge.upper()
            bw = c.stringWidth(badge_text, 'Inter-Medium', 5.5) + 4*mm
            c.rect(px2 + prog_w - bw - 2*mm, y - 5.5*mm, bw, 5*mm, fill=1, stroke=0)
            c.setFillColor(BLACK)
            c.drawString(px2 + prog_w - bw, y - 4*mm, badge_text)

        cy = y - 7*mm
        c.setFillColor(IVORY)
        c.setFont('Playfair', 11)
        c.drawString(px2 + 3*mm, cy, ptitle)
        cy -= 4*mm
        c.setFillColor(GREY)
        c.setFont('Cormorant-Italic', 7.5)
        c.drawString(px2 + 3*mm, cy, psub)
        cy -= 5*mm

        for sv, sl in pstats:
            c.setFillColor(GOLD)
            c.setFont('Playfair', 13)
            c.drawString(px2 + 3*mm, cy, sv)
            cy -= 4*mm
            c.setFillColor(GREY)
            c.setFont('Inter', 5.5)
            c.drawString(px2 + 3*mm, cy, sl.upper())
            cy -= 5.5*mm

        cy -= 1*mm
        horiz_rule(c, px2 + 3*mm, cy, prog_w - 6*mm)
        cy -= 4*mm

        for feat in pfeats:
            c.setFillColor(IVORY_65)
            c.setFont('Inter-Light', 6.5)
            # wrap
            words = feat.split()
            line = ''
            for w in words:
                t = (line + ' ' + w).strip()
                if c.stringWidth(t, 'Inter-Light', 6.5) <= prog_w - 6*mm:
                    line = t
                else:
                    c.drawString(px2 + 3*mm, cy, line)
                    cy -= 4*mm
                    line = w
            if line:
                c.drawString(px2 + 3*mm, cy, line)
            cy -= 5*mm

    footer_bar(c, 2)
    c.showPage()

    # Page 3: Module breakdown + Why Figment
    bg(c, BLACK)
    nav_brand(c)
    y = H - 22*mm
    label(c, 'The Four Modules', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 24)
    c.drawString(MAR_L, y, 'Every module. Mastered.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 8*mm

    modules = [
        ('Listening', '30 min · 40 Qs', [
            ('Section 1–2', 'Everyday social situations — form filling, maps, diagrams'),
            ('Section 3–4', 'Academic discussions and monologues'),
            ('Key strategies', 'Predict answers, follow signposting, manage note-taking speed'),
        ]),
        ('Reading', '60 min · 40 Qs', [
            ('Academic passages', '3 texts — matching, T/F/NG, heading matching, short answer'),
            ('Skimming/Scanning', 'Locate information rapidly without reading everything'),
            ('Vocabulary in context', 'Understand meaning from surrounding text'),
        ]),
        ('Writing', '60 min · 2 tasks', [
            ('Task 1 (20 min)', 'Describe a chart, graph, process, or map — 150+ words'),
            ('Task 2 (40 min)', 'Discursive essay: opinion, discussion, problem-solution'),
            ('Band 7+ formulas', 'Cohesion, coherence, lexical resource, grammatical range'),
        ]),
        ('Speaking', '11–14 min · 3 parts', [
            ('Part 1 — Introduction', 'Familiar topics: home, work, hobbies — 4–5 minutes'),
            ('Part 2 — Long Turn', 'Cue card: 2-minute speech on given topic'),
            ('Part 3 — Discussion', 'Abstract questions related to Part 2 topic'),
        ]),
    ]
    mod_w = CONTENT_W / 2 - 3*mm
    for mi, (mname, msub, mrows) in enumerate(modules):
        mx = MAR_L + (mi % 2) * (mod_w + 6*mm)
        my = y - (mi // 2) * (len(mrows) * 14*mm + 20*mm + 5*mm)
        mod_h = len(mrows) * 14*mm + 20*mm
        c.setFillColor(Color(11/255, 44/255, 74/255, 0.3))
        c.rect(mx, my - mod_h, mod_w, mod_h, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.rect(mx, my - 14*mm, mod_w, 14*mm, fill=1, stroke=0)
        c.setFillColor(IVORY)
        c.setFont('Playfair', 11)
        c.drawString(mx + 4*mm, my - 7*mm, mname)
        c.setFillColor(GOLD)
        c.setFont('Inter', 6)
        c.drawRightString(mx + mod_w - 4*mm, my - 7*mm, msub)
        dy = my - 18*mm
        for rname, rdesc in mrows:
            horiz_rule(c, mx + 4*mm, dy + 1*mm, mod_w - 8*mm)
            dy -= 3*mm
            c.setFillColor(IVORY)
            c.setFont('Inter-Medium', 7)
            c.drawString(mx + 4*mm, dy, rname)
            dy -= 3.5*mm
            c.setFillColor(IVORY_40)
            c.setFont('Inter-Light', 6)
            words = rdesc.split()
            line = ''
            for w in words:
                t = (line + ' ' + w).strip()
                if c.stringWidth(t, 'Inter-Light', 6) <= mod_w - 8*mm:
                    line = t
                else:
                    c.drawString(mx + 4*mm, dy, line)
                    dy -= 3.5*mm
                    line = w
            if line:
                c.drawString(mx + 4*mm, dy, line)
            dy -= 5.5*mm

    y -= 2 * (len(modules[0][2]) * 14*mm + 20*mm + 5*mm) + 5*mm

    label(c, 'Why Figment', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawString(MAR_L, y, 'The Figment difference.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 7*mm

    why = [
        ('All four modules covered', 'No gaps — every IELTS module gets dedicated sessions with targeted strategy and timed practice.'),
        ('Speaking practice circles', 'Regular group speaking practice sessions simulate the real interview environment and reduce exam anxiety.'),
        ('Live writing feedback', 'Task 1 and Task 2 submissions reviewed by faculty with band-level annotations and improvement notes.'),
        ('Enrichment coaching', 'Additional 1:1 sessions with Praveen Kumar (IIM Ahmedabad) for students targeting Band 8–9.'),
    ]
    why_w = CONTENT_W / 2 - 3*mm
    why_h = 22*mm
    for i, (wt, wb) in enumerate(why):
        wx = MAR_L + (i % 2) * (why_w + 6*mm)
        wy = y - (i // 2) * (why_h + 3*mm)
        c.setFillColor(WHITE_05)
        c.rect(wx, wy - why_h, why_w, why_h, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(wx, wy - why_h, 2, why_h, fill=1, stroke=0)
        c.setFillColor(IVORY)
        c.setFont('Playfair', 10)
        c.drawString(wx + 5*mm, wy - 7*mm, wt)
        body_text(c, wb, wx + 5*mm, wy - 12*mm, size=7, col=GREY,
                  max_width=why_w - 8*mm)

    footer_bar(c, 3)
    draw_team_page(c)
    c.save()
    print(f'✓  IELTS brochure saved → {path}')
    return path


# ══════════════════════════════════════════════════════════════════════════════
#  ACS (ADMISSIONS COUNSELLING) BROCHURE
# ══════════════════════════════════════════════════════════════════════════════

def make_acs():
    path = f'{OUT_DIR}/Figment_ACS_Brochure.pdf'
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle('Figment — Admissions Counselling Services Brochure')

    # Cover
    bg(c, BLACK)
    c.setFillColor(Color(11/255, 44/255, 74/255, 0.6))
    c.rect(0, 0, W, H * 0.4, fill=1, stroke=0)
    nav_brand(c)

    y = H * 0.55
    label(c, 'Admissions Counselling Services', MAR_L, y, size=6.5)
    y -= 8*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 52)
    c.drawString(MAR_L, y, 'Get')
    y -= 50*mm * 0.88
    c.setFillColor(GOLD)
    c.setFont('Cormorant-Italic', 58)
    c.drawString(MAR_L, y, 'Admitted.')
    y -= 12*mm
    gold_rule(c, MAR_L, y, 15*mm)
    y -= 7*mm
    c.setFillColor(IVORY_65)
    c.setFont('Cormorant-Italic', 12)
    c.drawString(MAR_L, y, 'Strategy. Story. Admission. End-to-end counselling from IIM alumni.')
    y -= 10*mm

    stats = [('6', 'Programmes'), ('Top 20', 'Universities Placed'), ('IIM', 'Faculty'), ('End-to-end', 'Support')]
    sw = CONTENT_W * 0.72 / len(stats)
    for i, (sv, sl) in enumerate(stats):
        sx = MAR_L + i*sw + sw/2
        c.setFillColor(GOLD)
        c.setFont('Playfair', 18)
        c.drawCentredString(sx, y, sv)
        c.setFillColor(GREY)
        c.setFont('Inter', 5.5)
        c.drawCentredString(sx, y - 5.5*mm, sl.upper())

    footer_bar(c, 1)
    c.showPage()

    # Page 2: Flagship programmes
    bg(c, CHARCOAL)
    nav_brand(c)
    y = H - 22*mm
    label(c, 'Our Flagship Programmes', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 24)
    c.drawString(MAR_L, y, 'The right programme for every aspiration.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 8*mm

    flagship = [
        {
            'badge': 'Elite Admit Programme',
            'title': 'Top 20 Universities — Worldwide',
            'price': '₹2,25,000',
            'target': 'Ivy League · MIT · Stanford · Oxbridge · Top-20 global',
            'features': [
                'Dedicated counsellor for all applications',
                'University shortlisting & strategy (up to 8 universities)',
                'Deep-dive personal statement coaching',
                'All supplemental essays — unlimited revisions',
                'CV/Résumé building & positioning',
                'Recommendation letter strategy & review',
                'Application portal management & deadline tracking',
                'Interview prep — multiple mock interviews',
                'Financial aid & scholarship application support',
                'Visa consultation (F1/study visa)',
            ],
            'bg': NAVY,
            'featured': True,
        },
        {
            'badge': 'Select Admit Programme',
            'title': 'Top 50 Universities — Worldwide',
            'price': '₹1,25,000',
            'target': 'Top-50 US/UK/Canada/Australia programmes',
            'features': [
                'Dedicated counsellor (up to 6 universities)',
                'University shortlisting & fit analysis',
                'Personal statement coaching & review',
                'Supplemental essays — up to 3 revisions each',
                'CV/Résumé review & polishing',
                'Recommendation letter guidance',
                'Application portal support',
                'Mock interview session (2 rounds)',
            ],
            'bg': Color(0, 0, 0, 0.4),
            'featured': False,
        },
    ]

    card_w = CONTENT_W / 2 - 3*mm
    for ci, prog in enumerate(flagship):
        cx = MAR_L + ci * (card_w + 6*mm)
        card_h = 115*mm
        c.setFillColor(prog['bg'])
        c.rect(cx, y - card_h, card_w, card_h, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(cx, y, card_w, 2, fill=1, stroke=0)

        cy = y - 6*mm
        label(c, prog['badge'], cx + 5*mm, cy)
        cy -= 5.5*mm
        c.setFillColor(IVORY)
        c.setFont('Playfair', 12)
        c.drawString(cx + 5*mm, cy, prog['title'])
        cy -= 4*mm
        c.setFillColor(IVORY_65)
        c.setFont('Cormorant-Italic', 8)
        c.drawString(cx + 5*mm, cy, prog['target'])
        cy -= 5*mm
        horiz_rule(c, cx + 5*mm, cy, card_w - 10*mm)
        cy -= 5*mm

        for feat in prog['features']:
            c.setFillColor(IVORY_65)
            c.setFont('Inter-Light', 6.5)
            c.drawString(cx + 5*mm, cy, '· ' + feat)
            cy -= 5*mm
        cy -= 1*mm
        c.setFillColor(IVORY)
        c.setFont('Playfair', 18)
        c.drawString(cx + 5*mm, cy, prog['price'])

    y -= 125*mm

    # Global Admit
    c.setFillColor(WHITE_05)
    c.rect(MAR_L, y - 20*mm, CONTENT_W, 20*mm, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(MAR_L, y, 2, 20*mm, fill=1, stroke=0)
    c.setFillColor(IVORY)
    c.setFont('Playfair', 12)
    c.drawString(MAR_L + 5*mm, y - 7*mm, 'Global Admit Programme')
    c.setFillColor(GREY)
    c.setFont('Inter', 6)
    c.drawString(MAR_L + 5*mm, y - 11*mm, 'TOP 250 UNIVERSITIES WORLDWIDE')
    c.setFillColor(IVORY_65)
    c.setFont('Inter-Light', 7)
    c.drawString(MAR_L + 5*mm, y - 15.5*mm, 'Broad university reach · Guidance on 8–12 applications · Essay coaching · Portal support')
    c.setFillColor(IVORY)
    c.setFont('Playfair', 12)
    c.drawRightString(MAR_L + CONTENT_W - 5*mm, y - 7*mm, 'Contact for pricing')

    footer_bar(c, 2)
    c.showPage()

    # Page 3: Specialised programmes + process
    bg(c, BLACK)
    nav_brand(c)
    y = H - 22*mm
    label(c, 'Specialised Programmes', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 24)
    c.drawString(MAR_L, y, 'Pathways for every destination.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 8*mm

    special = [
        ('Germany Structured Admit', 'Blocked Account · APS · Visa Strategy',
         ['University shortlisting for Germany\'s top TU institutions', 'APS certification guidance (crucial for Indian students)', 'Blocked account setup and documentation', 'German visa documentation and interview prep', 'Language requirement planning: German/English-taught'],
         'Contact for pricing'),
        ('International Pathway Programme', 'Foundation & Pathway Programmes',
         ['Pathway programmes in UK, Australia, Canada', 'University progression guarantee programmes', 'Conditional offer management', 'Pre-departure orientation and support', 'IELTS/English requirement planning'],
         '₹20,000'),
        ('Visa Assist Programme', 'Study Visa Documentation',
         ['Standard countries (US, UK, Canada, Aus): documentation review', 'USA F1: includes mock visa interview coaching', 'Complex countries: full documentation strategy', 'Visa rejection analysis and re-application support', 'SOP and financial documentation review'],
         'From ₹12,000'),
    ]

    spec_w = CONTENT_W / 3 - 3*mm
    for si, (stitle, ssub, sfeats, sprice) in enumerate(special):
        sx = MAR_L + si * (spec_w + 4.5*mm)
        spec_h = len(sfeats) * 10*mm + 32*mm
        c.setFillColor(Color(11/255, 44/255, 74/255, 0.3))
        c.rect(sx, y - spec_h, spec_w, spec_h, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(sx, y, spec_w, 2, fill=1, stroke=0)
        c.setFillColor(IVORY)
        c.setFont('Playfair', 10)
        # wrap title
        words = stitle.split()
        line = ''
        ty = y - 7*mm
        for w in words:
            t = (line + ' ' + w).strip()
            if c.stringWidth(t, 'Playfair', 10) <= spec_w - 6*mm:
                line = t
            else:
                c.drawString(sx + 4*mm, ty, line)
                ty -= 5*mm
                line = w
        c.drawString(sx + 4*mm, ty, line)
        ty -= 4.5*mm
        c.setFillColor(GREY)
        c.setFont('Cormorant-Italic', 7.5)
        c.drawString(sx + 4*mm, ty, ssub)
        ty -= 5*mm
        horiz_rule(c, sx + 4*mm, ty, spec_w - 8*mm)
        ty -= 4*mm
        for feat in sfeats:
            c.setFillColor(IVORY_65)
            c.setFont('Inter-Light', 6.5)
            words = feat.split()
            line = ''
            for w in words:
                t = (line + ' ' + w).strip()
                if c.stringWidth(t, 'Inter-Light', 6.5) <= spec_w - 8*mm:
                    line = t
                else:
                    c.drawString(sx + 4*mm, ty, line)
                    ty -= 4.5*mm
                    line = w
            if line:
                c.drawString(sx + 4*mm, ty, '· ' + line)
            ty -= 6*mm
        c.setFillColor(IVORY)
        c.setFont('Playfair', 12)
        c.drawString(sx + 4*mm, ty, sprice)

    y -= max(len(s[2]) for s in special) * 10*mm + 40*mm

    # Process
    label(c, 'Our Process', MAR_L, y)
    y -= 6*mm
    c.setFillColor(IVORY)
    c.setFont('Playfair', 20)
    c.drawString(MAR_L, y, 'How we get you in.')
    y -= 4*mm
    gold_rule(c, MAR_L, y)
    y -= 7*mm

    process = [
        ('01', 'Profile Assessment', 'We analyse your academics, test scores, work experience, and goals to identify the right universities and your realistic admit chances.'),
        ('02', 'Strategy & Shortlisting', 'Our experts build a portfolio of safety, match, and reach schools — calibrated to your profile and career goals, not generic rankings.'),
        ('03', 'Application Building', 'Essays, CV, recommendations, and supplementals — we craft every element of your application to tell a compelling, authentic story.'),
        ('04', 'Submit & Succeed', 'We manage deadlines, portals, and follow-ups. After admission, we guide you through financial aid, visa, and pre-departure steps.'),
    ]
    step_h = 16*mm
    for snum, stitle, sbody in process:
        c.setFillColor(WHITE_05)
        c.rect(MAR_L, y - step_h, CONTENT_W, step_h, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont('Cormorant-Italic', 16)
        c.drawString(MAR_L + 4*mm, y - 9.5*mm, snum)
        c.setFillColor(IVORY)
        c.setFont('Playfair', 10)
        c.drawString(MAR_L + 18*mm, y - 5.5*mm, stitle)
        body_text(c, sbody, MAR_L + 18*mm, y - 10.5*mm, size=7, col=GREY,
                  max_width=CONTENT_W - 22*mm)
        y -= step_h + 1.5*mm

    footer_bar(c, 3)
    draw_team_page(c)
    c.save()
    print(f'✓  ACS brochure saved → {path}')
    return path


# ══════════════════════════════════════════════════════════════════════════════
#  RUN ALL
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print(f'\nGenerating Figment brochures → {OUT_DIR}\n')
    results = []
    for fn in [make_sat, make_gre, make_gmat, make_ielts, make_acs]:
        try:
            results.append(fn())
        except Exception as e:
            import traceback
            print(f'✗  {fn.__name__} FAILED: {e}')
            traceback.print_exc()

    print(f'\n{"─"*50}')
    print(f'Done. {len(results)}/5 brochures generated.')
    print(f'Output: {OUT_DIR}')
