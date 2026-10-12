"""Builds the team's presenting guide (shrinkflation_poster_guide.docx) from figs/.

Run: uv run --no-project --with python-docx python build_guide.py
"""

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

NAVY, ORANGE, INK2 = RGBColor(0x0D, 0x36, 0x6B), RGBColor(0xC4, 0x4E, 0x1E), RGBColor(0x52, 0x51, 0x4E)

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin = sec.bottom_margin = Cm(2)

normal = doc.styles["Normal"]
normal.font.name = "Arial"
normal.font.size = Pt(10)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
normal.paragraph_format.space_after = Pt(5)
normal.paragraph_format.line_spacing = 1.15
for name, size, color in [("Heading 1", 15, NAVY), ("Heading 2", 12.5, NAVY), ("Heading 3", 10.5, INK2), ("Title", 22, NAVY), ("List Bullet", 10, None)]:
    st = doc.styles[name]
    st.font.name = "Arial"
    st.font.size = Pt(size)
    if color is not None:
        st.font.color.rgb = color
    rf = st.element.get_or_add_rPr().get_or_add_rFonts()
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):   # theme fonts override the named font
        rf.attrib.pop(qn(attr), None)
    rf.set(qn("w:ascii"), "Arial")
    rf.set(qn("w:hAnsi"), "Arial")
doc.styles["Heading 1"].paragraph_format.space_before = Pt(16)
doc.styles["Heading 2"].paragraph_format.space_before = Pt(14)
doc.styles["Heading 3"].paragraph_format.space_before = Pt(8)
doc.styles["Heading 3"].paragraph_format.space_after = Pt(2)
for _h in ("Heading 1", "Heading 2", "Heading 3"):
    doc.styles[_h].paragraph_format.keep_with_next = True

# page number in the footer
fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
for tag, text in [("begin", None), (None, "PAGE"), ("end", None)]:
    r = fp.add_run()
    r.font.size = Pt(8)
    if tag:
        el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), tag)
    else:
        el = OxmlElement("w:instrText"); el.set(qn("xml:space"), "preserve"); el.text = text
    r._r.append(el)


def para(text: str, style: str | None = None, size: float | None = None, color: RGBColor | None = None, bold_all: bool = False) -> None:
    """Paragraph with **bold** spans."""
    p = doc.add_paragraph(style=style)
    for i, chunk in enumerate(text.split("**")):
        if not chunk:
            continue
        r = p.add_run(chunk)
        r.bold = bold_all or i % 2 == 1
        if size:
            r.font.size = Pt(size)
        if color is not None:
            r.font.color.rgb = color


def bullets(items: list[str]) -> None:
    for t in items:
        para(t, style="List Bullet")


def qa(pairs: list[tuple[str, str]]) -> None:
    for q, a in pairs:
        para(f"**{q}** {a}")


def table(header: list[str], rows: list[list[str]], widths: list[float], bold_first: bool = True) -> None:
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for j, h in enumerate(header):
        t.rows[0].cells[j].text = h
    for row in rows:
        cells = t.add_row().cells
        for j, v in enumerate(row):
            cells[j].text = v
    for j, w in enumerate(widths):
        t.columns[j].width = Cm(w)
    for i, row in enumerate(t.rows):
        for j, w in enumerate(widths):
            cell = row.cells[j]
            cell.width = Cm(w)
            if i == 0:   # light header shading
                shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), "E3ECF8")
                cell._tc.get_or_add_tcPr().append(shd)
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.line_spacing = 1.05
                for r in p.runs:
                    r.font.size = Pt(9)
                    r.bold = i == 0 or (j == 0 and bold_first)
    doc.add_paragraph()


def lead(text: str) -> None:
    """Transition line that opens the next chart's page."""
    para(text, color=INK2)
    doc.paragraphs[-1].paragraph_format.page_break_before = True
    doc.paragraphs[-1].paragraph_format.keep_with_next = True


def chart(num: int, kind: str, fig: str, takeaway: str, sections: list[tuple[str, list[str] | str]]) -> None:
    h = doc.add_heading(f"Chart {num}: {kind}", level=2)
    h.paragraph_format.page_break_before = False   # each chart starts on the page its lead-in line (or the section intro) opens
    para(takeaway, size=11, color=ORANGE, bold_all=True)
    doc.paragraphs[-1].paragraph_format.keep_with_next = True
    doc.add_picture(f"figs/{fig}", width=Cm(7.9))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for head, body in sections:
        doc.add_heading(head, level=3)
        if isinstance(body, str):
            para(body)
        else:
            bullets(body)


# ================= front =================
doc.add_paragraph("Shrinkflation poster: guide for presenting", style="Title")
para("DAO2702 group assignment. What each chart says, how to read it, why it is on the poster and what to answer when asked.", color=INK2)

doc.add_heading("1. The story in one minute", level=1)
para("If you only get a minute, say this. Singapore's private homes did shrink to keep the price tag within reach. Homes built on land sold "
     "from 2009 to 2013 are about 40% smaller than homes on earlier land, and the gap is the same within each district. It worked because "
     "a new launch is priced per square foot, so a smaller unit means a lower price tag. The shrink happened in the years when home prices "
     "were furthest ahead of incomes.")
para("In 2019 URA tightened its cap on how many units a project may build, and the shrink stopped. Prices per square foot kept rising, so "
     "the price tag rises instead: a typical new launch cost 49% more in 2025 than in late 2020, and at 2025 launch prices the median "
     "household can borrow for less floor area than the median new unit.")

doc.add_heading("2. What we hand in", level=1)
bullets([
    "**Deadline:** Friday 16 October 2026, 23:59. Up to 24 hours late costs 20%. Later than that counts as no submission.",
    "**One zip file** named Poster_Jupyter, holding the single-sided A4 poster as a PDF and the code. The course outline asks for the code "
    "as HTML and the Canvas brief asks for IPYNB, so we hand in both: shrinkflation.ipynb and shrinkflation.html.",
    "**How it is graded:** mainly on the quality of the charts (the right chart for the data, following plotting conventions) and on the "
    "insights the charts and comments give. The poster should carry short comments with the key findings or recommendations.",
    "**Team Jupyter:** Martin, Huaitao (Aizen) Yu, Manan, Linda, Midhvan Agarwal and Hoyoung Hwang. Before submitting, check everyone's name is "
    "spelled the way they want it on the poster, export the PDF from PowerPoint and check it is one page.",
])

doc.add_heading("3. How the poster is built", level=1)
bullets([
    "**Top:** the question, with one grey line underneath holding the few terms you need to read the charts. The key terms table below explains them in full.",
    "**Row 1, what shrank (charts 1 to 3):** the size gap today, when it opened, and which sizes disappeared.",
    "**Row 2, is it real and how does it work (4 to 6):** a check that it is not location, what the shrink did to price tags, and how a launch is priced.",
    "**Row 3, why it happened and what changed (7 to 9):** affordability over 25 years, what a household can borrow, and what happened after the cap.",
    "**Bottom:** the answer, three findings that match the three rows, and a small footnote with data, limitations and sources.",
])
para("Every chart has one bold line on top. That line is the single most important takeaway, with a number you can read off the chart. "
     "When you present, say that line first, then point to where it comes from on the chart.")

doc.add_heading("4. Key terms", level=1)
table(["Term", "What it means", "Charts"], [
    ["Shrinkflation", "A product shrinks while its price stays put, so the price per unit rises without the price tag moving. The UK statistics "
                      "office (ONS) uses the term for groceries. Here the product is floor area.", "All"],
    ["PSF", "Price per square foot: price ÷ floor area.", "5, 6, 8, 9"],
    ["Price tag", "The total price of a home, floor area × PSF. It is what a buyer pays and borrows against.", "5, 8, 9"],
    ["New launch, resale, sub sale", "New launch: bought from the developer. Resale: second-hand. Sub sale: bought from someone who bought from the "
                                     "developer before the building was finished. Sub sales (4% of 2025) are left out of new-vs-resale comparisons.", "1, 6, 9"],
    ["Lease-start year", "The year a 99-year lease began. For a condo on government land it is roughly when the land was sold, which is when the "
                         "developer planned the unit sizes. We use it as a home's vintage. Freehold homes have none, so the vintage charts use "
                         "99-year leaseholds only.", "2 to 5"],
    ["Shoebox", "A unit of 506 sq ft (47 m²) or less.", "3"],
    ["URA unit cap", "Since January 2012 a condo outside the Central Area may have at most total floor area ÷ 70 m² units. From 17 January 2019 the "
                     "divisor is 85 m². More floor area per unit puts a floor under the average unit size.", "2, 3, 5, 9"],
    ["MAS loan limit (TDSR)", "Total debt servicing ratio: all loan repayments can take at most 55% of gross monthly income, worked out at 4% "
                              "interest or the actual rate, whichever is higher. Banks lend at most 75% of the price on a loan of 30 years or less.", "8"],
    ["CCR, RCR, OCR", "URA's three regions: core central (prime), rest of central (city fringe) and outside central (suburbs).", "9"],
    ["Median", "The middle value. Used throughout because a few very large or very expensive homes would pull an average.", "All"],
], [3.4, 11.2, 2.0])

doc.add_heading("5. Background in two minutes", level=1)
bullets([
    "Most Singaporeans live in public HDB flats. Our data covers only the private market: condominiums and apartments sold by developers "
    "and resold between owners.",
    "Much of the land for private homes is sold by the government through land tenders (the Government Land Sales programme). A developer who wins "
    "a site gets a 99-year lease, plans the units, then launches them for sale, usually before the building is finished.",
    "Two agencies set the rules that matter here. URA (Urban Redevelopment Authority) plans land use and publishes the transaction data and the "
    "price index. MAS (Monetary Authority of Singapore) sets the lending rules that cap how much a buyer can borrow.",
    "Singapore quotes property prices per square foot (PSF), and floor areas in square feet. 1 m² is about 10.76 sq ft, so 85 m² is about "
    "915 sq ft.",
])

doc.add_heading("6. The URA unit cap in detail", level=1)
para("A unit is one home in a building: one apartment or condo flat. A tower with 300 apartments has 300 units. The cap does not limit how "
     "small a single unit can be. It limits how many units a project may have:")
para("**Maximum number of units = total floor area of the project ÷ 85 m²** (70 m² from 2012 to 2018)")
bullets([
    "**Worked example:** a site allowed 17,000 m² of floor area may have at most 17,000 ÷ 85 = 200 units. Squeezing in 400 shoeboxes is no "
    "longer allowed, so the homes have to average about 85 m² of floor area each.",
    "**It is a floor on the average, not a fixed size.** A developer can still build some small units if other units are big, and can always "
    "choose fewer, bigger units.",
    "**Floor area here is gross floor area**, which includes a share of space such as corridors. The flat a buyer gets is smaller than its share "
    "of gross floor area, which is why the post-2019 medians on the poster sit around 760 to 860 sq ft and not at 915.",
    "**Where it applies:** projects outside the Central Area. In nine neighbourhoods (Marine Parade, Joo Chiat-Mountbatten, Telok Kurau-Jalan "
    "Eunos, Balestier, Stevens-Chancery, Pasir Panjang, Kovan-How Sun, Shelford and Loyang) the divisor is 100 m² [8]. Since January 2023 the "
    "Central Area has its own rule: at least 20% of units in a project must be 70 m² or larger [7].",
    "**Timeline:** 70 m² from January 2012 (announced in 2011), raised to 85 m² from 17 January 2019 (announced 17 October 2018) [5]. Before "
    "2012 there was no cap, which is when shoeboxes spread.",
    "**Why URA did it:** to curb the spread of shoebox units and to stop new projects from straining local roads, schools and transport with "
    "more households than an area was planned for [8].",
    "**How it shows on the poster:** the vertical lines in chart 2, shoeboxes falling from 13% to 9% in chart 3, homes on post-2019 land being 7% "
    "larger in chart 5, and floor area adding +7% to the price tag in chart 9.",
    "**What we cannot claim:** that the cap caused the shrink to stop. The timing fits, but no chart isolates the cap from everything else that "
    "happened in those years.",
])

doc.add_heading("7. Reading the statistics", level=1)
table(["Term", "Plain meaning", "Where"], [
    ["Median", "The middle value when everything is sorted. Half the homes are smaller, half bigger. Used because a few huge homes would drag an average up.", "All"],
    ["Middle 50% (interquartile range)", "The range from the 25th to the 75th percentile: where the middle half of homes sit.", "2, 6"],
    ["Log scale", "Each step on the axis multiplies the value instead of adding to it. On log axes, price = floor area × PSF becomes a straight "
                  "line, which is why the constant-price curves in chart 5 are straight.", "5"],
    ["Regression with controls", "A model that compares eras while holding other things fixed, here district, property type and year of sale. "
                                 "It answers: among otherwise similar homes, how much smaller is each era?", "4"],
    ["95% confidence interval", "The range the true value very likely sits in, given the data. If the interval does not cross zero, the gap is "
                                "not a fluke of which homes happened to sell.", "4"],
    ["Clustered standard errors", "Units in one project are designed together, so 1,000 sales in one project are not 1,000 independent "
                                  "observations. Clustering by project makes the intervals honest about that.", "4"],
    ["Geometric mean", "The average of the logs, turned back into a number. It lets a price change split exactly into a PSF part and a floor-area "
                       "part.", "9"],
    ["Index (2009 = 100)", "A series rescaled so one year equals 100. A value of 200 means double the base year.", "7"],
], [4.0, 10.6, 2.0])

doc.add_heading("8. Data and cleaning", level=1)
bullets([
    "**properties2025.csv** (course dataset): 24,151 private home transactions in 2025, 12 columns.",
    "**properties23.csv** (Lecture 6): 74,571 transactions from Aug 2020 to Dec 2023 with the same columns. Aug to Oct 2021 is missing in the "
    "file, and neither file covers 2024.",
    "**Cleaning:** the 2025 file spells freehold as \"freenhold\" in 4,600 rows, which is fixed. 155 rows with floor area under 200 or over "
    "5,000 sq ft are dropped (20 from 2025, 135 from 2020 to 2023). They are en-bloc sales of whole buildings and penthouses. 98,567 rows remain.",
    "**Vintage charts (2 to 5)** use the 66,237 sales of 99-year leaseholds with a lease-start year from 1990 onwards.",
    "**Outside data:** URA's private residential price index (quarterly, 1Q2009 = 100) and SingStat's yearly change in median household employment "
    "income, both from data.gov.sg; the 2025 median household income of S$12,446 from SingStat's Key Household Income Trends 2025; MAS loan rules; "
    "URA circular DC18-06.",
    "**Tools:** Python with Polars for the data, matplotlib for the charts and statsmodels for the regression. Everything is in "
    "shrinkflation.ipynb and runs top to bottom.",
])

# ================= charts =================
doc.add_heading("9. Files and how to rerun", level=1)
bullets([
    "**shrinkflation.ipynb:** the notebook we hand in. It loads and cleans the data, draws all nine charts, prints every number on the poster "
    "and ends with the conclusion and references. It runs top to bottom in Colab or Jupyter if the data folder sits next to it, and needs "
    "polars, numpy, matplotlib and statsmodels (Colab has all four).",
    "**data/** holds the four CSVs, **figs/** the nine charts at poster size. Edit poster text in **shrinkflation_poster.pptx**; the charts "
    "are images, so change them in the notebook and re-insert.",
])

doc.add_heading("10. Chart by chart", level=1).paragraph_format.page_break_before = True
para("Each chart below has the takeaway from the poster, what it shows, how to read it, why we picked that chart type, what to watch out for, "
     "and answers to questions you might get.")

chart(1, "back-to-back histogram", "01_histogram.png", "New launches are 21% smaller than resale homes", [
    ("What it shows", "The size of every home sold in 2025, split into new launches (10,643 sales) and resale homes (12,549). The median new unit "
                      "has 797 sq ft, the median resale home 1,012 sq ft. Homes of 1,200 sq ft or more make up 34% of resale sales but only 18% "
                      "of new launches. New launches also cost far more per sq ft: S$2,572 against S$1,747."),
    ("How to read it", ["Each bar is a 50 sq ft band. Orange bars above the axis are new launches, blue bars below are resale.",
                        "Bar height is that band's share of its own group, so both groups add up to 100% and can be compared even though "
                        "their sales counts differ.",
                        "The black lines mark the two medians. The grey area is 1,200 sq ft and up."]),
    ("Why this chart", "A histogram shows the whole shape of the sizes, not just an average. Putting the two groups back to back stops the bars "
                       "from overlapping, which turns two histograms on one axis into a muddy block. It also shows where the gap sits: new "
                       "launches pile up between 500 and 900 sq ft, and the long right tail is almost all blue."),
    ("Watch out for", "This compares what sold in 2025, not like-for-like homes. Resale homes are older and some are in different places. "
                      "That is why charts 2 to 4 compare homes by the year their land was sold and check for district."),
    ("If someone asks", ["Why medians? Floor area and price are skewed by a few very large homes. The median is the typical home.",
                         "Where are sub sales? They are new homes resold before completion, so they belong to neither group (939 sales, 4%)."]),
])
lead("Lead into chart 2: \"So new homes are smaller today. Chart 2 shows when that happened.\"")

chart(2, "line with interquartile band", "02_line_vintage.png", "Homes shrank 43% for land sold after 2008", [
    ("What it shows", "The floor area of every 2020 to 2025 sale of a 99-year leasehold, by the year its lease started. Homes on land sold up "
                      "to 2008 sat around 1,200 sq ft (median 1,238 for 2005 to 2008). For land sold in 2013 to 2015 the median is 710 sq ft, "
                      "43% smaller. Since then it has stayed between about 680 and 860 sq ft."),
    ("How to read it", ["The x-axis is the lease-start year, close to when the land was sold.",
                        "The blue line is the median floor area. The light band covers the middle 50% of units (25th to 75th percentile).",
                        "The two vertical lines mark URA's unit cap in 2012 (floor area ÷ 70 m²) and its tightening in 2019 (÷ 85 m²).",
                        "Years with fewer than 100 sales are left out."]),
    ("Why this chart", "A line is the natural form for change over time. The band adds the spread, which shows the whole range of sizes moved "
                       "down and not only the middle. The key choice is lease-start year instead of sale year: a resale home sold in 2025 was "
                       "designed when its land was sold, so lease-start year dates the design decision."),
    ("Watch out for", "The dip at 2002 is one year with few projects. Recent lease-start years have few sales so far (2025 has 781 sales from "
                      "3 projects), so the last point is noisy. The chart only includes homes that changed hands in 2020 to 2025."),
    ("If someone asks", ["Why is lease-start year the year the land was sold? A condo on government land gets a 99-year lease that starts "
                         "around when the land is awarded. The developer designs and launches within the next few years.",
                         "Did the cap stop the shrink? The timing fits, and URA brought in the cap to curb shoeboxes, but this chart on "
                         "its own cannot prove cause and effect."]),
])
lead("Lead into chart 3: \"Which sizes disappeared?\"")

chart(3, "100% stacked bar", "03_stacked_mix.png", "Shoeboxes rose from 1% to 13%, big homes fell from 34% to 8%", [
    ("What it shows", "The mix of sizes in each lease-start era, as shares of units."),
])
table(["Lease start", "≤506 (shoebox)", "507–750", "751–1,000", "1,001–1,300", ">1,300"], [
    ["1990–2008", "1%", "5%", "19%", "41%", "34%"],
    ["2009–2012", "9%", "23%", "28%", "24%", "16%"],
    ["2013–2018", "13%", "36%", "25%", "18%", "8%"],
    ["2019–2025", "9%", "38%", "23%", "19%", "11%"],
], [2.8, 2.8, 2.6, 2.6, 2.8, 2.6])
for head, body in [
    ("How to read it", ["Each bar is one era and adds up to 100%.",
                        "Segments run from small (orange shoebox) to large (darkest blue). The numbers inside are percentages.",
                        "n under each era is the number of sales behind the bar."]),
    ("Why this chart", "A 100% stacked bar compares the mix across groups of different sizes. Raw counts would mostly show how many homes "
                       "from each era happened to sell. Shoeboxes are orange because they are the size URA's cap was aimed at, and the blues "
                       "get darker as units get bigger, so order reads as order."),
    ("Watch out for", "The bands are in sq ft and do not map exactly onto bedrooms, because the data has no bedroom count. As a rough guide, "
                      "507 to 750 sq ft is one or two bedrooms and above 1,000 sq ft is three or more."),
    ("If someone asks", ["Did the cap work? Shoeboxes fell from 13% to 9% after 2019, but big homes stayed rare at 11%. The growth went to "
                         "507 to 750 sq ft, which rose from 5% to 38% of units."]),
]:
    doc.add_heading(head, level=3)
    bullets(body) if isinstance(body, list) else para(body)
lead("Lead into chart 4: \"Maybe newer homes are only smaller because they are built in different places. Chart 4 checks that.\"")

chart(4, "coefficient plot", "04_coefficients.png", "Within the same district the gap stays at −34%", [
    ("What it shows", "How much smaller homes from each era are than 1990 to 2008 homes, before and after holding location fixed. "
                      "2009–12: −26% raw, −25% controlled. 2013–18: −35% raw, −34% controlled. 2019–25: −33% raw, −32% controlled. "
                      "Every interval is far from zero."),
    ("How to read it", ["Each row is an era compared with 1990 to 2008, which sits on the zero line.",
                        "Grey hollow dot: the raw gap. Blue dot: the gap among homes in the same district, of the same type (apartment or "
                        "condominium) and sold in the same year. The lines are 95% confidence intervals.",
                        "If location explained the shrink, the blue dots would move towards zero. They barely move."]),
    ("Why this chart", "A coefficient plot shows a regression result, with its uncertainty, without a table of numbers. Putting the raw and "
                       "controlled estimates next to each other is the test itself: you see at once that the controls change almost nothing."),
    ("How it was done", ["Ordinary least squares of log floor area on era dummies. The controlled model adds dummies for district, property "
                         "type and year of sale.",
                         "Because the model is in logs, each coefficient converts to a percentage gap: exp(b) − 1.",
                         "Standard errors are clustered by project (464 projects). Units in one project are designed together, so treating "
                         "66,237 sales as independent would make the intervals far too narrow."]),
    ("Watch out for", "District is a broad control, and a regression cannot rule out every other difference between eras. R² is low (0.22) "
                      "because sizes vary a lot inside every era. That is fine here: the question is how big the era gap is, not predicting "
                      "the size of each unit."),
    ("If someone asks", ["Why log floor area? So the result is a percentage, which compares cleanly across eras.",
                         "Why not include new vs resale as a control? Almost every new sale is from the newest era, so the two would "
                         "measure the same thing and muddle the estimate."]),
])
lead("Lead into chart 5: \"So the shrink is real. What did it do to the price tag?\"")

chart(5, "scatter with constant-price curves", "05_scatter_isoprice.png", "Shrinking cut prices to S$1.45M; after 2019 they jump to S$2.05M", [
    ("What it shows", "2025 sales of 99-year leaseholds. From 1990–2008 land to 2013–2018 land, floor area fell 40% (1,216 to 732 sq ft) while "
                      "PSF rose 27% (S$1,510 to S$1,922), so the median price fell 16%, from S$1.72M to S$1.45M. Homes on post-2019 land are "
                      "7% larger (786 sq ft) and 31% dearer per sq ft (S$2,514), and their median price jumps to S$2.05M."),
    ("How to read it", ["Each small dot is one project (median floor area and PSF, projects with at least 10 sales). Colour is the era, "
                        "darker for newer.",
                        "The large dots are the era medians, labelled with the era's median price, and the arrows join them in time order.",
                        "Both axes are logarithmic. Since price = floor area × PSF, every point on one grey curve has the same price. Moving "
                        "up and to the left along a curve means a smaller home at a higher PSF for the same price tag. That move is "
                        "shrinkflation in one picture."]),
    ("Why this chart", "A scatter shows two measures at once, and the constant-price curves turn it into a direct test of the definition: did "
                       "the size fall while the price tag held? Using only 2025 sales keeps every price at the same date."),
    ("Watch out for", "These are 2025 prices, not the original launch prices. Older homes are also cheaper per sq ft because they are older "
                      "and have less lease left. So the chart shows the menu a 2025 buyer chooses from."),
    ("If someone asks", ["Did developers hold the price tag at launch? Our data starts in 2020, so we cannot see 2010 launch prices. What we "
                         "can show is that the smaller homes from that era still cost less today despite their higher PSF, which is the "
                         "trade the shrink was built for."]),
])
lead("Lead into chart 6: \"Why does a smaller home mean a lower price tag? Because of how launches are priced.\"")

chart(6, "violin", "06_violin_pricing.png", "Every unit size sells at its project's PSF, within 1.5%", [
    ("What it shows", "10,389 new-launch sales in 2025 from the 50 projects with at least 20 sales. Each unit's PSF is compared with the median "
                      "PSF of its own project. The medians by size band are −0.5% (shoebox), +0.6%, +0.2%, −0.3% and −1.4% (over 1,300 sq ft). "
                      "Within a project, a 10% larger unit costs only 0.08% less per sq ft."),
    ("How to read it", ["Each violin is a size band. Its width at any height shows how many units sit at that PSF difference.",
                        "The white dot is the median, the black bar the middle 50%.",
                        "The zero line means the same PSF as the rest of the project."]),
    ("Why this chart", "A violin shows the full spread for several groups side by side, more than a box plot does. Comparing each unit with "
                       "its own project takes location out, which would otherwise swamp everything else in PSF."),
    ("Why it matters", "If developers charged a large premium per sq ft for small units, shrinking would barely cut the price tag. Because PSF "
                       "is flat, the price tag falls one for one with floor area: a unit 20% smaller costs about 20% less. That is why shrinking "
                       "was the tool."),
    ("Watch out for", "Floor level and facing also move PSF within a project, which explains the spread around zero. Across the whole market, "
                      "small-unit projects do have higher PSF, because they tend to be in pricier places. That is why the comparison is made "
                      "within each project."),
    ("If someone asks", ["Why do people say shoeboxes are expensive per sq ft? Across the market they are, because they cluster in central "
                         "locations. Inside the same building they are priced like everything else."]),
])
lead("Lead into chart 7: \"So why did developers shrink homes from 2009 onwards? Chart 7 brings in outside data.\"")

chart(7, "diverging lollipop", "07_lollipop_macro.png", "Least affordable in 2007–13, when that land was sold", [
    ("What it shows", "How affordable private homes were each year against the 2001–2025 average. 2007 to 2013 were 6 to 18% less affordable "
                      "than usual, except 2009 (financial crisis). From 2014 incomes grew faster than prices; 2017 was 16% more affordable. "
                      "2025 is 2% below average."),
    ("How to read it", ["Each lollipop is a year. Orange above the line: less affordable than usual. Blue below: more affordable.",
                        "The grey band marks 2007 to 2013, when the land behind chart 2's smallest homes was sold."]),
    ("Why this chart", "A lollipop shows one value per year against a baseline with less ink than 25 bars, and the colours show the sign at "
                       "a glance. It brings in the outside data the assignment asked for, to explain why developers shrank homes then."),
    ("How it was done", ["Price: URA's non-landed price index (condos and apartments), averaged over each year's four quarters.",
                         "Income: SingStat's yearly change in median household employment income (including employer CPF), chained into "
                         "an index with 2000 = 100.",
                         "Ratio = price index ÷ income index, as a percentage above or below its 2001–2025 average. Both indices about "
                         "doubled from 2009 to 2025, which is why 2025 sits near average."]),
    ("Watch out for", "This is a ratio of two indices. It says when homes were more or less affordable than usual, not how many years of "
                      "income a home costs. It is also an association, since interest rates and cooling measures changed in 2007 to 2013 too."),
    ("If someone asks", ["If 2025 is about average, why are homes hard to afford? The index covers the whole private market. New launches cost "
                         "far more per sq ft than the market as a whole (S$2,572 against S$1,747 for resale), which chart 8 picks up."]),
])
lead("Lead into chart 8: \"What does that mean for an actual household today?\"")

chart(8, "sensitivity heat map", "08_heatmap_tdsr.png", "The median household can borrow for under 800 sq ft", [
    ("What it shows", "The largest home, in sq ft, a household can afford under MAS loan rules, for six incomes and seven PSF levels. At the "
                      "2025 median household income of S$12,446, the limit is a S$1.91M home. That buys 1,117 sq ft at the 2020 new-launch PSF "
                      "(S$1,712) but only 743 sq ft at the 2025 PSF (S$2,572), less than the median new unit of 797 sq ft."),
    ("How to read it", ["Rows are monthly household income, columns are PSF.",
                        "Each cell is the affordable floor area. Darker blue means more space.",
                        "Orange boxes are cells below 797 sq ft, the median new unit in 2025.",
                        "The arrows on top mark the median new-launch PSF in 2020 and in 2025."]),
    ("Why this chart", "A sensitivity table shows how the answer moves with two inputs at once. The colours let the eye find the cut-off, and "
                       "the numbers give the exact figure. It links the shrink to an outside rule: banks cap the price tag, not the PSF, so "
                       "when PSF rises the only thing that can give is floor area."),
    ("Worked example", ["Median income S$12,446 a month. The most that can go to repayments is 55% of that, S$6,845.",
                        "At 4% over 30 years, S$6,845 a month repays a loan of about S$1.43M.",
                        "A bank lends at most 75% of the price, so the price limit is S$1.43M ÷ 0.75 = S$1.91M.",
                        "At S$2,572 per sq ft that is 743 sq ft."]),
    ("Watch out for", "The model ignores other debts, which lower the limit, and extra cash or CPF beyond the 25% down payment, which raise it. "
                      "The income figure includes employer CPF contributions, which banks do not count, so real limits are a little lower. "
                      "Lower interest rates do not change the table, because banks must test at 4% even when the actual rate is lower."),
    ("If someone asks", ["Why 30 years? It is the longest tenure that still allows a 75% loan. Above 30 years MAS drops the limit to 55%.",
                         "Why 4%? MAS requires banks to work out repayments at 4% or the actual rate, whichever is higher."]),
])
lead("Lead into chart 9: \"And once URA stopped homes from shrinking, the price tag had nowhere to go but up.\"")

chart(9, "waterfall", "09_waterfall.png", "Price tag S$1.46M → S$2.18M, driven by PSF (+39%)", [
    ("What it shows", "The typical new-launch price in late 2020 (Aug to Dec, the first months in the Lecture 6 file) against 2025, split into "
                      "the effect of PSF and of floor area. The price rose 49%. Higher PSF added 39% (about S$575,000) and floor area 7% (about "
                      "S$145,000). Units got slightly bigger, not smaller."),
    ("How to read it", ["The grey bars are the starting and ending price.",
                        "The orange step is what higher PSF added, the blue step what the change in floor area added. They stack from left "
                        "to right."]),
    ("Why this chart", "A waterfall shows how a total changes through its parts, which is the exact question: did the price tag rise because "
                       "of PSF or because of size? Before 2019 shrinking pulled the price tag down. Here the size step points up, so the whole "
                       "PSF rise reaches the buyer."),
    ("How it was done", ["Geometric means, so log price = log PSF + log floor area splits the change exactly, with nothing left over.",
                         "Each region (CCR, RCR, OCR) is compared with itself and weighted by its share of 2025 launches (18%, 41% and 41%), "
                         "so a year with more prime launches does not look like a price rise."]),
    ("Watch out for", "Late 2020 is only five months, and the projects launching differ from year to year. Since June 2023 URA counts "
                      "air-conditioner ledges in a unit's strata area, so developers dropped them and reported unit sizes fell about 6% [7]. "
                      "That makes the +7% a slight underestimate of the space buyers actually gained."),
    ("If someone asks", ["Why are units getting bigger again? The 2019 cap means a project can build fewer units on the same floor area, so "
                         "the average unit has to be larger."]),
])

# ================= wider points =================
doc.add_heading("11. Design choices across the poster", level=1)
bullets([
    "Nine charts of nine different types, each picked for the question it answers.",
    "One takeaway line per chart, with a number that can be read off the chart.",
    "Colours carry the same meaning everywhere: orange is new launches, shoeboxes and price pressure; blue is resale and the baseline. "
    "Ordered things (eras, size bands, the heat map) use one blue that gets darker. The palette was checked for colour-blind separation.",
    "No chart has two y-axes. Two measures on different scales in one chart can suggest a link that is not there.",
    "Labels sit next to the data where possible, so nobody has to hunt in a legend.",
    "All charts use the same font and sizes and were drawn at the exact size they have on the poster, so nothing is stretched.",
])

doc.add_heading("12. Limitations", level=1)
bullets([
    "Eras are compared at 2025 prices, not their launch prices, and older homes also lose value with age and a shorter lease.",
    "The vintage charts only include homes that sold in 2020 to 2025. An era whose homes rarely trade can be under-represented.",
    "There is no bedroom count, so size bands stand in for unit types.",
    "2024 is missing, and so are Aug to Oct 2021.",
    "Households also got smaller: from 4.0 people in 1995 to 3.1 in 2024 [7]. Part of the shrink is buyers wanting less space. But floor area "
    "per household member also fell, from 357 sq ft in 2005 to 252 sq ft in 2015 [7], so homes shrank faster than households did.",
    "Since June 2023 strata area is measured differently, which lowers reported sizes by about 6% for new launches [7].",
    "All results are associations, not proven causes.",
])

doc.add_heading("13. Key numbers to remember", level=1)
table(["Number", "What it is", "Chart"], [
    ["797 vs 1,012 sq ft", "Median new launch vs median resale home, 2025 (−21%)", "1"],
    ["18% vs 34%", "Share of homes of 1,200 sq ft or more, new vs resale", "1"],
    ["1,238 → 710 sq ft", "Median size, land sold 2005–08 vs 2013–15 (−43%)", "2"],
    ["1% → 13% → 9%", "Shoebox share: pre-2009 land, 2013–18 land, post-2019 land", "3"],
    ["34% → 8% → 11%", "Share of homes over 1,300 sq ft, same eras", "3"],
    ["−34%", "Size gap for 2013–18 land within the same district, type and sale year", "4"],
    ["S$1.72M → S$1.45M → S$2.05M", "Median 2025 price: pre-2009 land, 2013–18 land, post-2019 land", "5"],
    ["within 1.5%", "How close every size band's PSF is to its project's PSF", "6"],
    ["+6% to +18%", "How much less affordable than usual homes were in 2007–13 (except 2009)", "7"],
    ["S$12,446 → S$1.91M → 743 sq ft", "Median income, the price it can borrow for, the floor area at 2025 launch PSF", "8"],
    ["+49% (PSF +39%, area +7%)", "Typical new-launch price, late 2020 to 2025", "9"],
    ["S$2,572 vs S$1,747", "Median PSF, new launch vs resale, 2025 (resale gives 47% more space per dollar)", "1, answer"],
], [4.6, 10.0, 2.0])

doc.add_heading("14. Questions to expect", level=1)
qa([
    ("Isn't this just smaller families?", "Partly, but homes shrank faster. Floor area per household member fell by about a quarter from 2005 "
                                          "to 2015, so households got less space per person, not just smaller homes for smaller households."),
    ("Isn't this just inflation?", "Shrinkflation is about what you get for the price tag. Up to 2019 the price tag was held down by shrinking. "
                                   "From 2020 to 2025 the rise came from PSF, and size went slightly up."),
    ("Why lease-start year and not completion year?", "The land sale is when the developer decides the sizes, and completion comes three to "
                                                      "five years later. The data also has no completion year."),
    ("Is the shrink good or bad?", "It kept price tags lower but gave buyers less space. The 2019 cap chose space over a lower price tag, and "
                                   "the cost of that shows up in chart 9."),
    ("What does it mean for a buyer?", "Compare PSF and space, not the price tag. In 2025 a resale home gives 47% more floor area per dollar "
                                       "than a new launch (S$1,747 against S$2,572 per sq ft), in exchange for an older building and a shorter lease."),
    ("And for policy?", "With unit sizes capped, affordability now depends on land supply and income growth. Developers can no longer shrink "
                        "their way to a lower price tag, so they compete on layouts that waste less space."),
    ("Does the cap set a minimum flat size?", "No. It caps how many units a project may have, which sets a floor on the average. Single small "
                                              "units are still allowed."),
    ("Why are post-2019 medians below 85 m²?", "The cap counts gross floor area, which includes a share of common space, so the flat itself is "
                                               "smaller. Medians also sit below averages because a few big units pull the average up."),
    ("Did the cap cause the shrink to stop?", "The timing fits and the cap was designed to do it, but our charts show timing, not proof."),
    ("What would you do with more time?", "Get launch prices from 2005 to 2019 from URA REALIS to see the price tags at the time, add bedroom "
                                          "counts, and compare projects whose land was sold just before and just after the 2019 cap."),
])

doc.add_heading("15. Presenting it in about five minutes", level=1)
table(["Part", "Time", "What to cover"], [
    ["Question and key terms", "40 s", "The question, shrinkflation, price tag = floor area × PSF, lease-start year."],
    ["Row 1: what shrank", "80 s", "Charts 1 to 3. Today's gap, when it opened, which sizes went."],
    ["Row 2: real and how", "80 s", "Charts 4 to 6. Not location, the price-tag trade, priced per sq ft."],
    ["Row 3: why and what changed", "80 s", "Charts 7 to 9. Affordability, borrowing limits, the price tag after the cap."],
    ["Answer", "40 s", "The answer line, the three findings, what it means for buyers and policy."],
], [4.2, 1.6, 10.8])
para("Lines you can say, one per part:")
bullets([
    "**Open:** \"Shrinkflation is less product for the same price tag. We asked whether Singapore's private homes did that, and whether it is "
    "still happening.\"",
    "**Row 1:** \"Today's new launches are 21% smaller than resale homes. The drop came with land sold after 2008, 43% in five years, and "
    "the big homes are what disappeared.\"",
    "**Row 2:** \"It is the same inside every district, so it is not location. And because launches are priced per square foot, a smaller "
    "home really does mean a lower price tag.\"",
    "**Row 3:** \"It happened when prices were furthest ahead of incomes. Then URA capped it, so now the price tag rises instead: plus 49% "
    "since 2020, at the edge of what a median household can borrow.\"",
    "**Close:** \"So yes, homes shrank to stay affordable, until the rules stopped it. For a buyer, compare price per square foot, not the "
    "price tag.\"",
    "Say each chart's bold takeaway first, then point at the part of the chart it comes from. Do not read the guide out loud.",
])

doc.add_heading("16. Sources", level=1)
for s in [
    "[1] URA REALIS private residential transactions: properties2025.csv (course dataset) and properties23.csv (Lecture 6).",
    "[2] URA, Private Residential Property Price Index (1Q2009 = 100), quarterly. https://data.gov.sg/datasets/d_97f8a2e995022d311c6c68cfda6d034c/view",
    "[3] SingStat, change in median household employment income, 2000 to 2025. https://data.gov.sg/datasets/d_968496622a54acf5f67256434453b94c/view. "
    "Median household income S$12,446: Key Household Income Trends 2025, press release of 9 Feb 2026.",
    "[4] MAS, TDSR of 55% (from 16 Dec 2021) and 4% interest rate floor (from 30 Sep 2022); loan tenure and LTV limits. "
    "https://www.mas.gov.sg/regulation/explainers/new-housing-loans/loan-tenure-and-loan-to-value-limits",
    "[5] URA circular DC18-06, 17 Oct 2018. https://www.ura.gov.sg/guidelines/archived-circulars/dc18-06/",
    "[6] ONS (2019), The impact of shrinkflation on CPIH, UK. https://www.ons.gov.uk/economy/inflationandpriceindices/articles/theimpactofshrinkflationoncpihuk/howmanyofourproductsaregettingsmaller",
    "[7] Lee Sze Teck (Huttons), Are home sizes in Singapore shrinking?, EdgeProp, 7 Mar 2025. https://www.edgeprop.sg/property-news/are-home-sizes-singapore-shrinking",
    "[8] EdgeProp, URA curbs excessive development of shoebox units, 17 Oct 2018. https://edgeprop.sg/property-news/ura-curbs-excessive-development-shoebox-units",
]:
    para(s, size=9)

doc.save("shrinkflation_poster_guide.docx")
print("saved shrinkflation_poster_guide.docx")
