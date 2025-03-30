import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from utils.data_fetcher import get_financial_ratios, get_income_statement, get_balance_sheet, get_cash_flow

def format_large_number(number, precision=2):
    """
    Format large numbers to more readable format (e.g., 1,000,000 -> 1M)
    
    Parameters:
        number (float): Number to format
        precision (int): Decimal precision
        
    Returns:
        str: Formatted string
    """
    if number is None:
        return "N/A"
    
    if abs(number) >= 1_000_000_000:
        return f"{number / 1_000_000_000:.{precision}f}B"
    elif abs(number) >= 1_000_000:
        return f"{number / 1_000_000:.{precision}f}M"
    elif abs(number) >= 1_000:
        return f"{number / 1_000:.{precision}f}K"
    else:
        return f"{number:.{precision}f}"


def format_percentage(number, precision=2):
    """
    Format a decimal as a percentage string
    
    Parameters:
        number (float): Number to format
        precision (int): Decimal precision
        
    Returns:
        str: Formatted percentage string
    """
    if number is None:
        return "N/A"
    
    return f"{number:.{precision}f}%"


def create_company_overview(stock_info):
    """
    Create a comprehensive company overview figure
    
    Parameters:
        stock_info (dict): Stock information
        
    Returns:
        plotly.graph_objects.Figure: Company overview figure
    """
    # Create figure
    fig = go.Figure()
    
    # Company name and symbol
    company_name = stock_info.get('name', 'N/A')
    symbol = stock_info.get('symbol', 'N/A').replace('.NS', '')
    
    # Format market cap
    market_cap = stock_info.get('market_cap', 0)
    market_cap_str = format_large_number(market_cap)
    
    # Get other key metrics
    sector = stock_info.get('sector', 'N/A')
    industry = stock_info.get('industry', 'N/A')
    current_price = stock_info.get('current_price', 0)
    pe_ratio = stock_info.get('pe_ratio', 0)
    eps = stock_info.get('eps', 0)
    dividend_yield = stock_info.get('dividend_yield', 0)
    fifty_two_week_high = stock_info.get('52_week_high', 0)
    fifty_two_week_low = stock_info.get('52_week_low', 0)
    
    # Create the overview text
    overview_text = f"""
    <span style='font-size: 24px; font-weight: bold;'>{company_name} ({symbol})</span><br>
    <span style='font-size: 18px;'>{sector} | {industry}</span><br>
    <br>
    <span style='font-size: 20px; font-weight: bold;'>₹{current_price:,.2f}</span><br>
    <br>
    <span style='font-size: 16px;'><b>Market Cap:</b> ₹{market_cap_str}</span><br>
    <span style='font-size: 16px;'><b>P/E Ratio:</b> {pe_ratio:.2f}</span><br>
    <span style='font-size: 16px;'><b>EPS:</b> ₹{eps:.2f}</span><br>
    <span style='font-size: 16px;'><b>Dividend Yield:</b> {dividend_yield:.2f}%</span><br>
    <span style='font-size: 16px;'><b>52-Week Range:</b> ₹{fifty_two_week_low:,.2f} - ₹{fifty_two_week_high:,.2f}</span><br>
    """
    
    # Add the overview text to the figure
    fig.add_annotation(
        text=overview_text,
        align="left",
        showarrow=False,
        xref="paper",
        yref="paper",
        x=0.01,
        y=0.99,
        font=dict(size=14),
    )
    
    # Update layout
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
    )
    
    # Remove axes
    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False)
    
    return fig


def create_financial_ratios_table(symbol):
    """
    Create a table of financial ratios for a given stock
    
    Parameters:
        symbol (str): Stock symbol
        
    Returns:
        plotly.graph_objects.Figure: Financial ratios table
    """
    # Get financial ratios
    ratios = get_financial_ratios(symbol)
    
    if not ratios:
        # Return empty figure with message if no data
        fig = go.Figure()
        fig.add_annotation(
            text="No financial ratio data available",
            align="center",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            font=dict(size=14),
        )
        return fig
    
    # Group ratios by category
    categories = {
        'Valuation Ratios': [
            'PE Ratio (TTM)',
            'Forward PE',
            'PEG Ratio',
            'Price to Sales (TTM)',
            'Price to Book',
            'Enterprise Value/EBITDA',
            'Enterprise Value/Revenue'
        ],
        'Profitability Ratios': [
            'Profit Margin',
            'Operating Margin (TTM)',
            'Return on Assets (TTM)',
            'Return on Equity (TTM)'
        ],
        'Growth Metrics': [
            'Revenue Growth (YoY)',
            'Earnings Growth (YoY)'
        ],
        'Dividend Metrics': [
            'Dividend Yield',
            'Dividend Rate',
            'Payout Ratio'
        ],
        'Risk Metrics': [
            'Beta (5Y Monthly)',
            'Debt to Equity',
            'Current Ratio',
            'Quick Ratio'
        ]
    }
    
    # Create figure with subplots for each category
    fig = make_subplots(
        rows=len(categories),
        cols=1,
        subplot_titles=list(categories.keys()),
        vertical_spacing=0.05,
    )
    
    # Set row heights based on number of ratios in each category
    row_heights = [len(ratios_list) * 30 for ratios_list in categories.values()]
    total_height = sum(row_heights)
    
    row_index = 1
    for category, ratios_list in categories.items():
        # Filter ratios for this category
        category_ratios = {key: ratios.get(key) for key in ratios_list if key in ratios}
        
        if category_ratios:
            # Create data for table
            ratio_names = list(category_ratios.keys())
            ratio_values = []
            
            for name, value in category_ratios.items():
                # Format percentages
                if any(metric in name for metric in ['Margin', 'Return', 'Growth', 'Yield', 'Payout']):
                    if value is not None:
                        ratio_values.append(f"{value:.2f}%")
                    else:
                        ratio_values.append("N/A")
                else:
                    if value is not None:
                        ratio_values.append(f"{value:.2f}")
                    else:
                        ratio_values.append("N/A")
            
            # Add table
            fig.add_trace(
                go.Table(
                    header=dict(
                        values=['Ratio', 'Value'],
                        font=dict(size=12, color='white'),
                        fill_color='#1E88E5',
                        align='left'
                    ),
                    cells=dict(
                        values=[ratio_names, ratio_values],
                        font=dict(size=11),
                        fill_color='white',
                        align='left'
                    )
                ),
                row=row_index,
                col=1
            )
        
        row_index += 1
    
    # Update layout
    fig.update_layout(
        height=total_height + 200,  # Add space for headers
        margin=dict(l=20, r=20, t=80, b=20),
        title=f"Financial Ratios - {symbol.replace('.NS', '')}",
        font=dict(
            family="Roboto, sans-serif",
            size=12,
            color="#212121"
        )
    )
    
    return fig


def create_income_statement_chart(symbol, period='annual'):
    """
    Create income statement visualization
    
    Parameters:
        symbol (str): Stock symbol
        period (str): 'annual' or 'quarterly'
        
    Returns:
        tuple: (chart figure, table figure)
    """
    # Get income statement data
    income_stmt = get_income_statement(symbol, period)
    
    # Create empty figures for chart and table
    chart_fig = go.Figure()
    table_fig = go.Figure()
    
    if income_stmt.empty:
        # Return empty figures with message if no data
        for fig in [chart_fig, table_fig]:
            fig.add_annotation(
                text="No income statement data available",
                align="center",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                font=dict(size=14),
            )
        return chart_fig, table_fig
    
    try:
        # Convert column headers (dates) to strings
        income_stmt.columns = [col.strftime('%Y-%m-%d') if hasattr(col, 'strftime') else str(col) for col in income_stmt.columns]
        
        # Select key metrics
        key_metrics = [
            'Total Revenue',
            'Gross Profit',
            'Operating Income',
            'Net Income',
            'EBITDA'
        ]
        
        # Filter for available metrics
        available_metrics = [metric for metric in key_metrics if metric in income_stmt.index]
        
        if not available_metrics:
            # If none of the key metrics are available, use what we have
            available_metrics = list(income_stmt.index)[:5]  # First 5 metrics
        
        # Create a new DataFrame with only the key metrics
        chart_data = income_stmt.loc[available_metrics]
        
        # Transpose so dates become rows
        chart_data = chart_data.transpose()
        chart_data.index = pd.to_datetime(chart_data.index)
        chart_data = chart_data.sort_index()
        
        # Reset index to make Date a column
        chart_data.reset_index(inplace=True)
        chart_data.rename(columns={'index': 'Date'}, inplace=True)
    
        # Create figure for key metrics over time
        colors = ['#1E88E5', '#43A047', '#E53935', '#9C27B0', '#FF9800']
        
        for i, metric in enumerate(available_metrics):
            chart_fig.add_trace(
                go.Bar(
                    x=chart_data['Date'],
                    y=chart_data[metric],
                    name=metric,
                    marker_color=colors[i % len(colors)]
                )
            )
        
        # Update layout
        chart_fig.update_layout(
            title=f"Income Statement - {symbol.replace('.NS', '')} ({period.capitalize()})",
            xaxis_title="Date",
            yaxis_title="Amount (₹)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500,
            margin=dict(l=50, r=50, t=80, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(
                family="Roboto, sans-serif",
                size=12,
                color="#212121"
            )
        )
        
        # Create table with full income statement
        table_data = income_stmt.copy()
        
        # Format numbers
        for col in table_data.columns:
            table_data[col] = table_data[col].apply(lambda x: format_large_number(x) if pd.notnull(x) else "N/A")
        
        table_fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=['Metric'] + list(table_data.columns),
                        font=dict(size=12, color='white'),
                        fill_color='#1E88E5',
                        align='left'
                    ),
                    cells=dict(
                        values=[table_data.index] + [table_data[col] for col in table_data.columns],
                        font=dict(size=11),
                        fill_color='white',
                        align=['left'] + ['right'] * len(table_data.columns)
                    )
                )
            ]
        )
        
        table_fig.update_layout(
            title=f"Detailed Income Statement - {symbol.replace('.NS', '')} ({period.capitalize()})",
            height=400 + 30 * len(table_data.index),  # Adjust height based on number of rows
            margin=dict(l=20, r=20, t=80, b=20),
            font=dict(
                family="Roboto, sans-serif",
                size=12,
                color="#212121"
            )
        )
    except Exception as e:
        print(f"Error creating income statement chart: {e}")
        chart_fig.add_annotation(
            text="Error creating income statement chart",
            align="center",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            font=dict(size=14),
        )
        
        table_fig.add_annotation(
            text="Error creating income statement table",
            align="center",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            font=dict(size=14),
        )
    
    return chart_fig, table_fig


def create_balance_sheet_chart(symbol, period='annual'):
    """
    Create balance sheet visualization
    
    Parameters:
        symbol (str): Stock symbol
        period (str): 'annual' or 'quarterly'
        
    Returns:
        tuple: (chart figure, table figure)
    """
    # Get balance sheet data
    balance_sheet = get_balance_sheet(symbol, period)
    
    # Create empty figures for chart and table
    chart_fig = go.Figure()
    table_fig = go.Figure()
    
    if balance_sheet.empty:
        # Return empty figures with message if no data
        for fig in [chart_fig, table_fig]:
            fig.add_annotation(
                text="No balance sheet data available",
                align="center",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                font=dict(size=14),
            )
        return chart_fig, table_fig
    
    try:
        # Convert column headers (dates) to strings
        balance_sheet.columns = [col.strftime('%Y-%m-%d') if hasattr(col, 'strftime') else str(col) for col in balance_sheet.columns]
        
        # Create asset and liability groups
        asset_items = [
            'Total Assets',
            'Total Current Assets',
            'Cash And Cash Equivalents',
            'Inventory',
            'Net Receivables',
            'Other Current Assets',
            'Property Plant Equipment',
            'Long Term Investments',
            'Goodwill',
            'Intangible Assets'
        ]
        
        liability_equity_items = [
            'Total Liabilities',
            'Total Current Liabilities',
            'Accounts Payable',
            'Short Term Debt',
            'Other Current Liabilities',
            'Long Term Debt',
            'Other Liabilities',
            'Total Stockholder Equity',
            'Common Stock',
            'Retained Earnings'
        ]
        
        # Filter for available items
        available_assets = [item for item in asset_items if item in balance_sheet.index]
        available_liabilities = [item for item in liability_equity_items if item in balance_sheet.index]
        
        if not available_assets or not available_liabilities:
            # If key metrics are not available, raise an exception to be caught by the outer try/except
            raise ValueError("Required balance sheet metrics not available")
        
        # Get the most recent date
        latest_date = balance_sheet.columns[0]
        
        # Create data for stacked bar chart
        assets_data = balance_sheet.loc[available_assets, latest_date].sort_values(ascending=False)
        liabilities_equity_data = balance_sheet.loc[available_liabilities, latest_date].sort_values(ascending=False)
        
        # Assets
        chart_fig.add_trace(
            go.Bar(
                x=['Assets'],
                y=[assets_data[0]],  # Total assets
                name='Total Assets',
                marker_color='#1E88E5'
            )
        )
        
        # Liabilities
        chart_fig.add_trace(
            go.Bar(
                x=['Liabilities & Equity'],
                y=[liabilities_equity_data[0] if len(liabilities_equity_data) > 0 else 0],  # Total liabilities
                name='Total Liabilities',
                marker_color='#E53935'
            )
        )
        
        # Equity (if available)
        equity_item = 'Total Stockholder Equity'
        if equity_item in balance_sheet.index:
            equity_value = balance_sheet.loc[equity_item, latest_date]
            chart_fig.add_trace(
                go.Bar(
                    x=['Liabilities & Equity'],
                    y=[equity_value],
                    name='Stockholder Equity',
                    marker_color='#43A047'
                )
            )
        
        # Update layout
        chart_fig.update_layout(
            title=f"Balance Sheet Overview - {symbol.replace('.NS', '')} ({latest_date})",
            yaxis_title="Amount (₹)",
            barmode='stack',
            height=500,
            margin=dict(l=50, r=50, t=80, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(
                family="Roboto, sans-serif",
                size=12,
                color="#212121"
            )
        )
        
        # Create detailed breakdown figures
        # Create table with full balance sheet
        table_data = balance_sheet.copy()
        
        # Format numbers
        for col in table_data.columns:
            table_data[col] = table_data[col].apply(lambda x: format_large_number(x) if pd.notnull(x) else "N/A")
        
        table_fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=['Metric'] + list(table_data.columns),
                        font=dict(size=12, color='white'),
                        fill_color='#1E88E5',
                        align='left'
                    ),
                    cells=dict(
                        values=[table_data.index] + [table_data[col] for col in table_data.columns],
                        font=dict(size=11),
                        fill_color='white',
                        align=['left'] + ['right'] * len(table_data.columns)
                    )
                )
            ]
        )
        
        table_fig.update_layout(
            title=f"Detailed Balance Sheet - {symbol.replace('.NS', '')} ({period.capitalize()})",
            height=400 + 30 * len(table_data.index),  # Adjust height based on number of rows
            margin=dict(l=20, r=20, t=80, b=20),
            font=dict(
                family="Roboto, sans-serif",
                size=12,
                color="#212121"
            )
        )
    except Exception as e:
        print(f"Error creating balance sheet chart: {e}")
        for fig in [chart_fig, table_fig]:
            fig.add_annotation(
                text="Error creating balance sheet visualization",
                align="center",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                font=dict(size=14),
            )
    
    return chart_fig, table_fig


def create_cash_flow_chart(symbol, period='annual'):
    """
    Create cash flow visualization
    
    Parameters:
        symbol (str): Stock symbol
        period (str): 'annual' or 'quarterly'
        
    Returns:
        tuple: (chart figure, table figure)
    """
    # Get cash flow data
    cash_flow = get_cash_flow(symbol, period)
    
    # Create empty figures for chart and table
    chart_fig = go.Figure()
    table_fig = go.Figure()
    
    if cash_flow.empty:
        # Return empty figures with message if no data
        for fig in [chart_fig, table_fig]:
            fig.add_annotation(
                text="No cash flow data available",
                align="center",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                font=dict(size=14),
            )
        return chart_fig, table_fig
    
    try:
        # Convert column headers (dates) to strings
        cash_flow.columns = [col.strftime('%Y-%m-%d') if hasattr(col, 'strftime') else str(col) for col in cash_flow.columns]
        
        # Select key metrics
        key_metrics = [
            'Operating Cash Flow',
            'Cash Flow From Investment',
            'Cash Flow From Financing',
            'Free Cash Flow',
            'Change In Cash'
        ]
        
        # Map standard names to possible variations in yfinance data
        metric_variations = {
            'Operating Cash Flow': ['Operating Cash Flow', 'Total Cash From Operating Activities'],
            'Cash Flow From Investment': ['Cash Flow From Investment', 'Total Cash From Investing Activities', 'Total Cashflows From Investing Activities'],
            'Cash Flow From Financing': ['Cash Flow From Financing', 'Total Cash From Financing Activities', 'Total Cash From Financing Activities'],
            'Free Cash Flow': ['Free Cash Flow'],
            'Change In Cash': ['Change In Cash', 'Change In Cash And Cash Equivalents']
        }
        
        # Find available metrics
        available_metrics = []
        metric_mapping = {}
        
        for standard_name, variations in metric_variations.items():
            for var in variations:
                if var in cash_flow.index:
                    available_metrics.append(var)
                    metric_mapping[var] = standard_name
                    break
        
        if not available_metrics:
            # If none of the key metrics are available, use what we have
            available_metrics = list(cash_flow.index)[:5]  # First 5 metrics
            for metric in available_metrics:
                metric_mapping[metric] = metric
        
        # Create a new DataFrame with only the key metrics
        chart_data = cash_flow.loc[available_metrics]
        
        # Transpose so dates become rows
        chart_data = chart_data.transpose()
        chart_data.index = pd.to_datetime(chart_data.index)
        chart_data = chart_data.sort_index()
        
        # Reset index to make Date a column
        chart_data.reset_index(inplace=True)
        chart_data.rename(columns={'index': 'Date'}, inplace=True)
        
        # Rename columns to standard names
        chart_data.rename(columns=metric_mapping, inplace=True)
        
        # Use standard names in the chart
        standard_names = list(set(metric_mapping.values()))
        
        colors = ['#1E88E5', '#E53935', '#43A047', '#9C27B0', '#FF9800']
        
        for i, metric in enumerate(standard_names):
            if metric in chart_data.columns:
                chart_fig.add_trace(
                    go.Bar(
                        x=chart_data['Date'],
                        y=chart_data[metric],
                        name=metric,
                        marker_color=colors[i % len(colors)]
                    )
                )
        
        # Update layout
        chart_fig.update_layout(
            title=f"Cash Flow - {symbol.replace('.NS', '')} ({period.capitalize()})",
            xaxis_title="Date",
            yaxis_title="Amount (₹)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500,
            margin=dict(l=50, r=50, t=80, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(
                family="Roboto, sans-serif",
                size=12,
                color="#212121"
            )
        )
        
        # Create table with full cash flow
        table_data = cash_flow.copy()
        
        # Format numbers
        for col in table_data.columns:
            table_data[col] = table_data[col].apply(lambda x: format_large_number(x) if pd.notnull(x) else "N/A")
        
        table_fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=['Metric'] + list(table_data.columns),
                        font=dict(size=12, color='white'),
                        fill_color='#1E88E5',
                        align='left'
                    ),
                    cells=dict(
                        values=[table_data.index] + [table_data[col] for col in table_data.columns],
                        font=dict(size=11),
                        fill_color='white',
                        align=['left'] + ['right'] * len(table_data.columns)
                    )
                )
            ]
        )
        
        table_fig.update_layout(
            title=f"Detailed Cash Flow - {symbol.replace('.NS', '')} ({period.capitalize()})",
            height=400 + 30 * len(table_data.index),  # Adjust height based on number of rows
            margin=dict(l=20, r=20, t=80, b=20),
            font=dict(
                family="Roboto, sans-serif",
                size=12,
                color="#212121"
            )
        )
    except Exception as e:
        print(f"Error creating cash flow chart: {e}")
        for fig in [chart_fig, table_fig]:
            fig.add_annotation(
                text="Error creating cash flow visualization",
                align="center",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                font=dict(size=14),
            )
    
    return chart_fig, table_fig
