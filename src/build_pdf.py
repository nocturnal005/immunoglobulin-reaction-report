"""Fillable AcroForm PDF: Immunoglobulin Home Therapy adverse reaction report.

For patients on IVIG or SCIG at home. Reported to the Immunology Specialist
Nurses / Immunology Consultant, Royal Free London.

Two-pass build so the footer can print a real "Page N of M".
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DIST = REPO / "dist"

OUT = DIST / "immunoglobulin-reaction-report.pdf"
SCRATCH = DIST / "_pagecount.pdf"          # deleted after the counting pass
QR_IMG = DIST / "qr-questionnaire.png"     # produced by make_qr.py - run that first
# shown as fallback text beside the QR, so it must match make_qr.FORM_URL
QR_URL_TEXT = "claude.ai/code/artifact/a4e2c535-41dc-4724-aeaa-5c377bccde39"

# ---- department contact details --------------------------------------------
TEL = "020 7794 0500, ext. 32232 or 32233"
TEL_SHORT = "020 7794 0500 ext. 32232/32233"
EMAIL = "rf-tr.clinicalimmunology@nhs.net"

PAGE_W, PAGE_H = A4
M = 44
TOP = 46
BOTTOM = 64
CW = PAGE_W - 2 * M

TEAL = colors.HexColor("#0B6B70")
TINT = colors.HexColor("#E4F1F1")
TEAL_LINE = colors.HexColor("#9CC8CA")
INK = colors.HexColor("#17262B")
MUTED = colors.HexColor("#506469")
LINE = colors.HexColor("#D3DFE0")
DANGER = colors.HexColor("#8F1D12")
DANGER_BG = colors.HexColor("#FDF0ED")
DANGER_STRONG = colors.HexColor("#B3261E")
WARN = colors.HexColor("#7A4A06")
WARN_BG = colors.HexColor("#FDF5E6")
WARN_STRONG = colors.HexColor("#B5790F")
WHITE = colors.white

c = None
y = 0
page_num = 1
TOTAL_PAGES = 1


# ------------------------------------------------------------- page furniture
def footer():
    c.setStrokeColor(LINE)
    c.setLineWidth(0.7)
    c.line(M, 44, PAGE_W - M, 44)
    c.setFont("Helvetica-Bold", 7.6)
    c.setFillColor(TEAL)
    c.drawString(M, 33, "Immunology Specialist Nurses   " + TEL_SHORT)
    c.setFont("Helvetica", 7.6)
    c.setFillColor(MUTED)
    c.drawString(M, 23, EMAIL)
    c.drawRightString(PAGE_W - M, 23, "Page %d of %d" % (page_num, TOTAL_PAGES))


def new_page():
    global y, page_num
    footer()
    c.showPage()
    page_num += 1
    y = PAGE_H - TOP


def ensure(h):
    if y - h < BOTTOM:
        new_page()


def wrapped(text, font, size, width, leading, color, x=None):
    global y
    for ln in simpleSplit(text, font, size, width):
        c.setFont(font, size)
        c.setFillColor(color)
        c.drawString(x if x is not None else M, y - size, ln)
        y -= leading


def gap(h):
    global y
    y -= h


def draw_tag(x, ybase, label):
    tw = c.stringWidth(label, "Helvetica-Bold", 7) + 1.0 * (len(label) - 1)
    c.setFillColor(TINT)
    c.setStrokeColor(TEAL_LINE)
    c.setLineWidth(0.8)
    c.roundRect(x, ybase - 1, tw + 12, 12.5, 6, stroke=1, fill=1)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x + 6, ybase + 2.6, label, charSpace=1.0)


def qlabel(text, tag=None, keep=0):
    """Question label. `keep` reserves room for the answers that follow so a
    question never gets orphaned at the foot of a page."""
    global y
    avail = CW - (58 if tag else 0)
    lines = simpleSplit(text, "Helvetica-Bold", 10.5, avail)
    ensure(len(lines) * 14 + 6 + keep)
    for i, ln in enumerate(lines):
        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(INK)
        c.drawString(M, y - 10.5, ln)
        if i == len(lines) - 1 and tag:
            tw = c.stringWidth(ln, "Helvetica-Bold", 10.5)
            draw_tag(M + tw + 8, y - 11.5, tag)
        y -= 14
    gap(3)


def hint(text):
    wrapped(text, "Helvetica", 8.8, CW, 11, MUTED)
    gap(3)


# ------------------------------------------------------------------ form bits
def text_field(name, tooltip, x, w, h=20, multiline=False):
    # Every field uses Helvetica on purpose. Mixing a second base font makes
    # reportlab emit a duplicate /Font key in the AcroForm resource dictionary,
    # which strict PDF readers reject.
    kwargs = {}
    if multiline:
        kwargs["fieldFlags"] = "multiline"
    c.acroForm.textfield(
        name=name, tooltip=tooltip, x=x, y=y - h, width=w, height=h,
        borderStyle="solid", borderWidth=1, borderColor=LINE, fillColor=WHITE,
        textColor=INK, fontName="Helvetica",
        fontSize=10, maxlen=4000 if multiline else 400,
        forceBorder=True, **kwargs)


def labeled_field(label, name, tooltip, hint_text=None, h=20):
    global y
    ensure(44 + (12 if hint_text else 0))
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(INK)
    c.drawString(M, y - 10, label)
    y -= 14
    if hint_text:
        hint(hint_text)
    text_field(name, tooltip, M, CW, h=h)
    y -= h + 11


def labeled_pair(l1, n1, t1, l2, n2, t2):
    global y
    ensure(44)
    half = (CW - 16) / 2
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(INK)
    c.drawString(M, y - 10, l1)
    c.drawString(M + half + 16, y - 10, l2)
    y -= 14
    text_field(n1, t1, M, half)
    text_field(n2, t2, M + half + 16, half)
    y -= 20 + 11


def radio_widget(x, ybottom, group, value, tooltip):
    """Clean circle drawn on the page; the widget itself is borderless because
    reportlab's own radio appearance uses an ugly shadowed-circle glyph."""
    c.setStrokeColor(MUTED)
    c.setLineWidth(1.1)
    c.circle(x + 6, ybottom + 6, 6, stroke=1, fill=0)
    c.acroForm.radio(
        name=group, value=value, tooltip=tooltip, selected=False,
        x=x, y=ybottom, size=12, buttonStyle="circle", shape="circle",
        borderWidth=0, borderColor=None, fillColor=None,
        textColor=TEAL, forceBorder=False)


def checkbox_widget(x, ybottom, name, tooltip, flag=False):
    c.acroForm.checkbox(
        name=name, tooltip=tooltip, x=x, y=ybottom, size=12,
        buttonStyle="check", borderWidth=1.1,
        borderColor=WARN_STRONG if flag else MUTED,
        fillColor=WARN_BG if flag else WHITE,
        textColor=TEAL, forceBorder=True)


def option(kind, group, value, label, desc=None, tooltip=None,
           inline=None, flag=False):
    """One radio or checkbox row. inline=(name, tooltip) adds a write-in line."""
    global y
    label_x = M + 20
    avail = CW - 20
    lab_font = "Helvetica-Bold" if desc else "Helvetica"
    lab_lines = simpleSplit(label, lab_font, 10, avail)
    desc_lines = simpleSplit(desc, "Helvetica", 8.8, avail) if desc else []
    h = len(lab_lines) * 13 + len(desc_lines) * 11 + (5 if inline else 2)
    ensure(h + 4)
    base = y - 11
    if kind == "radio":
        radio_widget(M, base - 1.5, group, value, tooltip or label)
    else:
        checkbox_widget(M, base - 1.5, group, tooltip or label, flag=flag)
    for i, ln in enumerate(lab_lines):
        c.setFont(lab_font, 10)
        c.setFillColor(INK)
        c.drawString(label_x, base - i * 13, ln)
    if inline:
        last = lab_lines[-1]
        lw = c.stringWidth(last, lab_font, 10)
        fx = label_x + lw + 7
        saved = y
        y = base + 11 - (len(lab_lines) - 1) * 13
        text_field(inline[0], inline[1], fx, max(90, PAGE_W - M - fx), h=16)
        y = saved
    y -= len(lab_lines) * 13
    for ln in desc_lines:
        c.setFont("Helvetica", 8.8)
        c.setFillColor(MUTED)
        c.drawString(label_x, y - 8.8, ln)
        y -= 11
    y -= 5 if inline else 2


def radio(group, value, label, desc=None, tooltip=None, inline=None):
    option("radio", group, value, label, desc, tooltip, inline)


def check(name, label, tooltip=None, inline=None, flag=False):
    option("check", name, None, label, None, tooltip, inline, flag)


def rule():
    global y
    gap(5)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.7)
    c.line(M, y, PAGE_W - M, y)
    gap(12)


def section_header(tag, title, sub):
    global y
    sub_lines = simpleSplit(sub, "Helvetica", 9.2, CW)
    ensure(25 + 19 + len(sub_lines) * 12 + 40)
    tw = c.stringWidth(tag, "Helvetica-Bold", 8) + 1.3 * (len(tag) - 1)
    c.setFillColor(TINT)
    c.setStrokeColor(TEAL_LINE)
    c.setLineWidth(1)
    c.roundRect(M, y - 16, tw + 20, 16, 8, stroke=1, fill=1)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(M + 10, y - 11.5, tag, charSpace=1.3)
    y -= 25
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(INK)
    c.drawString(M, y - 14, title)
    y -= 19
    for ln in sub_lines:
        c.setFont("Helvetica", 9.2)
        c.setFillColor(MUTED)
        c.drawString(M, y - 9.2, ln)
        y -= 12
    gap(8)


def alert_box(title, intro, bullets, tail, ink, bg, strong):
    global y
    pad = 12
    inner = CW - 2 * pad - 6
    intro_lines = simpleSplit(intro, "Helvetica-Bold", 9.2, inner)
    bullet_lines = [simpleSplit(b, "Helvetica-Bold", 9.2, inner - 12) for b in bullets]
    tail_lines = simpleSplit(tail, "Helvetica-Bold", 9.2, inner) if tail else []
    h = (pad + 14 + len(intro_lines) * 11.5 + 4 +
         sum(len(bl) for bl in bullet_lines) * 11.5 + 4 +
         len(tail_lines) * 11.5 + pad)
    ensure(h + 6)
    c.setFillColor(bg)
    c.setStrokeColor(strong)
    c.setLineWidth(1.2)
    c.roundRect(M, y - h, CW, h, 9, stroke=1, fill=1)
    c.setFillColor(strong)
    c.rect(M + 1, y - h + 3, 4.5, h - 6, stroke=0, fill=1)
    ty = y - pad
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(ink)
    c.drawString(M + pad + 6, ty - 10, title, charSpace=0.6)
    ty -= 20
    c.setFont("Helvetica-Bold", 9.2)
    for ln in intro_lines:
        c.drawString(M + pad + 6, ty - 9.2, ln)
        ty -= 11.5
    ty -= 4
    for bl in bullet_lines:
        for i, ln in enumerate(bl):
            if i == 0:
                c.drawString(M + pad + 8, ty - 9.2, "-")
            c.drawString(M + pad + 18, ty - 9.2, ln)
            ty -= 11.5
    ty -= 4
    for ln in tail_lines:
        c.drawString(M + pad + 6, ty - 9.2, ln)
        ty -= 11.5
    y -= h + 11


def info_box(title, lines_in):
    global y
    pad = 12
    inner = CW - 2 * pad
    body = []
    for ln in lines_in:
        body.extend(simpleSplit(ln, "Helvetica", 9.2, inner - 14))
    h = pad + 14 + len(body) * 12 + pad - 4
    ensure(h + 6)
    c.setFillColor(WHITE)
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.roundRect(M, y - h, CW, h, 9, stroke=1, fill=1)
    ty = y - pad
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(INK)
    c.drawString(M + pad, ty - 10, title)
    ty -= 20
    c.setFont("Helvetica", 9.2)
    c.setFillColor(MUTED)
    for ln in body:
        c.drawString(M + pad + 14, ty - 9.2, ln)
        ty -= 12
    ty = y - pad - 20
    for src in lines_in:
        n = len(simpleSplit(src, "Helvetica", 9.2, inner - 14))
        c.setFillColor(TEAL)
        c.circle(M + pad + 5, ty - 6, 2, stroke=0, fill=1)
        ty -= n * 12
    y -= h + 10


def contact_strip():
    """Prominent 'who to call' block, directly under the masthead."""
    global y
    pad = 10
    h = pad + 12 + 15 + 12 + pad - 4
    ensure(h + 6)
    c.setFillColor(TINT)
    c.setStrokeColor(TEAL_LINE)
    c.setLineWidth(1.2)
    c.roundRect(M, y - h, CW, h, 9, stroke=1, fill=1)
    ty = y - pad
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(MUTED)
    c.drawString(M + pad, ty - 9, "YOUR IMMUNOLOGY SPECIALIST NURSES", charSpace=0.9)
    ty -= 15
    c.setFont("Helvetica-Bold", 12.5)
    c.setFillColor(TEAL)
    c.drawString(M + pad, ty - 12.5, TEL)
    ty -= 14
    c.setFont("Helvetica", 9.4)
    c.setFillColor(INK)
    c.drawString(M + pad, ty - 9.4, EMAIL)
    y -= h + 8


def qr_box():
    global y
    h = 126
    ensure(h + 6)
    c.setFillColor(TINT)
    c.setStrokeColor(TEAL_LINE)
    c.setLineWidth(1.2)
    c.roundRect(M, y - h, CW, h, 9, stroke=1, fill=1)
    qs = 104
    qx, qy = M + 14, y - h + (h - qs) / 2
    c.setFillColor(WHITE)
    c.setStrokeColor(TEAL_LINE)
    c.setLineWidth(0.8)
    c.roundRect(qx - 5, qy - 5, qs + 10, qs + 10, 5, stroke=1, fill=1)
    c.drawImage(str(QR_IMG), qx, qy, width=qs, height=qs, mask=None)
    tx = qx + qs + 22
    tw = PAGE_W - M - 14 - tx
    ty = y - 21
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11.5)
    c.drawString(tx, ty, "Prefer to fill this in on your phone?")
    ty -= 15
    c.setFont("Helvetica", 9.2)
    c.setFillColor(MUTED)
    for ln in simpleSplit("Scan this code with your phone camera to open the same form online. "
                          "You can type your answers, stop and come back to them later, and "
                          "email the finished report straight to us.",
                          "Helvetica", 9.2, tw):
        c.drawString(tx, ty, ln)
        ty -= 11.5
    ty -= 3
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(TEAL)
    c.drawString(tx, ty, "Or type in: " + QR_URL_TEXT)
    y -= h + 8


# -------------------------------------------------------------------- content
def build(total_pages, out_path):
    global c, y, page_num, TOTAL_PAGES
    TOTAL_PAGES = total_pages
    page_num = 1
    c = canvas.Canvas(str(out_path), pagesize=A4)
    c.setTitle("Immunoglobulin Home Therapy - Adverse Reaction Report")
    c.setSubject("Report a reaction to IVIG or SCIG to the Immunology team")
    c.setAuthor("Clinical Immunology, Royal Free London")
    y = PAGE_H - TOP

    # ---------------- page 1: identity, contacts, triage ----------------
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(TEAL)
    c.drawString(M, y - 9, "IMMUNOLOGY HOME THERAPY", charSpace=1.5)
    y -= 17
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(INK)
    c.drawString(M, y - 22, "Immunoglobulin Reaction Report")
    y -= 29

    wrapped("For patients receiving immunoglobulin at home - IVIG (into a vein) or SCIG (under "
            "the skin). Please complete this form if you notice any unexpected side effect or "
            "reaction linked to your infusion, even if it seemed mild or settled on its own. "
            "It goes to your Immunology Specialist Nurse and Consultant.",
            "Helvetica", 9.6, CW, 12.5, MUTED)
    gap(5)

    contact_strip()

    alert_box(
        "CALL 999 NOW IF YOU HAVE ANY OF THESE",
        "Stop your infusion, stop filling in this form, and call 999 or go to your nearest "
        "A&E if you have:",
        ["Difficulty breathing, wheezing, or tightness in your throat",
         "Swelling of your face, lips, tongue, or throat",
         "A widespread rash together with feeling faint, dizzy, or unwell",
         "Chest pain or pressure",
         "Weakness or numbness down one side, a drooping face, slurred speech, or sudden "
         "loss of vision",
         "Pain, swelling, warmth, or redness in one leg or arm",
         "Collapse or loss of consciousness"],
        "Tell the paramedics or A&E staff that you receive immunoglobulin (IVIG or SCIG) at "
        "home, and bring your batch number if you can.",
        DANGER, DANGER_BG, DANGER_STRONG)

    alert_box(
        "CONTACT THE IMMUNOLOGY TEAM TODAY IF YOU HAVE",
        "These need to be looked at the same day. Call the Immunology Specialist Nurses on "
        + TEL + ", or NHS 111 if the line is closed - then complete this form afterwards:",
        ["A severe headache with a stiff neck, dislike of bright light, or vomiting",
         "Dark, cola-coloured, or red urine",
         "Yellowing of your skin or the whites of your eyes",
         "Unusual breathlessness or extreme tiredness that is new",
         "Passing much less urine than normal",
         "A fever with shivering or shaking (rigors)",
         "A rash that keeps spreading"],
        "If you are unsure how urgent your symptom is, always ring rather than wait.",
        WARN, WARN_BG, WARN_STRONG)

    info_box("How to fill in and send this form", [
        "You can type straight into this PDF and save it, or print it and write on it.",
        "Have your product box or vial label to hand - we need the batch number from it.",
        "Fill in as much as you can. If you are not sure of an answer, leave it blank rather "
        "than delay sending it.",
        "Email the completed form to " + EMAIL + ", or bring it to your next appointment.",
    ])

    qr_box()
    new_page()

    # ---------------- section 1 ----------------
    section_header("SECTION 1", "About you",
                   "So we can find your records and get back to you quickly.")
    labeled_field("Patient name", "p_name", "Your full name")
    labeled_pair("Date of birth", "p_dob", "Your date of birth",
                 "NHS or hospital number", "p_nhs", "Your NHS or hospital number")
    labeled_pair("Today's date", "p_today", "The date you are filling in this form",
                 "Best phone number today", "p_phone", "The best number to reach you on today")

    qlabel("Who is filling in this form?", keep=60)
    radio("filler", "The patient", "The patient")
    radio("filler", "Parent or guardian", "A parent or guardian")
    radio("filler", "Carer or family member", "A carer or family member - name:",
          inline=("filler_name", "Name of the carer or family member"))
    rule()

    # ---------------- section 2 ----------------
    section_header("SECTION 2", "Your immunoglobulin",
                   "Details of the infusion the reaction followed. The batch number is the most "
                   "important item on this page - it lets us trace the exact product you received.")

    qlabel("How do you receive your immunoglobulin?", keep=90)
    radio("route", "IVIG", "IVIG", "Into a vein, through a drip or line",
          tooltip="IVIG - into a vein")
    radio("route", "SCIG", "SCIG", "Under the skin, using a pump or rapid push",
          tooltip="SCIG - under the skin")
    radio("route", "Facilitated SCIG", "Facilitated SCIG",
          "Under the skin with hyaluronidase first, e.g. HyQvia",
          tooltip="Facilitated SCIG, e.g. HyQvia")
    gap(4)

    labeled_field("Brand name of your product", "prod_name",
                  "The brand name of your immunoglobulin",
                  hint_text="For example Privigen, Octagam, Intratect, Hizentra, Cuvitru, "
                            "HyQvia, Gammaplex, Subgam, Gamunex.")

    # batch box - visually emphasised
    bl = simpleSplit("Copy this exactly from the vial, bottle, or syringe label - letters and "
                     "numbers. If you used more than one vial, please list every batch number.",
                     "Helvetica", 8.8, CW - 24)
    bh = 12 + 15 + len(bl) * 11 + 40 + 10
    ensure(bh + 8)
    c.setFillColor(TINT)
    c.setStrokeColor(TEAL_LINE)
    c.setLineWidth(1.2)
    c.roundRect(M, y - bh, CW, bh, 9, stroke=1, fill=1)
    ty = y - 12
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColor(INK)
    c.drawString(M + 12, ty - 10.5, "Batch or lot number")
    ty -= 15
    c.setFont("Helvetica", 8.8)
    c.setFillColor(MUTED)
    for ln in bl:
        c.drawString(M + 12, ty - 8.8, ln)
        ty -= 11
    saved_y = y
    y = ty - 2
    text_field("prod_batch", "Batch or lot numbers - copy exactly from the label",
               M + 12, CW - 24, h=38, multiline=True)
    y = saved_y - bh - 12

    labeled_pair("Dose given (grams)", "dose_g", "For example 30 g",
                 "How often you have it", "dose_freq", "For example every week")
    labeled_pair("Date of that infusion", "inf_date",
                 "Date of the infusion the reaction followed",
                 "Time it started", "inf_time", "Time the infusion started")
    labeled_field("Number of infusion sites used (SCIG)", "inf_sites",
                  "For SCIG - how many sites, and where",
                  hint_text="For example: 2 sites, abdomen and thigh. Leave blank if you have IVIG.")

    qlabel("Was this a new batch number?", keep=64)
    hint("A batch number you had not used before.")
    radio("newbatch", "Yes", "Yes")
    radio("newbatch", "No", "No")
    radio("newbatch", "Not sure", "Not sure")
    gap(4)

    qlabel("Have you changed brand or product recently?", keep=52)
    radio("newprod", "Yes", "Yes, this is a different brand from my usual one")
    radio("newprod", "No", "No, it is my usual brand")
    radio("newprod", "Not sure", "Not sure")
    gap(4)

    qlabel("Was the infusion running faster than usual?", keep=68)
    radio("rate", "Faster", "Yes, faster than usual")
    radio("rate", "Usual rate", "No, my usual rate")
    radio("rate", "Slower", "It was slower than usual")
    radio("rate", "Not sure", "Not sure")
    gap(4)

    qlabel("Did you take your usual pre-medication before this infusion?", keep=76)
    hint("For example paracetamol, an antihistamine such as cetirizine, or a steroid.")
    radio("premed", "Yes", "Yes - what I took:",
          inline=("premed_what", "What pre-medication did you take?"))
    radio("premed", "Missed", "No, I missed it this time")
    radio("premed", "Not prescribed", "I am not prescribed any pre-medication")
    gap(4)

    qlabel("Were you unwell in the days before this infusion?", keep=56)
    hint("For example a cold, chest infection, urine infection, or a temperature.")
    radio("unwell", "Yes", "Yes - what was wrong:",
          inline=("unwell_what", "What were you unwell with?"))
    radio("unwell", "No", "No, I was well")
    rule()

    # ---------------- section 3 ----------------
    section_header("SECTION 3", "The reaction",
                   "Help us understand what you experienced and when.")

    qlabel("1. When did the reaction start?", keep=100)
    radio("onset", "During", "During the infusion")
    radio("onset", "Within 1 hour", "Within 1 hour of finishing")
    radio("onset", "1-6 hours", "1 to 6 hours after")
    radio("onset", "6-24 hours", "6 to 24 hours after")
    radio("onset", "1-3 days", "1 to 3 days after")
    radio("onset", "Over 3 days", "More than 3 days after")
    gap(3)
    labeled_pair("Date it started", "r_date", "Date the reaction started",
                 "Time it started", "r_time", "Time the reaction started")

    qlabel("2. Please describe what happened in your own words", keep=92)
    text_field("r_desc", "Describe what happened in your own words",
               M, CW, h=88, multiline=True)
    y -= 88 + 12

    qlabel("3. Which whole-body symptoms did you have?", keep=120)
    hint("Tick all that apply.")
    for nm, lb in [("sym_headache", "Headache"),
                   ("sym_fever", "Fever, chills, or shivering"),
                   ("sym_nausea", "Nausea or vomiting"),
                   ("sym_muscle", "Muscle aches"),
                   ("sym_joint", "Joint pain"),
                   ("sym_back", "Back pain"),
                   ("sym_tired", "Unusual tiredness or feeling washed out"),
                   ("sym_flu", "Flu-like feeling"),
                   ("sym_dizzy", "Dizziness or lightheadedness"),
                   ("sym_flush", "Flushing of the face"),
                   ("sym_rash", "Rash, hives, or itching"),
                   ("sym_palp", "Racing heart or palpitations"),
                   ("sym_tummy", "Tummy pain or diarrhoea")]:
        check(nm, lb)
    check("sym_bp", "Blood pressure change, if measured:",
          inline=("sym_bp_txt", "What was your blood pressure reading?"))
    check("sym_other", "Something else:",
          inline=("sym_other_txt", "Describe the other symptom"))
    gap(4)

    qlabel("4. Any symptoms at the infusion site?", tag="SCIG", keep=120)
    hint("Tick all that apply. Some site swelling and redness is normal with SCIG, but we "
         "still like to know about it.")
    for nm, lb in [("site_swell", "Swelling or a lump at the site"),
                   ("site_red", "Redness"),
                   ("site_itch", "Itching at the site"),
                   ("site_pain", "Pain or soreness"),
                   ("site_bruise", "Bruising"),
                   ("site_leak", "Fluid leaking from the site"),
                   ("site_hot", "The site felt hot"),
                   ("site_long", "A lump that lasted longer than 24 hours"),
                   ("site_none", "No site symptoms, or I have IVIG")]:
        check(nm, lb)
    gap(4)

    qlabel("5. Did you have any of these symptoms?", keep=130)
    hint("These ones we always want to know about straight away. If you tick any, please ring "
         "the Immunology Specialist Nurses on " + TEL + " today - do not wait for us to reply "
         "to this form.")
    for nm, lb in [("rf_headneck",
                    "Severe headache with a stiff neck, dislike of bright light, or vomiting"),
                   ("rf_urine", "Dark, cola-coloured, or red urine"),
                   ("rf_jaundice", "Yellowing of your skin or the whites of your eyes"),
                   ("rf_breath", "New breathlessness or extreme tiredness"),
                   ("rf_lessurine", "Passing much less urine than normal"),
                   ("rf_rigors", "Fever with shaking or rigors")]:
        check(nm, lb, flag=True)
    check("rf_none", "None of these")
    gap(4)

    qlabel("6. How long did the reaction last?", keep=100)
    radio("duration", "Ongoing", "It is still going on")
    radio("duration", "Under 1 hour", "Less than 1 hour")
    radio("duration", "1-6 hours", "1 to 6 hours")
    radio("duration", "6-24 hours", "6 to 24 hours")
    radio("duration", "1-3 days", "1 to 3 days")
    radio("duration", "Over 3 days", "More than 3 days")
    gap(4)

    qlabel("7. How severe would you rate this reaction?", keep=80)
    radio("severity", "Mild", "Mild", "I notice it, but it doesn't interfere with my day.",
          tooltip="Mild")
    radio("severity", "Moderate", "Moderate",
          "It is uncomfortable and making my daily activities difficult.", tooltip="Moderate")
    radio("severity", "Severe", "Severe",
          "It is highly painful or prevents me from doing my daily activities.",
          tooltip="Severe")
    gap(4)

    qlabel("8. Has this happened with your immunoglobulin before?", keep=68)
    radio("before", "First time", "No, this is the first time")
    radio("before", "Yes same product", "Yes, with this same product")
    radio("before", "Yes different product", "Yes, but with a different product")
    radio("before", "Not sure", "Not sure")
    rule()

    # ---------------- section 4 ----------------
    section_header("SECTION 4", "What you did",
                   "Help us understand how you managed the reaction so far.")

    qlabel("9. Did you slow down or stop the infusion?", keep=84)
    radio("stopped", "Slowed", "I slowed it down")
    radio("stopped", "Paused", "I paused it, then restarted")
    radio("stopped", "Stopped", "I stopped completely and did not restart")
    radio("stopped", "Carried on", "I carried on at the same rate")
    radio("stopped", "Not applicable", "Not applicable - I had already finished")
    gap(4)

    qlabel("10. If you slowed or stopped, did the symptoms improve?", keep=84)
    radio("improved", "Settled", "Yes, they settled")
    radio("improved", "A little", "They improved a little")
    radio("improved", "No change", "No change")
    radio("improved", "Worse", "They got worse")
    radio("improved", "Not applicable", "Not applicable")
    gap(4)

    qlabel("11. Did you finish the full dose?", keep=60)
    radio("finished", "Full dose", "Yes, I had the full dose")
    radio("finished", "Part", "I had part of it - roughly how much:",
          inline=("finished_how", "Roughly how much of the dose did you have?"))
    radio("finished", "None", "None of it")
    gap(4)

    qlabel("12. Did you take any medication to treat these symptoms?", keep=56)
    hint("For example paracetamol, ibuprofen, or an antihistamine such as cetirizine.")
    radio("meds", "No", "No")
    radio("meds", "Yes", "Yes - what and when:",
          inline=("meds_list", "What medication did you take, and when?"))
    gap(4)

    qlabel("13. Have you contacted anyone about this reaction yet?", keep=120)
    hint("Tick all that apply.")
    for nm, lb in [("con_none", "No, I am reporting it for the first time now"),
                   ("con_nurse", "Immunology Specialist Nurse"),
                   ("con_doctor", "Immunology doctor or consultant"),
                   ("con_homecare", "Homecare company nurse"),
                   ("con_gp", "GP"),
                   ("con_111", "NHS 111"),
                   ("con_ae", "A&E or 999")]:
        check(nm, lb)
    check("con_when", "Date and time I contacted them:",
          inline=("con_when_txt", "What date and time did you contact them?"))
    gap(4)

    qlabel("14. What were you advised to do?", keep=70)
    hint("Leave blank if you have not spoken to anyone yet.")
    text_field("advice", "What were you advised to do?", M, CW, h=56, multiline=True)
    y -= 56 + 12
    rule()

    # ---------------- section 5 ----------------
    section_header("SECTION 5", "Getting back to you",
                   "So the Immunology team can follow this up with you.")

    qlabel("15. How would you prefer us to contact you?", keep=90)
    hint("Tick all that work for you.")
    check("c_phone", "Phone call:", inline=("c_phone_txt", "Best number to call you on"))
    check("c_text", "Text message:", inline=("c_text_txt", "Mobile number for text messages"))
    check("c_email", "Email:", inline=("c_email_txt", "Email address"))
    check("c_visit", "Discuss at my next appointment or home visit")
    gap(4)

    qlabel("16. Can we leave a voicemail if you don't answer?", keep=40)
    radio("vm", "Yes", "Yes")
    radio("vm", "No", "No, please just try again")
    gap(4)

    qlabel("17. Did you feel you had clear instructions on what to do if you had a reaction?",
           tag="OPTIONAL", keep=56)
    radio("instr", "Yes", "Yes")
    radio("instr", "No", "No")
    radio("instr", "Not sure", "I'm not sure")
    gap(4)

    qlabel("18. Anything else you would like the team to know?", tag="OPTIONAL", keep=60)
    text_field("anything", "Anything else you would like the team to know?",
               M, CW, h=56, multiline=True)
    y -= 56 + 12

    gap(2)
    wrapped("Send your completed form to " + EMAIL + " or bring it to your next appointment. "
            "This form does not replace urgent medical care - if your symptoms get worse, "
            "contact the Immunology team, NHS 111, or 999.",
            "Helvetica-Oblique", 8.8, CW, 11.5, MUTED)

    footer()
    c.save()
    return page_num


if __name__ == "__main__":
    if not QR_IMG.exists():
        raise SystemExit("Missing %s - run 'python src/make_qr.py' first." % QR_IMG)
    DIST.mkdir(exist_ok=True)
    total = build(1, SCRATCH)          # pass 1: count pages
    build(total, OUT)                  # pass 2: real footers
    SCRATCH.unlink(missing_ok=True)
    print("Wrote %s - %d pages" % (OUT.relative_to(REPO), total))
