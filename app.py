import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- 1. PREMIUM PAGE SETUP ---
st.set_page_config(
    page_title="QuantShield Pro Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THE EXPANDED MONETIZATION SYSTEM (YOUR AFFILIATE HOOKS) ---
EXNESS_AFFILIATE_URL = "https://your-placeholder-link.com/exness"
HFM_AFFILIATE_URL = "https://your-placeholder-link.com/hfm"
TRADINGVIEW_AFFILIATE_URL = "https://your-placeholder-link.com/tradingview"
BINANCE_AFFILIATE_URL = "https://your-placeholder-link.com/binance"
LEDGER_WALLET_URL = "https://your-placeholder-link.com/hardware-wallet"

# --- 3. SESSION STATE ENGINE (Simulating User Trading Portfolio) ---
if "simulated_balance" not in st.session_state:
    st.session_state.simulated_balance = 10000.00
if "trade_history" not in st.session_state:
    st.session_state.trade_history = []

# --- 4. DYNAMIC MARKET DATA GENERATOR ---
def get_market_data(asset, timeframe):
    np.random.seed(seed=len(asset) + len(timeframe)) 
    periods = 120 if timeframe in ["5M", "15M"] else 80
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='H' if "M" in timeframe else 'D')
    
    base_price = {"EUR/USD": 1.09, "BTC/USD": 64000, "XAU/USD (Gold)": 2350, "GBP/USD": 1.27}[asset]
    volatility = {"EUR/USD": 0.001, "BTC/USD": 450, "XAU/USD (Gold)": 8.0, "GBP/USD": 0.0012}[asset]
    
    close_prices = np.random.normal(0, volatility, periods).cumsum() + base_price
    high_prices = close_prices + np.random.uniform(0, volatility * 1.5, periods)
    low_prices = close_prices - np.random.uniform(0, volatility * 1.5, periods)
    open_prices = close_prices + np.random.uniform(-volatility, volatility, periods)
    rsi = np.random.uniform(28, 76, periods)
    ema = pd.Series(close_prices).ewm(span=14).mean().values
    
    return pd.DataFrame({'Date': dates, 'Open': open_prices, 'High': high_prices, 'Low': low_prices, 'Close': close_prices, 'RSI': rsi, 'EMA': ema})

# --- 5. AD SPACE #1: GOOGLE ADSENSE TOP RUNNER ---
st.html(
    """
    <div style="background-color: #121212; border: 1px dashed #333; padding: 8px; border-radius: 4px; text-align: center; margin-bottom: 15px;">
        <span style="color: #666; font-size: 10px; display: block;">ADVERTISEMENT SLOT #1 (GOOGLE ADSENSE LEADERBOARD)</span>
        <strong style="color: #00e676;">[Top Banner Code Space - Earns per view]</strong>
    </div>
    """
)

# --- 6. USER INTERFACE CONTROLS (WATCHLIST & TIMEFRAME) ---
st.title("🛡️ QuantShield Advanced Market Intelligence")

control_col1, control_col2 = st.columns([2, 1])
with control_col1:
    selected_asset = st.selectbox("🎯 Target Asset Watchlist Selection:", ["EUR/USD", "BTC/USD", "XAU/USD (Gold)", "GBP/USD"])
with control_col2:
    selected_timeframe = st.radio("⏱️ Multi-Timeframe Matrix:", ["5M", "15M", "1H", "1D"], horizontal=True)

df = get_market_data(selected_asset, selected_timeframe)
latest_data = df.iloc[-1]

# --- 7. SIDEBAR HUB: PRO SYSTEM & BROKER LINKS ---
with st.sidebar:
    st.image("https://img.icons8.com/nolan/64/shield.png", width=50)
    st.header("QuantShield HQ")
    
    st.subheader("🤖 Subscriber Protocol")
    premium_active = st.toggle("Unlock Engine Commentary", value=False)
    
    st.divider()
    
    st.subheader("⚡ Execute Account Trades")
    st.caption("Direct integration to verified liquid global execution networks:")
    st.link_button("🌐 Open Verified Exness Account", EXNESS_AFFILIATE_URL, type="primary", use_container_width=True)
    st.link_button("📈 Open Regulated HFM Account", HFM_AFFILIATE_URL, use_container_width=True)
    st.link_button("🪙 Trade Crypto via Binance", BINANCE_AFFILIATE_URL, use_container_width=True)
    
    st.divider()
    st.html(
        f"""
        <div style="background-color: #1a1a1a; padding: 10px; border-radius: 4px; text-align: center; border: 1px solid #333;">
            <span style="color: #666; font-size: 10px; display: block;">SPONSORED PRODUCT</span>
            <a href="{LEDGER_WALLET_URL}" target="_blank" style="color: #ff9100; text-decoration: none; font-size: 12px; font-weight: bold;">
                🔒 Secure Your Crypto Assets with Ledger Wallets!
            </a>
        </div>
        """
    )

# --- 8. LIVE SIMULATED PORTFOLIO LEDGER (Practice Mode) ---
st.subheader("💼 Simulated Paper-Trading Portfolio")
port_col1, port_col2, port_col3 = st.columns(3)
port_col1.metric("Available Liquidity Balance", f"${st.session_state.simulated_balance:,.2f}")
port_col2.metric("Active Market Position Asset", selected_asset)

with port_col3:
    trade_action = st.radio("Simulate Execution Direction:", ["BUY (Long)", "SELL (Short)"], horizontal=True)
    if st.button("Execute Virtual Order Pattern", use_container_width=True):
        st.session_state.simulated_balance -= 50.00 
        st.session_state.trade_history.append(f"{datetime.now().strftime('%H:%M:%S')} - {trade_action} executed on {selected_asset} at price {latest_data['Close']:.4f}")
        st.success("Trade Recorded to Simulation Ledger System!")

# --- 9. CHARTS AND PERFORMANCE METRICS ---
st.divider()
metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
metrics_col1.metric("Current Spot Close", f"{latest_data['Close']:.4f}")
metrics_col2.metric("RSI Momentum Index", f"{latest_data['RSI']:.2f}")
metrics_col3.metric("Dynamic Moving Baseline (EMA 14)", f"{latest_data['EMA']:.4f}")

fig = go.Figure(data=[go.Candlestick(
    x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Candlesticks"
)])
fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA'], mode='lines', name='EMA (14)', line=dict(color='#ffeb3b', width=1.5)))
fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10), height=380)
st.plotly_chart(fig, use_container_width=True)

# --- 10. AD SPACE #3: INTERMEDIATE TRADINGVIEW AFFILIATE SPACE ---
st.subheader("🛠️ Recommended Pro Trading Infrastructure Tools")
ad_grid1, ad_grid2 = st.columns(2)
with ad_grid1:
    st.html(
        f"""
        <div style="background-color: #1c1d24; padding: 15px; border-radius: 6px; border: 1px solid #2962ff;">
            <h4 style="color: #2962ff; margin-top:0;">📊 Pro Charting Engine Allocation</h4>
            <p style="color: #ccc; font-size: 13px;">Unlock advanced technical charting definitions, custom script backtesting, and instant alert nodes via TradingView framework profiles.</p>
            <a href="{TRADINGVIEW_AFFILIATE_URL}" target="_blank" style="background-color: #2962ff; color: white; padding: 8px 12px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block; font-size: 12px;">Deploy TradingView Access Link</a>
        </div>
        """
    )
with ad_grid2:
    st.html(
        """
        <div style="background-color: #1e1e1e; border: 1px dashed #444; padding: 25px; border-radius: 6px; text-align: center; height: 100%;">
            <span style="color: #777; font-size: 11px; display: block;">NATIVE BANNER PROMOTION PLATFORM SLOT</span>
            <span style="color: #aaa; font-size: 13px; display:block; margin-top:10px;">[Insert Custom Software Review, Prop Firm Link, or Extra Ad Scripts Here]</span>
        </div>
        """
    )

# --- 11. AI COMMENTATOR FEED ---
st.divider()
st.subheader("🧠 AI Analytical Engine Intelligence Output")
if premium_active:
    rsi_val = latest_data['RSI']
    if rsi_val > 68:
        st.error(f"⚠️ **Engine Warning Matrix:** {selected_asset} shows extreme momentum at RSI **{rsi_val:.1f}**. Technical overbought protocols are highly active. Short positions are statistically favorable.")
    elif rsi_val < 35:
        st.success(f"📈 **Engine Entry Signal:** {selected_asset} index has bottomed out at RSI **{rsi_val:.1f}**. Oversold patterns confirmed close to multi-period EMA lines. Bullish scaling suggested.")
    else:
        st.info(f"🔄 **Engine Consolidation Framework:** {selected_asset} trading securely at RSI value **{rsi_val:.1f}**. No direct structural breakdown detected. Trend remains neutral.")
else:
    st.warning("🔒 AI Feedback Core is Encrypted. Please toggle the Premium Access Protocol in the side panel grid menu to unlock active metrics analysis.")

# --- 12. DATA HISTORY VIEW ---
if st.session_state.trade_history:
    with st.expander("📝 View Active Virtual Trading Ledger History Logs"):
        for log in reversed(st.session_state.trade_history):
            st.text(log)

# --- 13. AD SPACE #4: GOOGLE ADSENSE GLOBAL FOOTER ---
st.divider()
st.html(
    """
    <div style="background-color: #121212; border: 1px dashed #333; padding: 12px; border-radius: 4px; text-align: center;">
        <span style="color: #666; font-size: 10px; display: block; margin-bottom: 4px;">ADVERTISEMENT SLOT #4 (GOOGLE ADSENSE FOOTER MATCHED CONTENT)</span>
        <strong style="color: #00e676;">[Native Footer Ad Unit Script Placement Segment]</strong>
    </div>
    """
)
