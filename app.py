    import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="QuantShield | Live Market Dashboard", layout="wide", page_icon="🛡️")

# ---------------------------------------------------------
# SESSION STATE (Discipline Tracker memory for this session)
# ---------------------------------------------------------
if "loss_streak" not in st.session_state:
    st.session_state.loss_streak = 0
if "locked_until" not in st.session_state:
    st.session_state.locked_until = None
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []

LOSS_LIMIT = 3          # consecutive losses before lockout
COOLDOWN_MINUTES = 60   # how long the lock lasts

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.title("🛡️ QuantShield")
st.caption("Live market analysis + built-in trading discipline.")

# ---------------------------------------------------------
# TOP BANNER (mobile-first — visible without opening sidebar)
# ---------------------------------------------------------
banner_col1, banner_col2 = st.columns([3, 1])
with banner_col1:
    st.info("📊 Free live market analysis below. When you're ready to trade, open an account through the Binance link →")
with banner_col2:
    st.link_button(
        "Open Binance",
        "https://www.binance.com/activity/referral-entry/CPA?ref=CPA_00PZTVYM10",
        use_container_width=True
    )

with st.expander("ℹ️ How this works"):
    st.write(
        "QuantShield is a free tool: it pulls live price data and runs statistical "
        "indicators (Bollinger Bands, RSI) to flag potential setups in plain English. "
        "It doesn't place trades and never asks for any account password or login. "
        "If you open a Binance account through the link on this page, I earn a small "
        "commission at no extra cost to you — that's what keeps this dashboard free."
    )

st.markdown("---")

# ---------------------------------------------------------
# ASSET SELECTION
# ---------------------------------------------------------
col1, col2 = st.columns([2, 1])
with col1:
    ticker = st.selectbox(
        "Select Asset",
        ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"]
    )
with col2:
    period = st.selectbox("Time Range", ["5d", "1mo", "3mo", "6mo"], index=1)

# ---------------------------------------------------------
# DATA FETCH
# ---------------------------------------------------------
@st.cache_data(ttl=300)  # refresh every 5 minutes
def get_data(symbol, period):
    data = yf.download(symbol, period=period, interval="1d", progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

data = get_data(ticker, period)

if data.empty:
    st.error("No data available right now. Try a different asset or refresh in a moment.")
    st.stop()

# ---------------------------------------------------------
# MATH ENGINE: Bollinger Bands + RSI
# ---------------------------------------------------------
def add_indicators(df):
    df = df.copy()
    df["SMA20"] = df["Close"].rolling(window=20, min_periods=1).mean()
    df["STD20"] = df["Close"].rolling(window=20, min_periods=1).std()
    df["UpperBand"] = df["SMA20"] + (2 * df["STD20"])
    df["LowerBand"] = df["SMA20"] - (2 * df["STD20"])

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))
    df["RSI"] = df["RSI"].fillna(50)
    return df

data = add_indicators(data)

latest_close = float(data["Close"].iloc[-1])
latest_rsi = float(data["RSI"].iloc[-1])
latest_upper = float(data["UpperBand"].iloc[-1])
latest_lower = float(data["LowerBand"].iloc[-1])

# ---------------------------------------------------------
# PLAIN-ENGLISH SIGNAL (informational only — not a guarantee)
# ---------------------------------------------------------
if latest_close <= latest_lower and latest_rsi < 30:
    signal = "POTENTIAL OVERSOLD BOUNCE"
    signal_color = "green"
    explanation = "Price is below its lower band and RSI shows oversold momentum. Historically this *can* precede a bounce — it is not a guarantee."
elif latest_close >= latest_upper and latest_rsi > 70:
    signal = "POTENTIAL OVERBOUGHT PULLBACK"
    signal_color = "red"
    explanation = "Price is above its upper band and RSI shows overbought momentum. Historically this *can* precede a pullback — it is not a guarantee."
else:
    signal = "NEUTRAL / WAIT"
    signal_color = "gray"
    explanation = "No statistical edge detected right now. The math engine favors patience over forcing a trade."

# ---------------------------------------------------------
# ANALYSIS DASHBOARD
# ---------------------------------------------------------
st.subheader(f"Price Analysis: {ticker}")

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
metric_col1.metric("Live Price", f"${latest_close:,.2f}")
metric_col2.metric("RSI (14)", f"{latest_rsi:.1f}")
metric_col3.metric("Upper Band", f"${latest_upper:,.2f}")
metric_col4.metric("Lower Band", f"${latest_lower:,.2f}")

st.markdown(
    f"<h3 style='color:{signal_color};'>Signal: {signal}</h3>",
    unsafe_allow_html=True
)
st.write(explanation)

if signal != "NEUTRAL / WAIT":
    cta_col1, cta_col2 = st.columns([3, 1])
    with cta_col1:
        st.write("**See a setup like this?** Act on it directly on Binance.")
    with cta_col2:
        st.link_button(
            "Trade on Binance",
            "https://www.binance.com/activity/referral-entry/CPA?ref=CPA_00PZTVYM10",
            use_container_width=True
        )

# ---------------------------------------------------------
# CHART (fixed — correct orientation, dark theme, bands overlaid)
# ---------------------------------------------------------
fig = go.Figure()
fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Close Price", line=dict(color="#00D1B2", width=2)))
fig.add_trace(go.Scatter(x=data.index, y=data["UpperBand"], name="Upper Band", line=dict(color="rgba(255,80,80,0.5)", dash="dot")))
fig.add_trace(go.Scatter(x=data.index, y=data["LowerBand"], name="Lower Band", line=dict(color="rgba(80,200,120,0.5)", dash="dot")))
fig.add_trace(go.Scatter(x=data.index, y=data["SMA20"], name="20-Day Avg", line=dict(color="rgba(200,200,200,0.4)")))

fig.update_layout(
    template="plotly_dark",
    height=450,
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    yaxis_title="Price (USD)",
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# DISCIPLINE TRACKER (self-logged — no external account access)
# ---------------------------------------------------------
st.subheader("🧠 Discipline Tracker")
st.caption("Log your own trade outcomes. After 3 losses in a row, the tracker locks itself for an hour to force a cooldown.")

now = datetime.now()
is_locked = st.session_state.locked_until and now < st.session_state.locked_until

if is_locked:
    remaining = st.session_state.locked_until - now
    minutes_left = int(remaining.total_seconds() // 60) + 1
    st.error(f"🔒 LOCKED — {minutes_left} minute(s) remaining. Step away and let the market reset. Emotional trading after a losing streak is how accounts get wiped out.")
else:
    log_col1, log_col2 = st.columns(2)
    with log_col1:
        if st.button("✅ Log a WIN", use_container_width=True):
            st.session_state.loss_streak = 0
            st.session_state.trade_log.append({"time": now.strftime("%H:%M:%S"), "result": "WIN"})
            st.rerun()
    with log_col2:
        if st.button("❌ Log a LOSS", use_container_width=True):
            st.session_state.loss_streak += 1
            st.session_state.trade_log.append({"time": now.strftime("%H:%M:%S"), "result": "LOSS"})
            if st.session_state.loss_streak >= LOSS_LIMIT:
                st.session_state.locked_until = now + timedelta(minutes=COOLDOWN_MINUTES)
            st.rerun()

    st.write(f"Current consecutive losses: **{st.session_state.loss_streak} / {LOSS_LIMIT}**")

if st.session_state.trade_log:
    with st.expander("View trade log"):
        st.table(pd.DataFrame(st.session_state.trade_log[::-1]))

st.markdown("---")

# ---------------------------------------------------------
# AFFILIATE SECTION (sidebar — legitimate, no credentials handled)
# ---------------------------------------------------------
st.sidebar.markdown("### Ready to trade what you're analyzing?")
st.sidebar.write("Open a Binance account through the link below — sign-up happens entirely on Binance's own site.")
st.sidebar.link_button(
    "Open Binance",
    "https://www.binance.com/activity/referral-entry/CPA?ref=CPA_00PZTVYM10",
    use_container_width=True
)
st.sidebar.caption("Disclosure: this is an affiliate link. I may earn a commission if you sign up through it, at no extra cost to you.")

st.sidebar.markdown("---")
st.sidebar.caption(
    "⚠️ Not financial advice. Indicators shown (RSI, Bollinger Bands) are statistical tools, not guarantees. "
    "Markets carry risk of loss. Trade only what you can afford to lose."
)
