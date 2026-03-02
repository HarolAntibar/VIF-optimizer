"""
main.py
-------
Entry Point — Data Ingestion & Executive Summary Display
High-Ticket VIF Optimizer | Phase 1 of 3

Responsibilities:
    1. Load the marketing budget dataset from the canonical CSV path.
    2. Perform structural validation (schema, dtypes, null audit).
    3. Render a professional, executive-grade summary statistics table
       to stdout using tabulate.
    4. Surface a dataset health report for pre-analysis inspection.

Usage:
    python main.py

Dependencies:
    pandas, tabulate (installed in .venv)
"""

import sys
import io
import os
import pandas as pd
from tabulate import tabulate

# Ensure UTF-8 output on Windows terminals (avoids cp1252 UnicodeEncodeError
# when tabulate renders Unicode box-drawing characters in rounded_outline style)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_PATH = os.path.join("data", "marketing_budget_2025.csv")

EXPECTED_COLUMNS = [
    "TV_Spend",
    "Radio_Spend",
    "Social_Media_Spend",
    "Influencer_Fees",
    "Digital_Display_Spend",
    "Email_Marketing_Spend",
    "SEO_Budget",
    "Monthly_Revenue",
]

CURRENCY_COLUMNS = [
    "TV_Spend",
    "Radio_Spend",
    "Social_Media_Spend",
    "Influencer_Fees",
    "Digital_Display_Spend",
    "Email_Marketing_Spend",
    "SEO_Budget",
    "Monthly_Revenue",
]

DIVIDER = "=" * 78
THIN_DIVIDER = "-" * 78


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def fmt_usd(value: float) -> str:
    """Format a float as a USD currency string."""
    return f"${value:>14,.2f}"


def section_header(title: str) -> None:
    """Print a styled section header."""
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)


# ---------------------------------------------------------------------------
# Data Ingestion
# ---------------------------------------------------------------------------

def load_dataset(path: str) -> pd.DataFrame:
    """
    Load the marketing budget CSV dataset.

    Raises:
        FileNotFoundError: If the CSV does not exist at the specified path.
        ValueError: If expected columns are missing or dtypes are invalid.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"\n[FATAL] Dataset not found at: '{path}'\n"
            f"        Run 'python generate_data.py' to create the dataset first.\n"
        )

    df = pd.read_csv(path)

    # Schema validation
    missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(
            f"[FATAL] Schema mismatch. Missing columns: {sorted(missing_cols)}"
        )

    # Dtype validation — all columns must be numeric
    non_numeric = [
        col for col in EXPECTED_COLUMNS
        if not pd.api.types.is_numeric_dtype(df[col])
    ]
    if non_numeric:
        raise ValueError(
            f"[FATAL] Non-numeric dtypes detected in: {non_numeric}"
        )

    return df


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

def display_dataset_health(df: pd.DataFrame) -> None:
    """Render a concise dataset health report."""
    section_header("DATASET HEALTH REPORT")

    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()

    health_rows = [
        ["Dataset Path", DATA_PATH],
        ["Total Observations (Rows)", f"{df.shape[0]:,}"],
        ["Total Features (Columns)", f"{df.shape[1]:,}"],
        ["Total Null Values", f"{total_nulls:,} {'[OK]' if total_nulls == 0 else '[WARNING — nulls detected]'}"],
        ["Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"],
    ]

    print(tabulate(health_rows, headers=["Metric", "Value"], tablefmt="rounded_outline"))


def display_summary_statistics(df: pd.DataFrame) -> None:
    """
    Render a professional executive-grade summary statistics table.

    Displays: Count, Mean, Std Dev, Min, 25th Pct, Median, 75th Pct, Max
    for all numeric columns, formatted in USD.
    """
    section_header("EXECUTIVE DATASET SUMMARY — Marketing Budget 2025")
    print("  All monetary values expressed in USD (United States Dollars).\n")

    desc = df[CURRENCY_COLUMNS].describe().T  # shape: (n_cols, 8 stats)
    desc = desc[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]

    table_rows = []
    for col, row in desc.iterrows():
        table_rows.append([
            col,
            f"{int(row['count']):,}",
            fmt_usd(row["mean"]),
            fmt_usd(row["std"]),
            fmt_usd(row["min"]),
            fmt_usd(row["25%"]),
            fmt_usd(row["50%"]),
            fmt_usd(row["75%"]),
            fmt_usd(row["max"]),
        ])

    headers = ["Feature", "Count", "Mean", "Std Dev", "Min", "P25", "Median", "P75", "Max"]
    print(tabulate(table_rows, headers=headers, tablefmt="rounded_outline"))


def display_correlation_preview(df: pd.DataFrame) -> None:
    """
    Surface the top correlated variable pairs as a pre-analysis signal.
    Flags pairs with |r| > 0.80 as multicollinearity candidates.
    """
    section_header("CORRELATION PREVIEW — Multicollinearity Candidates")
    print("  Pairs with |r| > 0.80 flagged as HIGH multicollinearity risk.\n")

    predictor_cols = [c for c in CURRENCY_COLUMNS if c != "Monthly_Revenue"]
    corr_matrix = df[predictor_cols].corr()

    pairs = []
    for i, col_a in enumerate(predictor_cols):
        for col_b in predictor_cols[i + 1:]:
            r = corr_matrix.loc[col_a, col_b]
            if abs(r) > 0.40:  # surface meaningful relationships only
                flag = "*** CRITICAL ***" if abs(r) > 0.95 else ("** HIGH **" if abs(r) > 0.80 else "")
                pairs.append([col_a, col_b, f"{r:.4f}", flag])

    if pairs:
        pairs.sort(key=lambda x: abs(float(x[2])), reverse=True)
        print(tabulate(
            pairs,
            headers=["Variable A", "Variable B", "Pearson r", "Risk Flag"],
            tablefmt="rounded_outline"
        ))
    else:
        print("  No variable pairs with |r| > 0.40 detected.")


def display_next_steps() -> None:
    """Print an action-oriented next steps panel."""
    section_header("NEXT STEPS")
    steps = [
        ["1", "python vif_calculator.py", "Compute VIF scores & classify multicollinearity severity"],
        ["2", "python report_generator.py", "Generate executive-grade PDF report"],
    ]
    print(tabulate(steps, headers=["Step", "Command", "Action"], tablefmt="rounded_outline"))
    print()


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"\n{DIVIDER}")
    print("  HIGH-TICKET VIF OPTIMIZER")
    print("  Phase 1: Data Ingestion & Executive Summary")
    print(f"  Powered by Python | Pandas | Statsmodels")
    print(DIVIDER)

    # --- Ingest ---
    print(f"\n  [INFO] Loading dataset from: {DATA_PATH}")
    try:
        df = load_dataset(DATA_PATH)
    except (FileNotFoundError, ValueError) as exc:
        print(exc)
        sys.exit(1)
    print(f"  [INFO] Dataset loaded successfully. Shape: {df.shape}")

    # --- Report ---
    display_dataset_health(df)
    display_summary_statistics(df)
    display_correlation_preview(df)
    display_next_steps()


if __name__ == "__main__":
    main()
