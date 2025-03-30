import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_fetcher import get_stock_data, get_top_stocks_list, search_stocks
from utils.technical_indicators import (
    create_technical_chart,
    add_moving_average, 
    add_exponential_moving_average, 
    add_bollinger_bands, 
    add_rsi, 
    add_macd, 
    add_stochastic, 
    add_atr, 
    add_obv
)

st.set_page_config(
    page_title="Technical Indicators | Indian Stock Market Analysis",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("Technical Indicators")
    st.write("Apply technical analysis tools to analyze stock price patterns")
    
    # Stock selection and parameters
    st.header("Select Stock and Indicators")
    
    # Layout for stock selection
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        # Allow searching for stocks
        search_query = st.text_input("Search for a stock (name or symbol)", placeholder="e.g., RELIANCE or TCS")
    
    with col2:
        # Period selector
        periods = {
            "1 Month": "1mo", 
            "3 Months": "3mo", 
            "6 Months": "6mo", 
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y"
        }
        selected_period = st.selectbox("Time Period", list(periods.keys()), index=3)
        period = periods[selected_period]
    
    with col3:
        # Interval selector
        intervals = {
            "Daily": "1d",
            "Weekly": "1wk", 
            "Monthly": "1mo"
        }
        selected_interval = st.selectbox("Interval", list(intervals.keys()), index=0)
        interval = intervals[selected_interval]
    
    # Determine which stock to analyze
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
                            selected_stock = symbol
                
                if selected_stock:
                    stock_symbol = selected_stock
                else:
                    # Default to the first result if none selected
                    stock_symbol = search_results[0][0]
            else:
                st.warning(f"No stocks found matching '{search_query}'")
                # Default to a popular stock
                stock_symbol = "RELIANCE.NS"
        except Exception as e:
            st.error(f"Error searching for stocks: {e}")
            # Default to a popular stock
            stock_symbol = "RELIANCE.NS"
    else:
        # If no search, show top stocks for selection
        st.subheader("Popular Stocks")
        
        try:
            top_stocks = get_top_stocks_list()
            
            # Display top stocks as selectable buttons
            selected_stock = None
            cols = st.columns(5)  # Display 5 stocks per row
            
            for i, (symbol, name) in enumerate(top_stocks):
                col_idx = i % 5
                with cols[col_idx]:
                    if st.button(f"{name}", key=f"top_{symbol}"):
                        selected_stock = symbol
            
            if selected_stock:
                stock_symbol = selected_stock
            else:
                # Default to the first top stock
                stock_symbol = top_stocks[0][0]
        except Exception as e:
            st.error(f"Error loading popular stocks: {e}")
            # Default to a popular stock
            stock_symbol = "RELIANCE.NS"
    
    # Technical indicator selection
    st.subheader("Select Technical Indicators")
    
    # Create layout for indicator selection
    indicator_cols = st.columns(5)
    
    with indicator_cols[0]:
        use_sma = st.checkbox("Simple Moving Average (SMA)", value=True)
        use_ema = st.checkbox("Exponential Moving Average (EMA)", value=False)
        use_bollinger = st.checkbox("Bollinger Bands", value=True)
    
    with indicator_cols[1]:
        use_rsi = st.checkbox("Relative Strength Index (RSI)", value=True)
        use_macd = st.checkbox("MACD", value=True)
    
    with indicator_cols[2]:
        use_stoch = st.checkbox("Stochastic Oscillator", value=False)
        use_atr = st.checkbox("Average True Range (ATR)", value=False)
    
    with indicator_cols[3]:
        use_obv = st.checkbox("On Balance Volume (OBV)", value=False)
    
    with indicator_cols[4]:
        # Custom parameters for indicators
        sma_period_1 = st.number_input("SMA 1 Period", min_value=5, max_value=200, value=50, step=5, disabled=not use_sma)
        sma_period_2 = st.number_input("SMA 2 Period", min_value=5, max_value=200, value=200, step=5, disabled=not use_sma)
        ema_period = st.number_input("EMA Period", min_value=5, max_value=100, value=20, step=5, disabled=not use_ema)
    
    # Add a divider
    st.markdown("---")
    
    # Load and display technical analysis chart
    try:
        # Get stock data
        stock_data = get_stock_data(symbol=stock_symbol, period=period, interval=interval)
        
        if stock_data.empty:
            st.warning(f"No data available for {stock_symbol}")
            return
        
        # Create selected indicators list
        selected_indicators = []
        if use_sma:
            selected_indicators.append('sma')
        if use_ema:
            selected_indicators.append('ema')
        if use_bollinger:
            selected_indicators.append('bollinger')
        if use_rsi:
            selected_indicators.append('rsi')
        if use_macd:
            selected_indicators.append('macd')
        if use_stoch:
            selected_indicators.append('stoch')
        if use_atr:
            selected_indicators.append('atr')
        if use_obv:
            selected_indicators.append('obv')
        
        # Create a title for the chart
        chart_title = f"Technical Analysis: {stock_symbol.replace('.NS', '')} - {selected_period} ({selected_interval})"
        
        # Create the technical chart with selected indicators
        fig = create_technical_chart(stock_data, indicators=selected_indicators)
        fig.update_layout(title=chart_title)
        
        # Show chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Technical Analysis Explanation
        with st.expander("Technical Indicator Explanations"):
            st.subheader("Technical Indicators Guide")
            
            st.markdown("### Moving Averages")
            st.markdown("""
            **Simple Moving Average (SMA)**: A calculation that takes the arithmetic mean of a given set of prices over a specific number of days in the past. For example, a 20-day SMA is the average of the closing prices for the past 20 days.
            
            **Exponential Moving Average (EMA)**: Gives more weight to recent prices. The EMA reacts more significantly to recent price changes than a SMA, making it more responsive to new information.
            
            **Usage**: Moving averages help traders identify the direction of the trend. When the price is above a moving average, it generally indicates an uptrend. Crossovers between different moving averages can signal potential buy or sell opportunities.
            """)
            
            st.markdown("### Bollinger Bands")
            st.markdown("""
            Bollinger Bands consist of a middle band (SMA) with two outer bands that are standard deviations away from the middle band.
            
            **Upper Band**: Middle band + (Standard deviation × 2)
            **Lower Band**: Middle band - (Standard deviation × 2)
            
            **Usage**: Bollinger Bands help identify volatility and potential overbought/oversold conditions. When price touches the upper band, it may be overbought; when it touches the lower band, it may be oversold. The bands widen during volatile markets and contract during less volatile periods.
            """)
            
            st.markdown("### Relative Strength Index (RSI)")
            st.markdown("""
            RSI measures the speed and change of price movements, oscillating between 0 and 100.
            
            **RSI Formula**: 100 - (100 / (1 + RS)), where RS = Average Gain / Average Loss
            
            **Usage**: RSI helps identify overbought (above 70) or oversold (below 30) conditions. It can also show divergence, where the price makes a new high or low that isn't confirmed by the RSI, suggesting a potential reversal.
            """)
            
            st.markdown("### Moving Average Convergence Divergence (MACD)")
            st.markdown("""
            MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a security's price.
            
            **MACD Line**: 12-period EMA - 26-period EMA
            **Signal Line**: 9-period EMA of MACD Line
            **Histogram**: MACD Line - Signal Line
            
            **Usage**: The MACD indicator helps identify potential buy/sell signals. When the MACD line crosses above the signal line, it's a bullish signal. When it crosses below, it's bearish. The histogram represents the difference between MACD and signal line; larger bars indicate stronger momentum.
            """)
            
            st.markdown("### Stochastic Oscillator")
            st.markdown("""
            The Stochastic Oscillator is a momentum indicator that shows the location of the close relative to high-low range over a set number of periods.
            
            **%K (Fast Stochastic)**: 100 × ((Current Close - Lowest Low) / (Highest High - Lowest Low))
            **%D (Slow Stochastic)**: 3-period SMA of %K
            
            **Usage**: Readings above 80 indicate overbought conditions, while readings below 20 indicate oversold conditions. %K crossing above %D is a bullish signal, while %K crossing below %D is bearish.
            """)
            
            st.markdown("### Average True Range (ATR)")
            st.markdown("""
            ATR measures market volatility by decomposing the entire range of an asset price for that period.
            
            **True Range**: Max[(High - Low), abs(High - Previous Close), abs(Low - Previous Close)]
            **ATR**: Average of True Range over a specified period
            
            **Usage**: ATR is not directional; it measures volatility regardless of direction. Higher ATR values indicate higher volatility. It's often used to set stop-loss levels or to identify potential breakout opportunities.
            """)
            
            st.markdown("### On Balance Volume (OBV)")
            st.markdown("""
            OBV measures buying and selling pressure as a cumulative indicator that adds volume on up days and subtracts volume on down days.
            
            **Calculation**: If today's close > yesterday's close, then: OBV = Previous OBV + Today's Volume
            If today's close < yesterday's close, then: OBV = Previous OBV - Today's Volume
            
            **Usage**: OBV helps confirm price trends and potential reversals. When OBV rises, it indicates positive volume pressure that can lead to higher prices. When OBV falls, it shows negative volume pressure that can lead to lower prices.
            """)
    
    except Exception as e:
        st.error(f"Error generating technical analysis chart: {e}")
        st.info("Please try another stock or time period")
    
    # Footer
    st.markdown("---")
    st.caption("Technical analysis should not be used in isolation for investment decisions. This tool is for educational purposes only.")
    st.caption("Data sourced from Yahoo Finance via yfinance. For informational purposes only.")
    st.caption("© 2023 Indian Stock Market Analysis Platform")

if __name__ == "__main__":
    main()
