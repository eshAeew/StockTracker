import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_fetcher import get_nifty_data, get_sensex_data, get_top_gainers_losers, get_market_indices

# Configure page
st.set_page_config(
    page_title="Indian Stock Market Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def main():
    # Header with logo and title
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("https://images.unsplash.com/photo-1488459716781-31db52582fe9", width=100)
    with col2:
        st.title("Indian Stock Market Analysis")
        st.caption("Comprehensive analysis tools for investors and traders")

    # Market Overview Dashboard
    st.header("Market Dashboard")
    
    # Market indices
    indices_col1, indices_col2 = st.columns(2)
    
    try:
        # Fetch market data
        nifty_data = get_nifty_data()
        sensex_data = get_sensex_data()
        
        with indices_col1:
            # NIFTY 50 Card
            nifty_change_color = "green" if nifty_data['change_pct'] > 0 else "red"
            nifty_change_icon = "↗" if nifty_data['change_pct'] > 0 else "↘"
            st.metric(
                label="NIFTY 50", 
                value=f"₹{nifty_data['last_price']:,.2f}",
                delta=f"{nifty_change_icon} {nifty_data['change_pct']:.2f}%"
            )
            
        with indices_col2:
            # SENSEX Card
            sensex_change_color = "green" if sensex_data['change_pct'] > 0 else "red"
            sensex_change_icon = "↗" if sensex_data['change_pct'] > 0 else "↘"
            st.metric(
                label="BSE SENSEX", 
                value=f"₹{sensex_data['last_price']:,.2f}",
                delta=f"{sensex_change_icon} {sensex_data['change_pct']:.2f}%"
            )
    except Exception as e:
        st.error(f"Error fetching market data: {e}")
        st.warning("Displaying fallback data for visualization purposes.")
        # Fallback placeholder for market indices when API fails
        with indices_col1:
            st.metric(label="NIFTY 50", value="₹19,675.45", delta="0.32%")
        with indices_col2:
            st.metric(label="BSE SENSEX", value="₹65,928.53", delta="0.40%")
    
    # Market highlights
    st.subheader("Market Highlights")
    highlight_cols = st.columns(3)
    
    with highlight_cols[0]:
        st.image("https://images.unsplash.com/photo-1510247548804-1a5c6f550b2d", use_column_width=True)
        st.markdown("### Latest Market News")
        st.markdown("""
        - RBI maintains repo rate at 6.5%
        - Q2 results show positive trends
        - FII inflows remain strong
        """)
    
    with highlight_cols[1]:
        st.image("https://images.unsplash.com/photo-1508589066756-c5dfb2cb7587", use_column_width=True)
        st.markdown("### Top Performing Sectors")
        st.markdown("""
        - IT: +2.4%
        - Banking: +1.8%
        - Pharma: +1.2%
        """)
    
    with highlight_cols[2]:
        st.image("https://images.unsplash.com/photo-1526628953301-3e589a6a8b74", use_column_width=True)
        st.markdown("### Coming Up")
        st.markdown("""
        - Earnings reports next week
        - RBI policy meeting: Nov 8
        - Quarterly GDP data: Nov 30
        """)
    
    # Market summary
    st.subheader("Market Summary")
    
    try:
        # Fetch top gainers and losers
        top_gainers, top_losers = get_top_gainers_losers()
        
        gain_loss_cols = st.columns(2)
        
        with gain_loss_cols[0]:
            st.markdown("#### Top Gainers")
            st.dataframe(top_gainers[['Symbol', 'Company', 'Price', 'Change%']], use_container_width=True)
        
        with gain_loss_cols[1]:
            st.markdown("#### Top Losers")
            st.dataframe(top_losers[['Symbol', 'Company', 'Price', 'Change%']], use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching top gainers/losers: {e}")
    
    # Market Indices Visualization
    st.subheader("Market Indices Performance")
    
    try:
        # Fetch index data for plotting
        indices_data = get_market_indices()
        
        # Plot the data
        fig = px.line(
            indices_data, 
            x='Date', 
            y=['NIFTY50', 'BANKNIFTY', 'FINNIFTY'], 
            title='Major Indices (30 Days)',
            labels={'value': 'Index Value', 'variable': 'Index'},
            color_discrete_map={
                'NIFTY50': '#1E88E5',
                'BANKNIFTY': '#43A047',
                'FINNIFTY': '#E53935'
            }
        )
        
        fig.update_layout(
            legend_title_text='Index',
            xaxis_title='Date',
            yaxis_title='Value',
            plot_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching index data: {e}")
        
        # Fallback visualization with dummy data
        dates = pd.date_range(end=pd.Timestamp.now(), periods=30)
        dummy_data = pd.DataFrame({
            'Date': dates,
            'NIFTY50': [19000 + i*25 + (i**2)/2 for i in range(30)],
            'BANKNIFTY': [44000 + i*50 + (i**2) for i in range(30)],
            'FINNIFTY': [21000 + i*30 + (i**2)/1.5 for i in range(30)]
        })
        
        fig = px.line(
            dummy_data, 
            x='Date', 
            y=['NIFTY50', 'BANKNIFTY', 'FINNIFTY'], 
            title='Major Indices (30 Days) - Sample Data',
            labels={'value': 'Index Value', 'variable': 'Index'},
            color_discrete_map={
                'NIFTY50': '#1E88E5',
                'BANKNIFTY': '#43A047',
                'FINNIFTY': '#E53935'
            }
        )
        
        fig.update_layout(
            legend_title_text='Index',
            xaxis_title='Date',
            yaxis_title='Value',
            plot_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.info("This is a sample visualization. Connect to a data source for real market data.")
    
    # App navigation guide
    st.header("Navigation Guide")
    st.write("""
    Use the sidebar menu to navigate to different sections of the application:
    
    - **Market Overview**: Get a summary of market indices, top movers, and sector performance
    - **Stock Analysis**: Analyze individual stocks with interactive charts
    - **Technical Indicators**: Apply technical analysis tools to stock charts
    - **Fundamental Analysis**: View company financials and valuation metrics
    - **Sector Analysis**: Compare performance across market sectors
    - **Portfolio Tracker**: Track and analyze your investment portfolio
    """)
    
    # Footer
    st.markdown("---")
    st.caption("© 2023 Indian Stock Market Analysis Platform. Data provided for informational purposes only.")
    st.caption("Disclaimer: This is not investment advice. Always do your own research before making investment decisions.")

if __name__ == "__main__":
    main()
