"""
generate_data.py
----------------
Synthetic dataset generator for the High-Ticket VIF Optimizer.

Produces marketing_budget_2025.csv — a 200-row dataset modelling a
realistic marketing spend scenario where Social_Media_Spend and
Influencer_Fees carry a deliberate near-perfect linear relationship
(r > 0.95), simulating the real-world pattern where influencer
activations are always deployed in lockstep with paid social campaigns.

This structural collinearity will surface as CRITICAL VIF scores in the
subsequent analysis phase, validating the optimizer's detection engine.

Usage:
    python generate_data.py

Output:
    data/marketing_budget_2025.csv
"""

import os
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RANDOM_SEED = 42
N_ROWS = 200
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "marketing_budget_2025.csv")

rng = np.random.default_rng(RANDOM_SEED)

# ---------------------------------------------------------------------------
# Independent spend channels (minimally correlated by design)
# ---------------------------------------------------------------------------
tv_spend = rng.uniform(15_000, 120_000, N_ROWS).round(2)
radio_spend = rng.uniform(5_000, 40_000, N_ROWS).round(2)
digital_display_spend = rng.uniform(8_000, 75_000, N_ROWS).round(2)
email_marketing_spend = rng.uniform(1_500, 12_000, N_ROWS).round(2)
seo_budget = rng.uniform(3_000, 25_000, N_ROWS).round(2)

# ---------------------------------------------------------------------------
# Intentionally collinear channels: Social Media <-> Influencer Fees
# Influencer_Fees ≈ 0.72 * Social_Media_Spend + small Gaussian noise
# Achieved correlation target: r > 0.95
# ---------------------------------------------------------------------------
social_media_spend = rng.uniform(10_000, 90_000, N_ROWS).round(2)
noise = rng.normal(0, 2_500, N_ROWS)  # tight noise band to preserve high r
influencer_fees = (0.72 * social_media_spend + noise).clip(min=2_000).round(2)

# ---------------------------------------------------------------------------
# Dependent variable: Monthly Revenue
# A realistic linear combination of all channels + irreducible noise
# ---------------------------------------------------------------------------
monthly_revenue = (
    0.85 * tv_spend
    + 0.60 * radio_spend
    + 1.10 * social_media_spend
    + 0.95 * influencer_fees
    + 1.20 * digital_display_spend
    + 0.70 * email_marketing_spend
    + 0.50 * seo_budget
    + rng.normal(0, 18_000, N_ROWS)
).clip(min=50_000).round(2)

# ---------------------------------------------------------------------------
# Assemble DataFrame
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "TV_Spend": tv_spend,
    "Radio_Spend": radio_spend,
    "Social_Media_Spend": social_media_spend,
    "Influencer_Fees": influencer_fees,
    "Digital_Display_Spend": digital_display_spend,
    "Email_Marketing_Spend": email_marketing_spend,
    "SEO_Budget": seo_budget,
    "Monthly_Revenue": monthly_revenue,
})

# ---------------------------------------------------------------------------
# Persist to disk
# ---------------------------------------------------------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

# ---------------------------------------------------------------------------
# Validation report
# ---------------------------------------------------------------------------
corr = df["Social_Media_Spend"].corr(df["Influencer_Fees"])
print(f"[DATA GENERATOR] Dataset shape          : {df.shape}")
print(f"[DATA GENERATOR] Output path            : {OUTPUT_FILE}")
print(f"[DATA GENERATOR] Social_Media <-> Influencer correlation : {corr:.4f}")
print(f"[DATA GENERATOR] Status                 : {'PASS — r > 0.95 confirmed' if corr > 0.95 else 'WARNING — correlation below target'}")
print(f"[DATA GENERATOR] Null values            : {df.isnull().sum().sum()}")
print(f"[DATA GENERATOR] Generation complete.")
