import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_fetcher import get_stock_data, get_stock_info, get_top_stocks_list, search_stocks, get_financial_ratios
from utils.chart_utils import create_line_chart, create_pie_chart, create_candlestick_chart
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Portfolio Tracker | Indian Stock Market Analysis",
    page_icon="💼",
    layout="wide"
)

# Initialize session state variables
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=['Symbol', 'Name', 'Quantity', 'Buy Price', 'Buy Date', 'Current Price', 'Current Value', 'Gain/Loss', 'Gain/Loss %'])

if 'display_add_stock' not in st.session_state:
    st.session_state.display_add_stock = False

def toggle_add_stock():
    st.session_state.display_add_stock = not st.session_state.display_add_stock

def add_stock_to_portfolio(symbol, name, quantity, buy_price, buy_date):
    """Add a stock to the portfolio"""
    try:
        # Validate inputs
        if not symbol or not name or not quantity or not buy_price or not buy_date:
            st.error("All fields are required")
            return False
        
        # Check if stock already exists in portfolio
        if symbol in st.session_state.portfolio['Symbol'].values:
            st.error(f"{symbol} is already in your portfolio. Please use edit function instead.")
            return False
        
        # Get current stock data
        stock_data = get_stock_data(symbol, period="5d")
        if stock_data.empty:
            st.error(f"Could not fetch data for {symbol}")
            return False
        
        current_price = stock_data['Close'].iloc[-1]
        current_value = quantity * current_price
        gain_loss = current_value - (quantity * buy_price)
        gain_loss_pct = (gain_loss / (quantity * buy_price)) * 100
        
        # Create new row
        new_stock = pd.DataFrame({
            'Symbol': [symbol],
            'Name': [name],
            'Quantity': [quantity],
            'Buy Price': [buy_price],
            'Buy Date': [buy_date],
            'Current Price': [current_price],
            'Current Value': [current_value],
            'Gain/Loss': [gain_loss],
            'Gain/Loss %': [gain_loss_pct]
        })
        
        # Add to portfolio
        st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_stock], ignore_index=True)
        st.success(f"{symbol} added to portfolio")
        st.session_state.display_add_stock = False
        return True
    
    except Exception as e:
        st.error(f"Error adding stock: {e}")
        return False

def remove_stock(symbol):
    """Remove a stock from the portfolio"""
    st.session_state.portfolio = st.session_state.portfolio[st.session_state.portfolio['Symbol'] != symbol]
    st.success(f"{symbol} removed from portfolio")

def update_portfolio_prices():
    """Update current prices for all stocks in the portfolio"""
    updated_portfolio = st.session_state.portfolio.copy()
    
    for idx, row in st.session_state.portfolio.iterrows():
        try:
            # Get current stock data
            stock_data = get_stock_data(row['Symbol'], period="5d")
            if not stock_data.empty:
                current_price = stock_data['Close'].iloc[-1]
                current_value = row['Quantity'] * current_price
                gain_loss = current_value - (row['Quantity'] * row['Buy Price'])
                gain_loss_pct = (gain_loss / (row['Quantity'] * row['Buy Price'])) * 100
                
                # Update the values
                updated_portfolio.at[idx, 'Current Price'] = current_price
                updated_portfolio.at[idx, 'Current Value'] = current_value
                updated_portfolio.at[idx, 'Gain/Loss'] = gain_loss
                updated_portfolio.at[idx, 'Gain/Loss %'] = gain_loss_pct
        except Exception as e:
            st.warning(f"Could not update {row['Symbol']}: {e}")
    
    st.session_state.portfolio = updated_portfolio
    st.success("Portfolio prices updated")

def get_portfolio_summary():
    """Calculate summary statistics for the portfolio"""
    if st.session_state.portfolio.empty:
        return {
            'total_value': 0,
            'total_invested': 0,
            'total_gain_loss': 0,
            'total_gain_loss_pct': 0,
            'best_performer': {'symbol': None, 'gain_pct': 0},
            'worst_performer': {'symbol': None, 'gain_pct': 0}
        }
    
    # Calculate total portfolio values
    total_value = st.session_state.portfolio['Current Value'].sum()
    total_invested = (st.session_state.portfolio['Quantity'] * st.session_state.portfolio['Buy Price']).sum()
    total_gain_loss = total_value - total_invested
    total_gain_loss_pct = (total_gain_loss / total_invested) * 100 if total_invested > 0 else 0
    
    # Find best and worst performers
    best_idx = st.session_state.portfolio['Gain/Loss %'].idxmax() if len(st.session_state.portfolio) > 0 else None
    worst_idx = st.session_state.portfolio['Gain/Loss %'].idxmin() if len(st.session_state.portfolio) > 0 else None
    
    best_performer = {
        'symbol': st.session_state.portfolio.loc[best_idx, 'Symbol'] if best_idx is not None else None,
        'gain_pct': st.session_state.portfolio.loc[best_idx, 'Gain/Loss %'] if best_idx is not None else 0
    }
    
    worst_performer = {
        'symbol': st.session_state.portfolio.loc[worst_idx, 'Symbol'] if worst_idx is not None else None,
        'gain_pct': st.session_state.portfolio.loc[worst_idx, 'Gain/Loss %'] if worst_idx is not None else 0
    }
    
    return {
        'total_value': total_value,
        'total_invested': total_invested,
        'total_gain_loss': total_gain_loss,
        'total_gain_loss_pct': total_gain_loss_pct,
        'best_performer': best_performer,
        'worst_performer': worst_performer
    }

def main():
    st.title("Portfolio Tracker")
    st.write("Track and analyze your investment portfolio")
    
    # Portfolio summary section
    st.header("Portfolio Summary")
    
    # Get portfolio summary
    summary = get_portfolio_summary()
    
    # Create summary metrics
    if not st.session_state.portfolio.empty:
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            st.metric(
                label="Total Portfolio Value",
                value=f"₹{summary['total_value']:,.2f}"
            )
        
        with metrics_col2:
            st.metric(
                label="Total Invested",
                value=f"₹{summary['total_invested']:,.2f}"
            )
        
        with metrics_col3:
            # Format with up/down arrow
            gain_loss_icon = "↗" if summary['total_gain_loss'] >= 0 else "↘"
            gain_loss_color = "green" if summary['total_gain_loss'] >= 0 else "red"
            
            st.metric(
                label="Total Gain/Loss",
                value=f"₹{summary['total_gain_loss']:,.2f}",
                delta=f"{gain_loss_icon} {summary['total_gain_loss_pct']:.2f}%"
            )
        
        with metrics_col4:
            if summary['best_performer']['symbol']:
                st.metric(
                    label="Best Performer",
                    value=f"{summary['best_performer']['symbol']}",
                    delta=f"↗ {summary['best_performer']['gain_pct']:.2f}%"
                )
            else:
                st.metric(label="Best Performer", value="N/A")
        
        # Portfolio visualization
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            # Create allocation pie chart if portfolio is not empty
            if not st.session_state.portfolio.empty:
                # Create data for pie chart
                pie_data = st.session_state.portfolio[['Symbol', 'Current Value']].copy()
                
                # Create pie chart
                fig = create_pie_chart(
                    values=pie_data['Current Value'],
                    labels=pie_data['Symbol'],
                    title="Portfolio Allocation"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Add stocks to view portfolio allocation")
        
        with viz_col2:
            # Create performance comparison chart
            if not st.session_state.portfolio.empty and len(st.session_state.portfolio) > 1:
                # Create a bar chart for individual stock performance
                performance_data = st.session_state.portfolio[['Symbol', 'Gain/Loss %']].copy()
                
                # Sort by performance
                performance_data = performance_data.sort_values('Gain/Loss %', ascending=False)
                
                # Create bar colors based on gain/loss
                colors = ['#43A047' if x >= 0 else '#E53935' for x in performance_data['Gain/Loss %']]
                
                # Create bar chart
                fig = go.Figure()
                
                fig.add_trace(
                    go.Bar(
                        x=performance_data['Symbol'],
                        y=performance_data['Gain/Loss %'],
                        marker_color=colors,
                        text=performance_data['Gain/Loss %'].apply(lambda x: f"{x:.2f}%"),
                        textposition='auto'
                    )
                )
                
                fig.update_layout(
                    title="Stock Performance Comparison",
                    xaxis_title="Stock",
                    yaxis_title="Gain/Loss %",
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                # Add horizontal reference line at 0
                fig.add_shape(
                    type="line",
                    x0=-0.5,
                    y0=0,
                    x1=len(performance_data) - 0.5,
                    y1=0,
                    line=dict(
                        color="rgba(0, 0, 0, 0.3)",
                        width=1,
                        dash="dash"
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Add multiple stocks to view performance comparison")
    else:
        st.info("Your portfolio is empty. Add stocks to see summary information.")
    
    # Portfolio management section
    st.header("Portfolio Management")
    
    # Portfolio actions
    action_col1, action_col2, action_col3 = st.columns([1, 1, 2])
    
    with action_col1:
        if st.button("Add Stock", use_container_width=True):
            toggle_add_stock()
    
    with action_col2:
        if st.button("Update Prices", use_container_width=True, disabled=st.session_state.portfolio.empty):
            update_portfolio_prices()
    
    # Add stock form
    if st.session_state.display_add_stock:
        st.subheader("Add Stock to Portfolio")
        
        add_form_col1, add_form_col2 = st.columns(2)
        
        with add_form_col1:
            # Stock search
            search_query = st.text_input("Search for a stock", placeholder="e.g., RELIANCE or TCS", key="add_stock_search")
            
            selected_symbol = None
            selected_name = None
            
            if search_query:
                try:
                    search_results = search_stocks(search_query)
                    if search_results:
                        # Show search results as radio buttons
                        search_options = [f"{name} ({symbol})" for symbol, name in search_results]
                        selected_option = st.radio("Select a stock", search_options, key="search_results_radio")
                        
                        # Extract symbol and name from selected option
                        selected_idx = search_options.index(selected_option)
                        selected_symbol = search_results[selected_idx][0]
                        selected_name = search_results[selected_idx][1]
                    else:
                        st.warning(f"No stocks found matching '{search_query}'")
                except Exception as e:
                    st.error(f"Error searching for stocks: {e}")
        
        with add_form_col2:
            # Stock details input
            quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
            buy_price = st.number_input("Buy Price (₹)", min_value=0.01, step=0.01, value=100.00)
            buy_date = st.date_input("Buy Date", max_value=datetime.now().date())
            
            # Add button
            if st.button("Add to Portfolio", use_container_width=True, disabled=not selected_symbol):
                if add_stock_to_portfolio(selected_symbol, selected_name, quantity, buy_price, buy_date.strftime('%Y-%m-%d')):
                    st.rerun()
    
    # Current portfolio
    st.subheader("Current Holdings")
    
    if not st.session_state.portfolio.empty:
        # Format portfolio data for display
        display_portfolio = st.session_state.portfolio.copy()
        
        # Format currency values
        currency_cols = ['Buy Price', 'Current Price', 'Current Value', 'Gain/Loss']
        for col in currency_cols:
            display_portfolio[col] = display_portfolio[col].apply(lambda x: f"₹{x:,.2f}")
        
        # Format percentage values
        display_portfolio['Gain/Loss %'] = display_portfolio['Gain/Loss %'].apply(lambda x: f"{x:.2f}%")
        
        # Create styled dataframe
        st.dataframe(
            display_portfolio, 
            use_container_width=True,
            column_config={
                "Symbol": st.column_config.TextColumn("Symbol"),
                "Name": st.column_config.TextColumn("Company Name"),
                "Quantity": st.column_config.NumberColumn("Quantity"),
                "Buy Price": st.column_config.TextColumn("Buy Price"),
                "Buy Date": st.column_config.DateColumn("Buy Date"),
                "Current Price": st.column_config.TextColumn("Current Price"),
                "Current Value": st.column_config.TextColumn("Current Value"),
                "Gain/Loss": st.column_config.TextColumn("Gain/Loss"),
                "Gain/Loss %": st.column_config.TextColumn("Gain/Loss %")
            }
        )
        
        # Add remove buttons for each stock
        st.subheader("Remove Stocks")
        
        remove_cols = st.columns(5)  # 5 buttons per row
        
        for i, (idx, row) in enumerate(st.session_state.portfolio.iterrows()):
            col_idx = i % 5
            with remove_cols[col_idx]:
                if st.button(f"Remove {row['Symbol']}", key=f"remove_{row['Symbol']}"):
                    remove_stock(row['Symbol'])
                    st.rerun()
    else:
        st.info("Your portfolio is empty. Add stocks to track your investments.")
    
    # Portfolio analysis section
    if not st.session_state.portfolio.empty:
        st.header("Portfolio Analysis")
        
        # Historical performance
        st.subheader("Historical Performance")
        
        # Time period selector
        period_options = {
            "1 Month": "1mo", 
            "3 Months": "3mo", 
            "6 Months": "6mo", 
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y"
        }
        selected_period = st.selectbox("Select Time Period", list(period_options.keys()), index=2)
        period = period_options[selected_period]
        
        try:
            # Fetch historical data for each stock
            portfolio_history = {}
            
            with st.spinner("Fetching historical data..."):
                for idx, row in st.session_state.portfolio.iterrows():
                    symbol = row['Symbol']
                    stock_data = get_stock_data(symbol, period=period)
                    
                    if not stock_data.empty:
                        # Calculate weighted price based on quantity
                        portfolio_history[symbol] = stock_data[['Date', 'Close']].copy()
                        portfolio_history[symbol]['Weighted'] = portfolio_history[symbol]['Close'] * row['Quantity']
            
            if portfolio_history:
                # Combine all histories
                combined_history = None
                
                for symbol, data in portfolio_history.items():
                    if combined_history is None:
                        combined_history = data[['Date', 'Weighted']].rename(columns={'Weighted': symbol})
                    else:
                        combined_history = pd.merge(
                            combined_history,
                            data[['Date', 'Weighted']].rename(columns={'Weighted': symbol}),
                            on='Date',
                            how='outer'
                        )
                
                # Fill NaN values (for stocks that might not have data for some dates)
                combined_history = combined_history.fillna(method='ffill').fillna(method='bfill')
                
                # Calculate portfolio value for each date
                combined_history['Portfolio Value'] = combined_history.drop('Date', axis=1).sum(axis=1)
                
                # Create portfolio performance chart
                fig = go.Figure()
                
                fig.add_trace(
                    go.Scatter(
                        x=combined_history['Date'],
                        y=combined_history['Portfolio Value'],
                        name='Portfolio Value',
                        line=dict(color='#1E88E5', width=2)
                    )
                )
                
                fig.update_layout(
                    title=f"Portfolio Value Over Time ({selected_period})",
                    xaxis_title="Date",
                    yaxis_title="Value (₹)",
                    height=500,
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate and display key metrics
                if len(combined_history) > 1:
                    current_value = combined_history['Portfolio Value'].iloc[-1]
                    start_value = combined_history['Portfolio Value'].iloc[0]
                    total_return = ((current_value / start_value) - 1) * 100
                    
                    # Calculate annualized return
                    days = (combined_history['Date'].iloc[-1] - combined_history['Date'].iloc[0]).days
                    if days > 0:
                        annual_return = ((1 + total_return/100)**(365/days) - 1) * 100
                    else:
                        annual_return = 0
                    
                    # Calculate volatility
                    daily_returns = combined_history['Portfolio Value'].pct_change().dropna()
                    volatility = daily_returns.std() * (252 ** 0.5) * 100  # Annualized volatility
                    
                    # Display metrics
                    perf_col1, perf_col2, perf_col3 = st.columns(3)
                    
                    with perf_col1:
                        st.metric(
                            label=f"Total Return ({selected_period})",
                            value=f"{total_return:.2f}%"
                        )
                    
                    with perf_col2:
                        st.metric(
                            label="Annualized Return",
                            value=f"{annual_return:.2f}%"
                        )
                    
                    with perf_col3:
                        st.metric(
                            label="Annualized Volatility",
                            value=f"{volatility:.2f}%"
                        )
            else:
                st.info("Could not fetch historical data for your portfolio stocks")
        
        except Exception as e:
            st.error(f"Error analyzing portfolio history: {e}")
        
        # Sector allocation
        st.subheader("Sector Allocation")
        
        try:
            # Get sector information for each stock
            sectors = {}
            
            for idx, row in st.session_state.portfolio.iterrows():
                symbol = row['Symbol']
                current_value = row['Current Value']
                
                # Get stock info to extract sector
                stock_info = get_stock_info(symbol)
                
                if stock_info and 'sector' in stock_info:
                    sector = stock_info['sector']
                    
                    if sector in sectors:
                        sectors[sector] += current_value
                    else:
                        sectors[sector] = current_value
                else:
                    # If sector information is not available
                    if 'Unknown' in sectors:
                        sectors['Unknown'] += current_value
                    else:
                        sectors['Unknown'] = current_value
            
            if sectors:
                sector_col1, sector_col2 = st.columns(2)
                
                with sector_col1:
                    # Create pie chart
                    fig = create_pie_chart(
                        values=list(sectors.values()),
                        labels=list(sectors.keys()),
                        title="Portfolio Sector Allocation"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with sector_col2:
                    # Create sector breakdown table
                    sector_df = pd.DataFrame({
                        'Sector': list(sectors.keys()),
                        'Value': list(sectors.values()),
                        'Allocation (%)': [value/sum(sectors.values())*100 for value in sectors.values()]
                    })
                    
                    # Sort by allocation
                    sector_df = sector_df.sort_values('Allocation (%)', ascending=False)
                    
                    # Format values
                    sector_df['Value'] = sector_df['Value'].apply(lambda x: f"₹{x:,.2f}")
                    sector_df['Allocation (%)'] = sector_df['Allocation (%)'].apply(lambda x: f"{x:.2f}%")
                    
                    st.dataframe(sector_df, use_container_width=True)
                    
                    # Diversification score
                    # A simple way to measure diversification: higher is more diversified
                    # Uses a normalized Herfindahl-Hirschman Index
                    sector_values = np.array(list(sectors.values()))
                    sector_weights = sector_values / np.sum(sector_values)
                    hhi = np.sum(sector_weights ** 2)
                    
                    # Convert to a 0-100 diversification score (100 is perfectly diversified)
                    n = len(sectors)
                    diversification_score = 100 * (1 - (hhi - 1/n) / (1 - 1/n)) if n > 1 else 0
                    
                    st.metric(
                        label="Sector Diversification Score",
                        value=f"{diversification_score:.1f}/100",
                        help="Higher values indicate better sector diversification. Above 70 is generally considered well-diversified."
                    )
            else:
                st.info("Could not determine sector allocation for your portfolio")
        
        except Exception as e:
            st.error(f"Error analyzing sector allocation: {e}")
    
    # Footer
    st.markdown("---")
    st.caption("This is a simulation tool for educational purposes. No real money is invested.")
    st.caption("© 2023 Indian Stock Market Analysis Platform")

if __name__ == "__main__":
    main()
