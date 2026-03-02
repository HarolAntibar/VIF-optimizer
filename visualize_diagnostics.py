import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- EXECUTIVE BRAND PALETTE ---
NAVY_BLUE = '#001f3f'   # Header background
CRITICAL_RED = '#b00020' # Critical Alert (VIF > 10)
SUCCESS_GREEN = '#2e7d32' # Acceptable range
LIGHT_GREY = '#f5f5f5'   # Background for plots

def generate_correlation_assets():
    # 1. Path Detection
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data', 'marketing_budget_2025.csv')
    output_dir = os.path.join(base_dir, 'output', 'visuals')
    
    if not os.path.exists(data_path):
        print(f"❌ [CRITICAL] Data not found at: {data_path}")
        return

    # 2. Load Data
    df = pd.read_csv(data_path)
    os.makedirs(output_dir, exist_ok=True)

    # Global Style Setup
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = LIGHT_GREY
    plt.rcParams['font.family'] = 'sans-serif'

    # --- ASSET A: Scatter Plot (The Smoking Gun) ---
    plt.figure(figsize=(10, 7))
    correlation = df['Social_Media_Spend'].corr(df['Influencer_Fees'])
    
    # Regression plot with Navy and Red (Matching the Report's "Critical" theme)
    sns.regplot(
        x='Social_Media_Spend', 
        y='Influencer_Fees', 
        data=df, 
        scatter_kws={'alpha':0.4, 'color': NAVY_BLUE}, 
        line_kws={'color': CRITICAL_RED, 'lw': 4, 'label': f'Correlation r = {correlation:.4f}'}
    )
    
    plt.title('CAPITAL REDUNDANCY AUDIT: FEATURE OVERLAP', fontsize=16, fontweight='bold', color=NAVY_BLUE, pad=20)
    plt.xlabel('Social Media Spend (USD)', fontsize=12, fontweight='semibold')
    plt.ylabel('Influencer Fees (USD)', fontsize=12, fontweight='semibold')
    plt.legend(facecolor='white', frameon=True, edgecolor=NAVY_BLUE)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'correlation_scatter.png'), dpi=300)
    plt.close()

    # --- ASSET B: Heatmap (Executive Overview) ---
    plt.figure(figsize=(12, 10))
    
    # Custom colormap from Green (Good) to Red (Critical)
    cmap = sns.diverging_palette(130, 10, as_cmap=True) # Green to Red
    
    sns.heatmap(
        df.corr(), 
        annot=True, 
        cmap=cmap, 
        center=0, 
        fmt=".2f", 
        linewidths=1.5,
        cbar_kws={"shrink": .8},
        annot_kws={"weight": "bold", "size": 12}
    )
    
    plt.title('STRATEGIC VARIABLE CORRELATION MATRIX', fontsize=18, fontweight='bold', color=NAVY_BLUE, pad=25)
    plt.xticks(rotation=45, ha='right', fontweight='semibold')
    plt.yticks(fontweight='semibold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'), dpi=300)
    plt.close()

    print(f"\n✅ [SUCCESS] Visuals exported with Executive Palette to: {output_dir}")

if __name__ == "__main__":
    generate_correlation_assets()