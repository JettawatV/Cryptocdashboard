import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import websocket
import ta
import threading
import time

class BinanceAPI:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.websocket_url = "wss://stream.binance.com:9443/ws"
        self.ws = None
        self.current_price = None
        self.current_volume = None

    def get_historical_klines(self, symbol="BTCUSDT", interval="1d", limit=1000):
        """Fetch historical klines/candlestick data"""
        endpoint = f"{self.base_url}/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        try:
            response = requests.get(endpoint, params=params)
            data = response.json()
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'quote_volume']
            df[numeric_columns] = df[numeric_columns].astype(float)
            
            return df
        except Exception as e:
            st.error(f"Error fetching historical data: {e}")
            return None

    def get_ticker_24h(self, symbol="BTCUSDT"):
        """Get 24-hour ticker statistics"""
        endpoint = f"{self.base_url}/ticker/24hr"
        params = {"symbol": symbol}
        
        try:
            response = requests.get(endpoint, params=params)
            return response.json()
        except Exception as e:
            st.error(f"Error fetching ticker data: {e}")
            return None

    def get_exchange_info(self):
        """Get exchange information including trading pairs"""
        endpoint = f"{self.base_url}/exchangeInfo"
        try:
            response = requests.get(endpoint)
            return response.json()
        except Exception as e:
            st.error(f"Error fetching exchange info: {e}")
            return None

    def start_websocket(self, symbol="btcusdt"):
        """Start WebSocket connection for real-time price updates"""
        def on_message(ws, message):
            data = json.loads(message)
            if 'p' in data:  # Price data
                self.current_price = float(data['p'])
            if 'q' in data:  # Volume data
                self.current_volume = float(data['q'])

        def on_error(ws, error):
            print(f"WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            print("WebSocket connection closed")

        def on_open(ws):
            print("WebSocket connection opened")
            # Subscribe to trade stream
            subscribe_message = {
                "method": "SUBSCRIBE",
                "params": [f"{symbol}@trade"],
                "id": 1
            }
            ws.send(json.dumps(subscribe_message))

        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            f"{self.websocket_url}/{symbol}@trade",
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )

        # Start WebSocket connection in a separate thread
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

    def stop_websocket(self):
        """Stop WebSocket connection"""
        if self.ws:
            self.ws.close()

def calculate_technical_indicators(df):
    """Calculate various technical indicators"""
    # Moving Averages
    df['SMA_20'] = ta.trend.sma_indicator(df['close'], window=20)
    df['SMA_50'] = ta.trend.sma_indicator(df['close'], window=50)
    df['EMA_20'] = ta.trend.ema_indicator(df['close'], window=20)
    
    # RSI
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)
    
    # MACD
    macd = ta.trend.MACD(df['close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['MACD_Hist'] = macd.macd_diff()
    
    # Bollinger Bands
    bollinger = ta.volatility.BollingerBands(df['close'])
    df['BB_Upper'] = bollinger.bollinger_hband()
    df['BB_Lower'] = bollinger.bollinger_lband()
    df['BB_Middle'] = bollinger.bollinger_mavg()
    
    return df

def plot_technical_analysis(df):
    """Create technical analysis plots"""
    fig = make_subplots(rows=3, cols=1, 
                       shared_xaxes=True,
                       vertical_spacing=0.05,
                       row_heights=[0.6, 0.2, 0.2])

    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price'
    ), row=1, col=1)

    # Add Moving Averages
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['SMA_20'],
                            name='SMA 20', line=dict(color='blue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['SMA_50'],
                            name='SMA 50', line=dict(color='orange')), row=1, col=1)
    
    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['BB_Upper'],
                            name='BB Upper', line=dict(color='gray', dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['BB_Lower'],
                            name='BB Lower', line=dict(color='gray', dash='dash')), row=1, col=1)

    # Volume
    fig.add_trace(go.Bar(x=df['timestamp'], y=df['volume'],
                        name='Volume'), row=2, col=1)

    # MACD
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['MACD'],
                            name='MACD', line=dict(color='blue')), row=3, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['MACD_Signal'],
                            name='Signal', line=dict(color='orange')), row=3, col=1)
    fig.add_trace(go.Bar(x=df['timestamp'], y=df['MACD_Hist'],
                        name='MACD Histogram'), row=3, col=1)

    fig.update_layout(
        title_text="Technical Analysis",
        xaxis_title="Date",
        height=900,
        showlegend=True,
        template="plotly_dark"
    )

    return fig

# Initialize Binance API
binance = BinanceAPI()

# Streamlit app
st.set_page_config(page_title="Crypto Analysis Dashboard", layout="wide")
st.title("Crypto Analysis Dashboard")

# Sidebar
st.sidebar.title("Settings")

# Get available trading pairs
exchange_info = binance.get_exchange_info()
if exchange_info and 'symbols' in exchange_info:
    trading_pairs = [symbol['symbol'] for symbol in exchange_info['symbols']]
else:
    st.error("Failed to fetch exchange info or missing 'symbols' key")
    trading_pairs = []

# Timeframe selection
timeframe_options = {
    '1 Hour': '1h',
    '4 Hours': '4h',
    '1 Day': '1d',
    '1 Week': '1w'
}
selected_timeframe = st.sidebar.selectbox("Select Timeframe", list(timeframe_options.keys()))

# Start WebSocket connection for real-time updates
if 'websocket_started' not in st.session_state:
    st.session_state.websocket_started = False
    
if selected_pair:
    binance.start_websocket(selected_pair.lower())
else:
    st.error("No trading pair selected")
    
if not st.session_state.websocket_started:
    binance.start_websocket(selected_pair.lower())
    st.session_state.websocket_started = True

# Get historical data
df = binance.get_historical_klines(
    symbol=selected_pair,
    interval=timeframe_options[selected_timeframe]
)

if df is not None:
    # Calculate technical indicators
    df = calculate_technical_indicators(df)
    
    # Get current market data
    ticker_data = binance.get_ticker_24h(selected_pair)
    
    if ticker_data:
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Price",
                f"${float(ticker_data['lastPrice']):.2f}",
                f"{float(ticker_data['priceChangePercent'])}%"
            )
        
        with col2:
            st.metric(
                "24h Volume",
                f"${float(ticker_data['volume']):,.0f}"
            )
        
        with col3:
            st.metric(
                "24h High",
                f"${float(ticker_data['highPrice']):,.2f}"
            )
        
        with col4:
            st.metric(
                "24h Low",
                f"${float(ticker_data['lowPrice']):,.2f}"
            )
    
    # Display technical analysis chart
    tech_analysis_fig = plot_technical_analysis(df)
    st.plotly_chart(tech_analysis_fig, use_container_width=True)
    
    # Display technical indicators
    st.subheader("Technical Indicators")
    latest = df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        rsi_color = "🔴" if latest['RSI'] > 70 else "🟢" if latest['RSI'] < 30 else "⚪"
        st.metric("RSI", f"{rsi_color} {latest['RSI']:.2f}")
    
    with col2:
        macd_signal = "🔴" if latest['MACD'] < latest['MACD_Signal'] else "🟢"
        st.metric("MACD", f"{macd_signal} {latest['MACD']:.2f}")
    
    with col3:
        price_sma20 = "🔴" if latest['close'] < latest['SMA_20'] else "🟢"
        st.metric("Price vs SMA20", f"{price_sma20} {(latest['close']/latest['SMA_20']-1)*100:.2f}%")
    
    with col4:
        bb_position = ((latest['close'] - latest['BB_Lower']) / 
                      (latest['BB_Upper'] - latest['BB_Lower']))
        st.metric("BB Position", f"{bb_position:.2f}")

# Cleanup WebSocket on app shutdown
def cleanup():
    binance.stop_websocket()

st.on_script_run_end(cleanup)

# [Previous code remains the same until before the cleanup function]

def get_btc_dominance():
    """Calculate Bitcoin dominance using Binance data"""
    try:
        # Get all USDT trading pairs ticker data
        response = requests.get("https://api.binance.com/api/v3/ticker/24hr")
        all_tickers = response.json()
        
        # Calculate total market cap (approximate using USDT pairs)
        total_market_cap = sum(
            float(ticker['lastPrice']) * float(ticker['volume'])
            for ticker in all_tickers
            if ticker['symbol'].endswith('USDT')
        )
        
        # Get BTC market cap
        btc_ticker = next(ticker for ticker in all_tickers if ticker['symbol'] == 'BTCUSDT')
        btc_market_cap = float(btc_ticker['lastPrice']) * float(btc_ticker['volume'])
        
        return (btc_market_cap / total_market_cap) * 100
    except Exception as e:
        st.error(f"Error calculating BTC dominance: {e}")
        return None

def get_funding_rate():
    """Get funding rate from Binance Futures"""
    try:
        response = requests.get("https://fapi.binance.com/fapi/v1/fundingRate", 
                              params={"symbol": "BTCUSDT"})
        data = response.json()
        if data:
            return float(data[0]['fundingRate']) * 100
    except Exception as e:
        st.error(f"Error fetching funding rate: {e}")
        return None

def get_open_interest():
    """Get open interest from Binance Futures"""
    try:
        response = requests.get("https://fapi.binance.com/fapi/v1/openInterest", 
                              params={"symbol": "BTCUSDT"})
        data = response.json()
        if data:
            return float(data['openInterest'])
    except Exception as e:
        st.error(f"Error fetching open interest: {e}")
        return None

# After the technical indicators section, add:
if selected_pair == 'BTCUSDT':
    st.subheader("Today's Insights")
    
    # Get additional metrics
    btc_dominance = get_btc_dominance()
    funding_rate = get_funding_rate()
    open_interest = get_open_interest()
    
    # Format current timestamp
    current_time = datetime.now().strftime("%A, %B %d, %Y")
    
    # Create insights text
    insights_text = f"""
    {current_time} insights:
    
    **Bitcoin**'s price is currently at **${float(ticker_data['lastPrice']):,.2f}**, with a 24-hour trading volume of 
    **${float(ticker_data['volume']):,.2f}** ({float(ticker_data['priceChangePercent']):+.2f}%). """
    
    if btc_dominance:
        insights_text += f"BTC dominance is at **{btc_dominance:.1f}%**. "
    
    if funding_rate:
        insights_text += f"The current funding rate is **{funding_rate:+.4f}%**. "
    
    if open_interest:
        oi_value = float(ticker_data['lastPrice']) * open_interest
        insights_text += f"Open interest stands at **${oi_value/1e9:.2f}B**. "
    
    insights_text += f"""
    The 24-hour price range is between **${float(ticker_data['lowPrice']):,.2f}** and **${float(ticker_data['highPrice']):,.2f}**.
    RSI is currently at **{latest['RSI']:.1f}**, indicating {'overbought' if latest['RSI'] > 70 else 'oversold' if latest['RSI'] < 30 else 'neutral'} conditions.
    """
    
    st.markdown(insights_text)
