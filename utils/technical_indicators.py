import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def add_moving_average(fig, data, window, column='Close', name=None, color=None, row=1, col=1):
    """
    Add a simple moving average to a plotly figure
    
    Parameters:
        fig (plotly.graph_objects.Figure): Plotly figure to add the MA to
        data (pd.DataFrame): DataFrame containing the price data
        window (int): Window size for the moving average
        column (str): Column name to calculate MA on (default: 'Close')
        name (str): Name for the MA line (default: f'{window}-day MA')
        color (str): Color for the MA line
        row (int): Row in subplot grid
        col (int): Column in subplot grid
        
    Returns:
        plotly.graph_objects.Figure: Updated figure with MA
    """
    ma = data[column].rolling(window=window).mean()
    
    if name is None:
        name = f'{window}-day MA'
        
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=ma,
            name=name,
            line=dict(color=color, width=1.5),
        ),
        row=row,
        col=col
    )
    
    return fig


def add_exponential_moving_average(fig, data, window, column='Close', name=None, color=None, row=1, col=1):
    """
    Add an exponential moving average to a plotly figure
    
    Parameters:
        fig (plotly.graph_objects.Figure): Plotly figure to add the EMA to
        data (pd.DataFrame): DataFrame containing the price data
        window (int): Window size for the exponential moving average
        column (str): Column name to calculate EMA on (default: 'Close')
        name (str): Name for the EMA line (default: f'{window}-day EMA')
        color (str): Color for the EMA line
        row (int): Row in subplot grid
        col (int): Column in subplot grid
        
    Returns:
        plotly.graph_objects.Figure: Updated figure with EMA
    """
    ema = data[column].ewm(span=window, adjust=False).mean()
    
    if name is None:
        name = f'{window}-day EMA'
        
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=ema,
            name=name,
            line=dict(color=color, width=1.5),
        ),
        row=row,
        col=col
    )
    
    return fig


def add_bollinger_bands(fig, data, window=20, num_std=2, column='Close', row=1, col=1):
    """
    Add Bollinger Bands to a plotly figure
    
    Parameters:
        fig (plotly.graph_objects.Figure): Plotly figure to add the Bollinger Bands to
        data (pd.DataFrame): DataFrame containing the price data
        window (int): Window size for the moving average
        num_std (int): Number of standard deviations for the bands
        column (str): Column name to calculate bands on (default: 'Close')
        row (int): Row in subplot grid
        col (int): Column in subplot grid
        
    Returns:
        plotly.graph_objects.Figure: Updated figure with Bollinger Bands
    """
    ma = data[column].rolling(window=window).mean()
    std = data[column].rolling(window=window).std()
    
    upper_band = ma + (std * num_std)
    lower_band = ma - (std * num_std)
    
    # Add the moving average
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=ma,
            name=f'{window}-day MA',
            line=dict(color='rgba(30, 136, 229, 0.8)', width=1),
        ),
        row=row,
        col=col
    )
    
    # Add the upper band
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=upper_band,
            name='Upper Band',
            line=dict(color='rgba(0, 0, 0, 0)'),
            showlegend=False,
        ),
        row=row,
        col=col
    )
    
    # Add the lower band
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=lower_band,
            name='Lower Band',
            line=dict(color='rgba(0, 0, 0, 0)'),
            fill='tonexty',
            fillcolor='rgba(30, 136, 229, 0.1)',
            showlegend=False,
        ),
        row=row,
        col=col
    )
    
    # Add the upper band (visible line)
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=upper_band,
            name='Upper Band',
            line=dict(color='rgba(30, 136, 229, 0.5)', width=1, dash='dash'),
        ),
        row=row,
        col=col
    )
    
    # Add the lower band (visible line)
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=lower_band,
            name='Lower Band',
            line=dict(color='rgba(30, 136, 229, 0.5)', width=1, dash='dash'),
        ),
        row=row,
        col=col
    )
    
    return fig


def calculate_rsi(data, window=14, column='Close'):
    """
    Calculate the Relative Strength Index (RSI)
    
    Parameters:
        data (pd.DataFrame): DataFrame containing the price data
        window (int): Window size for RSI calculation (default: 14)
        column (str): Column name to calculate RSI on (default: 'Close')
        
    Returns:
        pd.Series: RSI values
    """
    delta = data[column].diff()
    
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def add_rsi(fig, data, window=14, column='Close', row=2, col=1):
    """
    Add Relative Strength Index (RSI) to a plotly figure
    
    Parameters:
        fig (plotly.graph_objects.Figure): Plotly figure to add the RSI to
        data (pd.DataFrame): DataFrame containing the price data
        window (int): Window size for RSI calculation (default: 14)
        column (str): Column name to calculate RSI on (default: 'Close')
        row (int): Row in subplot grid
        col (int): Column in subplot grid
        
    Returns:
        plotly.graph_objects.Figure: Updated figure with RSI
    """
    rsi = calculate_rsi(data, window, column)
    
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=rsi,
            name=f'RSI ({window})',
            line=dict(color='#E53935', width=1.5),
        ),
        row=row,
        col=col
    )
    
    # Add overbought line
    fig.add_trace(
        go.Scatter(
            x=[data['Date'].iloc[0], data['Date'].iloc[-1]],
            y=[70, 70],
            name='Overbought',
            line=dict(color='rgba(229, 57, 53, 0.3)', width=1, dash='dash'),
            showlegend=False,
        ),
        row=row,
        col=col
    )
    
    # Add oversold line
    fig.add_trace(
        go.Scatter(
            x=[data['Date'].iloc[0], data['Date'].iloc[-1]],
            y=[30, 30],
            name='Oversold',
            line=dict(color='rgba(67, 160, 71, 0.3)', width=1, dash='dash'),
            showlegend=False,
        ),
        row=row,
        col=col
    )
    
    # Add middle line
    fig.add_trace(
        go.Scatter(
            x=[data['Date'].iloc[0], data['Date'].iloc[-1]],
            y=[50, 50],
            name='Middle',
            line=dict(color='rgba(0, 0, 0, 0.2)', width=1, dash='dash'),
            showlegend=False,
        ),
        row=row,
        col=col
    )
    
    # Update y-axis
    fig.update_yaxes(
        title_text="RSI",
        range=[0, 100],
        row=row,
        col=col
    )
    
    return fig


def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9, column='Close'):
    """
    Calculate the Moving Average Convergence Divergence (MACD)
    
    Parameters:
        data (pd.DataFrame): DataFrame containing the price data
        fast_period (int): Fast period for EMA calculation (default: 12)
        slow_period (int): Slow period for EMA calculation (default: 26)
        signal_period (int): Signal line period (default: 9)
        column (str): Column name to calculate MACD on (default: 'Close')
        
    Returns:
        tuple: MACD line, Signal line, Histogram
    """
    fast_ema = data[column].ewm(span=fast_period, adjust=False).mean()
    slow_ema = data[column].ewm(span=slow_period, adjust=False).mean()
    
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def add_macd(fig, data, fast_period=12, slow_period=26, signal_period=9, column='Close', row=3, col=1):
    """
    Add Moving Average Convergence Divergence (MACD) to a plotly figure
    
    Parameters:
        fig (plotly.graph_objects.Figure): Plotly figure to add the MACD to
        data (pd.DataFrame): DataFrame containing the price data
        fast_period (int): Fast period for EMA calculation (default: 12)
        slow_period (int): Slow period for EMA calculation (default: 26)
        signal_period (int): Signal line period (default: 9)
        column (str): Column name to calculate MACD on (default: 'Close')
        row (int): Row in subplot grid
        col (int): Column in subplot grid
        
    Returns:
        plotly.graph_objects.Figure: Updated figure with MACD
    """
    macd_line, signal_line, histogram = calculate_macd(data, fast_period, slow_period, signal_period, column)
    
    # Add MACD line
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=macd_line,
            name='MACD',
            line=dict(color='#1E88E5', width=1.5),
        ),
        row=row,
        col=col
    )
    
    # Add Signal line
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=signal_line,
            name='Signal',
            line=dict(color='#FF9800', width=1.5),
        ),
        row=row,
        col=col
    )
    
    # Add Histogram
    colors = ['#43A047' if val >= 0 else '#E53935' for val in histogram]
    
    fig.add_trace(
        go.Bar(
            x=data['Date'],
            y=histogram,
            name='Histogram',
            marker_color=colors,
            opacity=0.5,
        ),
        row=row,
        col=col
    )
    
    # Update y-axis
    fig.update_yaxes(
        title_text="MACD",
        row=row,
        col=col
    )
    
    return fig


def calculate_stochastic(data, k_period=14, d_period=3, smooth_k=3):
    """
    Calculate the Stochastic Oscillator
    
    Parameters:
        data (pd.DataFrame): DataFrame containing the price data
        k_period (int): K period (default: 14)
        d_period (int): D period (default: 3)
        smooth_k (int): Smoothing for K (default: 3)
        
    Returns:
        tuple: %K, %D
    """
    low_min = data['Low'].rolling(window=k_period).min()
    high_max = data['High'].rolling(window=k_period).max()
    
    # Fast %K
    fast_k = 100 * ((data['Close'] - low_min) / (high_max - low_min))
    
    # Slow %K (smoothed fast %K)
    k = fast_k.rolling(window=smooth_k).mean()
    
    # Slow %D
    d = k.rolling(window=d_period).mean()
    
    return k, d


def add_stochastic(fig, data, k_period=14, d_period=3, smooth_k=3, row=4, col=1):
    """
    Add Stochastic Oscillator to a plotly figure
    
    Parameters:
        fig (plotly.graph_objects.Figure): Plotly figure to add the Stochastic to
        data (pd.DataFrame): DataFrame containing the price data
        k_period (int): K period (default: 14)
        d_period (int): D period (default: 3)
        smooth_k (int): Smoothing for K (default: 3)
        row (int): Row in subplot grid
        col (int): Column in subplot grid
        
    Returns:
        plotly.graph_objects.Figure: Updated figure with Stochastic
    """
    k, d = calculate_stochastic(data, k_period, d_period, smooth_k)
    
    # Add %K line
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=k,
            name='%K',
            line=dict(color='#1E88E5', width=1.5),
        ),
        row=row,
        col=col
    )
    
    # Add %D line
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=d,
            name='%D',
            line=dict(color='#FF9800', width=1.5),
        ),
        row=row,
        col=col
    )
    
    # Add overbought line
    fig.add_trace(
        go.Scatter(
            x=[data['Date'].iloc[0], data['Date'].iloc[-1]],
            y=[80, 80],
            name='Overbought',
            line=dict(color='rgba(229, 57, 53, 0.3)', width=1, dash='dash'),
            showlegend=False,
        ),
        row=row,
        col=col
    )
    
    # Add oversold line
    fig.add_trace(
        go.Scatter(
            x=[data['Date'].iloc[0], data['Date'].iloc[-1]],
            y=[20, 20],
            name='Oversold',
            line=dict(color='rgba(67, 160, 71, 0.3)', width=1, dash='dash'),
            showlegend=False,
        ),
        row=row,
        col=col
    )
    
    # Update y-axis
    fig.update_yaxes(
        title_text="Stochastic",
        range=[0, 100],
        row=row,
        col=col
    )
    
    return fig


def calculate_atr(data, window=14):
    """
    Calculate the Average True Range (ATR)
    
    Parameters:
        data (pd.DataFrame): DataFrame containing the price data
        window (int): Window size for ATR calculation (default: 14)
        
    Returns:
        pd.Series: ATR values
    """
    high_low = data['High'] - data['Low']
    high_close = (data['High'] - data['Close'].shift()).abs()
    low_close = (data['Low'] - data['Close'].shift()).abs()
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    
    atr = true_range.rolling(window=window).mean()
    
    return atr


def add_atr(fig, data, window=14, row=5, col=1):
    """
    Add Average True Range (ATR) to a plotly figure
    
    Parameters:
        fig (plotly.graph_objects.Figure): Plotly figure to add the ATR to
        data (pd.DataFrame): DataFrame containing the price data
        window (int): Window size for ATR calculation (default: 14)
        row (int): Row in subplot grid
        col (int): Column in subplot grid
        
    Returns:
        plotly.graph_objects.Figure: Updated figure with ATR
    """
    atr = calculate_atr(data, window)
    
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=atr,
            name=f'ATR ({window})',
            line=dict(color='#9C27B0', width=1.5),
        ),
        row=row,
        col=col
    )
    
    # Update y-axis
    fig.update_yaxes(
        title_text="ATR",
        row=row,
        col=col
    )
    
    return fig


def calculate_on_balance_volume(data):
    """
    Calculate On Balance Volume (OBV)
    
    Parameters:
        data (pd.DataFrame): DataFrame containing the price and volume data
        
    Returns:
        pd.Series: OBV values
    """
    obv = pd.Series(index=data.index, dtype='float64')
    obv.iloc[0] = 0
    
    for i in range(1, len(data)):
        if data['Close'].iloc[i] > data['Close'].iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + data['Volume'].iloc[i]
        elif data['Close'].iloc[i] < data['Close'].iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - data['Volume'].iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]
    
    return obv


def add_obv(fig, data, row=6, col=1):
    """
    Add On Balance Volume (OBV) to a plotly figure
    
    Parameters:
        fig (plotly.graph_objects.Figure): Plotly figure to add the OBV to
        data (pd.DataFrame): DataFrame containing the price and volume data
        row (int): Row in subplot grid
        col (int): Column in subplot grid
        
    Returns:
        plotly.graph_objects.Figure: Updated figure with OBV
    """
    obv = calculate_on_balance_volume(data)
    
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=obv,
            name='OBV',
            line=dict(color='#795548', width=1.5),
        ),
        row=row,
        col=col
    )
    
    # Add 20-day EMA of OBV
    obv_ema = obv.ewm(span=20, adjust=False).mean()
    
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=obv_ema,
            name='OBV EMA (20)',
            line=dict(color='#FFB300', width=1.5, dash='dash'),
        ),
        row=row,
        col=col
    )
    
    # Update y-axis
    fig.update_yaxes(
        title_text="OBV",
        row=row,
        col=col
    )
    
    return fig


def create_technical_chart(data, indicators=None):
    """
    Create a comprehensive technical analysis chart with selected indicators
    
    Parameters:
        data (pd.DataFrame): DataFrame containing the price data
        indicators (list): List of indicators to include
        
    Returns:
        plotly.graph_objects.Figure: Technical analysis chart
    """
    if indicators is None:
        indicators = ['sma', 'ema', 'bollinger']
    
    # Count the number of subplots needed
    subplot_count = 1  # Main price chart
    
    if 'rsi' in indicators:
        subplot_count += 1
    if 'macd' in indicators:
        subplot_count += 1
    if 'stoch' in indicators:
        subplot_count += 1
    if 'atr' in indicators:
        subplot_count += 1
    if 'obv' in indicators:
        subplot_count += 1
    
    # Create subplot heights
    heights = [0.5]  # Main price chart gets 50% of the height
    remaining_height = 0.5  # Remaining 50% for indicators
    
    if subplot_count > 1:
        indicator_height = remaining_height / (subplot_count - 1)
        heights.extend([indicator_height] * (subplot_count - 1))
    
    # Create subplots
    fig = make_subplots(
        rows=subplot_count,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=heights,
        subplot_titles=["Price Chart"]
    )
    
    # Add main price candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data['Date'],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price',
            increasing_line_color='#26A69A',  # green
            decreasing_line_color='#EF5350',  # red
        ),
        row=1,
        col=1
    )
    
    # Add volume bars
    colors = ['#26A69A' if data['Close'].iloc[i] >= data['Open'].iloc[i] else '#EF5350' 
              for i in range(len(data))]
    
    fig.add_trace(
        go.Bar(
            x=data['Date'],
            y=data['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.3,
            marker_line_width=0,
            showlegend=False
        ),
        row=1,
        col=1
    )
    
    # Add indicators to the main chart
    current_row = 1
    
    # Simple Moving Averages
    if 'sma' in indicators:
        fig = add_moving_average(fig, data, window=50, color='#1E88E5', row=1, col=1)
        fig = add_moving_average(fig, data, window=200, color='#E53935', row=1, col=1)
    
    # Exponential Moving Averages
    if 'ema' in indicators:
        fig = add_exponential_moving_average(fig, data, window=20, color='#FFB300', row=1, col=1)
    
    # Bollinger Bands
    if 'bollinger' in indicators:
        fig = add_bollinger_bands(fig, data, window=20, num_std=2, row=1, col=1)
    
    # RSI
    if 'rsi' in indicators:
        current_row += 1
        fig = add_rsi(fig, data, window=14, row=current_row, col=1)
        fig.update_layout(
            annotations=[
                dict(
                    text="RSI (14)",
                    xref="paper",
                    yref="paper",
                    x=0,
                    y=1 - (current_row - 1.5) * heights[current_row - 1],
                    xanchor="left",
                    yanchor="middle",
                    showarrow=False,
                    font=dict(size=12)
                )
            ]
        )
    
    # MACD
    if 'macd' in indicators:
        current_row += 1
        fig = add_macd(fig, data, row=current_row, col=1)
        fig.update_layout(
            annotations=[
                dict(
                    text="MACD",
                    xref="paper",
                    yref="paper",
                    x=0,
                    y=1 - (current_row - 1.5) * heights[current_row - 1],
                    xanchor="left",
                    yanchor="middle",
                    showarrow=False,
                    font=dict(size=12)
                )
            ]
        )
    
    # Stochastic Oscillator
    if 'stoch' in indicators:
        current_row += 1
        fig = add_stochastic(fig, data, row=current_row, col=1)
        fig.update_layout(
            annotations=[
                dict(
                    text="Stochastic",
                    xref="paper",
                    yref="paper",
                    x=0,
                    y=1 - (current_row - 1.5) * heights[current_row - 1],
                    xanchor="left",
                    yanchor="middle",
                    showarrow=False,
                    font=dict(size=12)
                )
            ]
        )
    
    # ATR
    if 'atr' in indicators:
        current_row += 1
        fig = add_atr(fig, data, row=current_row, col=1)
        fig.update_layout(
            annotations=[
                dict(
                    text="ATR (14)",
                    xref="paper",
                    yref="paper",
                    x=0,
                    y=1 - (current_row - 1.5) * heights[current_row - 1],
                    xanchor="left",
                    yanchor="middle",
                    showarrow=False,
                    font=dict(size=12)
                )
            ]
        )
    
    # OBV
    if 'obv' in indicators:
        current_row += 1
        fig = add_obv(fig, data, row=current_row, col=1)
        fig.update_layout(
            annotations=[
                dict(
                    text="On Balance Volume",
                    xref="paper",
                    yref="paper",
                    x=0,
                    y=1 - (current_row - 1.5) * heights[current_row - 1],
                    xanchor="left",
                    yanchor="middle",
                    showarrow=False,
                    font=dict(size=12)
                )
            ]
        )
    
    # Update layout
    fig.update_layout(
        title='Technical Analysis Chart',
        xaxis_rangeslider_visible=False,
        height=800,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=50, r=50, t=100, b=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Roboto, sans-serif",
            size=12,
            color="#212121"
        )
    )
    
    # Update y-axis for main price chart
    fig.update_yaxes(
        title_text="Price",
        row=1,
        col=1
    )
    
    # Update x-axis
    fig.update_xaxes(
        title_text="Date",
        rangeslider_visible=False,
        row=subplot_count,
        col=1
    )
    
    return fig
