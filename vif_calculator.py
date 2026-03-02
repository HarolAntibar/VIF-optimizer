"""
vif_calculator.py
-----------------
Phase 2 Core Engine — Variance Inflation Factor Computation
High-Ticket VIF Optimizer

Responsibilities:
    1. Load the marketing budget dataset from the canonical data path.
    2. Construct the full-rank design matrix and append an intercept term.
    3. Compute the Variance Inflation Factor (VIF) for each predictor variable
       using Statsmodels' authoritative variance_inflation_factor function.
    4. Classify each score against the defined severity taxonomy.
    5. Render a professional, executive-grade VIF results table to stdout.
    6. Export the structured results DataFrame for consumption by the
       report generation pipeline (report_generator.py).

Usage:
    python vif_calculator.py

Exports (importable):
    load_and_compute_vif(data_path) -> pd.DataFrame
"""

import sys
import os
import numpy as np
import pandas as pd
from tabulate import tabulate
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools import add_constant

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_PATH = os.path.join("data", "marketing_budget_2025.csv")

PREDICTOR_COLUMNS = [
    "TV_Spend",
    "Radio_Spend",
    "Social_Media_Spend",
    "Influencer_Fees",
    "Digital_Display_Spend",
    "Email_Marketing_Spend",
    "SEO_Budget",
]

# Severity taxonomy — evaluated in descending threshold order.
# Each entry: (min_vif, severity_label, short_action, long_action)
SEVERITY_TAXONOMY = [
    (
        30.0,
        "CRITICAL",
        "Mandatory remediation — composite or eliminate immediately",
        "This variable exhibits severe multicollinearity. Its regression coefficient is statistically arbitrary and cannot support any budget allocation decision. Immediate remediation is required: construct a composite index, apply PCA, or eliminate the variable prior to modelling.",
    ),
    (
        10.0,
        "HIGH",
        "Significant inflation — apply Ridge regression or PCA",
        "Significant collinearity is present. Coefficient estimates are unreliable for strategic interpretation. Apply L2 regularisation (Ridge Regression) as an interim measure and investigate the correlation structure to determine whether feature engineering or dimensionality reduction is appropriate.",
    ),
    (
        5.0,
        "ELEVATED",
        "Monitor closely; consider feature engineering",
        "Moderate collinearity detected. While OLS estimates remain usable, this variable warrants close scrutiny. Consider feature engineering or cross-validation to assess coefficient stability before incorporating into a production attribution model.",
    ),
    (
        1.0,
        "ACCEPTABLE",
        "No action required — within tolerable bounds",
        "This variable is sufficiently independent of other predictors. No remediation is required. Coefficient estimates are reliable and can be used with confidence in regression and attribution models.",
    ),
]

# Terminal display labels (ASCII-safe, no emoji dependency)
SEVERITY_DISPLAY = {
    "CRITICAL":   "[!!] CRITICAL",
    "HIGH":       "[! ] HIGH",
    "ELEVATED":   "[~ ] ELEVATED",
    "ACCEPTABLE": "[OK] ACCEPTABLE",
}

DIVIDER     = "=" * 92
THIN_DIVIDER = "-" * 92


# ---------------------------------------------------------------------------
# Core computational functions
# ---------------------------------------------------------------------------

def classify_vif(score: float) -> tuple:
    """
    Classify a VIF score against the severity taxonomy.

    Returns:
        (severity: str, short_action: str, long_action: str)
    """
    for threshold, severity, short_action, long_action in SEVERITY_TAXONOMY:
        if score >= threshold:
            return severity, short_action, long_action
    return "ACCEPTABLE", "No action required — within tolerable bounds", SEVERITY_TAXONOMY[-1][3]


def load_and_compute_vif(data_path: str = DATA_PATH) -> pd.DataFrame:
    """
    Load the dataset, construct the design matrix, and compute VIF for
    all predictor variables defined in PREDICTOR_COLUMNS.

    The intercept term is appended via statsmodels.tools.add_constant
    prior to computation. Infinite VIF values (arising from perfect
    linear dependence) are capped at 9_999.99 for display purposes.

    Returns:
        pd.DataFrame with columns:
            Variable, VIF_Score, Severity, Short_Action, Long_Action
        Sorted descending by VIF_Score.
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"[FATAL] Dataset not found: '{data_path}'\n"
            f"        Run 'python generate_data.py' first."
        )

    df = pd.read_csv(data_path)
    missing = set(PREDICTOR_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"[FATAL] Missing columns in dataset: {sorted(missing)}")

    X = df[PREDICTOR_COLUMNS].copy().astype(float)
    X_const = add_constant(X, has_constant="add")  # intercept at column index 0

    records = []
    for i, col in enumerate(PREDICTOR_COLUMNS):
        raw_score = variance_inflation_factor(X_const.values, i + 1)  # +1 skips intercept

        # Cap infinite scores (perfect collinearity edge case)
        score = min(raw_score, 9_999.99) if not np.isnan(raw_score) else 9_999.99

        severity, short_action, long_action = classify_vif(score)
        records.append({
            "Variable":     col,
            "VIF_Score":    round(score, 4),
            "Severity":     severity,
            "Short_Action": short_action,
            "Long_Action":  long_action,
        })

    result = (
        pd.DataFrame(records)
        .sort_values("VIF_Score", ascending=False)
        .reset_index(drop=True)
    )
    return result


# ---------------------------------------------------------------------------
# Terminal display
# ---------------------------------------------------------------------------

def display_vif_table(vif_df: pd.DataFrame) -> None:
    """
    Render an executive-grade VIF results table to stdout.
    Includes a severity summary panel and a full ranked results table.
    """
    critical_count  = (vif_df["Severity"] == "CRITICAL").sum()
    high_count      = (vif_df["Severity"] == "HIGH").sum()
    elevated_count  = (vif_df["Severity"] == "ELEVATED").sum()
    acceptable_count = (vif_df["Severity"] == "ACCEPTABLE").sum()
    max_vif         = vif_df["VIF_Score"].max()
    alert_status    = "CRITICAL ALERT" if critical_count > 0 else ("ALERT" if high_count > 0 else "PASS")

    print(f"\n{DIVIDER}")
    print("  VIF ANALYSIS RESULTS  —  Marketing Budget 2025")
    print(f"  Predictor Variables Audited: {len(vif_df)}  |  Alert Threshold: VIF >= 10.0  |  Status: {alert_status}")
    print(DIVIDER)

    # Severity summary panel
    print(f"\n  SEVERITY DISTRIBUTION:")
    summary = [
        [SEVERITY_DISPLAY["CRITICAL"],   f"{critical_count} variable(s)"],
        [SEVERITY_DISPLAY["HIGH"],        f"{high_count} variable(s)"],
        [SEVERITY_DISPLAY["ELEVATED"],    f"{elevated_count} variable(s)"],
        [SEVERITY_DISPLAY["ACCEPTABLE"],  f"{acceptable_count} variable(s)"],
    ]
    for label, count in summary:
        print(f"    {label:<22}  {count}")

    print(f"\n  Maximum VIF Score Recorded:  {max_vif:.4f}")
    print()

    # Full results table
    rows = []
    for _, row in vif_df.iterrows():
        rows.append([
            row["Variable"],
            f"{row['VIF_Score']:>12.4f}",
            SEVERITY_DISPLAY[row["Severity"]],
            row["Short_Action"],
        ])

    print(tabulate(
        rows,
        headers=["Predictor Variable", "VIF Score", "Severity Classification", "Recommended Action"],
        tablefmt="rounded_outline",
        colalign=("left", "right", "left", "left"),
    ))

    print()

    # Interpretation callout
    flagged = vif_df[vif_df["VIF_Score"] >= 10.0]
    if not flagged.empty:
        print(f"  {THIN_DIVIDER}")
        print(f"  AUDIT FINDING: {len(flagged)} variable(s) exceed the VIF >= 10 capital inefficiency threshold.")
        for _, row in flagged.iterrows():
            print(f"    - {row['Variable']} (VIF = {row['VIF_Score']:.4f}) : {SEVERITY_DISPLAY[row['Severity']]}")
        print(f"  {THIN_DIVIDER}")

    print()


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def main() -> pd.DataFrame:
    print(f"\n{DIVIDER}")
    print("  HIGH-TICKET VIF OPTIMIZER")
    print("  Phase 2: Multicollinearity Analysis — Variance Inflation Factor Computation")
    print(f"  Engine: Python | Statsmodels 0.14 | OLS-Based VIF via Design Matrix Decomposition")
    print(DIVIDER)

    print(f"\n  [INFO] Loading dataset from:  {DATA_PATH}")
    try:
        vif_df = load_and_compute_vif()
    except (FileNotFoundError, ValueError) as exc:
        print(exc)
        sys.exit(1)

    print(f"  [INFO] VIF computation complete — {len(vif_df)} predictor variables analyzed.\n")
    display_vif_table(vif_df)

    print(f"  [INFO] Proceed to PDF generation: python report_generator.py")
    print()

    return vif_df


if __name__ == "__main__":
    main()
