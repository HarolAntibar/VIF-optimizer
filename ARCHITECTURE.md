# High-Ticket VIF Optimizer — System Architecture

> **Version:** 1.0.0 | **Status:** Active Development | **Classification:** Internal Engineering Reference

---

## 1. Executive Summary

The **High-Ticket VIF Optimizer** is a professional-grade Python analytics engine designed to detect, quantify, and resolve multicollinearity within high-value marketing budget datasets. By systematically computing the **Variance Inflation Factor (VIF)** across all predictor variables, the system surfaces hidden statistical dependencies that silently degrade regression model reliability — a critical quality gate before any budget attribution or ROI forecasting model enters production.

The output is an executive-ready PDF report suitable for C-suite delivery, supported by a reproducible, auditable Python pipeline.

---

## 2. Standardized Technology Stack

| Layer               | Technology         | Version Constraint | Rationale                                                    |
|---------------------|--------------------|--------------------|--------------------------------------------------------------|
| Runtime             | Python             | ≥ 3.10             | Stable typing, performance, broad ecosystem support          |
| Data Manipulation   | Pandas             | ≥ 2.0              | Industry-standard DataFrame operations for structured data   |
| Numerical Compute   | NumPy              | ≥ 1.25             | Vectorized array operations; Pandas dependency               |
| Statistical Engine  | Statsmodels        | ≥ 0.14             | Authoritative OLS regression and VIF computation via `variance_inflation_factor` |
| Table Rendering     | Tabulate           | ≥ 0.9              | Elegant CLI-side tabular output for developer inspection     |
| PDF Generation      | fpdf2              | ≥ 2.7              | Lightweight, dependency-free PDF authoring for executive reports |
| Environment         | venv               | stdlib             | Hermetic, reproducible dependency isolation                  |

---

## 3. Repository Structure

```
upwork-vif-optimizer/
│
├── ARCHITECTURE.md              # This document — system design reference
├── .claudeignore                # Governance: paths excluded from AI context
├── .venv/                       # Isolated Python environment (not committed)
│
├── data/
│   └── marketing_budget_2025.csv  # Synthetic 200-row marketing spend dataset
│
├── main.py                      # Entry point: data ingestion + summary display
├── vif_calculator.py            # Core engine: VIF computation + alert classification
├── report_generator.py          # Executive layer: PDF report authoring
│
└── output/
    └── vif_report_2025.pdf      # Generated executive PDF report
```

---

## 4. Core Logic Architecture

The system is organized into three sequential, decoupled modules. Data flows unidirectionally through the pipeline: **Ingestion → Analysis → Reporting**.

```
┌─────────────────────────────────────────────────────────────────┐
│                     VIF OPTIMIZER PIPELINE                      │
│                                                                 │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────┐  │
│  │   DATA       │    │   VIF            │    │  EXECUTIVE   │  │
│  │   INGESTION  │───▶│   CALCULATION    │───▶│  REPORTING   │  │
│  │   (main.py)  │    │  (vif_calc...)   │    │  (report...) │  │
│  └──────────────┘    └──────────────────┘    └──────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.1 Module 1 — Data Ingestion (`main.py`)

**Responsibility:** Load, validate, and surface the raw dataset for human inspection before any statistical transformation occurs.

**Workflow:**
1. Read `marketing_budget_2025.csv` into a Pandas DataFrame.
2. Perform structural validation: assert expected columns exist, check for null values, confirm numeric dtypes.
3. Render a professional summary statistics table to stdout using `tabulate`.
4. Emit a dataset health report: shape, dtypes, null counts, and descriptive statistics.

**Design Principles:**
- Fail-fast on data integrity violations — no silent bad-data propagation.
- Human-readable output at every stage.

---

### 4.2 Module 2 — VIF Calculation (`vif_calculator.py`)

**Responsibility:** Compute the Variance Inflation Factor for each predictor variable and classify severity against defined thresholds.

**Algorithm:**
For each predictor variable $X_j$, VIF is computed as:

$$\text{VIF}_j = \frac{1}{1 - R^2_j}$$

where $R^2_j$ is the coefficient of determination from regressing $X_j$ on all remaining predictors using Statsmodels OLS.

**Severity Classification Matrix:**

| VIF Range      | Status      | Alert Level | Recommended Action                        |
|----------------|-------------|-------------|-------------------------------------------|
| 1.0 – 4.9      | ACCEPTABLE  | None        | No action required                        |
| 5.0 – 9.9      | ELEVATED    | WARNING     | Monitor; consider feature engineering     |
| 10.0 – 29.9    | HIGH        | ALERT       | Investigate correlation structure         |
| ≥ 30.0         | CRITICAL    | CRITICAL    | Mandatory remediation before model use    |

**Outputs:**
- A ranked DataFrame of variables sorted by VIF score (descending).
- Correlation heatmap data for the report layer.
- A plain-English remediation recommendation per flagged variable.

---

### 4.3 Module 3 — Executive Reporting (`report_generator.py`)

**Responsibility:** Synthesize the VIF analysis into a polished, client-deliverable PDF document using `fpdf2`.

**Report Structure:**
1. **Cover Page** — Project title, dataset name, analysis date, classification.
2. **Executive Summary** — One-page narrative: total variables analyzed, count by severity tier, top finding.
3. **Full VIF Table** — All variables with VIF scores, severity badges, and recommended actions.
4. **Correlation Analysis** — Textual analysis of the highest-correlated variable pairs driving elevated VIF.
5. **Remediation Roadmap** — Prioritized action list: drop, transform, or combine collinear features.
6. **Methodology Appendix** — Statistical definitions, VIF formula, threshold rationale.

---

## 5. Data Schema

The canonical input dataset (`marketing_budget_2025.csv`) conforms to the following schema:

| Column                | Type    | Unit | Description                                              |
|-----------------------|---------|------|----------------------------------------------------------|
| `TV_Spend`            | float64 | USD  | Monthly television advertising expenditure              |
| `Radio_Spend`         | float64 | USD  | Monthly radio advertising expenditure                   |
| `Social_Media_Spend`  | float64 | USD  | Monthly paid social media expenditure                   |
| `Influencer_Fees`     | float64 | USD  | Monthly influencer partnership fees                     |
| `Digital_Display_Spend` | float64 | USD | Monthly programmatic/display ad spend                  |
| `Email_Marketing_Spend` | float64 | USD | Monthly email campaign expenditure                     |
| `SEO_Budget`          | float64 | USD  | Monthly SEO tooling and agency fees                     |
| `Monthly_Revenue`     | float64 | USD  | Observed monthly revenue (dependent variable)           |

**Known Multicollinearity:** `Social_Media_Spend` and `Influencer_Fees` are intentionally correlated (r > 0.95) to simulate a realistic budget attribution problem where influencer campaigns are always activated alongside social media pushes.

---

## 6. Multicollinearity: Business Context

### Why This Matters for High-Ticket Clients

When a marketing mix model (MMM) or attribution model is trained with collinear predictors, the following failure modes emerge:

- **Coefficient instability:** Small perturbations in input data cause extreme swings in attributed ROI per channel.
- **Inflated standard errors:** Confidence intervals on spend elasticity become too wide to support budget decisions.
- **False attribution:** Budget that "belongs" to Social Media may be incorrectly credited to Influencer spend, or vice versa, leading to misallocation of seven-figure budgets.

The VIF Optimizer resolves this by providing a **pre-model audit** that quantifies and prioritizes multicollinearity risk before any modelling work begins.

---

## 7. Engineering Principles

1. **Reproducibility First:** All random data generation uses a fixed seed (`RANDOM_SEED = 42`). Results must be identical across all environments.
2. **Explicit Over Implicit:** No silent defaults. Every parameter, threshold, and configuration value is declared explicitly in code.
3. **Separation of Concerns:** Ingestion, computation, and reporting are fully decoupled. Each module can be tested and replaced independently.
4. **Executive-Grade Output:** All user-facing output — whether CLI tables or PDF pages — must meet professional presentation standards.
5. **Fail Fast:** Invalid data, missing columns, or type mismatches raise immediately with actionable error messages.

---

## 8. Execution Sequence

```bash
# Step 1: Activate the isolated environment
source .venv/Scripts/activate          # Windows / Git Bash
# source .venv/bin/activate            # macOS / Linux

# Step 2: Inspect the dataset
python main.py

# Step 3: Run VIF analysis (upcoming)
python vif_calculator.py

# Step 4: Generate executive PDF report (upcoming)
python report_generator.py
```

---

*Architecture document maintained by the project engineering lead. Update this document whenever a new module is introduced or the data schema changes.*
