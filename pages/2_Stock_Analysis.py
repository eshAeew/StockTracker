import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_fetcher import get_stock_data, get_stock_info, get_top_stocks_list, search_stocks
from utils.chart_utils import create_candlestick_chart

st.set_page_config(
    page_title="Stock Analysis | Indian Stock Market Analysis",
    page_icon="📈",
    layout="wide"
)

def main():
    st.title("Stock Analysis")
    st.write("Analyze individual stocks with interactive charts and key metrics")
    
    # Stock search and selection
    st.header("Select a Stock")
    
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        # Allow searching for stocks
        search_query = st.text_input("Search for a stock (name or symbol)", placeholder="e.g., RELIANCE or TCS")
    
    with search_col2:
        # Period selector
        periods = {
            "1 Week": "5d",
            "1 Month": "1mo", 
            "3 Months": "3mo", 
            "6 Months": "6mo", 
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y"
        }
        selected_period = st.selectbox("Time Period", list(periods.keys()), index=4)
        period = periods[selected_period]
    
    # Get stock data based on search or selection
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
    
    # Add a divider
    st.markdown("---")
    
    # Load and display stock data
    try:
        # Get stock data
        stock_data = get_stock_data(symbol=stock_symbol, period=period)
        
        if stock_data.empty:
            st.warning(f"No data available for {stock_symbol}")
            return
        
        # Get stock info for the header
        stock_info = get_stock_info(stock_symbol)
        
        # Display stock name and current info
        if stock_info:
            company_name = stock_info.get('name', stock_symbol.replace('.NS', ''))
            
            # Calculate price change
            current_price = stock_data['Close'].iloc[-1]
            prev_price = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else current_price
            price_change = current_price - prev_price
            price_change_pct = (price_change / prev_price) * 100 if prev_price > 0 else 0
            
            # Display stock header
            st.header(f"{company_name} ({stock_symbol.replace('.NS', '')})")
            
            # Key metrics in columns
            metric_cols = st.columns(5)
            
            with metric_cols[0]:
                change_icon = "↗" if price_change >= 0 else "↘"
                st.metric(
                    label="Current Price",
                    value=f"₹{current_price:,.2f}",
                    delta=f"{change_icon} {price_change_pct:.2f}%"
                )
            
            with metric_cols[1]:
                # 52-week high
                week_52_high = stock_info.get('52_week_high', 0)
                st.metric(
                    label="52-Week High",
                    value=f"₹{week_52_high:,.2f}"
                )
            
            with metric_cols[2]:
                # 52-week low
                week_52_low = stock_info.get('52_week_low', 0)
                st.metric(
                    label="52-Week Low",
                    value=f"₹{week_52_low:,.2f}"
                )
            
            with metric_cols[3]:
                # PE Ratio
                pe_ratio = stock_info.get('pe_ratio', 0)
                st.metric(
                    label="P/E Ratio",
                    value=f"{pe_ratio:.2f}"
                )
            
            with metric_cols[4]:
                # Market Cap
                market_cap = stock_info.get('market_cap', 0)
                market_cap_formatted = ""
                if market_cap >= 1_000_000_000_000:
                    market_cap_formatted = f"₹{market_cap/1_000_000_000_000:.2f}T"
                elif market_cap >= 1_000_000_000:
                    market_cap_formatted = f"₹{market_cap/1_000_000_000:.2f}B"
                elif market_cap >= 1_000_000:
                    market_cap_formatted = f"₹{market_cap/1_000_000:.2f}M"
                else:
                    market_cap_formatted = f"₹{market_cap:,.2f}"
                
                st.metric(
                    label="Market Cap",
                    value=market_cap_formatted
                )
        else:
            st.header(f"{stock_symbol.replace('.NS', '')}")
        
        # Create chart
        chart_title = f"{stock_symbol.replace('.NS', '')} Stock Price Chart - {selected_period}"
        fig = create_candlestick_chart(stock_data, title=chart_title)
        
        # Show chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional stock details in tabs
        st.subheader("Stock Details")
        tab1, tab2, tab3 = st.tabs(["Overview", "Performance Metrics", "Price History"])
        
        with tab1:
            # Show company overview
            if stock_info:
                overview_cols = st.columns(2)
                
                with overview_cols[0]:
                    st.subheader("Company Information")
                    st.markdown(f"**Sector:** {stock_info.get('sector', 'N/A')}")
                    st.markdown(f"**Industry:** {stock_info.get('industry', 'N/A')}")
                    st.markdown(f"**Dividend Yield:** {stock_info.get('dividend_yield', 0):.2f}%")
                    st.markdown(f"**Book Value:** ₹{stock_info.get('book_value', 0):.2f}")
                
                with overview_cols[1]:
                    st.subheader("Trading Information")
                    st.markdown(f"**Current Price:** ₹{current_price:,.2f}")
                    st.markdown(f"**Day Range:** ₹{stock_data['Low'].iloc[-1]:,.2f} - ₹{stock_data['High'].iloc[-1]:,.2f}")
                    
                    # Calculate 30-day average volume
                    if len(stock_data) >= 30:
                        avg_volume = stock_data['Volume'].tail(30).mean()
                    else:
                        avg_volume = stock_data['Volume'].mean()
                    
                    st.markdown(f"**Avg. Volume (30D):** {avg_volume:,.0f}")
            else:
                st.info("Detailed company information not available")
        
        with tab2:
            # Calculate performance metrics
            if len(stock_data) > 0:
                performance_cols = st.columns(3)
                
                # Calculate returns for different periods
                current_price = stock_data['Close'].iloc[-1]
                
                # 1 week return
                week_1_idx = -5 if len(stock_data) >= 5 else 0
                week_1_price = stock_data['Close'].iloc[week_1_idx] if week_1_idx < 0 else stock_data['Close'].iloc[0]
                week_1_return = ((current_price / week_1_price) - 1) * 100
                
                # 1 month return
                month_1_idx = -20 if len(stock_data) >= 20 else 0
                month_1_price = stock_data['Close'].iloc[month_1_idx] if month_1_idx < 0 else stock_data['Close'].iloc[0]
                month_1_return = ((current_price / month_1_price) - 1) * 100
                
                # 3 month return
                month_3_idx = -60 if len(stock_data) >= 60 else 0
                month_3_price = stock_data['Close'].iloc[month_3_idx] if month_3_idx < 0 else stock_data['Close'].iloc[0]
                month_3_return = ((current_price / month_3_price) - 1) * 100
                
                # 6 month return
                month_6_idx = -120 if len(stock_data) >= 120 else 0
                month_6_price = stock_data['Close'].iloc[month_6_idx] if month_6_idx < 0 else stock_data['Close'].iloc[0]
                month_6_return = ((current_price / month_6_price) - 1) * 100
                
                # 1 year return
                year_1_idx = -240 if len(stock_data) >= 240 else 0
                year_1_price = stock_data['Close'].iloc[year_1_idx] if year_1_idx < 0 else stock_data['Close'].iloc[0]
                year_1_return = ((current_price / year_1_price) - 1) * 100
                
                # Display returns
                with performance_cols[0]:
                    st.subheader("Period Returns")
                    st.markdown(f"**1 Week:** {week_1_return:.2f}%")
                    st.markdown(f"**1 Month:** {month_1_return:.2f}%")
                    st.markdown(f"**3 Months:** {month_3_return:.2f}%")
                    st.markdown(f"**6 Months:** {month_6_return:.2f}%")
                    st.markdown(f"**1 Year:** {year_1_return:.2f}%")
                
                # Calculate volatility
                daily_returns = stock_data['Close'].pct_change().dropna()
                volatility = daily_returns.std() * (252 ** 0.5) * 100  # Annualized volatility
                
                # Calculate max drawdown
                cumulative_returns = (1 + daily_returns).cumprod()
                running_max = cumulative_returns.cummax()
                drawdown = (cumulative_returns / running_max) - 1
                max_drawdown = drawdown.min() * 100
                
                with performance_cols[1]:
                    st.subheader("Risk Metrics")
                    st.markdown(f"**Volatility (Annual):** {volatility:.2f}%")
                    st.markdown(f"**Max Drawdown:** {max_drawdown:.2f}%")
                
                # Calculate additional metrics
                # Daily mean return
                mean_return = daily_returns.mean() * 100
                
                # Positive days ratio
                positive_days = (daily_returns > 0).sum()
                total_days = len(daily_returns)
                positive_days_ratio = (positive_days / total_days) * 100
                
                with performance_cols[2]:
                    st.subheader("Additional Metrics")
                    st.markdown(f"**Mean Daily Return:** {mean_return:.2f}%")
                    st.markdown(f"**Positive Days:** {positive_days_ratio:.2f}%")
            else:
                st.info("Insufficient data to calculate performance metrics")
        
        with tab3:
            # Display price history table
            if not stock_data.empty:
                # Format the data for display
                display_data = stock_data.copy()
                
                # Convert date format
                if 'Date' in display_data.columns:
                    display_data['Date'] = pd.to_datetime(display_data['Date']).dt.strftime('%Y-%m-%d')
                
                # Round price values
                price_columns = ['Open', 'High', 'Low', 'Close']
                for col in price_columns:
                    if col in display_data.columns:
                        display_data[col] = display_data[col].round(2)
                
                # Format volume
                if 'Volume' in display_data.columns:
                    display_data['Volume'] = display_data['Volume'].apply(lambda x: f"{x:,}")
                
                # Add daily change and change percent columns
                if 'Close' in display_data.columns:
                    display_data['Change'] = stock_data['Close'].diff().round(2)
                    display_data['Change%'] = (stock_data['Close'].pct_change() * 100).round(2)
                
                # Reorder columns
                columns_order = ['Date', 'Open', 'High', 'Low', 'Close', 'Change', 'Change%', 'Volume']
                display_data = display_data[[col for col in columns_order if col in display_data.columns]]
                
                # Display the data
                st.dataframe(display_data, use_container_width=True)
            else:
                st.info("No price history data available")
        
    except Exception as e:
        st.error(f"Error loading stock data: {e}")
        st.info("Please try another stock or time period")
    
    # Footer
    st.markdown("---")
    st.caption("Data sourced from Yahoo Finance via yfinance. For informational purposes only.")
    st.caption("© 2023 Indian Stock Market Analysis Platform")

if __name__ == "__main__":
    main()
