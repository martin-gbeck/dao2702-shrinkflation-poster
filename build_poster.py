"""Builds the A4 poster (shrinkflation_poster.pptx) from the figures in figs/.

Run: uv run --no-project --with python-pptx python build_poster.py
"""

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

NAVY, BLUE2, INK, INK2, MUTED = "0d366b", "1c5cab", "0b0b0b", "52514e", "6f6e69"
CARD, INTRO = "f4f5f7", "eef4fc"
FONT = "Arial"

SW, SH, M = 8.27, 11.69, 0.3
CW = SW - 2 * M
GUT = 0.14
COL = (CW - 2 * GUT) / 3

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(SW), Inches(SH)
slide = prs.slides.add_slide(prs.slide_layouts[6])


def box(x: float, y: float, w: float, h: float, fill: str, name: str, shape: MSO_SHAPE = MSO_SHAPE.ROUNDED_RECTANGLE) -> None:
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.name = name
    s.fill.solid()
    s.fill.fore_color.rgb = RGBColor.from_string(fill)
    s.line.fill.background()
    s.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = 0.04


def text(x: float, y: float, w: float, h: float, paras: list[list[tuple[str, dict[str, object]]]], name: str,
         size: float = 6.3, color: str = INK, align: PP_ALIGN = PP_ALIGN.LEFT, anchor: MSO_ANCHOR = MSO_ANCHOR.TOP,
         space_after: float = 0) -> None:
    """paras: one list of (run text, run options) per paragraph. Options: b, color, size."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, runs in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        p.line_spacing = 1.05
        for t, o in runs:
            r = p.add_run()
            r.text = t
            r.font.name = FONT
            r.font.size = Pt(float(o.get("size", size)))
            r.font.bold = bool(o.get("b", False))
            r.font.color.rgb = RGBColor.from_string(str(o.get("color", color)))


# ---------- title block ----------
text(M, 0.2, CW, 0.42, [[("Shrinkflation in Singapore's Private Homes", {"b": True})]], "Title", size=23, color=NAVY)
text(M, 0.62, CW, 0.2, [[("Homes shrank by 40% to keep the price tag within reach. Since URA capped unit numbers, the price tag rises instead.", {})]],
     "Subtitle", size=9.5, color=INK)
text(M, 0.84, CW, 0.14, [[("DAO2702 Group Assignment  ·  Team [team name]  ·  [member names]", {})]], "Team line", size=6.5, color=MUTED)

# ---------- introduction ----------
IY, IH = 1.03, 0.86
box(M, IY, CW, IH, INTRO, "Introduction card")
icw = (CW - 0.2 - 2 * 0.18) / 3
intro = [
    ("Shrinkflation in housing",
     "Shrinkflation means a product gets smaller while its price stays put, so the price per unit rises without the tag moving [7]. "
     "In a home, the product is floor area, the unit price is price per sq ft (PSF) and the tag is the total price, which is what "
     "a bank lends against. MAS caps repayments at 55% of income, tested at 4% interest or more [4]."),
    ("Question",
     "Did Singapore's private homes shrink to keep the total price within reach, and is that still happening in 2025? "
     "Row 1 shows what shrank, row 2 whether the shrink is real and how it works, and row 3 why it happened and what changed "
     "once URA capped the number of units a project may build [5]."),
    ("Data",
     "24,131 URA transactions from 2025 and 74,436 from Aug 2020 to Dec 2023 [1], after dropping 155 rows outside 200–5,000 sq ft "
     "and fixing the 'freenhold' typo. A home's vintage is its lease-start year (99-year leaseholds, 66,237 sales), close to the year "
     "its land was sold. Outside data: URA price index [2], SingStat income [3], MAS rules [4]."),
]
for k, (head, body) in enumerate(intro):
    text(M + 0.1 + k * (icw + 0.18), IY + 0.08, icw, IH - 0.14,
         [[(head, {"b": True, "size": 7, "color": NAVY})], [(body, {})]], f"Intro {head}", size=6.2, color=INK, space_after=1.5)

# ---------- panels ----------
ROWS = ["WHAT SHRANK", "IS IT REAL, AND HOW DOES IT WORK?", "WHY IT HAPPENED, AND WHAT CHANGED"]
PANELS = [
    ("01_histogram.png", "New launches in 2025 are 21% smaller than resale homes",
     "Share of 2025 sales per 50 sq ft band, new launches above the axis and resale below. Median new unit 797 sq ft against "
     "1,012 for resale. Homes of 1,200 sq ft or more are 34% of resale but only 18% of new launches."),
    ("02_line_vintage.png", "Homes on land sold after 2008 are 43% smaller",
     "Median and middle 50% of floor area by lease-start year, all 2020–25 sales. Sizes held near 1,240 sq ft until 2008, fell to "
     "710 sq ft for land sold in 2013–15 and stayed there, the floor set by URA's caps on units per project [5]."),
    ("03_stacked_mix.png", "Shoeboxes went from 1% to 13% of homes, big homes from 34% to 8%",
     "Unit-size mix by lease-start era. One- and two-bedroom sizes (507–750 sq ft) grew from 5% to 38% of units. The 2019 cap "
     "pushed shoeboxes back to 9%, but homes over 1,300 sq ft stayed rare at 11%."),
    ("04_coefficients.png", "The shrink is the same inside each district",
     "Regression of log floor area on lease-start era against 1990–08 (66,237 sales, 95% intervals clustered by 464 projects). "
     "Holding district, type and sale year fixed moves each gap by about one point, so location does not explain the shrink."),
    ("05_scatter_isoprice.png", "Smaller homes kept the price tag down until the 2019 cap",
     "2025 prices. Dots are projects, large markers era medians; points on one grey curve cost the same. From 1990–08 to 2013–18 "
     "floor area fell 40% and PSF rose 27%, and the median price fell from S$1.72M to S$1.45M. Post-2019 homes are 7% larger and cost S$2.05M."),
    ("06_violin_pricing.png", "A launch is priced per sq ft, so floor area is the only lever on the price tag",
     "2025 new sales in 50 projects with 20+ sales (10,389 units), each unit's PSF against its own project's median. Every size "
     "band's median sits within 1.5% of zero. Price moves one for one with floor area, so a lower price tag means fewer sq ft."),
    ("07_lollipop_macro.png", "Prices ran furthest ahead of incomes in 2007–13, when that land was sold",
     "URA non-landed price index [2] ÷ median household income [3], against the 2001–25 average. Every year from "
     "2007 to 2013 except 2009 was 6–18% less affordable than usual. Incomes then caught up, and by 2025 the ratio was near average."),
    ("08_heatmap_tdsr.png", "At 2025 launch prices, the median household can borrow for 743 sq ft",
     "Affordable area = largest loan under MAS rules (repayments ≤55% of income at 4% [4]) ÷ 75% LTV ÷ PSF. Orange boxes miss "
     "the 797 sq ft median new unit. At median income (S$12,446 [3]) reach fell from 1,117 sq ft at 2020 PSF to 743. "
     "Rate cuts below 4% change nothing."),
    ("09_waterfall.png", "With shrinking capped, the new-launch price tag rose 49% in five years",
     "Typical new-launch price, late 2020 against 2025, split exactly into PSF and floor area (geometric means, each region against "
     "itself, 2025 weights). PSF added 39% and floor area 7%. Units no longer shrink, so buyers now pay the whole PSF rise."),
]
FIG_W, FIG_H = 2.3, 1.55
LABEL_H, PANEL_H, ROW_GAP = 0.18, 2.5, 0.04
y = IY + IH + 0.06
for r, label in enumerate(ROWS):
    text(M, y, CW, LABEL_H, [[(f"{r + 1}   {label}", {"b": True})]], f"Row {r + 1} label", size=6.8, color=BLUE2, anchor=MSO_ANCHOR.MIDDLE)
    py = y + LABEL_H + 0.02
    for c in range(3):
        k = r * 3 + c
        fig, head, cap = PANELS[k]
        px = M + c * (COL + GUT)
        box(px, py, COL, PANEL_H, CARD, f"Panel {k + 1} card")
        badge = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(px + 0.08), Inches(py + 0.08), Inches(0.2), Inches(0.2))
        badge.name = f"Panel {k + 1} number"
        badge.fill.solid(); badge.fill.fore_color.rgb = RGBColor.from_string(NAVY); badge.line.fill.background(); badge.shadow.inherit = False
        tf = badge.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        run = p.add_run(); run.text = str(k + 1); run.font.name = FONT; run.font.size = Pt(7); run.font.bold = True
        run.font.color.rgb = RGBColor.from_string("ffffff")
        text(px + 0.34, py + 0.06, COL - 0.42, 0.32, [[(head, {"b": True})]], f"Panel {k + 1} headline", size=7.2, color=INK,
             anchor=MSO_ANCHOR.MIDDLE)
        pic = slide.shapes.add_picture(f"figs/{fig}", Inches(px + (COL - FIG_W) / 2), Inches(py + 0.39), Inches(FIG_W), Inches(FIG_H))
        pic.name = f"Panel {k + 1} figure"
        text(px + 0.09, py + 0.39 + FIG_H + 0.03, COL - 0.18, PANEL_H - 0.39 - FIG_H - 0.06, [[(cap, {})]], f"Panel {k + 1} caption",
             size=5.7, color=INK2)
    y = py + PANEL_H + ROW_GAP

# ---------- conclusion ----------
CY, CH = y + 0.03, 0.93
box(M, CY, CW, CH, NAVY, "Conclusion card")
aw = CW * 0.49
text(M + 0.12, CY + 0.08, aw - 0.2, CH - 0.14, [
    [("Answer", {"b": True, "size": 7.5, "color": "ffffff"})],
    [("Yes, until URA stopped it. Homes on land sold in 2009–13, when prices ran furthest ahead of incomes, are about 40% smaller "
      "than earlier homes in the same districts, and that kept their price tags down. Launches are priced per sq ft, so cutting floor "
      "area was the only way. URA's unit caps put a floor under sizes near 750 sq ft. Since then the PSF rise has gone straight into "
      "the price tag (+49% from late 2020 to 2025), which now sits at the edge of what a median household can borrow.", {"color": "ffffff"})],
], "Answer text", size=6.3, space_after=1.5)
rx = M + aw + 0.05
text(rx, CY + 0.08, CW - aw - 0.17, CH - 0.14, [
    [("Recommendations", {"b": True, "size": 7.5, "color": "ffffff"})],
    [("Buyers: ", {"b": True, "color": "ffffff"}),
     ("compare PSF and space, not the price tag. A 2025 resale home gives 47% more floor area per dollar than a new launch "
      "(S$1,747 against S$2,572 PSF), in exchange for age and a shorter lease.", {"color": "ffffff"})],
    [("Developers: ", {"b": True, "color": "ffffff"}),
     ("with shrinking capped, layouts that waste less space are what is left to compete on.", {"color": "ffffff"})],
    [("Policymakers: ", {"b": True, "color": "ffffff"}),
     ("the cap protects living space but moves the pressure onto price. Affordability now rests on land supply and income "
      "growth.", {"color": "ffffff"})],
], "Recommendations text", size=6.2, space_after=1.2)

# ---------- limitations and references ----------
FY = CY + CH + 0.05
text(M, FY, CW, SH - FY - 0.08, [
    [("Limitations. ", {"b": True}),
     ("Eras are compared at 2025 prices, not their launch prices, and older homes are also cheaper per sq ft because of age and lease "
      "decay. No bedroom count; strata-area rules changed in June 2023 [6]; 2024 is missing; income includes employer CPF, so true "
      "borrowing power is a little lower. All results are associations, not causal effects.", {})],
    [("References. ", {"b": True}),
     ("[1] URA REALIS via DAO2702 (properties2025.csv; Lecture 6 properties23.csv). [2] URA Private Residential Property Price Index, "
      "data.gov.sg. [3] SingStat household employment income, data.gov.sg; Key Household Income Trends 2025. [4] MAS: TDSR 55% "
      "(Dec 2021) and 4% rate floor (Sep 2022), via DBS. [5] URA circular DC18-06 (2018). [6] Huttons via EdgeProp (2025), Are home "
      "sizes in Singapore shrinking? [7] ONS (2019), The impact of shrinkflation on CPIH. Code: shrinkflation.ipynb.", {})],
], "Limitations and references", size=5.2, color=MUTED, space_after=1)

prs.save("shrinkflation_poster.pptx")
print("saved shrinkflation_poster.pptx")
