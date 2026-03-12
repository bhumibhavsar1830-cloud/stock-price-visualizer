import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime, timedelta

# ── Page Config ───────────────────────────────────────────
st.set_page_config(page_title="Stock Price Visualizer", page_icon="📈", layout="wide")

# ── Dark Theme ────────────────────────────────────────────
st.markdown("""
<style>
body { background-color: #0a0a0a; }
.stApp { background: linear-gradient(135deg, #0a0a0a 0%, #0d1117 100%); }
h1 { color: #00E87A !important; }
.metric-card {
    background: #0d1117;
    border: 1px solid #1a2a1a;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ── Generate Synthetic Stock Data ─────────────────────────
def generate_stock_data(ticker, days=365, seed=42):
    np.random.seed(seed)
    dates = pd.date_range(end=datetime.today(), periods=days, freq='B')
    prices = {
        "TATAMOTORS": 600, "RELIANCE": 2400, "INFOSYS": 1500,
        "WIPRO": 400, "HDFC": 1600
    }
    base = prices.get(ticker, 1000)
    returns = np.random.normal(0.0005, 0.015, days)
    price = base * np.cumprod(1 + returns)
    volume = np.random.randint(500000, 5000000, days)
    df = pd.DataFrame({
        'Date': dates,
        'Open': price * np.random.uniform(0.99, 1.01, days),
        'High': price * np.random.uniform(1.01, 1.03, days),
        'Low':  price * np.random.uniform(0.97, 0.99, days),
        'Close': price,
        'Volume': volume
    })
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    df['Daily_Return'] = df['Close'].pct_change() * 100
    return df

# ── Sidebar ───────────────────────────────────────────────
st.sidebar.title("📊 Stock Settings")
ticker = st.sidebar.selectbox("Select Stock", ["TATAMOTORS", "RELIANCE", "INFOSYS", "WIPRO", "HDFC"])
period = st.sidebar.selectbox("Time Period", ["1 Month", "3 Months", "6 Months", "1 Year"])
chart_type = st.sidebar.selectbox("Chart Type", ["Line Chart", "Candlestick Style", "Area Chart"])

period_map = {"1 Month": 22, "3 Months": 66, "6 Months": 132, "1 Year": 365}
days = period_map[period]

seeds = {"TATAMOTORS": 42, "RELIANCE": 7, "INFOSYS": 13, "WIPRO": 21, "HDFC": 33}
df = generate_stock_data(ticker, days=365, seed=seeds[ticker])
df_filtered = df.tail(days)

# ── Header ────────────────────────────────────────────────
st.title("📈 Stock Price Visualizer")
st.markdown(f"### {ticker} — {period} Analysis")
st.markdown("---")

# ── Metrics ───────────────────────────────────────────────
current = df_filtered['Close'].iloc[-1]
prev    = df_filtered['Close'].iloc[-2]
change  = current - prev
pct     = (change / prev) * 100
high52  = df_filtered['High'].max()
low52   = df_filtered['Low'].min()
avg_vol = df_filtered['Volume'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Price", f"₹{current:.2f}", f"{pct:+.2f}%")
col2.metric("52W High", f"₹{high52:.2f}")
col3.metric("52W Low", f"₹{low52:.2f}")
col4.metric("Avg Volume", f"{avg_vol/1e6:.2f}M")

st.markdown("---")

# ── Main Chart ────────────────────────────────────────────
plt.style.use('dark_background')
fig, axes = plt.subplots(2, 1, figsize=(14, 9), gridspec_kw={'height_ratios': [3, 1]})
fig.patch.set_facecolor('#0d1117')

ax1 = axes[0]
ax1.set_facecolor('#0d1117')

if chart_type == "Line Chart":
    ax1.plot(df_filtered['Date'], df_filtered['Close'], color='#00E87A', linewidth=2, label='Close Price')
    ax1.plot(df_filtered['Date'], df_filtered['MA20'], color='#FF6B6B', linewidth=1.2, linestyle='--', label='MA20')
    ax1.plot(df_filtered['Date'], df_filtered['MA50'], color='#FFD93D', linewidth=1.2, linestyle='--', label='MA50')

elif chart_type == "Area Chart":
    ax1.fill_between(df_filtered['Date'], df_filtered['Close'], alpha=0.3, color='#00E87A')
    ax1.plot(df_filtered['Date'], df_filtered['Close'], color='#00E87A', linewidth=2, label='Close Price')
    ax1.plot(df_filtered['Date'], df_filtered['MA20'], color='#FF6B6B', linewidth=1.2, linestyle='--', label='MA20')

else:  # Candlestick Style
    for _, row in df_filtered.iterrows():
        color = '#00E87A' if row['Close'] >= row['Open'] else '#FF6B6B'
        ax1.plot([row['Date'], row['Date']], [row['Low'], row['High']], color=color, linewidth=0.8)
        ax1.bar(row['Date'], abs(row['Close'] - row['Open']), bottom=min(row['Open'], row['Close']),
                color=color, width=0.6, alpha=0.8)

ax1.set_title(f'{ticker} Stock Price — {period}', color='white', fontsize=16, fontweight='bold', pad=15)
ax1.set_ylabel('Price (₹)', color='#00E87A', fontsize=12)
ax1.legend(loc='upper left', facecolor='#0d1117', edgecolor='#1a2a1a', labelcolor='white')
ax1.grid(color='#1a2a1a', linestyle='--', alpha=0.5)
ax1.tick_params(colors='gray')
ax1.spines['bottom'].set_color('#1a2a1a')
ax1.spines['left'].set_color('#1a2a1a')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# Volume
ax2 = axes[1]
ax2.set_facecolor('#0d1117')
colors = ['#00E87A' if df_filtered['Close'].iloc[i] >= df_filtered['Close'].iloc[i-1]
          else '#FF6B6B' for i in range(len(df_filtered))]
ax2.bar(df_filtered['Date'], df_filtered['Volume'], color=colors, alpha=0.7, width=0.6)
ax2.set_ylabel('Volume', color='#00E87A', fontsize=10)
ax2.set_xlabel('Date', color='gray', fontsize=10)
ax2.grid(color='#1a2a1a', linestyle='--', alpha=0.3)
ax2.tick_params(colors='gray')
ax2.spines['bottom'].set_color('#1a2a1a')
ax2.spines['left'].set_color('#1a2a1a')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

plt.tight_layout()
st.pyplot(fig)
plt.close()

# ── Returns Distribution ──────────────────────────────────
st.markdown("---")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📊 Daily Returns Distribution")
    fig2, ax = plt.subplots(figsize=(7, 4))
    fig2.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#0d1117')
    returns_clean = df_filtered['Daily_Return'].dropna()
    sns.histplot(returns_clean, bins=30, color='#00E87A', alpha=0.7, ax=ax, kde=True,
                 line_kws={'color': '#FFD93D', 'linewidth': 2})
    ax.set_title('Daily Returns (%)', color='white', fontsize=13, fontweight='bold')
    ax.set_xlabel('Return (%)', color='gray')
    ax.set_ylabel('Frequency', color='gray')
    ax.tick_params(colors='gray')
    ax.grid(color='#1a2a1a', linestyle='--', alpha=0.4)
    for spine in ax.spines.values(): spine.set_color('#1a2a1a')
    st.pyplot(fig2)
    plt.close()

with col_b:
    st.subheader("📉 Correlation Heatmap")
    fig3, ax = plt.subplots(figsize=(7, 4))
    fig3.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#0d1117')
    corr_df = df_filtered[['Open', 'High', 'Low', 'Close', 'Volume']].corr()
    sns.heatmap(corr_df, annot=True, fmt='.2f', cmap='Greens', ax=ax,
                linewidths=0.5, linecolor='#0d1117',
                annot_kws={"size": 10, "color": "white"})
    ax.set_title('Feature Correlation', color='white', fontsize=13, fontweight='bold')
    ax.tick_params(colors='gray')
    st.pyplot(fig3)
    plt.close()

# ── Data Table ────────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Recent Stock Data")
display_df = df_filtered[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].tail(10).copy()
display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
for col in ['Open', 'High', 'Low', 'Close']:
    display_df[col] = display_df[col].apply(lambda x: f"₹{x:.2f}")
display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x:,}")
st.dataframe(display_df.set_index('Date'), use_container_width=True)

st.markdown("---")
st.caption("Built with Python | Matplotlib | Seaborn | Streamlit | Pandas")
