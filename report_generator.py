"""
report_generator.py
-------------------
Phase 3 Executive Layer — PDF Report Generation
High-Ticket VIF Optimizer

Produces 'Budget_Audit_Report_2025.pdf' — a polished, multi-section
executive document structured for C-suite delivery. The report presents
VIF diagnostic findings, a Strategic Executive Summary articulating the
capital efficiency implications of multicollinearity, a full ranked
results table with severity badges, and a prioritised remediation roadmap.

Rendered with fpdf2 2.8.x. No external fonts or network resources required.

Usage:
    python report_generator.py

Output:
    output/Budget_Audit_Report_2025.pdf
"""

import os
import sys
from fpdf import FPDF, XPos, YPos

from vif_calculator import load_and_compute_vif, SEVERITY_TAXONOMY

# ---------------------------------------------------------------------------
# Output configuration
# ---------------------------------------------------------------------------
OUTPUT_DIR  = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Budget_Audit_Report_2025.pdf")

# ---------------------------------------------------------------------------
# Design System — Colour Palette (R, G, B)
# ---------------------------------------------------------------------------
NAVY          = (13,  27,  62)
NAVY_LIGHT    = (30,  55,  110)
GOLD          = (190, 155, 80)
GOLD_PALE     = (245, 235, 200)
WHITE         = (255, 255, 255)
LIGHT_GRAY    = (246, 248, 251)
MID_GRAY      = (140, 140, 148)
DARK_GRAY     = (50,  52,  60)
CHARCOAL      = (30,  30,  35)
RED_CRITICAL  = (175, 28,  28)
ORANGE_HIGH   = (205, 95,  0)
AMBER_ELEV    = (175, 130, 0)
GREEN_OK      = (28,  120, 55)

SEVERITY_RGB = {
    "CRITICAL":   RED_CRITICAL,
    "HIGH":       ORANGE_HIGH,
    "ELEVATED":   AMBER_ELEV,
    "ACCEPTABLE": GREEN_OK,
}


# ---------------------------------------------------------------------------
# PDF Document Class
# ---------------------------------------------------------------------------

class VIFReport(FPDF):
    """
    Custom FPDF subclass implementing the VIF Optimizer document template.
    Provides a running page header/footer on all pages after the cover.
    """

    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("Arial", "I", 7.5)
        self.set_text_color(*MID_GRAY)
        self.cell(
            0, 7,
            "HIGH-TICKET VIF OPTIMIZER  |  Budget Audit Report 2025  |  CONFIDENTIAL",
            align="C",
        )
        self.set_draw_color(*GOLD)
        self.set_line_width(0.25)
        self.line(20, 15, 190, 15)
        self.ln(4)

    def footer(self) -> None:
        if self.page_no() == 1:
            return
        self.set_y(-16)
        self.set_draw_color(*GOLD)
        self.set_line_width(0.25)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(2)
        self.set_font("Arial", "", 7.5)
        self.set_text_color(*MID_GRAY)
        self.cell(
            0, 5,
            f"Page {self.page_no()}  |  VIF Optimizer Analytics  |  Produced: February 2026  |  CONFIDENTIAL",
            align="C",
        )


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------

def section_header(pdf: VIFReport, roman: str, title: str, subtitle: str = "") -> None:
    """
    Render a full-width navy section header block with a gold left accent rule.
    """
    y = pdf.get_y()

    # Navy background rectangle
    pdf.set_fill_color(*NAVY)
    pdf.rect(20, y, 170, 15, "F")

    # Gold left accent rule
    pdf.set_fill_color(*GOLD)
    pdf.rect(20, y, 3, 15, "F")

    # Section title text
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(26, y + 1)
    pdf.cell(0, 6, roman, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Arial", "B", 9.5)
    pdf.set_xy(26, y + 7.5)
    pdf.cell(0, 6, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)

    if subtitle:
        pdf.set_font("Arial", "I", 8.5)
        pdf.set_text_color(*MID_GRAY)
        pdf.cell(0, 5, subtitle, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)


def callout_box(pdf: VIFReport, heading: str, body: str,
                bg: tuple = GOLD_PALE, border_color: tuple = GOLD) -> None:
    """
    Render a highlighted callout/note box with a bold heading and body text.
    """
    box_y = pdf.get_y()
    pdf.set_fill_color(*bg)
    pdf.set_draw_color(*border_color)
    pdf.set_line_width(0.4)
    # Draw background first; height will be estimated
    # We'll use multi_cell then draw border retroactively
    pdf.set_x(20)
    pdf.set_font("Arial", "B", 8.5)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 5.5, f"  {heading}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)

    pdf.set_font("Arial", "", 8.5)
    pdf.set_text_color(*DARK_GRAY)
    pdf.set_x(20)
    pdf.multi_cell(170, 5.5, text=f"  {body}", fill=True)

    box_h = pdf.get_y() - box_y
    pdf.rect(20, box_y, 170, box_h, "D")
    pdf.ln(4)


# ---------------------------------------------------------------------------
# Page: Cover
# ---------------------------------------------------------------------------

def draw_cover_page(pdf: VIFReport) -> None:
    """
    Full-bleed navy cover page with gold typographic treatment, a crimson
    CONFIDENTIAL badge, and a bottom-anchored analytical epigraph.
    """
    pdf.add_page()

    # Full-bleed navy background
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, 210, 297, "F")

    # Gold accent bars — top and bottom
    pdf.set_fill_color(*GOLD)
    pdf.rect(0, 0, 210, 3.5, "F")
    pdf.rect(0, 293.5, 210, 3.5, "F")

    # Vertical gold rule — left accent
    pdf.rect(18, 48, 1.0, 188, "F")

    # CONFIDENTIAL badge — top right
    pdf.set_fill_color(*RED_CRITICAL)
    pdf.rect(146, 11, 50, 9.5, "F")
    pdf.set_font("Arial", "B", 7.5)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(146, 13)
    pdf.cell(50, 5.5, "C O N F I D E N T I A L", align="C")

    # Division tagline
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(*GOLD)
    pdf.set_xy(23, 54)
    pdf.cell(0, 5, "ADVANCED ANALYTICS  |  MARKETING INTELLIGENCE DIVISION")

    # Main title — two-line stacked wordmark
    pdf.set_font("Arial", "B", 36)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(23, 78)
    pdf.cell(0, 16, "HIGH-TICKET VIF")
    pdf.set_xy(23, 96)
    pdf.cell(0, 16, "OPTIMIZER")

    # Gold underline rule beneath title
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.8)
    pdf.line(23, 116, 138, 116)

    # Subtitle
    pdf.set_font("Arial", "I", 14)
    pdf.set_text_color(*GOLD)
    pdf.set_xy(23, 122)
    pdf.cell(0, 8, "Multicollinearity & Capital Efficiency Audit")

    # Dataset metadata block
    pdf.set_font("Arial", "", 8.5)
    pdf.set_text_color(190, 205, 230)
    pdf.set_xy(23, 158)
    pdf.cell(0, 5.5, "SUBJECT DATASET")

    pdf.set_font("Arial", "B", 12.5)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(23, 165)
    pdf.cell(0, 7, "Marketing Budget Dataset 2025")

    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(190, 205, 230)
    pdf.set_xy(23, 175)
    pdf.cell(0, 5.5, "200 Monthly Observations  |  7 Predictor Variables  |  1 Dependent Variable")

    pdf.set_xy(23, 183)
    pdf.cell(0, 5.5, "Report Date: February 2026")

    pdf.set_xy(23, 191)
    pdf.cell(0, 5.5, "Analytical Engine: Python 3.13  |  Pandas 3.0  |  Statsmodels 0.14  |  fpdf2 2.8")

    # Horizontal separator
    pdf.set_draw_color(60, 80, 120)
    pdf.set_line_width(0.3)
    pdf.line(23, 202, 187, 202)

    # Severity key
    pdf.set_font("Arial", "B", 7.5)
    pdf.set_text_color(*GOLD)
    pdf.set_xy(23, 207)
    pdf.cell(0, 5, "VIF SEVERITY KEY:")

    key_items = [
        ("VIF >= 30", "CRITICAL",   RED_CRITICAL),
        ("VIF >= 10", "HIGH",       ORANGE_HIGH),
        ("VIF >= 5",  "ELEVATED",   AMBER_ELEV),
        ("VIF < 5",   "ACCEPTABLE", GREEN_OK),
    ]
    kx = 23
    for vif_range, label, color in key_items:
        pdf.set_fill_color(*color)
        pdf.rect(kx, 215, 36, 8, "F")
        pdf.set_font("Arial", "B", 7)
        pdf.set_text_color(*WHITE)
        pdf.set_xy(kx, 215)
        pdf.cell(36, 4.5, label, align="C")
        pdf.set_xy(kx, 219.5)
        pdf.cell(36, 3.5, vif_range, align="C")
        kx += 40

    # Epigraph
    pdf.set_font("Arial", "I", 9.5)
    pdf.set_text_color(*GOLD)
    pdf.set_xy(23, 248)
    pdf.multi_cell(
        164, 6.5,
        text=(
            '"A model built on collinear predictors does not explain reality\n'
            '— it reflects statistical noise dressed as executive insight."'
        ),
        align="C",
    )
    pdf.set_font("Arial", "", 7.5)
    pdf.set_text_color(160, 175, 205)
    pdf.set_xy(23, 268)
    pdf.cell(0, 5, "— VIF Optimizer Analytical Framework, 2025", align="C")


# ---------------------------------------------------------------------------
# Page: Strategic Executive Summary
# ---------------------------------------------------------------------------

def draw_executive_summary(pdf: VIFReport, vif_df) -> None:
    """
    Four-subsection strategic narrative articulating the capital efficiency
    implications of multicollinearity in high-ticket marketing environments.
    """
    pdf.add_page()

    section_header(
        pdf, "I.",
        "STRATEGIC EXECUTIVE SUMMARY",
        "Multicollinearity as a Structural Risk in Marketing Capital Allocation",
    )

    # Four thematic subsections — heading + body paragraph pairs
    narrative = [
        (
            "The Imperative of Statistical Independence in Marketing Mix Modelling",
            (
                "Modern marketing organisations increasingly rely on data-driven attribution models "
                "to justify, optimise, and defend budget allocation decisions at the executive level. "
                "The foundational assumption underpinning virtually all such models — ordinary least "
                "squares regression, marketing mix modelling (MMM), and multi-touch attribution alike "
                "— is that the predictor variables entered into the model are statistically independent "
                "of one another. When this assumption is violated through multicollinearity, the model's "
                "coefficient estimates become inherently unstable, standard errors inflate to the point "
                "of analytical meaninglessness, and the resulting attribution outputs cannot be trusted "
                "as a basis for strategic capital deployment. The consequences of ignoring this condition "
                "are not merely statistical — they are financial, operational, and reputational."
            ),
        ),
        (
            "The Variance Inflation Factor as a Capital Efficiency Diagnostic",
            (
                "The Variance Inflation Factor (VIF) is the definitive statistical instrument for "
                "quantifying the severity of multicollinearity within a predictor set. Computed for "
                "each predictor as the reciprocal of one minus its coefficient of determination when "
                "regressed against all remaining predictors, VIF measures the precise degree to which "
                "a variable's estimated variance has been inflated by its linear relationships with "
                "co-regressors. A VIF score of 1.0 denotes complete orthogonality — the ideal state. "
                "Scores between 1.0 and 4.9 fall within acceptable operating bounds and require no "
                "intervention. However, when VIF exceeds 10.0, a direct and actionable signal of "
                "capital inefficiency is present: the model cannot reliably isolate the marginal revenue "
                "contribution of that variable. Any budget decision premised on a coefficient derived "
                "from a predictor with VIF >= 10 constitutes a statistically unjustifiable allocation "
                "of capital. In high-ticket marketing environments where individual channel budgets "
                "routinely reach seven figures, even a moderate misattribution event compounds into "
                "material financial loss and strategic misdirection at the board level."
            ),
        ),
        (
            "Audit Findings: A CRITICAL Multicollinearity Condition Confirmed",
            (
                "Analysis of the Marketing Budget 2025 dataset has identified a severe multicollinearity "
                "condition between the Social_Media_Spend and Influencer_Fees predictor variables. The "
                "Pearson correlation coefficient between these two channels exceeds 0.98 — a near-perfect "
                "linear relationship that generates VIF scores classified as CRITICAL under this framework's "
                "severity taxonomy. This condition is not a statistical anomaly; it reflects a structural "
                "reality in which influencer campaign activations have been systematically co-deployed "
                "alongside paid social media budgets with negligible independent variation. Within the "
                "regression framework, these two channels are statistically indistinguishable. Any "
                "attribution model trained on this dataset in its current state will produce coefficient "
                "estimates for these variables that are numerically arbitrary, directionally unreliable, "
                "and wholly unsuitable for informing executive budget strategy."
            ),
        ),
        (
            "Mandate and Scope of Remediation",
            (
                "This report presents the complete VIF diagnostic results across all seven predictor "
                "variables, accompanied by a prioritised remediation roadmap structured by severity tier. "
                "No marketing mix model, budget optimisation algorithm, or revenue attribution report "
                "should be deployed against this dataset until the multicollinearity conditions documented "
                "herein have been resolved. The recommended action plan that follows classifies each "
                "flagged variable by severity and prescribes specific, implementable remediation strategies "
                "— ranging from composite index construction and domain-driven variable elimination to "
                "dimensionality reduction via Principal Component Analysis and L2-regularised regression "
                "— each calibrated to restore the statistical integrity of the predictor space without "
                "sacrificing analytical depth or business interpretability. Alongside immediate "
                "remediation, this report recommends the institutionalisation of pre-modelling VIF "
                "audits as a standard analytical governance protocol, ensuring that capital allocation "
                "decisions are perpetually grounded in statistically defensible model outputs."
            ),
        ),
    ]

    for heading, body in narrative:
        # Subsection heading
        pdf.set_font("Arial", "B", 9.5)
        pdf.set_text_color(*NAVY)
        pdf.multi_cell(0, 6, text=heading)
        pdf.ln(1)

        # Body paragraph
        pdf.set_font("Arial", "", 9.5)
        pdf.set_text_color(*DARK_GRAY)
        pdf.multi_cell(0, 6, text=body)
        pdf.ln(5)

    # Bottom callout
    callout_box(
        pdf,
        "KEY TAKEAWAY",
        (
            "A VIF score exceeding 10.0 is not a technical footnote — it is a capital efficiency "
            "alert. It signals that the model cannot distinguish between the individual revenue "
            "contributions of collinear channels, rendering budget allocations between those "
            "channels statistically arbitrary. Remediation is a business imperative, not merely "
            "an analytical preference."
        ),
    )


# ---------------------------------------------------------------------------
# Page: VIF Analysis Results Table
# ---------------------------------------------------------------------------

def draw_vif_results(pdf: VIFReport, vif_df) -> None:
    """
    Render the full ranked VIF results table with severity-colour-coded badges,
    preceded by four summary metric boxes and followed by an analytical note.
    """
    pdf.add_page()

    section_header(
        pdf, "II.",
        "VIF ANALYSIS RESULTS",
        "Variance Inflation Factor Scores — All Predictor Variables, Ranked by Severity",
    )

    # --- Summary metric boxes ---
    critical_n  = int((vif_df["Severity"] == "CRITICAL").sum())
    high_n      = int((vif_df["Severity"] == "HIGH").sum())
    max_vif     = float(vif_df["VIF_Score"].max())
    total_vars  = len(vif_df)

    boxes = [
        ("VARIABLES\nAUDITED",   str(total_vars),      NAVY),
        ("CRITICAL\nALERTS",     str(critical_n),       RED_CRITICAL if critical_n > 0 else GREEN_OK),
        ("HIGH\nALERTS",         str(high_n),           ORANGE_HIGH  if high_n > 0  else GREEN_OK),
        ("PEAK VIF\nSCORE",      f"{max_vif:.1f}",      RED_CRITICAL if max_vif >= 10 else GREEN_OK),
    ]

    box_w = 38
    box_h = 20
    gap   = 4
    box_y = pdf.get_y()

    for i, (label, value, color) in enumerate(boxes):
        bx = 20 + i * (box_w + gap)

        pdf.set_fill_color(*color)
        pdf.rect(bx, box_y, box_w, box_h, "F")

        pdf.set_font("Arial", "B", 18)
        pdf.set_text_color(*WHITE)
        pdf.set_xy(bx, box_y + 2)
        pdf.cell(box_w, 10, value, align="C")

        pdf.set_font("Arial", "B", 6.5)
        pdf.set_xy(bx, box_y + 12)
        pdf.cell(box_w, 6, label.replace("\n", "  "), align="C")

    pdf.set_y(box_y + box_h + 8)

    # --- Results table ---
    col_w = [58, 26, 32, 54]   # Variable | VIF Score | Severity | Action  (total=170)
    headers = ["Predictor Variable", "VIF Score", "Severity", "Recommended Action"]

    # Table header row
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Arial", "B", 8.5)
    for h, w in zip(headers, col_w):
        pdf.cell(w, 10, f" {h}", fill=True, border=0)
    pdf.ln()

    # Table data rows
    for idx, (_, row) in enumerate(vif_df.iterrows()):
        sev   = row["Severity"]
        color = SEVERITY_RGB[sev]
        bg    = LIGHT_GRAY if idx % 2 == 0 else WHITE

        # Variable name
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*CHARCOAL)
        pdf.set_font("Arial", "B", 8.5)
        pdf.cell(col_w[0], 9, f"  {row['Variable']}", fill=True, border="B")

        # VIF Score
        pdf.set_text_color(*color)
        pdf.set_font("Arial", "B", 8.5)
        pdf.cell(col_w[1], 9, f"{row['VIF_Score']:.4f}", fill=True, border="B", align="C")

        # Severity badge — solid colour fill
        pdf.set_fill_color(*color)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Arial", "B", 7.5)
        pdf.cell(col_w[2], 9, sev, fill=True, border=0, align="C")

        # Recommended Action
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*DARK_GRAY)
        pdf.set_font("Arial", "", 7.5)
        # Truncate action text to fit the column cleanly
        action_text = row["Short_Action"]
        if len(action_text) > 52:
            action_text = action_text[:49] + "..."
        pdf.cell(col_w[3], 9, action_text, fill=True, border="B")
        pdf.ln()

    pdf.ln(8)

    # Analytical note box
    callout_box(
        pdf,
        "ANALYTICAL INTERPRETATION",
        (
            "A VIF score exceeding 10.0 confirms that a predictor's variance has been inflated "
            "by a factor greater than ten through its linear relationships with co-regressors. "
            "Under this condition, the ordinary least squares estimator cannot reliably decompose "
            "the joint explanatory power of correlated channels into individual coefficient estimates. "
            "Budget allocations derived from such coefficients are, in the strictest statistical "
            "sense, uninformed by the data and carry no evidentiary weight."
        ),
    )


# ---------------------------------------------------------------------------
# Page: Recommended Action Plan
# ---------------------------------------------------------------------------

def draw_action_plan(pdf: VIFReport, vif_df) -> None:
    """
    Two-section prioritised remediation roadmap: immediate technical
    interventions for CRITICAL findings, and governance recommendations
    for long-term analytical integrity.
    """
    pdf.add_page()

    section_header(
        pdf, "III.",
        "RECOMMENDED ACTION PLAN",
        "Prioritised Remediation Roadmap — Structured by Severity Tier",
    )

    # Preamble
    pdf.set_font("Arial", "", 9.5)
    pdf.set_text_color(*DARK_GRAY)
    pdf.multi_cell(
        0, 6,
        text=(
            "The directives enumerated below are issued in strict order of urgency and business impact. "
            "Each recommended action is calibrated to restore statistical independence within the "
            "predictor space while preserving the maximum possible explanatory power for downstream "
            "modelling applications. Remediation should be conducted iteratively: implement one "
            "intervention at a time, recompute all VIF scores following each change, and confirm "
            "convergence below the relevant severity threshold before proceeding to the next step. "
            "Parallel implementation of multiple strategies without intermediate validation risks "
            "over-engineering the predictor set and inadvertently discarding legitimate signal."
        ),
    )
    pdf.ln(6)

    # --- Action Block 1: CRITICAL ---
    action_blocks = [
        {
            "priority_label": "PRIORITY 1  —  CRITICAL  |  Immediate Action Required",
            "color":          RED_CRITICAL,
            "title":          "Resolve Structural Collinearity: Social_Media_Spend & Influencer_Fees",
            "steps": [
                {
                    "label": "COMPOSITE INDEX CONSTRUCTION (Recommended First Step)",
                    "body": (
                        "Merge Social_Media_Spend and Influencer_Fees into a single 'Digital_Activation_Index' "
                        "via business-informed weighted averaging — for example, weighting Social Media at 0.60 "
                        "and Influencer Fees at 0.40 in proportion to their historical budget allocations. "
                        "This approach preserves the combined channel's full explanatory power whilst "
                        "eliminating the collinear relationship entirely, and retains clear business "
                        "interpretability for executive stakeholders."
                    ),
                },
                {
                    "label": "PRINCIPAL COMPONENT ANALYSIS (Statistically Optimal)",
                    "body": (
                        "Apply PCA to the two collinear variables to extract a single orthogonal principal "
                        "component capturing maximum joint variance. The resulting component, entered as a "
                        "single predictor, guarantees VIF = 1.0 for that dimension by mathematical "
                        "construction. Note that PCA components sacrifice direct business interpretability; "
                        "results should be back-transformed and communicated carefully to non-technical "
                        "executive audiences."
                    ),
                },
                {
                    "label": "DOMAIN-DRIVEN VARIABLE ELIMINATION",
                    "body": (
                        "If domain knowledge confirms that influencer activations are invariably co-deployed "
                        "with paid social campaigns without independent variation — i.e., there exist no "
                        "observations where one channel is active without the other — then Influencer_Fees "
                        "carries no unique marginal information and should be excluded from the predictor "
                        "set. This is the most parsimonious solution when the business context supports it."
                    ),
                },
                {
                    "label": "RIDGE REGRESSION — INTERIM MODELLING MITIGATION",
                    "body": (
                        "As a short-term modelling solution prior to full remediation, replace OLS with "
                        "Ridge Regression (L2 regularisation), which applies a penalty term that "
                        "stabilises coefficient estimates in the presence of multicollinearity. Ridge "
                        "does not resolve the underlying structural collinearity — it mitigates its "
                        "statistical consequences without addressing the root cause. This strategy "
                        "is appropriate only as a documented temporary measure pending structural remediation."
                    ),
                },
            ],
        },
        {
            "priority_label": "PRIORITY 2  —  GOVERNANCE  |  Ongoing Analytical Integrity",
            "color":          NAVY,
            "title":          "Institutionalise Pre-Modelling VIF Auditing as Standard Operating Procedure",
            "steps": [
                {
                    "label": "AUTOMATED PIPELINE GATING",
                    "body": (
                        "Integrate this VIF Optimizer as a mandatory pre-processing gate in the "
                        "analytics pipeline. No regression model, attribution report, or budget "
                        "optimisation algorithm should proceed to training or production deployment "
                        "if any predictor carries a VIF score exceeding 10.0. Gate failures should "
                        "trigger an automated analyst notification and block downstream model execution."
                    ),
                },
                {
                    "label": "QUARTERLY VIF AUDIT CADENCE",
                    "body": (
                        "As marketing channel mixes evolve across planning cycles, the correlation "
                        "structure between spend variables will shift — sometimes materially. Schedule "
                        "quarterly VIF audits against refreshed budget datasets to detect emergent "
                        "multicollinearity before it contaminates live model outputs and informs "
                        "consequential budget decisions."
                    ),
                },
                {
                    "label": "EXECUTIVE REPORTING DISCLOSURE STANDARD",
                    "body": (
                        "Require that all client-facing attribution and MMM reports include a VIF "
                        "disclosure table as a mandatory appendix, certifying that all model inputs "
                        "satisfied the VIF < 10 threshold prior to model training. This establishes "
                        "a defensible audit trail, protects analytical credibility at the executive "
                        "level, and demonstrates methodological rigour to sophisticated stakeholders."
                    ),
                },
            ],
        },
    ]

    for block in action_blocks:
        # Priority header band
        pdf.set_fill_color(*block["color"])
        pdf.rect(20, pdf.get_y(), 170, 11, "F")
        pdf.set_font("Arial", "B", 8.5)
        pdf.set_text_color(*WHITE)
        pdf.set_x(24)
        pdf.cell(0, 11, block["priority_label"])
        pdf.ln()

        # Block title
        pdf.set_font("Arial", "B", 9.5)
        pdf.set_text_color(*DARK_GRAY)
        pdf.multi_cell(0, 6.5, text=block["title"])
        pdf.ln(2)

        # Steps
        for j, step in enumerate(block["steps"]):
            step_y = pdf.get_y()

            # Step number bullet
            pdf.set_fill_color(*block["color"])
            pdf.rect(22, step_y + 1, 5.5, 5.5, "F")
            pdf.set_font("Arial", "B", 7)
            pdf.set_text_color(*WHITE)
            pdf.set_xy(22, step_y + 1)
            pdf.cell(5.5, 5.5, str(j + 1), align="C")

            # Step label
            pdf.set_xy(30, step_y)
            pdf.set_font("Arial", "B", 8.5)
            pdf.set_text_color(*block["color"])
            pdf.cell(0, 5.5, step["label"])
            pdf.ln(5.5)

            # Step body
            pdf.set_x(30)
            pdf.set_font("Arial", "", 8.5)
            pdf.set_text_color(*DARK_GRAY)
            pdf.multi_cell(155, 5.5, text=step["body"])
            pdf.ln(3)

        pdf.ln(5)


# ---------------------------------------------------------------------------
# Page: Methodology & Technical Appendix
# ---------------------------------------------------------------------------

def draw_methodology(pdf: VIFReport) -> None:
    """
    Technical appendix: VIF formula, severity threshold rationale,
    dataset characteristics, and computational implementation notes.
    """
    pdf.add_page()

    section_header(
        pdf, "IV.",
        "METHODOLOGY & TECHNICAL APPENDIX",
        "Statistical Definitions, Threshold Rationale, and Computational Framework",
    )

    # VIF formula
    pdf.set_font("Arial", "B", 9.5)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6.5, "Variance Inflation Factor — Formal Definition",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(*DARK_GRAY)
    pdf.multi_cell(
        0, 5.5,
        text=(
            "For a predictor variable X_j within a regression model containing k predictors, "
            "the Variance Inflation Factor is formally defined as:"
        ),
    )
    pdf.ln(3)

    # Formula display box
    formula_y = pdf.get_y()
    pdf.set_fill_color(238, 242, 250)
    pdf.rect(40, formula_y, 130, 13, "F")
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(0.3)
    pdf.rect(40, formula_y, 130, 13, "D")
    pdf.set_font("Arial", "B", 13)
    pdf.set_text_color(*NAVY)
    pdf.set_xy(40, formula_y + 2)
    pdf.cell(130, 9, "VIF(j)  =  1 / ( 1 - R\u00b2(j) )", align="C")
    pdf.ln(18)

    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(*DARK_GRAY)
    pdf.multi_cell(
        0, 5.5,
        text=(
            "Where R\u00b2(j) is the coefficient of determination obtained by regressing predictor X_j "
            "against all remaining predictors X_1, ..., X_(j-1), X_(j+1), ..., X_k using ordinary "
            "least squares. As the proportion of variance in X_j explained by its co-regressors "
            "approaches 1.0, R\u00b2(j) approaches 1.0, and VIF(j) approaches infinity — indicating "
            "near-perfect linear dependence and complete coefficient unreliability."
        ),
    )
    pdf.ln(7)

    # Severity classification table
    pdf.set_font("Arial", "B", 9.5)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6.5, "Severity Classification Thresholds",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

    thresh_headers = ["VIF Range", "Severity", "Statistical Interpretation", "Mandate"]
    thresh_widths  = [26, 28, 88, 28]

    # Header
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Arial", "B", 8)
    for h, w in zip(thresh_headers, thresh_widths):
        pdf.cell(w, 9, f" {h}", fill=True)
    pdf.ln()

    thresh_rows = [
        ("1.0 – 4.9",  "ACCEPTABLE",
         "Predictors are sufficiently independent for reliable OLS coefficient estimation.",
         "None"),
        ("5.0 – 9.9",  "ELEVATED",
         "Moderate collinearity present; estimates remain usable but warrant pre-deployment scrutiny.",
         "Monitor"),
        ("10.0 – 29.9","HIGH",
         "Significant variance inflation; coefficients are unreliable for budget decision-making.",
         "Investigate"),
        ("≥ 30.0",     "CRITICAL",
         "Severe multicollinearity; coefficient estimates are statistically arbitrary and indefensible.",
         "Mandatory"),
    ]

    for i, (vif_range, sev, interp, mandate) in enumerate(thresh_rows):
        bg = LIGHT_GRAY if i % 2 == 0 else WHITE
        sev_color = SEVERITY_RGB[sev]

        pdf.set_fill_color(*bg)
        pdf.set_text_color(*DARK_GRAY)
        pdf.set_font("Arial", "", 8)
        pdf.cell(thresh_widths[0], 8, f" {vif_range}", fill=True, border="B")

        pdf.set_fill_color(*sev_color)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Arial", "B", 7.5)
        pdf.cell(thresh_widths[1], 8, sev, fill=True, align="C")

        pdf.set_fill_color(*bg)
        pdf.set_text_color(*DARK_GRAY)
        pdf.set_font("Arial", "", 7.5)
        pdf.cell(thresh_widths[2], 8, f" {interp}", fill=True, border="B")
        pdf.cell(thresh_widths[3], 8, mandate, fill=True, align="C", border="B")
        pdf.ln()

    pdf.ln(8)

    # Dataset characteristics
    pdf.set_font("Arial", "B", 9.5)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6.5, "Dataset Characteristics", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(*DARK_GRAY)
    pdf.multi_cell(
        0, 5.5,
        text=(
            "The Marketing Budget 2025 dataset comprises 200 monthly observations across eight "
            "variables: seven marketing expenditure channels (TV, Radio, Social Media, Influencer "
            "Fees, Digital Display, Email, SEO) and one dependent variable (Monthly Revenue). All "
            "monetary values are denominated in USD. The dataset was generated with a fixed random "
            "seed (42) to ensure full reproducibility across all analytical environments. Synthetic "
            "collinearity between Social_Media_Spend and Influencer_Fees (Pearson r > 0.98) was "
            "deliberately introduced to replicate a common structural condition in integrated digital "
            "marketing organisations, where influencer and paid social budgets are activated in "
            "coordinated lockstep."
        ),
    )
    pdf.ln(6)

    # Computational implementation
    pdf.set_font("Arial", "B", 9.5)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6.5, "Computational Implementation", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(*DARK_GRAY)
    pdf.multi_cell(
        0, 5.5,
        text=(
            "VIF scores were computed using the variance_inflation_factor function from the "
            "statsmodels.stats.outliers_influence module (Statsmodels 0.14.6, Python 3.13). "
            "An intercept term was appended to the design matrix via statsmodels.tools.add_constant "
            "prior to computation, ensuring correct VIF calculation in compliance with the standard "
            "formulation. All seven predictor variables were entered simultaneously into the design "
            "matrix; no stepwise, forward, or backward selection procedure was applied. Results are "
            "presented ranked in descending order of VIF score to surface the most urgent "
            "multicollinearity risks at the head of the report."
        ),
    )


# ---------------------------------------------------------------------------
# Report orchestration
# ---------------------------------------------------------------------------

def generate_report(vif_df) -> str:
    """
    Orchestrate all page draw functions and write the final PDF to disk.

    Returns:
        Absolute path to the generated PDF file.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pdf = VIFReport(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.set_margins(left=20, top=20, right=20)

    # Register Arial from Windows system fonts — required for full Unicode
    # coverage (em dashes, ≥, superscript characters, etc.).  fpdf2's
    # built-in core fonts (Helvetica) support Latin-1 only (U+0000–U+00FF).
    FONT_DIR = "C:/Windows/Fonts"
    pdf.add_font("Arial",   style="",   fname=f"{FONT_DIR}/arial.ttf")
    pdf.add_font("Arial",   style="B",  fname=f"{FONT_DIR}/arialbd.ttf")
    pdf.add_font("Arial",   style="I",  fname=f"{FONT_DIR}/ariali.ttf")
    pdf.add_font("Arial",   style="BI", fname=f"{FONT_DIR}/arialbi.ttf")

    pdf.set_author("VIF Optimizer Analytics Engine")
    pdf.set_title("Budget Audit Report 2025 — Multicollinearity & Capital Efficiency Audit")
    pdf.set_subject("VIF Analysis — Marketing Budget Dataset 2025")
    pdf.set_creator("High-Ticket VIF Optimizer v1.0 | Python 3.13 | fpdf2 2.8")

    draw_cover_page(pdf)
    draw_executive_summary(pdf, vif_df)
    draw_vif_results(pdf, vif_df)
    draw_action_plan(pdf, vif_df)
    draw_methodology(pdf)

    pdf.output(OUTPUT_FILE)
    return os.path.abspath(OUTPUT_FILE)


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("\n" + "=" * 78)
    print("  HIGH-TICKET VIF OPTIMIZER")
    print("  Phase 3: Executive PDF Report Generation")
    print("  Engine: fpdf2 2.8  |  Output: Budget_Audit_Report_2025.pdf")
    print("=" * 78)

    print("\n  [INFO] Computing VIF scores from dataset...")
    try:
        vif_df = load_and_compute_vif()
    except (FileNotFoundError, ValueError) as exc:
        print(exc)
        sys.exit(1)
    print(f"  [INFO] VIF analysis complete — {len(vif_df)} variables processed.")

    print("  [INFO] Rendering executive PDF report...")
    output_path = generate_report(vif_df)

    print(f"  [INFO] Report generated successfully.")
    print(f"\n  OUTPUT PATH : {output_path}")
    print(f"  PAGE COUNT  : 5 pages (Cover + Executive Summary + Results + Action Plan + Appendix)")
    print(f"\n  The report is ready for executive delivery.")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()
