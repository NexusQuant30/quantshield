import streamlit as st
import yfinance as yf
import pandas as pd

# Set up the app layout
st.set_page_config(page_title="QuantShield Dashboard", layout="wide")

st.title("QuantShield: Live Market Dashboard")

# 1. Choose your crypto
ticker = st.selectbox("Select Cryptocurrency", ["BTC-USD", "ETH-USD", "SOL-USD"])

# 2. Fetch real data
@st.cache_data
def get_data(symbol):
    data = yf.download(symbol, period="1mo", interval="1d")
    return data

# Display data
data = get_data(ticker)

# 3. Show the chart
st.subheader(f"Price Analysis for {ticker}")
if not data.empty:
    st.line_chart(data['Close'])
else:
    st.write("Data not available.")

# 4. Affiliate Section
st.sidebar.markdown("---")
st.sidebar.subheader("Ready to trade?")
# Your live referral link is now linked here
st.sidebar.markdown("[Click here to start trading on Binance](https://www.binance.com/activity/referral-entry/CPA?ref=CPA_00PZTVYM10)")
