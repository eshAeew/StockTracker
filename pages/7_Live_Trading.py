import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta
from utils.data_fetcher import get_stock_data, search_stocks, get_top_stocks_list
from utils.live_data_streamer import generate_live_data as stream_live_data

st.set_page_config(
    page_title="Live Trading | Indian Stock Market Analysis",
    page_icon="⚡",
    layout="wide"
)

# Initialize session state variables
if 'live_data' not in st.session_state:
    st.session_state.live_data = pd.DataFrame(columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    
if 'selected_symbol' not in st.session_state:
    st.session_state.selected_symbol = "RELIANCE.NS"
    
if 'selected_name' not in st.session_state:
    st.session_state.selected_name = "Reliance Industries"
    
if 'timeframe' not in st.session_state:
    st.session_state.timeframe = "1m"  # Default 1 minute

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
    
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = datetime.now()

def generate_live_data(symbol, timeframe, num_points=100):
    """
    Generate live data for a stock
    In a real implementation, this would fetch from a real-time API
    """
    try:
        # Get historical data to use as a base
        if timeframe in ["1m", "2m", "5m", "15m", "30m", "60m", "90m"]:
            # For intraday timeframes, get 5 days of data
            base_data = get_stock_data(symbol, period="5d", interval=timeframe)
        else:
            # For daily or longer timeframes
            base_data = get_stock_data(symbol, period="1mo", interval=timeframe)
        
        if base_data.empty:
            # If no data, create synthetic data
            current_time = datetime.now()
            times = [current_time - timedelta(minutes=i) for i in range(num_points, 0, -1)]
            
            # Generate a price series with some volatility
            last_price = np.random.uniform(500, 5000)
            price_volatility = last_price * 0.002  # 0.2% volatility
            
            data = []
            for i in range(num_points):
                price_change = np.random.normal(0, price_volatility)
                open_price = last_price
                close_price = open_price + price_change
                high_price = max(open_price, close_price) + abs(np.random.normal(0, price_volatility * 0.5))
                low_price = min(open_price, close_price) - abs(np.random.normal(0, price_volatility * 0.5))
                volume = np.random.randint(1000, 100000)
                
                data.append({
                    'Time': times[i],
                    'Open': open_price,
                    'High': high_price,
                    'Low': low_price,
                    'Close': close_price,
                    'Volume': volume
                })
                
                last_price = close_price
            
            # Create DataFrame
            df = pd.DataFrame(data)
            df['Time'] = pd.to_datetime(df['Time'])
            df = df.sort_values('Time')
            
            return df
        else:
            # Use real historical data, but add the most recent simulated candle
            df = base_data.copy()
            
            # Ensure we have 'Date' column properly named
            if 'Datetime' in df.columns:
                df.rename(columns={'Datetime': 'Time'}, inplace=True)
            else:
                df.rename(columns={'Date': 'Time'}, inplace=True)
            
            # Generate the latest candle
            last_price = df['Close'].iloc[-1]
            price_volatility = last_price * 0.002  # 0.2% volatility
            
            # Calculate new time based on timeframe
            last_time = df['Time'].iloc[-1]
            
            if timeframe == "1m":
                new_time = last_time + timedelta(minutes=1)
            elif timeframe == "5m":
                new_time = last_time + timedelta(minutes=5)
            elif timeframe == "15m":
                new_time = last_time + timedelta(minutes=15)
            elif timeframe == "30m":
                new_time = last_time + timedelta(minutes=30)
            elif timeframe == "60m":
                new_time = last_time + timedelta(hours=1)
            elif timeframe == "1d":
                new_time = last_time + timedelta(days=1)
            else:
                new_time = datetime.now()
            
            # Generate new price
            price_change = np.random.normal(0, price_volatility)
            open_price = last_price
            close_price = open_price + price_change
            high_price = max(open_price, close_price) + abs(np.random.normal(0, price_volatility * 0.5))
            low_price = min(open_price, close_price) - abs(np.random.normal(0, price_volatility * 0.5))
            volume = np.random.randint(1000, 100000)
            
            # Add new candle
            new_candle = pd.DataFrame({
                'Time': [new_time],
                'Open': [open_price],
                'High': [high_price],
                'Low': [low_price],
                'Close': [close_price],
                'Volume': [volume]
            })
            
            # Append new candle and limit to last 100 points
            df = pd.concat([df, new_candle], ignore_index=True)
            
            # Return the last 100 points
            return df.tail(num_points)
            
    except Exception as e:
        st.error(f"Error generating live data: {e}")
        return pd.DataFrame()
        
def update_live_chart(fig, data):
    """Update the live chart with new data"""
    if data.empty:
        return fig
        
    # Update the candlestick data
    fig.data[0].x = data['Time']
    fig.data[0].open = data['Open']
    fig.data[0].high = data['High']
    fig.data[0].low = data['Low']
    fig.data[0].close = data['Close']
    
    # If the chart has volume, update it too
    if len(fig.data) > 1:
        fig.data[1].x = data['Time']
        fig.data[1].y = data['Volume']
        
        # Update volume colors based on price change
        colors = ['#26A69A' if data['Close'].iloc[i] >= data['Open'].iloc[i] else '#EF5350' 
                  for i in range(len(data))]
        fig.data[1].marker.color = colors
    
    # Update the x-axis range to show the latest candles
    fig.update_layout(
        xaxis_range=[data['Time'].iloc[0], data['Time'].iloc[-1] + pd.Timedelta(minutes=2)],
        yaxis_range=[data['Low'].min() * 0.995, data['High'].max() * 1.005]
    )
    
    return fig

def create_live_chart(data, title="Live Price Chart"):
    """Create a live candlestick chart"""
    # Create subplot layout with volume
    fig = go.Figure()
    
    # Add candlestick chart
    candlestick = go.Candlestick(
        x=data['Time'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Price",
        increasing_line_color='#26A69A',  # green
        decreasing_line_color='#EF5350',  # red
    )
    
    fig.add_trace(candlestick)
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Price (₹)",
        xaxis_rangeslider_visible=False,
        height=600,
        width=None,  # Full width
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='#131722',  # Dark background like Olymp
        paper_bgcolor='#131722',  # Dark background
        font=dict(
            family="Roboto, sans-serif",
            size=12,
            color="#FFFFFF"  # White text
        ),
        yaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.1)'  # Subtle grid lines
        ),
        xaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.1)'  # Subtle grid lines
        )
    )
    
    return fig

def main():
    st.title("Live Trading View")
    st.write("Real-time candlestick charts with second-by-second updates")
    
    # Stock selection and parameters
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        # Create a search box with button
        search_query = st.text_input("Search Stock", placeholder="e.g., RELIANCE, TCS")
        
    with col2:
        # Timeframe selection
        timeframes = {
            "1 Minute": "1m",
            "5 Minutes": "5m",
            "15 Minutes": "15m",
            "30 Minutes": "30m",
            "1 Hour": "60m",
            "1 Day": "1d"
        }
        selected_tf = st.selectbox("Timeframe", list(timeframes.keys()))
        st.session_state.timeframe = timeframes[selected_tf]
    
    with col3:
        # Auto-refresh toggle
        st.session_state.auto_refresh = st.checkbox("Auto Refresh", value=st.session_state.auto_refresh)
    
    with col4:
        # Manual refresh button
        if st.button("Refresh Now"):
            st.session_state.last_update_time = datetime.now()
    
    # Process stock search
    if search_query:
        try:
            search_results = search_stocks(search_query)
            if search_results:
                # Show search results
                st.subheader("Search Results")
                
                # Create selectable buttons for search results
                selected_stock = None
                cols = st.columns(4)  # Display up to 4 stocks per row
                
                for i, (symbol, name) in enumerate(search_results):
                    col_idx = i % 4
                    with cols[col_idx]:
                        if st.button(f"{name} ({symbol})", key=f"search_{symbol}"):
                            st.session_state.selected_symbol = symbol
                            st.session_state.selected_name = name
                            st.session_state.last_update_time = datetime.now()
                            selected_stock = True
                
                if not selected_stock:
                    # If no selection, default to first result
                    pass
            else:
                st.warning(f"No stocks found matching '{search_query}'")
        except Exception as e:
            st.error(f"Error searching for stocks: {e}")
    else:
        # If no search, show top stocks for quick selection
        st.subheader("Popular Stocks")
        
        try:
            top_stocks = get_top_stocks_list()
            
            # Display top stocks as selectable buttons
            selected = False
            cols = st.columns(5)  # Display 5 stocks per row
            
            for i, (symbol, name) in enumerate(top_stocks):
                col_idx = i % 5
                with cols[col_idx]:
                    if st.button(f"{name}", key=f"top_{symbol}"):
                        st.session_state.selected_symbol = symbol
                        st.session_state.selected_name = name
                        st.session_state.last_update_time = datetime.now()
                        selected = True
            
            if not selected:
                # No selection, keep existing
                pass
        except Exception as e:
            st.error(f"Error loading popular stocks: {e}")
    
    # Add a divider
    st.markdown("---")
    
    # Display selected stock and current price
    symbol_display = st.session_state.selected_symbol.replace('.NS', '')
    st.header(f"{st.session_state.selected_name} ({symbol_display}) - {selected_tf}")
    
    # Generate or update live data
    current_time = datetime.now()
    time_diff = (current_time - st.session_state.last_update_time).total_seconds()
    
    # Auto-refresh every second if enabled
    if st.session_state.auto_refresh or time_diff > 5:
        # Use the enhanced live data streamer for more realistic second-by-second updates
        st.session_state.live_data = stream_live_data(
            st.session_state.selected_symbol, 
            st.session_state.timeframe
        )
        st.session_state.last_update_time = current_time
    
    # Create or update chart
    if not st.session_state.live_data.empty:
        # Get the latest price and change
        latest_close = st.session_state.live_data['Close'].iloc[-1]
        prev_close = st.session_state.live_data['Close'].iloc[-2] if len(st.session_state.live_data) > 1 else latest_close
        price_change = latest_close - prev_close
        price_change_pct = (price_change / prev_close) * 100 if prev_close > 0 else 0
        
        # Display price metrics
        price_color = "green" if price_change >= 0 else "red"
        change_icon = "↗" if price_change >= 0 else "↘"
        
        # Create a row for price display
        price_col1, price_col2, price_col3 = st.columns([1, 1, 3])
        
        with price_col1:
            st.metric(
                label="Current Price",
                value=f"₹{latest_close:.2f}",
                delta=f"{change_icon} {price_change:.2f}"
            )
        
        with price_col2:
            st.metric(
                label="Change %",
                value=f"{price_change_pct:.2f}%",
                delta=None
            )
        
        # Create live chart
        chart_title = f"{symbol_display} - {selected_tf} Chart"
        fig = create_live_chart(st.session_state.live_data, title=chart_title)
        
        # Display chart
        chart_placeholder = st.empty()
        chart_placeholder.plotly_chart(fig, use_container_width=True)
        
        # Auto-refresh with a placeholder to avoid full page reloads
        if st.session_state.auto_refresh:
            status_placeholder = st.empty()
            
            # Simulate real-time updates
            for i in range(100):
                # Only continue if auto-refresh is still enabled
                if not st.session_state.auto_refresh:
                    break
                    
                # Update status message
                status_placeholder.info(f"Live updates active - Last update: {datetime.now().strftime('%H:%M:%S')}")
                
                # Generate new data point using the enhanced streamer
                new_data = stream_live_data(
                    st.session_state.selected_symbol, 
                    st.session_state.timeframe
                )
                
                if not new_data.empty:
                    # Update the chart
                    st.session_state.live_data = new_data
                    fig = update_live_chart(fig, new_data)
                    chart_placeholder.plotly_chart(fig, use_container_width=True)
                    
                    # Update price metrics
                    latest_close = new_data['Close'].iloc[-1]
                    prev_close = new_data['Close'].iloc[-2] if len(new_data) > 1 else latest_close
                    price_change = latest_close - prev_close
                    price_change_pct = (price_change / prev_close) * 100 if prev_close > 0 else 0
                    
                    change_icon = "↗" if price_change >= 0 else "↘"
                    with price_col1:
                        st.metric(
                            label="Current Price",
                            value=f"₹{latest_close:.2f}",
                            delta=f"{change_icon} {price_change:.2f}"
                        )
                    
                    with price_col2:
                        st.metric(
                            label="Change %",
                            value=f"{price_change_pct:.2f}%",
                            delta=None
                        )
                
                # Wait for a short time to simulate real-time
                time.sleep(1)
        
        # Price history table
        with st.expander("Price History"):
            # Format the data for display
            display_data = st.session_state.live_data.copy()
            
            # Format the time
            display_data['Time'] = pd.to_datetime(display_data['Time']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Round price values
            price_columns = ['Open', 'High', 'Low', 'Close']
            for col in price_columns:
                display_data[col] = display_data[col].round(2)
            
            # Add change column
            display_data['Change'] = st.session_state.live_data['Close'].diff().round(2)
            display_data['Change%'] = (st.session_state.live_data['Close'].pct_change() * 100).round(2)
            
            # Reorder and display
            display_data = display_data[['Time', 'Open', 'High', 'Low', 'Close', 'Change', 'Change%', 'Volume']]
            st.dataframe(display_data, use_container_width=True)
    else:
        st.warning("No data available for the selected stock. Please try another stock or timeframe.")
    
    # Advanced trading tools expander
    with st.expander("Trading Tools"):
        # Create tabs for different tools
        tool_tab1, tool_tab2, tool_tab3 = st.tabs(["Price Alerts", "Quick Analysis", "Trade Simulator"])
        
        with tool_tab1:
            st.subheader("Set Price Alerts")
            
            alert_col1, alert_col2 = st.columns(2)
            
            with alert_col1:
                alert_price = st.number_input("Alert Price (₹)", min_value=0.01, value=latest_close)
                alert_condition = st.selectbox("Condition", ["Price rises above", "Price falls below"])
                
                if st.button("Set Alert"):
                    st.success(f"Alert set: {alert_condition} ₹{alert_price:.2f}")
            
            with alert_col2:
                st.subheader("Active Alerts")
                st.info("No active alerts. Set an alert to get notified when price conditions are met.")
        
        with tool_tab2:
            st.subheader("Quick Technical Analysis")
            
            # Simple technical indicators
            quick_col1, quick_col2 = st.columns(2)
            
            with quick_col1:
                # Calculate some basic indicators
                if not st.session_state.live_data.empty:
                    close_prices = st.session_state.live_data['Close']
                    
                    # Calculate short and long-term moving averages
                    short_ma = close_prices.rolling(window=5).mean().iloc[-1]
                    long_ma = close_prices.rolling(window=20).mean().iloc[-1]
                    
                    # Determine trend
                    if short_ma > long_ma:
                        trend = "Bullish 📈"
                        trend_color = "green"
                    else:
                        trend = "Bearish 📉"
                        trend_color = "red"
                    
                    st.markdown(f"**Current Trend:** <span style='color:{trend_color}'>{trend}</span>", unsafe_allow_html=True)
                    st.write(f"5-period MA: ₹{short_ma:.2f}")
                    st.write(f"20-period MA: ₹{long_ma:.2f}")
                    
                    # Price range
                    day_high = st.session_state.live_data['High'].max()
                    day_low = st.session_state.live_data['Low'].min()
                    
                    st.write(f"Period High: ₹{day_high:.2f}")
                    st.write(f"Period Low: ₹{day_low:.2f}")
                    st.write(f"Range: ₹{(day_high - day_low):.2f}")
            
            with quick_col2:
                # Support and resistance levels (simplified)
                if not st.session_state.live_data.empty:
                    price_range = st.session_state.live_data['High'].max() - st.session_state.live_data['Low'].min()
                    mid_price = (st.session_state.live_data['High'].max() + st.session_state.live_data['Low'].min()) / 2
                    
                    resistance2 = mid_price + price_range * 0.5
                    resistance1 = mid_price + price_range * 0.25
                    support1 = mid_price - price_range * 0.25
                    support2 = mid_price - price_range * 0.5
                    
                    st.subheader("Support & Resistance")
                    st.write(f"Resistance 2: ₹{resistance2:.2f}")
                    st.write(f"Resistance 1: ₹{resistance1:.2f}")
                    st.write(f"Support 1: ₹{support1:.2f}")
                    st.write(f"Support 2: ₹{support2:.2f}")
        
        with tool_tab3:
            st.subheader("Trade Simulator")
            
            sim_col1, sim_col2 = st.columns(2)
            
            with sim_col1:
                trade_type = st.selectbox("Trade Type", ["Buy (Long)", "Sell (Short)"])
                trade_amount = st.number_input("Investment Amount (₹)", min_value=1000, value=10000, step=1000)
                entry_price = st.number_input("Entry Price (₹)", min_value=0.01, value=latest_close)
                
                take_profit = st.number_input(
                    "Take Profit Price (₹)", 
                    min_value=0.01, 
                    value=latest_close * 1.05 if trade_type == "Buy (Long)" else latest_close * 0.95
                )
                
                stop_loss = st.number_input(
                    "Stop Loss Price (₹)", 
                    min_value=0.01, 
                    value=latest_close * 0.95 if trade_type == "Buy (Long)" else latest_close * 1.05
                )
                
                if st.button("Calculate"):
                    # Calculate shares
                    shares = trade_amount / entry_price
                    
                    # Calculate profit/loss scenarios
                    profit = shares * (take_profit - entry_price) if trade_type == "Buy (Long)" else shares * (entry_price - take_profit)
                    loss = shares * (stop_loss - entry_price) if trade_type == "Buy (Long)" else shares * (entry_price - stop_loss)
                    
                    profit_pct = ((take_profit / entry_price) - 1) * 100 if trade_type == "Buy (Long)" else ((entry_price / take_profit) - 1) * 100
                    loss_pct = ((stop_loss / entry_price) - 1) * 100 if trade_type == "Buy (Long)" else ((entry_price / stop_loss) - 1) * 100
                    
                    # Risk-reward ratio
                    risk_reward = abs(profit / loss) if loss != 0 else float('inf')
                    
                    with sim_col2:
                        st.subheader("Trade Analysis")
                        st.write(f"Shares: {shares:.2f}")
                        st.write(f"Potential Profit: ₹{profit:.2f} ({profit_pct:.2f}%)")
                        st.write(f"Potential Loss: ₹{abs(loss):.2f} ({abs(loss_pct):.2f}%)")
                        st.write(f"Risk-Reward Ratio: {risk_reward:.2f}")
                        
                        # Add recommendation
                        if risk_reward >= 2:
                            st.success("Favorable risk-reward ratio (>= 2:1)")
                        else:
                            st.warning("Unfavorable risk-reward ratio (< 2:1)")
    
    # Footer
    st.markdown("---")
    st.caption("Real-time data is simulated for educational purposes. In a production environment, real-time data would be fetched from appropriate APIs.")
    st.caption(f"© {datetime.now().year} Indian Stock Market Analysis Platform. Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()