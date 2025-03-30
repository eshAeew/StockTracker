import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_fetcher import get_top_stocks_list, get_stock_info

st.set_page_config(
    page_title="Stock Screener | Indian Stock Market Analysis",
    page_icon="🔍",
    layout="wide"
)

def main():
    st.title("Stock Screener")
    st.write("Find stocks matching specific criteria")
    
    # Define screening criteria
    st.sidebar.header("Screening Criteria")
    
    # Market Cap Range
    st.sidebar.subheader("Market Cap")
    market_cap_options = ["All", "Large Cap (>₹20,000 Cr)", "Mid Cap (₹5,000 - ₹20,000 Cr)", "Small Cap (<₹5,000 Cr)"]
    market_cap_selection = st.sidebar.selectbox("Market Cap Range", market_cap_options)
    
    # P/E Ratio Range
    st.sidebar.subheader("P/E Ratio")
    pe_min, pe_max = st.sidebar.slider("P/E Ratio Range", 0.0, 100.0, (0.0, 50.0))
    
    # Dividend Yield
    st.sidebar.subheader("Dividend Yield")
    div_yield_min = st.sidebar.slider("Minimum Dividend Yield (%)", 0.0, 10.0, 0.0)
    
    # Sectors
    st.sidebar.subheader("Sector")
    sectors = ["All", "IT", "Banking", "Auto", "Pharma", "FMCG", "Energy", "Metals", "Infrastructure"]
    selected_sector = st.sidebar.selectbox("Select Sector", sectors)
    
    # Price Range
    st.sidebar.subheader("Stock Price")
    price_min, price_max = st.sidebar.slider("Price Range (₹)", 0, 5000, (0, 5000))
    
    # 52 Week Performance
    st.sidebar.subheader("52 Week Performance")
    perf_options = ["All", "New 52-Week High", "Near 52-Week High (>90%)", "Near 52-Week Low (<10%)", "New 52-Week Low"]
    perf_selection = st.sidebar.selectbox("Performance vs 52-Week Range", perf_options)
    
    # Additional Technical Criteria
    st.sidebar.subheader("Technical Criteria")
    show_crossover = st.sidebar.checkbox("MA Crossover (20 Day > 50 Day)")
    show_bullish = st.sidebar.checkbox("Bullish MACD")
    show_volume_spike = st.sidebar.checkbox("Volume > 2x Average")
    
    # Search Button
    search_clicked = st.sidebar.button("Screen Stocks", type="primary")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if search_clicked:
            # In a real app, this would query a database or API with the criteria
            # For this example, we'll use a predefined list and filter it
            
            # Get stock list
            stocks_data = get_sample_stocks_data()
            
            # Apply filters
            filtered_stocks = filter_stocks(
                stocks_data, 
                market_cap_selection, 
                (pe_min, pe_max), 
                div_yield_min, 
                selected_sector, 
                (price_min, price_max), 
                perf_selection,
                show_crossover,
                show_bullish,
                show_volume_spike
            )
            
            # Display results
            st.header(f"Screening Results: {len(filtered_stocks)} Stocks Found")
            if not filtered_stocks.empty:
                # Add columns for visual indicators
                filtered_stocks['Trend'] = filtered_stocks['Performance (1M)'].apply(
                    lambda x: "📈" if x > 0 else "📉"
                )
                
                # Format percentage columns
                for col in ['Performance (1M)', 'Performance (3M)', 'Performance (1Y)', 'Dividend Yield']:
                    filtered_stocks[col] = filtered_stocks[col].apply(lambda x: f"{x:.2f}%")
                
                # Format price columns
                for col in ['Current Price', 'Market Cap (Cr)']:
                    filtered_stocks[col] = filtered_stocks[col].apply(lambda x: f"₹{x:,.2f}")
                
                # Display table with pagination
                st.dataframe(
                    filtered_stocks[['Symbol', 'Name', 'Sector', 'Current Price', 'P/E Ratio', 
                                     'Dividend Yield', 'Market Cap (Cr)', 'Trend']], 
                    use_container_width=True
                )
                
                # Plot sector distribution
                sector_counts = filtered_stocks['Sector'].value_counts()
                
                # Create pie chart
                fig = px.pie(
                    values=sector_counts.values,
                    names=sector_counts.index,
                    title="Sector Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.info("No stocks match your criteria. Please adjust your filters.")
                
        else:
            st.info("Use the filters on the sidebar and click 'Screen Stocks' to find matching stocks.")
            
            # Sample distribution info when no search is performed
            st.subheader("About the Stock Screener")
            st.write("""
            This tool allows you to filter stocks based on various financial and technical criteria:
            
            1. **Fundamental Criteria** - Filter by market cap, P/E ratio, dividend yield, sector, and price range
            2. **Technical Criteria** - Find stocks with specific technical patterns like moving average crossovers
            3. **Performance Filters** - Screen stocks based on their performance relative to 52-week highs/lows
            
            Use the sidebar to set your criteria and click "Screen Stocks" to see matching results.
            """)
    
    with col2:
        if search_clicked and not filtered_stocks.empty:
            st.subheader("Stock Selection")
            selected_stock = st.selectbox(
                "Select a stock to view details", 
                filtered_stocks['Symbol'].tolist(),
                format_func=lambda x: f"{x} - {filtered_stocks[filtered_stocks['Symbol'] == x]['Name'].iloc[0]}"
            )
            
            # Show stock details
            if selected_stock:
                st.subheader(f"{selected_stock} Quick Overview")
                
                # Get the selected stock data
                stock_data = filtered_stocks[filtered_stocks['Symbol'] == selected_stock].iloc[0]
                
                # Create metrics
                st.metric("Current Price", stock_data['Current Price'])
                st.metric("P/E Ratio", f"{float(stock_data['P/E Ratio']):.2f}")
                st.metric("Dividend Yield", stock_data['Dividend Yield'])
                st.metric("Market Cap", stock_data['Market Cap (Cr)'])
                
                # Quick performance chart
                st.subheader("Performance Overview")
                
                performance_data = {
                    'Period': ['1 Month', '3 Months', '1 Year'],
                    'Performance (%)': [
                        float(stock_data['Performance (1M)'].replace('%', '')),
                        float(stock_data['Performance (3M)'].replace('%', '')),
                        float(stock_data['Performance (1Y)'].replace('%', ''))
                    ]
                }
                
                perf_df = pd.DataFrame(performance_data)
                
                fig = px.bar(
                    perf_df,
                    x='Period',
                    y='Performance (%)',
                    color='Performance (%)',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    range_color=[-10, 10],
                    title="Performance Comparison"
                )
                
                st.plotly_chart(fig, use_container_width=True)

def get_sample_stocks_data():
    """Get sample stock data for the screener"""
    # In a real app, this would fetch from an API or database
    # For demonstration, we'll create a sample DataFrame
    
    # Generate sample data for demonstration
    np.random.seed(42)  # For reproducible results
    
    symbols = [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR", "SBIN", "BAJFINANCE", 
        "BHARTIARTL", "KOTAKBANK", "ASIANPAINT", "LT", "AXISBANK", "MARUTI", "TITAN",
        "SUNPHARMA", "INDUSINDBK", "ULTRACEMCO", "TATAMOTORS", "JSWSTEEL", "NESTLEIND",
        "BAJAJFINSV", "NTPC", "HCLTECH", "ADANIENT", "WIPRO", "POWERGRID", "TATASTEEL",
        "GRASIM", "TECHM", "HINDALCO", "DIVISLAB", "DLF", "CIPLA", "ADANIPORTS", "HEROMOTOCO",
        "TATACONSUM", "BAJAJ-AUTO", "EICHERMOT", "SHREECEM", "UPL", "APOLLOHOSP", "COALINDIA",
        "ONGC", "BRITANNIA", "ITC", "SBILIFE", "BPCL", "HDFCLIFE", "M&M"
    ]
    
    names = [
        "Reliance Industries", "Tata Consultancy Services", "HDFC Bank", "Infosys", 
        "ICICI Bank", "Hindustan Unilever", "State Bank of India", "Bajaj Finance",
        "Bharti Airtel", "Kotak Mahindra Bank", "Asian Paints", "Larsen & Toubro",
        "Axis Bank", "Maruti Suzuki", "Titan Company", "Sun Pharmaceutical", 
        "IndusInd Bank", "UltraTech Cement", "Tata Motors", "JSW Steel", "Nestle India",
        "Bajaj Finserv", "NTPC", "HCL Technologies", "Adani Enterprises", "Wipro",
        "Power Grid Corporation", "Tata Steel", "Grasim Industries", "Tech Mahindra",
        "Hindalco Industries", "Divi's Laboratories", "DLF", "Cipla", "Adani Ports",
        "Hero MotoCorp", "Tata Consumer Products", "Bajaj Auto", "Eicher Motors",
        "Shree Cement", "UPL", "Apollo Hospitals", "Coal India", "Oil & Natural Gas Corp",
        "Britannia Industries", "ITC", "SBI Life Insurance", "Bharat Petroleum", 
        "HDFC Life Insurance", "Mahindra & Mahindra"
    ]
    
    sectors = [
        "Energy", "IT", "Banking", "IT", "Banking", "FMCG", "Banking", "Financial Services",
        "Telecom", "Banking", "FMCG", "Infrastructure", "Banking", "Auto", "Consumer Goods",
        "Pharma", "Banking", "Cement", "Auto", "Metals", "FMCG", "Financial Services",
        "Energy", "IT", "Infrastructure", "IT", "Energy", "Metals", "Cement", "IT",
        "Metals", "Pharma", "Real Estate", "Pharma", "Infrastructure", "Auto",
        "FMCG", "Auto", "Auto", "Cement", "Chemicals", "Healthcare", "Energy",
        "Energy", "FMCG", "FMCG", "Insurance", "Energy", "Insurance", "Auto"
    ]
    
    # Generate random prices between 100 and 5000
    prices = np.random.uniform(100, 5000, len(symbols))
    
    # Generate P/E ratios (10-50)
    pe_ratios = np.random.uniform(10, 50, len(symbols))
    
    # Generate dividend yields (0-5%)
    div_yields = np.random.uniform(0, 5, len(symbols))
    
    # Generate market caps (1,000 Cr to 1,00,000 Cr)
    market_caps = np.random.uniform(1000, 100000, len(symbols))
    
    # Performance metrics
    perf_1m = np.random.uniform(-10, 15, len(symbols))
    perf_3m = np.random.uniform(-15, 25, len(symbols))
    perf_1y = np.random.uniform(-20, 40, len(symbols))
    
    # Technical indicators (binary for this demonstration)
    ma_crossover = np.random.choice([True, False], len(symbols))
    bullish_macd = np.random.choice([True, False], len(symbols))
    volume_spike = np.random.choice([True, False], len(symbols))
    
    # 52-week data
    week_52_high = prices * np.random.uniform(1.05, 1.3, len(symbols))
    week_52_low = prices * np.random.uniform(0.6, 0.9, len(symbols))
    
    # Create DataFrame
    data = {
        'Symbol': symbols,
        'Name': names,
        'Sector': sectors,
        'Current Price': prices,
        'P/E Ratio': pe_ratios,
        'Dividend Yield': div_yields,
        'Market Cap (Cr)': market_caps,
        'Performance (1M)': perf_1m,
        'Performance (3M)': perf_3m,
        'Performance (1Y)': perf_1y,
        'MA Crossover': ma_crossover,
        'Bullish MACD': bullish_macd,
        'Volume Spike': volume_spike,
        '52W High': week_52_high,
        '52W Low': week_52_low
    }
    
    return pd.DataFrame(data)

def filter_stocks(df, market_cap, pe_range, min_div_yield, sector, price_range, perf_selection, ma_crossover, bullish_macd, volume_spike):
    """Filter stocks based on criteria"""
    filtered_df = df.copy()
    
    # Market Cap filter
    if market_cap == "Large Cap (>₹20,000 Cr)":
        filtered_df = filtered_df[filtered_df['Market Cap (Cr)'] > 20000]
    elif market_cap == "Mid Cap (₹5,000 - ₹20,000 Cr)":
        filtered_df = filtered_df[(filtered_df['Market Cap (Cr)'] >= 5000) & (filtered_df['Market Cap (Cr)'] <= 20000)]
    elif market_cap == "Small Cap (<₹5,000 Cr)":
        filtered_df = filtered_df[filtered_df['Market Cap (Cr)'] < 5000]
    
    # P/E Ratio filter
    pe_min, pe_max = pe_range
    filtered_df = filtered_df[(filtered_df['P/E Ratio'] >= pe_min) & (filtered_df['P/E Ratio'] <= pe_max)]
    
    # Dividend Yield filter
    filtered_df = filtered_df[filtered_df['Dividend Yield'] >= min_div_yield]
    
    # Sector filter
    if sector != "All":
        filtered_df = filtered_df[filtered_df['Sector'] == sector]
    
    # Price Range filter
    price_min, price_max = price_range
    filtered_df = filtered_df[(filtered_df['Current Price'] >= price_min) & (filtered_df['Current Price'] <= price_max)]
    
    # 52 Week Performance filter
    if perf_selection == "New 52-Week High":
        filtered_df = filtered_df[filtered_df['Current Price'] >= filtered_df['52W High'] * 0.995]
    elif perf_selection == "Near 52-Week High (>90%)":
        filtered_df = filtered_df[filtered_df['Current Price'] >= filtered_df['52W High'] * 0.9]
    elif perf_selection == "Near 52-Week Low (<10%)":
        filtered_df = filtered_df[filtered_df['Current Price'] <= filtered_df['52W Low'] * 1.1]
    elif perf_selection == "New 52-Week Low":
        filtered_df = filtered_df[filtered_df['Current Price'] <= filtered_df['52W Low'] * 1.005]
    
    # Technical Criteria filters
    if ma_crossover:
        filtered_df = filtered_df[filtered_df['MA Crossover'] == True]
    
    if bullish_macd:
        filtered_df = filtered_df[filtered_df['Bullish MACD'] == True]
    
    if volume_spike:
        filtered_df = filtered_df[filtered_df['Volume Spike'] == True]
    
    return filtered_df

if __name__ == "__main__":
    main()