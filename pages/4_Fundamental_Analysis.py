import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_fetcher import (
    get_stock_info, 
    get_financial_ratios, 
    get_income_statement, 
    get_balance_sheet, 
    get_cash_flow,
    get_top_stocks_list,
    search_stocks
)
from utils.fundamental_analysis import (
    create_company_overview,
    create_financial_ratios_table,
    create_income_statement_chart,
    create_balance_sheet_chart,
    create_cash_flow_chart
)

st.set_page_config(
    page_title="Fundamental Analysis | Indian Stock Market Analysis",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("Fundamental Analysis")
    st.write("Analyze company financials and valuation metrics")
    
    # Stock selection
    st.header("Select a Company")
    
    # Stock search
    search_query = st.text_input("Search for a company (name or symbol)", placeholder="e.g., RELIANCE or TCS")
    
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
                st.warning(f"No companies found matching '{search_query}'")
                # Default to a popular stock
                stock_symbol = "RELIANCE.NS"
        except Exception as e:
            st.error(f"Error searching for companies: {e}")
            # Default to a popular stock
            stock_symbol = "RELIANCE.NS"
    else:
        # If no search, show top stocks for selection
        st.subheader("Popular Companies")
        
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
            st.error(f"Error loading popular companies: {e}")
            # Default to a popular stock
            stock_symbol = "RELIANCE.NS"
    
    # Add a divider
    st.markdown("---")
    
    # Load and display fundamental analysis data
    try:
        # Get stock info
        stock_info = get_stock_info(stock_symbol)
        
        if not stock_info:
            st.warning(f"No fundamental data available for {stock_symbol}")
            return
        
        # Company name for display
        company_name = stock_info.get('name', stock_symbol.replace('.NS', ''))
        
        # Company overview section
        st.header(f"{company_name} ({stock_symbol.replace('.NS', '')})")
        
        # Create company overview figure
        overview_fig = create_company_overview(stock_info)
        st.plotly_chart(overview_fig, use_container_width=True)
        
        # Create tabs for different financial data
        tab1, tab2, tab3, tab4 = st.tabs(["Financial Ratios", "Income Statement", "Balance Sheet", "Cash Flow"])
        
        with tab1:
            st.subheader("Key Financial Ratios")
            
            # Create financial ratios table
            ratios_fig = create_financial_ratios_table(stock_symbol)
            st.plotly_chart(ratios_fig, use_container_width=True)
            
            # Financial ratios explanation
            with st.expander("Financial Ratios Explanation"):
                st.markdown("""
                ### Valuation Ratios
                - **PE Ratio (TTM)**: Price-to-Earnings ratio measures the current share price relative to its per-share earnings over the last 12 months. Higher PE suggests expectations of higher growth.
                - **Forward PE**: Similar to PE ratio but uses forecasted earnings.
                - **PEG Ratio**: PE ratio divided by the growth rate of earnings. A lower PEG (< 1) may indicate an undervalued stock.
                - **Price to Sales (TTM)**: Share price divided by sales per share. Lower values may indicate undervaluation.
                - **Price to Book**: Share price divided by book value per share. Values under 1 might suggest an undervalued stock.
                - **Enterprise Value/EBITDA**: A ratio used to determine the value of a company. Lower values may indicate undervaluation.
                
                ### Profitability Ratios
                - **Profit Margin**: Net income divided by revenue, showing how efficiently a company converts sales into profit.
                - **Operating Margin (TTM)**: Operating income divided by revenue, showing operational efficiency.
                - **Return on Assets (TTM)**: Net income divided by total assets, showing how efficiently assets are used.
                - **Return on Equity (TTM)**: Net income divided by shareholder equity, indicating profitability from shareholder investments.
                
                ### Growth Metrics
                - **Revenue Growth (YoY)**: Year-over-year percentage increase in company revenue.
                - **Earnings Growth (YoY)**: Year-over-year percentage increase in earnings.
                
                ### Dividend Metrics
                - **Dividend Yield**: Annual dividend per share divided by share price.
                - **Dividend Rate**: Annual dividend payment per share.
                - **Payout Ratio**: Proportion of earnings paid out as dividends.
                
                ### Risk Metrics
                - **Beta (5Y Monthly)**: Measure of stock volatility compared to the market. Beta > 1 indicates higher volatility.
                - **Debt to Equity**: Total liabilities divided by shareholder equity, showing financial leverage.
                - **Current Ratio**: Current assets divided by current liabilities, indicating short-term liquidity.
                - **Quick Ratio**: (Current assets - inventory) divided by current liabilities, a more conservative liquidity measure.
                """)
        
        with tab2:
            st.subheader("Income Statement Analysis")
            
            # Period selection for financial statements
            period_options = ["annual", "quarterly"]
            selected_period = st.radio("Select Period", period_options, horizontal=True)
            
            # Create income statement charts
            income_chart, income_table = create_income_statement_chart(stock_symbol, period=selected_period)
            
            # Show income statement chart
            st.plotly_chart(income_chart, use_container_width=True)
            
            # Show detailed income statement table
            with st.expander("View Detailed Income Statement"):
                st.plotly_chart(income_table, use_container_width=True)
            
            # Income statement explanation
            with st.expander("Income Statement Explanation"):
                st.markdown("""
                ### Income Statement Components
                - **Total Revenue**: The total amount of money generated from sales of products/services.
                - **Cost of Revenue**: Direct costs attributable to the production of goods/services.
                - **Gross Profit**: Total Revenue - Cost of Revenue
                - **Operating Expenses**: Costs associated with running the business (not directly tied to production).
                - **Operating Income**: Gross Profit - Operating Expenses
                - **Net Income**: The final profit after all expenses, taxes, and costs.
                - **EBITDA**: Earnings Before Interest, Taxes, Depreciation, and Amortization.
                - **EPS (Earnings Per Share)**: Net Income ÷ Outstanding Shares
                
                ### What to Look For
                - **Revenue Growth**: Is the company growing its top line year over year?
                - **Margin Expansion**: Are gross, operating, and net margins improving over time?
                - **Expense Control**: Is the company managing its expenses effectively?
                - **Earnings Consistency**: Are earnings stable or volatile?
                - **Seasonal Patterns**: Many businesses have seasonal fluctuations in quarterly reports.
                """)
        
        with tab3:
            st.subheader("Balance Sheet Analysis")
            
            # Create balance sheet charts
            balance_chart, balance_table = create_balance_sheet_chart(stock_symbol, period=selected_period)
            
            # Show balance sheet chart
            st.plotly_chart(balance_chart, use_container_width=True)
            
            # Show detailed balance sheet table
            with st.expander("View Detailed Balance Sheet"):
                st.plotly_chart(balance_table, use_container_width=True)
            
            # Balance sheet explanation
            with st.expander("Balance Sheet Explanation"):
                st.markdown("""
                ### Balance Sheet Components
                - **Total Assets**: Everything the company owns (current assets + non-current assets).
                - **Current Assets**: Assets expected to be converted to cash within one year (cash, inventory, receivables).
                - **Non-current Assets**: Long-term assets (property, equipment, investments).
                - **Total Liabilities**: Everything the company owes (current liabilities + non-current liabilities).
                - **Current Liabilities**: Obligations due within one year (payables, short-term debt).
                - **Non-current Liabilities**: Long-term obligations (long-term debt, deferred taxes).
                - **Stockholder Equity**: Assets - Liabilities (represents ownership value).
                
                ### What to Look For
                - **Debt Levels**: Is the company taking on too much debt?
                - **Working Capital**: Current Assets - Current Liabilities (positive is good).
                - **Asset Growth**: Is the company growing its asset base?
                - **Cash Reserves**: Does the company have sufficient cash for operations?
                - **Equity Growth**: Is shareholder value increasing over time?
                - **Debt-to-Equity Ratio**: Lower ratios generally indicate less risk.
                """)
        
        with tab4:
            st.subheader("Cash Flow Analysis")
            
            # Create cash flow charts
            cash_flow_chart, cash_flow_table = create_cash_flow_chart(stock_symbol, period=selected_period)
            
            # Show cash flow chart
            st.plotly_chart(cash_flow_chart, use_container_width=True)
            
            # Show detailed cash flow table
            with st.expander("View Detailed Cash Flow Statement"):
                st.plotly_chart(cash_flow_table, use_container_width=True)
            
            # Cash flow explanation
            with st.expander("Cash Flow Statement Explanation"):
                st.markdown("""
                ### Cash Flow Statement Components
                - **Operating Cash Flow**: Cash generated from day-to-day business operations.
                - **Cash Flow from Investment**: Cash used for investment in assets or received from asset sales.
                - **Cash Flow from Financing**: Cash from debt, equity issuance, or payments to shareholders.
                - **Free Cash Flow**: Operating Cash Flow - Capital Expenditures.
                - **Change in Cash**: Net change in cash position over the period.
                
                ### What to Look For
                - **Positive Operating Cash Flow**: Does the core business generate cash?
                - **Capital Expenditure Trends**: Is the company investing in growth?
                - **Free Cash Flow**: Is there sufficient cash after investments?
                - **Financing Activities**: Is the company raising funds or returning to shareholders?
                - **Cash Conversion**: How efficiently is the company converting profits to cash?
                - **Sustainability**: Can the company fund operations and growth without external financing?
                """)
    
    except Exception as e:
        st.error(f"Error loading fundamental analysis data: {e}")
        st.info("Please try another company")
    
    # Footer
    st.markdown("---")
    st.caption("Fundamental analysis data sourced from Yahoo Finance via yfinance. For informational purposes only.")
    st.caption("© 2023 Indian Stock Market Analysis Platform")

if __name__ == "__main__":
    main()
