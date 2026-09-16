
# ============================================================
# Nifty50 Equity Peer Comparison Analysis
# Author: Khooshi Mangal
# Description: Automated peer benchmarking report for 15 
# Nifty50 stocks using Python, yfinance, Pandas, and Matplotlib
# ============================================================

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Configuration ────────────────────────────────────────────

TICKERS = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS',
    'ICICIBANK.NS', 'SBIN.NS',
    'BAJFINANCE.NS', 'BHARTIARTL.NS', 'WIPRO.NS',
    'AXISBANK.NS', 'KOTAKBANK.NS', 'LT.NS',
    'MARUTI.NS', 'TITAN.NS', 'HCLTECH.NS'
]

BENCHMARK = '^NSEI'

SHORT_NAMES = {
    'RELIANCE.NS': 'Reliance',
    'TCS.NS': 'TCS',
    'HDFCBANK.NS': 'HDFC Bank',
    'INFY.NS': 'Infosys',
    'ICICIBANK.NS': 'ICICI Bank',
    'SBIN.NS': 'SBI',
    'BAJFINANCE.NS': 'Bajaj Fin',
    'BHARTIARTL.NS': 'Airtel',
    'WIPRO.NS': 'Wipro',
    'AXISBANK.NS': 'Axis Bank',
    'KOTAKBANK.NS': 'Kotak Bank',
    'LT.NS': 'L&T',
    'MARUTI.NS': 'Maruti',
    'TITAN.NS': 'Titan',
    'HCLTECH.NS': 'HCLTech'
}

PERIOD = '1y'
NAVY   = '#1F3864'
BLUE   = '#2E75B6'
ORANGE = '#ED7D31'
GREEN  = '#70AD47'
GREY   = '#F0F4F8'

# ── 1. Download Price Data ───────────────────────────────────

print("Downloading stock data from Yahoo Finance...")

raw = yf.download(TICKERS, period=PERIOD, auto_adjust=True)
prices = raw['Close']

benchmark_raw = yf.download(
    BENCHMARK,
    period=PERIOD,
    auto_adjust=True
)

benchmark = benchmark_raw['Close']

prices.columns = [SHORT_NAMES[t] for t in prices.columns]
prices.dropna(how='all', inplace=True)

print(f"Data loaded: {len(prices)} trading days, {len(prices.columns)} stocks\n")

# ─2. Calculate Returns & Risk Metrics ─────────────────────

daily_returns = prices.pct_change().dropna(how='all')
daily_returns.dropna(axis=1, how='all', inplace=True)
prices = prices[daily_returns.columns]
RISK_FREE_RATE = 0.0

summary = pd.DataFrame(index=prices.columns)
summary['1Y Return (%)']     = ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100
benchmark_return = float(((benchmark.iloc[-1] / benchmark.iloc[0]) - 1) * 100)
summary['Excess Return (%)'] = (summary['1Y Return (%)']- benchmark_return)
summary['Volatility (%)']    = daily_returns.std() * (252 ** 0.5) * 100
summary['Sharpe Ratio']      = (
    (daily_returns.mean() * 252 - RISK_FREE_RATE) /
    (daily_returns.std()  * (252 ** 0.5))
)
summary['Max Drawdown (%)']  = (
    (prices / prices.cummax() - 1).min() * 100
)
summary['Avg Daily Vol (%)'] = daily_returns.std() * 100

summary = summary.round(2)

# ── 3. Print Summary Table ──────────────────────


print("=" * 65)
print("NIFTY50 PEER COMPARISON — 1 YEAR PERFORMANCE SUMMARY")
print(f"Nifty 50 Benchmark Return: {benchmark_return:.2f}%")
print("=" * 65)
print(summary.to_string())
print("=" * 65)

# ── 4. Plot 1 — Cumulative Returns ──────────────────────────

cumulative = (1 + daily_returns).cumprod()
benchmark_cumulative = benchmark / benchmark.iloc[0]

fig1, ax1 = plt.subplots(figsize=(14, 7))
fig1.patch.set_facecolor(GREY)
ax1.set_facecolor('white')

for col in cumulative.columns:
    ax1.plot(cumulative.index, cumulative[col],
             linewidth=1.2, alpha=0.7)
ax1.plot(
    benchmark_cumulative.index,
    benchmark_cumulative.values,
    color=NAVY,
    linestyle='--',
    linewidth=2.2,
    label='Nifty 50 Benchmark'
)

ax1.axhline(y=1, color='black', linestyle='--',
            linewidth=0.8, alpha=0.4)

ax1.set_title('Cumulative Returns — 15 Nifty50 Stocks (1 Year)',
              fontsize=14, fontweight='bold', color=NAVY, pad=15)
ax1.set_xlabel('Date', fontsize=11, color=NAVY)
ax1.set_ylabel('Growth of ₹1 Invested', fontsize=11, color=NAVY)
ax1.legend(loc='upper left',
           fontsize=7, ncol=2, framealpha=0.8)
ax1.grid(True, alpha=0.3)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('01_cumulative_returns.png', dpi=150,
            bbox_inches='tight', facecolor=GREY)
plt.close()
print("Saved: 01_cumulative_returns.png")

# ── 5. Plot 2 — 1Y Return Ranked Bar Chart ──────────────────

sorted_returns = summary['1Y Return (%)'].sort_values(ascending=True)
colours = [GREEN if x >= 0 else ORANGE for x in sorted_returns]

fig2, ax2 = plt.subplots(figsize=(12, 7))
fig2.patch.set_facecolor(GREY)
ax2.set_facecolor('white')

bars = ax2.barh(sorted_returns.index, sorted_returns.values,
                color=colours, edgecolor='white', height=0.6)

for bar, val in zip(bars, sorted_returns.values):
    ax2.text(val + (0.5 if val >= 0 else -0.5),
             bar.get_y() + bar.get_height() / 2,
             f'{val:.1f}%',
             va='center',
             ha='left' if val >= 0 else 'right',
             fontsize=9, color=NAVY, fontweight='bold')

ax2.axvline(x=0, color='black', linewidth=0.8)
ax2.set_title('1-Year Return Ranked — 15 Nifty50 Stocks',
              fontsize=14, fontweight='bold', color=NAVY, pad=15)
ax2.set_xlabel('1-Year Return (%)', fontsize=11, color=NAVY)
ax2.grid(True, axis='x', alpha=0.3)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('02_returns_ranked.png', dpi=150,
            bbox_inches='tight', facecolor=GREY)
plt.close()
print("Saved: 02_returns_ranked.png")

# ── 6. Plot 3 — Risk vs Return Scatter ──────────────────────

fig3, ax3 = plt.subplots(figsize=(12, 7))
fig3.patch.set_facecolor(GREY)
ax3.set_facecolor('white')

sc = ax3.scatter(
    summary['Volatility (%)'],
    summary['1Y Return (%)'],
    s=120, color=NAVY, alpha=0.8, edgecolors='white', linewidth=1.5
)

for idx, row in summary.iterrows():
    ax3.annotate(idx,
                 (row['Volatility (%)'], row['1Y Return (%)']),
                 textcoords='offset points', xytext=(8, 4),
                 fontsize=8, color=NAVY)

ax3.axhline(y=0, color='black', linestyle='--',
            linewidth=0.8, alpha=0.4)
ax3.axvline(x=summary['Volatility (%)'].mean(),
            color=ORANGE, linestyle='--',
            linewidth=0.8, alpha=0.6,
            label=f"Avg Volatility ({summary['Volatility (%)'].mean():.1f}%)")

ax3.set_title('Risk vs Return — Volatility vs 1-Year Return',
              fontsize=14, fontweight='bold', color=NAVY, pad=15)
ax3.set_xlabel('Annualised Volatility (%)', fontsize=11, color=NAVY)
ax3.set_ylabel('1-Year Return (%)', fontsize=11, color=NAVY)
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('03_risk_vs_return.png', dpi=150,
            bbox_inches='tight', facecolor=GREY)
plt.close()
print("Saved: 03_risk_vs_return.png")

# ── 7. Plot 4 — Correlation Heatmap ─────────────────────────

corr = daily_returns.corr()

fig4, ax4 = plt.subplots(figsize=(13, 10))
fig4.patch.set_facecolor(GREY)

mask = pd.DataFrame(False, index=corr.index, columns=corr.columns)
for i in range(len(mask)):
    for j in range(i):
        mask.iloc[i, j] = True

sns.heatmap(
    corr,
    mask=mask,
    annot=True, fmt='.2f',
    cmap='Blues',
    center=0.5,
    square=True,
    linewidths=0.5,
    annot_kws={'size': 7},
    ax=ax4,
    cbar_kws={'shrink': 0.8}
)

ax4.set_title('Return Correlation Matrix — 15 Nifty50 Stocks',
              fontsize=14, fontweight='bold', color=NAVY, pad=15)

plt.tight_layout()
plt.savefig('04_correlation_heatmap.png', dpi=150,
            bbox_inches='tight', facecolor=GREY)
plt.close()
print("Saved: 04_correlation_heatmap.png")

# ── 8. Plot 5 — Sharpe Ratio Comparison ─────────────────────

sorted_sharpe = summary['Sharpe Ratio'].sort_values(ascending=True)
colours_s = [GREEN if x >= 1 else BLUE if x >= 0 else ORANGE
             for x in sorted_sharpe]

fig5, ax5 = plt.subplots(figsize=(12, 7))
fig5.patch.set_facecolor(GREY)
ax5.set_facecolor('white')

bars5 = ax5.barh(sorted_sharpe.index, sorted_sharpe.values,
                 color=colours_s, edgecolor='white', height=0.6)

for bar, val in zip(bars5, sorted_sharpe.values):
    ax5.text(val + 0.02,
             bar.get_y() + bar.get_height() / 2,
             f'{val:.2f}',
             va='center', fontsize=9,
             color=NAVY, fontweight='bold')

ax5.axvline(x=1, color=GREEN, linestyle='--',
            linewidth=1, alpha=0.7, label='Sharpe = 1 reference')
ax5.axvline(x=0, color='black', linewidth=0.8)

ax5.set_title('Sharpe Ratio Comparison — Risk-Adjusted Returns',
              fontsize=14, fontweight='bold', color=NAVY, pad=15)
ax5.set_xlabel('Sharpe Ratio', fontsize=11, color=NAVY)
ax5.legend(fontsize=9)
ax5.grid(True, axis='x', alpha=0.3)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('05_sharpe_ratio.png', dpi=150,
            bbox_inches='tight', facecolor=GREY)
plt.close()
print("Saved: 05_sharpe_ratio.png")
# ── 9. Plot 6 — Maximum Drawdown Comparison ─────────────────

sorted_drawdown = summary['Max Drawdown (%)'].sort_values(ascending=True)

fig6, ax6 = plt.subplots(figsize=(12, 7))
fig6.patch.set_facecolor(GREY)
ax6.set_facecolor('white')

bars6 = ax6.barh(
    sorted_drawdown.index,
    sorted_drawdown.values,
    color=ORANGE,
    edgecolor='white',
    height=0.6
)

for bar, val in zip(bars6, sorted_drawdown.values):
    ax6.text(
        val - 0.8,
        bar.get_y() + bar.get_height() / 2,
        f'{val:.1f}%',
        va='center',
        ha='right',
        fontsize=9,
        color=NAVY,
        fontweight='bold'
    )

ax6.axvline(x=0, color='black', linewidth=0.8)

ax6.set_title(
    'Maximum Drawdown — Downside Risk Comparison',
    fontsize=14,
    fontweight='bold',
    color=NAVY,
    pad=15
)

ax6.set_xlabel(
    'Maximum Drawdown (%)',
    fontsize=11,
    color=NAVY
)

ax6.grid(True, axis='x', alpha=0.3)
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)

ax6.set_xlim(summary['Max Drawdown (%)'].min() - 5, 0)

plt.tight_layout()

plt.savefig(
    '06_max_drawdown.png',
    dpi=150,
    bbox_inches='tight',
    facecolor=GREY
)

plt.close()

print("Saved: 06_max_drawdown.png")
# ─ 10. Export Summary Table as CSV ──────────────────────────

summary.to_csv('peer_comparison_summary.csv')
print("Saved: peer_comparison_summary.csv")

# ─ 11. Done ─────────────────────────────────────────────────

print("\n" + "=" * 65)
print("ANALYSIS COMPLETE — 6 charts + 1 CSV exported")
print("Files saved to:", '/Users/khooshimangal/Desktop/equity-peer-analysis/')
print("=" * 65)
