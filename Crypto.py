import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="Crypto Dashboard",
    page_icon="📈",
    layout="wide"
)

# Binance API Base URL
BINANCE_BASE_URL = "https://api.binance.com"

# Function to get Binance market data
def get_binance_data(symbol, interval, limit=100):
    """Fetch historical market data from Binance"""
    try:
        url = f"{BINANCE_BASE_URL}/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        response = requests.get(url, params=params)
        data = response.json()

        if isinstance(data, dict) and "code" in data:  # Binance API Error
            st.error(f"Binance API Error: {data['msg']}")
            return None

        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "num_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df[["open", "high", "low", "close", "volume"]] = df[
            ["open", "high", "low", "close", "volume"]
        ].astype(float)

        return df
    except Exception as e:
        st.error(f"Error fetching Binance data: {e}")
        return None

# Function to get real-time crypto market data
def get_binance_ticker(symbol):
    """Fetch real-time price & market stats from Binance"""
    try:
        url = f"{BINANCE_BASE_URL}/api/v3/ticker/24hr"
        params = {"symbol": symbol}
        response = requests.get(url, params=params)
        data = response.json()

        if "code" in data:
            st.error(f"Binance API Error: {data['msg']}")
            return None

        return {
            "price": float(data["lastPrice"]),
            "change": float(data["priceChangePercent"]),
            "volume": float(data["quoteVolume"])
        }
    except Exception as e:
        st.error(f"Error fetching Binance ticker: {e}")
        return None

# Function to get Bitcoin blockchain stats
def get_blockchain_info():
    """Fetch Bitcoin network statistics from Blockchain.info API"""
    try:
        difficulty_url = "https://blockchain.info/q/getdifficulty"
        hashrate_url = "https://blockchain.info/q/hashrate"
        
        difficulty = requests.get(difficulty_url).json()
        hashrate = requests.get(hashrate_url).json()
        
        return {
            'difficulty': difficulty,
            'hashrate': hashrate / 1e6  # Convert to EH/s
        }
    except Exception as e:
        st.error(f"Error fetching blockchain data: {e}")
        return None

# Sidebar settings
st.sidebar.title("Settings")

# Cryptocurrency selection (Binance pairs)
crypto_options = {
    "Bitcoin (BTC)": "BTCUSDT",
    "Ethereum (ETH)": "ETHUSDT",
    "Binance Coin (BNB)": "BNBUSDT",
    "Solana (SOL)": "SOLUSDT",
    "Cardano (ADA)": "ADAUSDT"
}
selected_crypto = st.sidebar.selectbox(
    "Select Cryptocurrency", list(crypto_options.keys())
)

# Timeframe selection (Binance intervals)
timeframe_options = {
    "1 Min": "1m",
    "5 Min": "5m",
    "15 Min": "15m",
    "1 Hour": "1h",
    "4 Hours": "4h",
    "1 Day": "1d",
    "1 Week": "1w"
}
selected_timeframe = st.sidebar.selectbox(
    "Select Timeframe", list(timeframe_options.keys())
)

# Load Binance data
crypto_symbol = crypto_options[selected_crypto]
interval = timeframe_options[selected_timeframe]

df = get_binance_data(crypto_symbol, interval)
ticker = get_binance_ticker(crypto_symbol)

# Dashboard Title
st.title("Crypto Analysis Dashboard")
st.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Display real-time market data
if ticker:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Current Price", f"${ticker['price']:,.2f}")

    with col2:
        st.metric("24h Change", f"{ticker['change']}%", delta=ticker['change'])

    with col3:
        st.metric("24h Volume", f"${ticker['volume']:,.2f}")

# Display historical data
if df is not None and not df.empty:
    st.subheader(f"{selected_crypto} - {selected_timeframe} Chart")

    # Candlestick Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["timestamp"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Candlesticks"
    ))
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Line Chart
    st.subheader("Closing Price Trend")
    st.line_chart(df.set_index("timestamp")["close"])

# Display Bitcoin-specific metrics
if selected_crypto == "Bitcoin (BTC)":
    blockchain_info = get_blockchain_info()

    if blockchain_info:
        st.subheader("Bitcoin Network Metrics")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Network Difficulty", f"{blockchain_info['difficulty']/1e12:.2f}T")
        
        with col2:
            st.metric("Hashrate", f"{blockchain_info['hashrate']:.2f} EH/s")
