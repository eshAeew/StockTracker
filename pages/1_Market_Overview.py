import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_fetcher import get_nifty_data, get_sensex_data, get_top_gainers_losers, get_market_indices, get_sector_performance

st.set_page_config(
    page_title="Market Overview | Indian Stock Market Analysis",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("Market Overview")
    st.write("Get a comprehensive view of the Indian stock market performance")
    
    # Market metrics at a glance
    st.header("Market at a Glance")
    
    try:
        # Fetch market data
        nifty_data = get_nifty_data()
        sensex_data = get_sensex_data()
        
        # Create market overview cards
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            nifty_change_color = "green" if nifty_data['change_pct'] > 0 else "red"
            nifty_change_icon = "↗" if nifty_data['change_pct'] > 0 else "↘"
            st.metric(
                label="NIFTY 50", 
                value=f"₹{nifty_data['last_price']:,.2f}",
                delta=f"{nifty_change_icon} {nifty_data['change_pct']:.2f}%"
            )
            
        with metrics_col2:
            sensex_change_color = "green" if sensex_data['change_pct'] > 0 else "red"
            sensex_change_icon = "↗" if sensex_data['change_pct'] > 0 else "↘"
            st.metric(
                label="BSE SENSEX", 
                value=f"₹{sensex_data['last_price']:,.2f}",
                delta=f"{sensex_change_icon} {sensex_data['change_pct']:.2f}%"
            )
            
        with metrics_col3:
            # Add NIFTY Bank (dummy data as fallback)
            bank_nifty_value = 44250.75
            bank_nifty_change = 0.45
            st.metric(
                label="NIFTY BANK", 
                value=f"₹{bank_nifty_value:,.2f}",
                delta=f"↗ {bank_nifty_change:.2f}%"
            )
            
        with metrics_col4:
            # Add India VIX (dummy data as fallback)
            india_vix_value = 13.85
            india_vix_change = -2.25
            st.metric(
                label="INDIA VIX", 
                value=f"{india_vix_value:.2f}",
                delta=f"↘ {india_vix_change:.2f}%"
            )
    except Exception as e:
        st.error(f"Error fetching market metrics: {e}")
        # Fallback placeholder for market indices
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        with metrics_col1:
            st.metric(label="NIFTY 50", value="₹19,675.45", delta="0.32%")
        with metrics_col2:
            st.metric(label="BSE SENSEX", value="₹65,928.53", delta="0.40%")
        with metrics_col3:
            st.metric(label="NIFTY BANK", value="₹44,250.75", delta="0.45%")
        with metrics_col4:
            st.metric(label="INDIA VIX", value="13.85", delta="-2.25%")
    
    # Market indices performance
    st.header("Market Indices Performance")
    
    # Time period selector
    period_options = {
        "7 Days": 7,
        "30 Days": 30,
        "90 Days": 90,
        "6 Months": 180,
        "1 Year": 365
    }
    selected_period = st.selectbox("Select Time Period", list(period_options.keys()), index=1)
    days = period_options[selected_period]
    
    try:
        # Fetch index data for plotting
        indices_data = get_market_indices(days=days)
        
        # Normalize data to 100 at the beginning for better comparison
        normalized_data = pd.DataFrame({'Date': indices_data['Date']})
        
        for col in indices_data.columns:
            if col != 'Date':
                first_value = indices_data[col].iloc[0]
                normalized_data[col] = (indices_data[col] / first_value) * 100
        
        # Plot the data
        fig = px.line(
            normalized_data, 
            x='Date', 
            y=['NIFTY50', 'BANKNIFTY', 'FINNIFTY'], 
            title=f'Major Indices Performance ({selected_period})',
            labels={'value': 'Normalized Value (Base 100)', 'variable': 'Index'},
            color_discrete_map={
                'NIFTY50': '#1E88E5',
                'BANKNIFTY': '#43A047',
                'FINNIFTY': '#E53935'
            }
        )
        
        fig.update_layout(
            legend_title_text='Index',
            xaxis_title='Date',
            yaxis_title='Normalized Value (Base 100)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching index data: {e}")
        st.info("Unable to load market indices performance chart. Please try again later.")
    
    # Top gainers and losers
    st.header("Top Movers")
    
    try:
        # Fetch top gainers and losers
        top_gainers, top_losers = get_top_gainers_losers(count=5)
        
        movers_col1, movers_col2 = st.columns(2)
        
        with movers_col1:
            st.subheader("Top Gainers")
            if not top_gainers.empty:
                st.dataframe(top_gainers, use_container_width=True)
            else:
                st.info("No data available for top gainers")
            
        with movers_col2:
            st.subheader("Top Losers")
            if not top_losers.empty:
                st.dataframe(top_losers, use_container_width=True)
            else:
                st.info("No data available for top losers")
    except Exception as e:
        st.error(f"Error fetching top movers: {e}")
        st.info("Unable to load top gainers and losers. Please try again later.")
    
    # Sector performance
    st.header("Sector Performance")
    
    try:
        # Fetch sector performance data
        sector_data = get_sector_performance(days=days)
        
        # Plot sector performance
        fig = px.line(
            sector_data, 
            x='Date', 
            y=['Banking', 'IT', 'Pharma', 'Auto', 'Energy'], 
            title=f'Sector Performance ({selected_period})',
            labels={'value': 'Performance (Base 100)', 'variable': 'Sector'},
            color_discrete_map={
                'Banking': '#1E88E5',
                'IT': '#43A047',
                'Pharma': '#E53935',
                'Auto': '#9C27B0',
                'Energy': '#FF9800'
            }
        )
        
        fig.update_layout(
            legend_title_text='Sector',
            xaxis_title='Date',
            yaxis_title='Performance (Base 100)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        
        # Add horizontal reference line at 100 (base)
        fig.add_shape(
            type="line",
            x0=sector_data['Date'].iloc[0],
            y0=100,
            x1=sector_data['Date'].iloc[-1],
            y1=100,
            line=dict(
                color="rgba(0, 0, 0, 0.3)",
                width=1,
                dash="dash"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching sector performance: {e}")
        st.info("Unable to load sector performance chart. Please try again later.")
    
    # Market breadth
    st.header("Market Breadth")
    
    try:
        # Generate sample market breadth data
        # In a real application, this would come from an API
        
        # Create sample data for advances/declines
        dates = pd.date_range(end=pd.Timestamp.now(), periods=days)
        advances = [int(np.random.normal(1000, 200)) for _ in range(days)]
        declines = [int(np.random.normal(800, 200)) for _ in range(days)]
        unchanged = [int(np.random.normal(200, 50)) for _ in range(days)]
        
        breadth_data = pd.DataFrame({
            'Date': dates,
            'Advances': advances,
            'Declines': declines,
            'Unchanged': unchanged
        })
        
        # Create stacked bar chart
        fig = go.Figure()
        
        fig.add_trace(
            go.Bar(
                x=breadth_data['Date'],
                y=breadth_data['Advances'],
                name='Advances',
                marker_color='#43A047'
            )
        )
        
        fig.add_trace(
            go.Bar(
                x=breadth_data['Date'],
                y=breadth_data['Declines'],
                name='Declines',
                marker_color='#E53935'
            )
        )
        
        fig.add_trace(
            go.Bar(
                x=breadth_data['Date'],
                y=breadth_data['Unchanged'],
                name='Unchanged',
                marker_color='#9E9E9E'
            )
        )
        
        fig.update_layout(
            title='Market Breadth (Advances vs Declines)',
            xaxis_title='Date',
            yaxis_title='Number of Stocks',
            barmode='stack',
            height=500,
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        breadth_col1, breadth_col2 = st.columns([2, 1])
        
        with breadth_col1:
            st.plotly_chart(fig, use_container_width=True)
            
        with breadth_col2:
            # Show current day's stats
            st.subheader("Today's Market Breadth")
            
            today_stats = {
                'Advances': advances[-1],
                'Declines': declines[-1],
                'Unchanged': unchanged[-1],
                'Total': advances[-1] + declines[-1] + unchanged[-1],
                'Advance/Decline Ratio': advances[-1] / declines[-1]
            }
            
            # Display as metrics
            st.metric("Advances", f"{today_stats['Advances']}")
            st.metric("Declines", f"{today_stats['Declines']}")
            st.metric("Unchanged", f"{today_stats['Unchanged']}")
            st.metric("Advance/Decline Ratio", f"{today_stats['Advance/Decline Ratio']:.2f}")
    except Exception as e:
        st.error(f"Error generating market breadth data: {e}")
        st.info("Unable to load market breadth chart. Please try again later.")
    
    # Market news
    st.header("Market News")
    
    # In a real application, this would fetch from a news API
    news_data = [
        {
            "title": "RBI Maintains Repo Rate at 6.5% for Fourth Consecutive Policy Review",
            "source": "Economic Times",
            "time": "3 hours ago",
            "content": "The Reserve Bank of India (RBI) maintained the repo rate at 6.5% for the fourth consecutive policy review, focusing on controlling inflation while supporting economic growth."
        },
        {
            "title": "Q2 Results: IT Companies Show Resilience Amid Global Headwinds",
            "source": "Business Standard",
            "time": "6 hours ago",
            "content": "Major Indian IT companies reported better-than-expected Q2 results, showing resilience despite global economic uncertainties and cost-cutting measures by clients."
        },
        {
            "title": "FII Inflows Continue to Strengthen, Domestic Mutual Funds See Record SIP Numbers",
            "source": "Mint",
            "time": "Yesterday",
            "content": "Foreign Institutional Investors (FIIs) continue to pour money into Indian equities while domestic mutual funds report record-high Systematic Investment Plan (SIP) collections for the fifth consecutive month."
        },
        {
            "title": "Government Announces Infrastructure Push with ₹10 Lakh Crore Outlay",
            "source": "Financial Express",
            "time": "2 days ago",
            "content": "The government has announced a major infrastructure development plan with a ₹10 lakh crore outlay over the next three years, focusing on highways, railways, and urban development."
        }
    ]
    
    for i, news in enumerate(news_data):
        with st.expander(f"{news['title']} - {news['source']} ({news['time']})", expanded=(i == 0)):
            st.write(news['content'])
    
    # Market calendar
    st.header("Market Calendar")
    
    # Create tabs for different calendar views
    cal_tab1, cal_tab2, cal_tab3 = st.tabs(["Upcoming Events", "Earnings Calendar", "Dividends"])
    
    with cal_tab1:
        events_data = [
            {"date": "Nov 8, 2023", "event": "RBI Monetary Policy Meeting", "details": "The Reserve Bank of India will announce its bi-monthly monetary policy decision."},
            {"date": "Nov 15, 2023", "event": "WPI Inflation Data", "details": "Wholesale Price Index inflation data for October 2023 will be released."},
            {"date": "Nov 30, 2023", "event": "Q2 GDP Data", "details": "India's Q2 FY24 GDP data will be released by the government."},
            {"date": "Dec 7, 2023", "event": "RBI Monetary Policy Meeting", "details": "The last monetary policy meeting of the calendar year."}
        ]
        
        for event in events_data:
            st.markdown(f"**{event['date']}**: {event['event']}")
            st.caption(event['details'])
            st.markdown("---")
    
    with cal_tab2:
        earnings_data = [
            {"date": "Nov 10, 2023", "company": "Coal India", "expected_eps": "₹4.20", "prev_quarter": "₹3.95"},
            {"date": "Nov 12, 2023", "company": "Tata Motors", "expected_eps": "₹12.50", "prev_quarter": "₹10.75"},
            {"date": "Nov 14, 2023", "company": "Hindalco", "expected_eps": "₹8.30", "prev_quarter": "₹7.85"},
            {"date": "Nov 15, 2023", "company": "ONGC", "expected_eps": "₹11.20", "prev_quarter": "₹11.75"}
        ]
        
        earnings_df = pd.DataFrame(earnings_data)
        st.dataframe(earnings_df, use_container_width=True)
    
    with cal_tab3:
        dividend_data = [
            {"company": "TCS", "ex_date": "Oct 25, 2023", "amount": "₹8.00", "yield": "0.8%"},
            {"company": "Infosys", "ex_date": "Oct 28, 2023", "amount": "₹6.50", "yield": "0.5%"},
            {"company": "HUL", "ex_date": "Nov 2, 2023", "amount": "₹17.00", "yield": "0.7%"},
            {"company": "HDFC Bank", "ex_date": "Nov 10, 2023", "amount": "₹11.50", "yield": "0.4%"}
        ]
        
        dividend_df = pd.DataFrame(dividend_data)
        st.dataframe(dividend_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.caption("Data displayed here is for demonstration purposes. In a production environment, real-time data would be fetched from appropriate APIs.")
    st.caption("© 2023 Indian Stock Market Analysis Platform. Last updated: " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()
