import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_fetcher import get_stock_data, get_stock_info, search_stocks
from utils.chart_utils import create_candlestick_chart

st.set_page_config(
    page_title="Watchlists | Indian Stock Market Analysis",
    page_icon="👁️",
    layout="wide"
)

# Initialize session state variables for watchlists
if 'watchlists' not in st.session_state:
    st.session_state.watchlists = {
        "Default": []  # Default watchlist
    }

if 'display_add_stock' not in st.session_state:
    st.session_state.display_add_stock = False

if 'current_watchlist' not in st.session_state:
    st.session_state.current_watchlist = "Default"

if 'watchlist_prices' not in st.session_state:
    st.session_state.watchlist_prices = {}

def toggle_add_stock():
    st.session_state.display_add_stock = not st.session_state.display_add_stock

def add_stock_to_watchlist(symbol, watchlist_name):
    """Add a stock to the selected watchlist"""
    if symbol in st.session_state.watchlists[watchlist_name]:
        st.error(f"{symbol} is already in your {watchlist_name} watchlist")
        return False
    
    st.session_state.watchlists[watchlist_name].append(symbol)
    st.success(f"{symbol} added to {watchlist_name} watchlist")
    return True

def remove_stock_from_watchlist(symbol, watchlist_name):
    """Remove a stock from the selected watchlist"""
    if symbol in st.session_state.watchlists[watchlist_name]:
        st.session_state.watchlists[watchlist_name].remove(symbol)
        # Also remove from prices cache if exists
        if symbol in st.session_state.watchlist_prices:
            del st.session_state.watchlist_prices[symbol]
        st.success(f"{symbol} removed from {watchlist_name} watchlist")
        return True
    return False

def create_new_watchlist(name):
    """Create a new watchlist"""
    if name in st.session_state.watchlists:
        st.error(f"Watchlist '{name}' already exists")
        return False
    
    st.session_state.watchlists[name] = []
    st.session_state.current_watchlist = name
    st.success(f"Created new watchlist: {name}")
    return True

def delete_watchlist(name):
    """Delete a watchlist"""
    if name == "Default":
        st.error("Cannot delete the Default watchlist")
        return False
    
    if name in st.session_state.watchlists:
        del st.session_state.watchlists[name]
        st.session_state.current_watchlist = "Default"
        st.success(f"Deleted watchlist: {name}")
        return True
    return False

def update_watchlist_prices():
    """Update prices for all stocks in all watchlists"""
    all_symbols = set()
    for watchlist in st.session_state.watchlists.values():
        all_symbols.update(watchlist)
    
    updated_prices = {}
    with st.spinner("Updating prices..."):
        for symbol in all_symbols:
            try:
                stock_data = get_stock_data(symbol, period="5d")
                if not stock_data.empty:
                    # Get latest price and daily change
                    current_price = stock_data['Close'].iloc[-1]
                    prev_price = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else current_price
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                    
                    # Get stock info
                    stock_info = get_stock_info(symbol)
                    name = stock_info.get('name', symbol) if stock_info else symbol
                    
                    updated_prices[symbol] = {
                        'name': name,
                        'price': current_price,
                        'change_pct': change_pct,
                        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
            except Exception as e:
                st.warning(f"Could not update {symbol}: {e}")
    
    st.session_state.watchlist_prices = updated_prices
    st.success("Watchlist prices updated")
    return True

def main():
    st.title("Watchlists")
    st.write("Create and manage watchlists to track stocks of interest")
    
    # Sidebar for watchlist management
    st.sidebar.header("Watchlist Management")
    
    # Select watchlist
    st.sidebar.subheader("Select Watchlist")
    selected_watchlist = st.sidebar.selectbox(
        "Choose a watchlist", 
        list(st.session_state.watchlists.keys()),
        index=list(st.session_state.watchlists.keys()).index(st.session_state.current_watchlist)
    )
    
    # Update current watchlist if changed
    if selected_watchlist != st.session_state.current_watchlist:
        st.session_state.current_watchlist = selected_watchlist
    
    # Create new watchlist
    st.sidebar.subheader("Create New Watchlist")
    new_watchlist_name = st.sidebar.text_input("New Watchlist Name")
    if st.sidebar.button("Create Watchlist", disabled=not new_watchlist_name):
        create_new_watchlist(new_watchlist_name)
        st.rerun()
    
    # Delete watchlist
    if st.session_state.current_watchlist != "Default":
        if st.sidebar.button(f"Delete '{st.session_state.current_watchlist}' Watchlist"):
            delete_watchlist(st.session_state.current_watchlist)
            st.rerun()
    
    # Main content area
    st.header(f"{st.session_state.current_watchlist} Watchlist")
    
    # Watchlist actions
    action_col1, action_col2 = st.columns(2)
    
    with action_col1:
        if st.button("Add Stock", use_container_width=True):
            toggle_add_stock()
    
    with action_col2:
        if st.button("Update Prices", use_container_width=True):
            update_watchlist_prices()
    
    # Add stock form
    if st.session_state.display_add_stock:
        st.subheader("Add Stock to Watchlist")
        
        # Stock search
        search_query = st.text_input("Search for a stock", placeholder="e.g., RELIANCE or TCS", key="watchlist_search")
        
        selected_symbol = None
        
        if search_query:
            try:
                search_results = search_stocks(search_query)
                if search_results:
                    # Show search results as radio buttons
                    search_options = [f"{name} ({symbol})" for symbol, name in search_results]
                    selected_option = st.radio("Select a stock", search_options, key="watchlist_search_results")
                    
                    # Extract symbol from selected option
                    selected_idx = search_options.index(selected_option)
                    selected_symbol = search_results[selected_idx][0]
                    
                    # Add button
                    if st.button("Add to Watchlist", use_container_width=True, disabled=not selected_symbol):
                        if add_stock_to_watchlist(selected_symbol, st.session_state.current_watchlist):
                            st.session_state.display_add_stock = False
                            st.rerun()
                else:
                    st.warning(f"No stocks found matching '{search_query}'")
            except Exception as e:
                st.error(f"Error searching for stocks: {e}")
    
    # Display current watchlist
    current_stocks = st.session_state.watchlists[st.session_state.current_watchlist]
    
    if current_stocks:
        # Update prices or use cached values
        watchlist_data = []
        
        for symbol in current_stocks:
            if symbol in st.session_state.watchlist_prices:
                # Use cached data
                stock_data = st.session_state.watchlist_prices[symbol]
                watchlist_data.append({
                    'Symbol': symbol,
                    'Name': stock_data['name'],
                    'Price': stock_data['price'],
                    'Change (%)': stock_data['change_pct'],
                    'Last Updated': stock_data['last_updated']
                })
            else:
                # If no cached data, just add the symbol
                watchlist_data.append({
                    'Symbol': symbol,
                    'Name': symbol,
                    'Price': None,
                    'Change (%)': None,
                    'Last Updated': None
                })
        
        # Create DataFrame
        watchlist_df = pd.DataFrame(watchlist_data)
        
        # Format values
        display_watchlist = watchlist_df.copy()
        
        # Apply conditional formatting
        if not display_watchlist.empty and 'Change (%)' in display_watchlist.columns:
            display_watchlist['Status'] = display_watchlist['Change (%)'].apply(
                lambda x: '📈' if x is not None and x > 0 else ('📉' if x is not None and x < 0 else '—')
            )
            
            # Format numeric columns
            if 'Price' in display_watchlist.columns:
                display_watchlist['Price'] = display_watchlist['Price'].apply(
                    lambda x: f"₹{x:,.2f}" if x is not None else "—"
                )
            
            if 'Change (%)' in display_watchlist.columns:
                display_watchlist['Change (%)'] = display_watchlist['Change (%)'].apply(
                    lambda x: f"{x:+.2f}%" if x is not None else "—"
                )
        
        # Display the watchlist
        st.dataframe(
            display_watchlist, 
            use_container_width=True,
            column_config={
                "Symbol": st.column_config.TextColumn("Symbol"),
                "Name": st.column_config.TextColumn("Name"),
                "Price": st.column_config.TextColumn("Price"),
                "Change (%)": st.column_config.TextColumn("Change (%)"),
                "Status": st.column_config.TextColumn("Status"),
                "Last Updated": st.column_config.TextColumn("Last Updated")
            }
        )
        
        # Stock analysis section
        st.header("Stock Analysis")
        
        # Allow user to select a stock for detailed view
        selected_analysis_stock = st.selectbox(
            "Select a stock to analyze",
            current_stocks,
            format_func=lambda s: f"{s} - {st.session_state.watchlist_prices.get(s, {}).get('name', s) if s in st.session_state.watchlist_prices else s}"
        )
        
        if selected_analysis_stock:
            analysis_period_options = {
                "1 Week": "1wk",
                "1 Month": "1mo", 
                "3 Months": "3mo", 
                "6 Months": "6mo", 
                "1 Year": "1y",
                "2 Years": "2y"
            }
            
            analysis_col1, analysis_col2 = st.columns(2)
            
            with analysis_col1:
                analysis_period = st.selectbox("Select Period", list(analysis_period_options.keys()), index=2)
            
            with analysis_col2:
                chart_type = st.selectbox("Chart Type", ["Candlestick", "Line"])
            
            period_code = analysis_period_options[analysis_period]
            
            try:
                # Get stock data
                stock_data = get_stock_data(selected_analysis_stock, period=period_code, interval="1d")
                
                if not stock_data.empty:
                    # Create chart
                    if chart_type == "Candlestick":
                        fig = create_candlestick_chart(stock_data, title=f"{selected_analysis_stock} - {analysis_period}")
                    else:
                        fig = go.Figure()
                        fig.add_trace(
                            go.Scatter(
                                x=stock_data['Date'],
                                y=stock_data['Close'],
                                mode='lines',
                                name='Close Price',
                                line=dict(color='#1E88E5', width=2)
                            )
                        )
                        
                        fig.update_layout(
                            title=f"{selected_analysis_stock} - {analysis_period}",
                            xaxis_title="Date",
                            yaxis_title="Price (₹)",
                            height=500,
                            plot_bgcolor='rgba(0,0,0,0)'
                        )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Key statistics
                    st.subheader("Key Statistics")
                    
                    # Calculate statistics
                    current_price = stock_data['Close'].iloc[-1]
                    change_1d = ((stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]) / stock_data['Close'].iloc[-2]) * 100 if len(stock_data) > 1 else 0
                    high_52w = stock_data['High'].max()
                    low_52w = stock_data['Low'].min()
                    
                    # Current price relative to 52-week range (0-100%)
                    range_position = ((current_price - low_52w) / (high_52w - low_52w)) * 100 if (high_52w - low_52w) > 0 else 50
                    
                    # Volatility (standard deviation of daily returns)
                    daily_returns = stock_data['Close'].pct_change().dropna()
                    volatility = daily_returns.std() * (252 ** 0.5) * 100  # Annualized volatility
                    
                    # Display statistics in columns
                    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                    
                    with stat_col1:
                        st.metric(
                            label="Current Price",
                            value=f"₹{current_price:,.2f}",
                            delta=f"{change_1d:+.2f}%"
                        )
                    
                    with stat_col2:
                        st.metric(
                            label="52-Week High",
                            value=f"₹{high_52w:,.2f}"
                        )
                    
                    with stat_col3:
                        st.metric(
                            label="52-Week Low",
                            value=f"₹{low_52w:,.2f}"
                        )
                    
                    with stat_col4:
                        st.metric(
                            label="Volatility (Annualized)",
                            value=f"{volatility:.2f}%"
                        )
                    
                    # Create a 52-week range visualization
                    st.subheader("52-Week Range")
                    
                    # Create a horizontal bar chart representing the 52-week range
                    fig = go.Figure()
                    
                    # Add range bar
                    fig.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=range_position,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "Position in 52-Week Range"},
                            gauge={
                                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                                'bar': {'color': "darkblue"},
                                'bgcolor': "white",
                                'borderwidth': 2,
                                'bordercolor': "gray",
                                'steps': [
                                    {'range': [0, 25], 'color': '#ffcdd2'},
                                    {'range': [25, 75], 'color': '#fff9c4'},
                                    {'range': [75, 100], 'color': '#c8e6c9'}
                                ],
                            }
                        )
                    )
                    
                    fig.update_layout(
                        height=200,
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Simple moving averages
                    st.subheader("Moving Averages")
                    
                    # Calculate moving averages
                    stock_data['MA_50'] = stock_data['Close'].rolling(window=50).mean()
                    stock_data['MA_200'] = stock_data['Close'].rolling(window=200).mean()
                    
                    # Create chart
                    fig = go.Figure()
                    
                    fig.add_trace(
                        go.Scatter(
                            x=stock_data['Date'],
                            y=stock_data['Close'],
                            mode='lines',
                            name='Price',
                            line=dict(color='#1E88E5', width=2)
                        )
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=stock_data['Date'],
                            y=stock_data['MA_50'],
                            mode='lines',
                            name='50-Day MA',
                            line=dict(color='#43A047', width=1.5)
                        )
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=stock_data['Date'],
                            y=stock_data['MA_200'],
                            mode='lines',
                            name='200-Day MA',
                            line=dict(color='#E53935', width=1.5)
                        )
                    )
                    
                    fig.update_layout(
                        title="Price with Moving Averages",
                        xaxis_title="Date",
                        yaxis_title="Price (₹)",
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Provide technical analysis insights
                    latest_close = stock_data['Close'].iloc[-1]
                    latest_ma50 = stock_data['MA_50'].iloc[-1]
                    latest_ma200 = stock_data['MA_200'].iloc[-1]
                    
                    ma_insights = []
                    
                    if latest_close > latest_ma50:
                        ma_insights.append("Price is above 50-day MA, suggesting short-term bullish trend")
                    else:
                        ma_insights.append("Price is below 50-day MA, suggesting short-term bearish trend")
                    
                    if latest_close > latest_ma200:
                        ma_insights.append("Price is above 200-day MA, suggesting long-term bullish trend")
                    else:
                        ma_insights.append("Price is below 200-day MA, suggesting long-term bearish trend")
                    
                    if latest_ma50 > latest_ma200:
                        ma_insights.append("50-day MA is above 200-day MA (Golden Cross), suggesting bullish momentum")
                    else:
                        ma_insights.append("50-day MA is below 200-day MA (Death Cross), suggesting bearish momentum")
                    
                    # Display insights
                    st.subheader("Technical Insights")
                    for insight in ma_insights:
                        st.markdown(f"- {insight}")
                else:
                    st.warning(f"No data available for {selected_analysis_stock}")
            except Exception as e:
                st.error(f"Error analyzing stock: {e}")
            
            # Add button to remove stock from watchlist
            if st.button(f"Remove {selected_analysis_stock} from Watchlist", use_container_width=True):
                if remove_stock_from_watchlist(selected_analysis_stock, st.session_state.current_watchlist):
                    st.rerun()
    else:
        st.info(f"Your {st.session_state.current_watchlist} watchlist is empty. Add stocks to track them.")
    
    # Footer
    st.markdown("---")
    st.caption("© 2023 Indian Stock Market Analysis Platform. Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()