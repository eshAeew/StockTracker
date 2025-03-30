import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_fetcher import get_sector_performance, get_stock_data
from utils.chart_utils import create_sector_performance_chart, create_heatmap, create_pie_chart

st.set_page_config(
    page_title="Sector Analysis | Indian Stock Market Analysis",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("Sector Analysis")
    st.write("Compare performance across market sectors and understand sector dynamics")
    
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
        # Fetch sector performance data
        sector_data = get_sector_performance(days=days)
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["Sector Performance", "Relative Strength", "Sector Correlation", "Market Composition"])
        
        with tab1:
            st.subheader(f"Sector Performance Over {selected_period}")
            
            # Create sector performance chart
            fig = create_sector_performance_chart(sector_data, title=f"Sector Performance ({selected_period})")
            
            # Show chart
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate sector performance table data
            performance_data = {}
            
            for sector in sector_data.columns:
                if sector != 'Date':
                    # Calculate returns for different periods
                    latest = sector_data[sector].iloc[-1]
                    start = sector_data[sector].iloc[0]
                    return_pct = ((latest / start) - 1) * 100
                    
                    # Calculate volatility
                    returns = sector_data[sector].pct_change().dropna()
                    volatility = returns.std() * (252 ** 0.5) * 100  # Annualized volatility
                    
                    # Store data
                    performance_data[sector] = {
                        'Return (%)': round(return_pct, 2),
                        'Volatility (%)': round(volatility, 2),
                        'Risk-Adjusted Return': round(return_pct / volatility if volatility > 0 else 0, 2)
                    }
            
            # Convert to DataFrame for display
            if performance_data:
                performance_df = pd.DataFrame.from_dict(performance_data, orient='index')
                
                # Sort by return
                performance_df = performance_df.sort_values('Return (%)', ascending=False)
                
                # Show the table
                st.subheader("Sector Performance Summary")
                st.dataframe(performance_df, use_container_width=True)
                
                # Add explanation of metrics
                with st.expander("Metric Explanations"):
                    st.markdown("""
                    - **Return (%)**: Percentage change in sector value over the selected period
                    - **Volatility (%)**: Annualized standard deviation of daily returns, a measure of risk
                    - **Risk-Adjusted Return**: Return divided by volatility, higher is better (similar to Sharpe ratio without risk-free rate)
                    """)
            else:
                st.info("No sector performance data available")
        
        with tab2:
            st.subheader("Sector Relative Strength")
            
            # Calculate relative strength compared to market (average of all sectors)
            if len(sector_data.columns) > 1:
                # Create a copy of the data
                rs_data = sector_data.copy()
                
                # Calculate market average (equally weighted)
                sectors = [col for col in rs_data.columns if col != 'Date']
                rs_data['Market'] = rs_data[sectors].mean(axis=1)
                
                # Calculate relative performance (sector / market)
                relative_data = pd.DataFrame({'Date': rs_data['Date']})
                
                for sector in sectors:
                    relative_data[sector] = (rs_data[sector] / rs_data['Market']) * 100
                
                # Create the chart
                fig = px.line(
                    relative_data, 
                    x='Date', 
                    y=sectors,
                    title=f"Sector Relative Strength vs Market ({selected_period})",
                    labels={'value': 'Relative Strength (Market=100)', 'variable': 'Sector'},
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
                    yaxis_title='Relative Strength',
                    height=500,
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                # Add horizontal reference line at 100 (market performance)
                fig.add_shape(
                    type="line",
                    x0=relative_data['Date'].iloc[0],
                    y0=100,
                    x1=relative_data['Date'].iloc[-1],
                    y1=100,
                    line=dict(
                        color="rgba(0, 0, 0, 0.3)",
                        width=1,
                        dash="dash"
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate latest relative strength values
                latest_rs = {}
                
                for sector in sectors:
                    latest_rs[sector] = relative_data[sector].iloc[-1]
                
                # Convert to DataFrame and sort
                latest_rs_df = pd.DataFrame.from_dict(latest_rs, orient='index', columns=['Relative Strength'])
                latest_rs_df = latest_rs_df.sort_values('Relative Strength', ascending=False)
                
                # Show current relative strength
                st.subheader("Current Sector Relative Strength")
                
                # Create columns for displaying data
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    st.dataframe(latest_rs_df, use_container_width=True)
                
                with col2:
                    # Create horizontal bar chart
                    bar_fig = go.Figure()
                    
                    bar_fig.add_trace(
                        go.Bar(
                            y=latest_rs_df.index,
                            x=latest_rs_df['Relative Strength'],
                            orientation='h',
                            marker_color=['#1E88E5' if x > 100 else '#E53935' for x in latest_rs_df['Relative Strength']]
                        )
                    )
                    
                    bar_fig.update_layout(
                        title='Sector Relative Strength vs Market (Current)',
                        xaxis_title='Relative Strength (Market=100)',
                        yaxis_title='Sector',
                        height=300,
                        xaxis=dict(range=[min(80, latest_rs_df['Relative Strength'].min() - 5), 
                                          max(120, latest_rs_df['Relative Strength'].max() + 5)]),
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    # Add vertical reference line at 100 (market performance)
                    bar_fig.add_shape(
                        type="line",
                        x0=100,
                        y0=-0.5,
                        x1=100,
                        y1=len(latest_rs_df) - 0.5,
                        line=dict(
                            color="rgba(0, 0, 0, 0.3)",
                            width=1,
                            dash="dash"
                        )
                    )
                    
                    st.plotly_chart(bar_fig, use_container_width=True)
                
                # Add explanation
                with st.expander("Relative Strength Explanation"):
                    st.markdown("""
                    **Relative Strength** compares a sector's performance to the overall market.
                    
                    - **Value > 100**: The sector is outperforming the market
                    - **Value = 100**: The sector is performing exactly in line with the market
                    - **Value < 100**: The sector is underperforming the market
                    
                    Relative strength is useful for identifying which sectors are leading or lagging the broader market.
                    """)
            else:
                st.info("Insufficient sector data to calculate relative strength")
        
        with tab3:
            st.subheader("Sector Correlation Analysis")
            
            # Calculate correlation between sectors
            if len(sector_data.columns) > 2:  # Need at least 2 sectors plus Date column
                # Create returns data
                sectors = [col for col in sector_data.columns if col != 'Date']
                returns_data = pd.DataFrame()
                
                for sector in sectors:
                    returns_data[sector] = sector_data[sector].pct_change().dropna()
                
                # Calculate correlation matrix
                corr_matrix = returns_data.corr()
                
                # Create heatmap
                correlation_fig = create_heatmap(
                    data=corr_matrix.values,
                    x_labels=corr_matrix.columns,
                    y_labels=corr_matrix.index,
                    title="Sector Correlation Matrix"
                )
                
                st.plotly_chart(correlation_fig, use_container_width=True)
                
                # Add explanation
                with st.expander("Correlation Explanation"):
                    st.markdown("""
                    **Correlation** measures how closely two sectors move in relation to each other.
                    
                    - **+1.0**: Perfect positive correlation (sectors move exactly together)
                    - **0.0**: No correlation (sectors move independently)
                    - **-1.0**: Perfect negative correlation (sectors move exactly opposite)
                    
                    **Why It Matters**:
                    - **Portfolio Diversification**: Lower correlation between sectors reduces overall portfolio risk
                    - **Sector Rotation**: Understanding which sectors tend to move together helps in planning sector rotation strategies
                    - **Risk Management**: Building a portfolio with less correlated sectors can improve risk-adjusted returns
                    """)
            else:
                st.info("Insufficient sector data to calculate correlations")
        
        with tab4:
            st.subheader("Market Composition")
            
            # Market capitalization data (sample data, in a real app would be fetched from API)
            market_cap_data = {
                'Banking': 28.5,
                'IT': 18.2,
                'Energy': 15.7,
                'FMCG': 10.3,
                'Pharma': 8.6,
                'Auto': 7.4,
                'Metals': 5.8,
                'Telecom': 3.2,
                'Others': 2.3
            }
            
            # Create pie chart
            mcap_fig = create_pie_chart(
                values=list(market_cap_data.values()),
                labels=list(market_cap_data.keys()),
                title="NSE Market Capitalization by Sector"
            )
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.plotly_chart(mcap_fig, use_container_width=True)
            
            with col2:
                st.subheader("Sector Weights")
                
                # Convert to DataFrame for display
                mcap_df = pd.DataFrame.from_dict(market_cap_data, orient='index', columns=['Weight (%)'])
                mcap_df = mcap_df.sort_values('Weight (%)', ascending=False)
                
                st.dataframe(mcap_df, use_container_width=True)
                
                # Calculate top sectors cumulative weight
                cumulative_weight = mcap_df['Weight (%)'].cumsum()
                top_3_weight = cumulative_weight.iloc[2]
                top_5_weight = cumulative_weight.iloc[4]
                
                st.markdown(f"**Top 3 Sectors:** {top_3_weight:.1f}% of market")
                st.markdown(f"**Top 5 Sectors:** {top_5_weight:.1f}% of market")
            
            # Add explanation
            with st.expander("Market Composition Explanation"):
                st.markdown("""
                **Market Composition** shows the breakdown of the overall market by sector.
                
                - Larger sectors have more influence on the overall market movement
                - Sector weights change over time as companies grow or shrink
                - In the Indian market, Banking/Financial, IT, and Energy typically represent a significant portion
                
                **Investment Implications**:
                - An index fund will be heavily weighted toward the largest sectors
                - For equal exposure across sectors, investors need to deliberately overweight smaller sectors
                - Understanding sector weights helps evaluate if your portfolio is appropriately diversified
                """)
            
            # Sector composition (sample data for key sectors)
            st.subheader("Key Companies in Major Sectors")
            
            sector_companies = {
                'Banking': [
                    {'Company': 'HDFC Bank', 'Weight': 25.3, 'Return': 12.5},
                    {'Company': 'ICICI Bank', 'Weight': 18.7, 'Return': 15.2},
                    {'Company': 'SBI', 'Weight': 15.4, 'Return': 18.7},
                    {'Company': 'Kotak Mahindra', 'Weight': 12.2, 'Return': 8.3},
                    {'Company': 'Axis Bank', 'Weight': 10.8, 'Return': 14.1}
                ],
                'IT': [
                    {'Company': 'TCS', 'Weight': 38.2, 'Return': 5.8},
                    {'Company': 'Infosys', 'Weight': 28.5, 'Return': 4.2},
                    {'Company': 'HCL Tech', 'Weight': 10.3, 'Return': 7.5},
                    {'Company': 'Wipro', 'Weight': 9.8, 'Return': -2.3},
                    {'Company': 'Tech Mahindra', 'Weight': 5.4, 'Return': -5.1}
                ],
                'Pharma': [
                    {'Company': 'Sun Pharma', 'Weight': 22.5, 'Return': 9.2},
                    {'Company': 'Dr Reddy\'s', 'Weight': 15.8, 'Return': 12.4},
                    {'Company': 'Cipla', 'Weight': 13.2, 'Return': 8.7},
                    {'Company': 'Divis Labs', 'Weight': 10.5, 'Return': -3.8},
                    {'Company': 'Biocon', 'Weight': 8.7, 'Return': -7.2}
                ]
            }
            
            # Create tabs for each sector
            sector_tabs = st.tabs(list(sector_companies.keys()))
            
            for i, sector in enumerate(sector_companies.keys()):
                with sector_tabs[i]:
                    # Convert to DataFrame
                    sector_df = pd.DataFrame(sector_companies[sector])
                    
                    # Create columns for data and chart
                    comp_col1, comp_col2 = st.columns([3, 2])
                    
                    with comp_col1:
                        # Show table
                        st.dataframe(sector_df, use_container_width=True)
                    
                    with comp_col2:
                        # Create pie chart of sector composition
                        sector_comp_fig = create_pie_chart(
                            values=sector_df['Weight'],
                            labels=sector_df['Company'],
                            title=f"{sector} Sector Composition"
                        )
                        
                        st.plotly_chart(sector_comp_fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading sector analysis data: {e}")
        st.info("Unable to load sector analysis. Please try again later.")
    
    # Footer
    st.markdown("---")
    st.caption("Sector analysis data is indicative and for educational purposes only.")
    st.caption("© 2023 Indian Stock Market Analysis Platform")

if __name__ == "__main__":
    main()
