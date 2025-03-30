import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots

def create_candlestick_chart(data, title="Stock Price Chart", include_volume=True):
    """
    Create a candlestick chart with volume bars
    
    Parameters:
        data (pd.DataFrame): DataFrame with OHLCV data
        title (str): Chart title
        include_volume (bool): Whether to include volume bars
        
    Returns:
        plotly.graph_objects.Figure: Candlestick chart
    """
    # Create subplot layout
    if include_volume:
        fig = make_subplots(
            rows=2, 
            cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.02, 
            row_heights=[0.8, 0.2]
        )
    else:
        fig = go.Figure()
    
    # Add candlestick chart
    candlestick = go.Candlestick(
        x=data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Price",
        increasing_line_color='#26A69A',  # green
        decreasing_line_color='#EF5350',  # red
    )
    
    if include_volume:
        fig.add_trace(candlestick, row=1, col=1)
    else:
        fig.add_trace(candlestick)
    
    # Add volume bars if requested
    if include_volume and 'Volume' in data.columns:
        # Color volume bars based on price change
        colors = ['#26A69A' if data['Close'].iloc[i] >= data['Open'].iloc[i] else '#EF5350' 
                  for i in range(len(data))]
        
        fig.add_trace(
            go.Bar(
                x=data['Date'],
                y=data['Volume'],
                name="Volume",
                marker_color=colors,
                opacity=0.8,
            ),
            row=2, col=1
        )
        
        # Update y-axis for volume
        fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        xaxis_rangeslider_visible=False,
        height=600,
        width=None,  # Full width
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Roboto, sans-serif",
            size=12,
            color="#212121"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_line_chart(data, x_column, y_columns, title="Line Chart", colors=None):
    """
    Create a line chart for multiple series
    
    Parameters:
        data (pd.DataFrame): DataFrame with data
        x_column (str): Column name for x-axis
        y_columns (list): List of column names for y-axis
        title (str): Chart title
        colors (list): List of colors for each line
        
    Returns:
        plotly.graph_objects.Figure: Line chart
    """
    if colors is None:
        colors = ['#1E88E5', '#43A047', '#E53935', '#9C27B0', '#FF9800']
    
    fig = go.Figure()
    
    for i, column in enumerate(y_columns):
        fig.add_trace(
            go.Scatter(
                x=data[x_column],
                y=data[column],
                name=column,
                line=dict(color=colors[i % len(colors)], width=2),
                mode='lines'
            )
        )
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title=x_column,
        yaxis_title="Value",
        height=500,
        width=None,  # Full width
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Roboto, sans-serif",
            size=12,
            color="#212121"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_comparison_chart(data_dict, title="Stock Comparison"):
    """
    Create a comparison chart for multiple stocks
    
    Parameters:
        data_dict (dict): Dictionary with stock symbols as keys and DataFrames as values
        title (str): Chart title
        
    Returns:
        plotly.graph_objects.Figure: Comparison chart
    """
    fig = go.Figure()
    
    colors = ['#1E88E5', '#43A047', '#E53935', '#9C27B0', '#FF9800']
    
    for i, (symbol, data) in enumerate(data_dict.items()):
        # Calculate percentage change from the first day
        if len(data) > 0:
            first_price = data['Close'].iloc[0]
            pct_change = (data['Close'] / first_price - 1) * 100
            
            fig.add_trace(
                go.Scatter(
                    x=data['Date'],
                    y=pct_change,
                    name=symbol.replace('.NS', ''),
                    line=dict(color=colors[i % len(colors)], width=2),
                    mode='lines'
                )
            )
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Percentage Change (%)",
        height=500,
        width=None,  # Full width
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Roboto, sans-serif",
            size=12,
            color="#212121"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add horizontal reference line at 0%
    fig.add_shape(
        type="line",
        x0=fig.data[0].x[0] if fig.data else 0,
        y0=0,
        x1=fig.data[0].x[-1] if fig.data else 1,
        y1=0,
        line=dict(
            color="rgba(0, 0, 0, 0.3)",
            width=1,
            dash="dash"
        )
    )
    
    return fig


def create_sector_performance_chart(data, title="Sector Performance"):
    """
    Create a sector performance chart
    
    Parameters:
        data (pd.DataFrame): DataFrame with sector performance data
        title (str): Chart title
        
    Returns:
        plotly.graph_objects.Figure: Sector performance chart
    """
    fig = go.Figure()
    
    sectors = [col for col in data.columns if col != 'Date']
    colors = ['#1E88E5', '#43A047', '#E53935', '#9C27B0', '#FF9800']
    
    for i, sector in enumerate(sectors):
        fig.add_trace(
            go.Scatter(
                x=data['Date'],
                y=data[sector],
                name=sector,
                line=dict(color=colors[i % len(colors)], width=2),
                mode='lines'
            )
        )
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Performance (Base 100)",
        height=500,
        width=None,  # Full width
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Roboto, sans-serif",
            size=12,
            color="#212121"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add horizontal reference line at 100 (base)
    fig.add_shape(
        type="line",
        x0=data['Date'].iloc[0],
        y0=100,
        x1=data['Date'].iloc[-1],
        y1=100,
        line=dict(
            color="rgba(0, 0, 0, 0.3)",
            width=1,
            dash="dash"
        )
    )
    
    return fig


def create_heatmap(data, x_labels, y_labels, title="Correlation Heatmap"):
    """
    Create a heatmap for correlation or other matrix data
    
    Parameters:
        data (np.ndarray): 2D array of values
        x_labels (list): Labels for x-axis
        y_labels (list): Labels for y-axis
        title (str): Chart title
        
    Returns:
        plotly.graph_objects.Figure: Heatmap
    """
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=x_labels,
        y=y_labels,
        colorscale='RdBu_r',  # Red-Blue diverging colorscale
        zmid=0,  # Center the colorscale at 0
        colorbar=dict(
            title="Value",
            titleside="right"
        )
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        height=600,
        width=None,  # Full width
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Roboto, sans-serif",
            size=12,
            color="#212121"
        )
    )
    
    return fig


def create_pie_chart(values, labels, title="Pie Chart"):
    """
    Create a pie chart
    
    Parameters:
        values (list): Values for sectors
        labels (list): Labels for sectors
        title (str): Chart title
        
    Returns:
        plotly.graph_objects.Figure: Pie chart
    """
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        textinfo='percent+label',
        insidetextorientation='radial',
        marker=dict(
            colors=['#1E88E5', '#43A047', '#E53935', '#9C27B0', '#FF9800', 
                    '#00ACC1', '#F57C00', '#8E24AA', '#5C6BC0', '#66BB6A']
        )
    )])
    
    # Update layout
    fig.update_layout(
        title=title,
        height=500,
        width=None,  # Full width
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Roboto, sans-serif",
            size=12,
            color="#212121"
        )
    )
    
    return fig


def create_bar_chart(x, y, names=None, title="Bar Chart", orientation='v'):
    """
    Create a bar chart
    
    Parameters:
        x (list): X values
        y (list): Y values
        names (list): Names for bars
        title (str): Chart title
        orientation (str): 'v' for vertical, 'h' for horizontal
        
    Returns:
        plotly.graph_objects.Figure: Bar chart
    """
    if orientation == 'v':
        # Vertical bar chart
        fig = go.Figure(data=[go.Bar(
            x=x,
            y=y,
            name=names[i] if names else None,
            marker_color=['#1E88E5', '#43A047', '#E53935', '#9C27B0', '#FF9800']
        )])
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="X",
            yaxis_title="Y",
        )
    else:
        # Horizontal bar chart
        fig = go.Figure(data=[go.Bar(
            y=x,
            x=y,
            name=names[i] if names else None,
            marker_color=['#1E88E5', '#43A047', '#E53935', '#9C27B0', '#FF9800'],
            orientation='h'
        )])
        
        # Update layout
        fig.update_layout(
            title=title,
            yaxis_title="Y",
            xaxis_title="X",
        )
    
    # Common layout settings
    fig.update_layout(
        height=500,
        width=None,  # Full width
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Roboto, sans-serif",
            size=12,
            color="#212121"
        )
    )
    
    return fig
