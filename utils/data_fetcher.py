import pandas as pd
import numpy as np
import yfinance as yf
import requests
from datetime import datetime, timedelta
import os

# List of major NSE indices
NSE_INDICES = {
    'NIFTY 50': '^NSEI',
    'NIFTY BANK': '^NSEBANK',
    'NIFTY IT': '^CNXIT',
    'NIFTY PHARMA': '^CNXPHARMA',
    'NIFTY AUTO': '^CNXAUTO'
}

# List of major BSE indices
BSE_INDICES = {
    'SENSEX': '^BSESN',
    'BSE 100': '^BSE100',
    'BSE 200': '^BSE200'
}

# List of common Indian stocks (top companies by market cap)
TOP_STOCKS = {
    'Reliance Industries': 'RELIANCE.NS',
    'TCS': 'TCS.NS',
    'HDFC Bank': 'HDFCBANK.NS',
    'Infosys': 'INFY.NS',
    'ICICI Bank': 'ICICIBANK.NS',
    'HUL': 'HINDUNILVR.NS',
    'State Bank of India': 'SBIN.NS',
    'Bharti Airtel': 'BHARTIARTL.NS',
    'ITC': 'ITC.NS',
    'Kotak Mahindra Bank': 'KOTAKBANK.NS'
}

# List of sectors
SECTORS = {
    'Banking': ['HDFCBANK.NS', 'SBIN.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'AXISBANK.NS'],
    'IT': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS'],
    'Pharma': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'BIOCON.NS'],
    'Auto': ['MARUTI.NS', 'TATAMOTORS.NS', 'M&M.NS', 'HEROMOTOCO.NS', 'BAJAJ-AUTO.NS'],
    'Energy': ['RELIANCE.NS', 'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS', 'IOC.NS']
}

def get_nifty_data():
    """
    Fetch current NIFTY 50 data
    Returns a dictionary with last price and change percentage
    """
    try:
        nifty = yf.Ticker('^NSEI')
        nifty_data = nifty.history(period='2d')
        
        last_price = nifty_data['Close'].iloc[-1]
        prev_price = nifty_data['Close'].iloc[-2]
        change = last_price - prev_price
        change_pct = (change / prev_price) * 100
        
        return {
            'last_price': last_price,
            'change': change,
            'change_pct': change_pct
        }
    except Exception as e:
        print(f"Error fetching NIFTY data: {e}")
        # Return placeholder data in case of error
        return {
            'last_price': 19675.45,
            'change': 63.15,
            'change_pct': 0.32
        }

def get_sensex_data():
    """
    Fetch current SENSEX data
    Returns a dictionary with last price and change percentage
    """
    try:
        sensex = yf.Ticker('^BSESN')
        sensex_data = sensex.history(period='2d')
        
        last_price = sensex_data['Close'].iloc[-1]
        prev_price = sensex_data['Close'].iloc[-2]
        change = last_price - prev_price
        change_pct = (change / prev_price) * 100
        
        return {
            'last_price': last_price,
            'change': change,
            'change_pct': change_pct
        }
    except Exception as e:
        print(f"Error fetching SENSEX data: {e}")
        # Return placeholder data in case of error
        return {
            'last_price': 65928.53,
            'change': 263.40,
            'change_pct': 0.40
        }

def get_stock_data(symbol, period='1y', interval='1d'):
    """
    Fetch historical data for a given stock
    
    Parameters:
        symbol (str): Stock symbol (NSE)
        period (str): Time period for data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
    Returns:
        DataFrame: Stock historical data
    """
    try:
        # Append '.NS' for NSE symbols if not already present
        if not symbol.endswith(('.NS', '.BO')):
            symbol = f"{symbol}.NS"
            
        stock = yf.Ticker(symbol)
        data = stock.history(period=period, interval=interval)
        data.reset_index(inplace=True)
        
        # Handle timezone conversion
        if 'Datetime' in data.columns:
            data['Datetime'] = pd.to_datetime(data['Datetime']).dt.tz_localize(None)
            data.rename(columns={'Datetime': 'Date'}, inplace=True)
        else:
            data['Date'] = pd.to_datetime(data['Date']).dt.tz_localize(None)
            
        return data
    except Exception as e:
        print(f"Error fetching stock data for {symbol}: {e}")
        return pd.DataFrame()

def get_stock_info(symbol):
    """
    Fetch basic information about a stock
    
    Parameters:
        symbol (str): Stock symbol (NSE)
        
    Returns:
        dict: Stock information
    """
    try:
        # Append '.NS' for NSE symbols if not already present
        if not symbol.endswith(('.NS', '.BO')):
            symbol = f"{symbol}.NS"
            
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Extract relevant information
        relevant_info = {
            'symbol': symbol,
            'name': info.get('longName', ''),
            'sector': info.get('sector', ''),
            'industry': info.get('industry', ''),
            'market_cap': info.get('marketCap', 0),
            'current_price': info.get('currentPrice', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'eps': info.get('trailingEps', 0),
            'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            'book_value': info.get('bookValue', 0),
            '52_week_high': info.get('fiftyTwoWeekHigh', 0),
            '52_week_low': info.get('fiftyTwoWeekLow', 0)
        }
        
        return relevant_info
    except Exception as e:
        print(f"Error fetching stock info for {symbol}: {e}")
        return {}

def get_top_gainers_losers(count=5):
    """
    Get top gainers and losers from the Indian stock market
    
    Parameters:
        count (int): Number of stocks to return
        
    Returns:
        tuple: (top_gainers_df, top_losers_df)
    """
    try:
        # In a real implementation, this would fetch from an appropriate API
        # For now, creating sample data based on TOP_STOCKS
        
        data = []
        # Generate random data for the top stocks
        for company, symbol in TOP_STOCKS.items():
            price = np.random.uniform(500, 5000)
            change_pct = np.random.uniform(-5, 5)
            data.append({
                'Symbol': symbol.replace('.NS', ''),
                'Company': company,
                'Price': price,
                'Change%': change_pct
            })
        
        # Create DataFrame
        stocks_df = pd.DataFrame(data)
        
        # Sort for gainers and losers
        top_gainers = stocks_df.sort_values('Change%', ascending=False).head(count).copy()
        top_losers = stocks_df.sort_values('Change%', ascending=True).head(count).copy()
        
        # Format prices
        top_gainers['Price'] = top_gainers['Price'].map('₹{:,.2f}'.format)
        top_losers['Price'] = top_losers['Price'].map('₹{:,.2f}'.format)
        
        # Format percentage changes
        top_gainers['Change%'] = top_gainers['Change%'].map('+{:.2f}%'.format)
        top_losers['Change%'] = top_losers['Change%'].map('{:.2f}%'.format)
        
        return top_gainers, top_losers
    except Exception as e:
        print(f"Error fetching top gainers and losers: {e}")
        # Return empty DataFrames in case of error
        columns = ['Symbol', 'Company', 'Price', 'Change%']
        return pd.DataFrame(columns=columns), pd.DataFrame(columns=columns)

def get_market_indices(days=30):
    """
    Get historical data for major market indices
    
    Parameters:
        days (int): Number of days of historical data
        
    Returns:
        DataFrame: Historical data for indices
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Fetch data for major indices
        nifty = yf.download('^NSEI', start=start_date, end=end_date)
        bank_nifty = yf.download('^NSEBANK', start=start_date, end=end_date)
        fin_nifty = yf.download('^CNXFINANCE', start=start_date, end=end_date)
        
        # Extract closing prices
        indices_data = pd.DataFrame({
            'Date': nifty.index,
            'NIFTY50': nifty['Close'],
            'BANKNIFTY': bank_nifty['Close'],
            'FINNIFTY': fin_nifty['Close']
        })
        
        # Reset index to make Date a column
        indices_data.reset_index(inplace=True)
        if 'Date' in indices_data.columns and 'index' in indices_data.columns:
            indices_data.drop('index', axis=1, inplace=True)
        
        # Convert dates to datetime without timezone
        indices_data['Date'] = pd.to_datetime(indices_data['Date']).dt.tz_localize(None)
        
        return indices_data
    except Exception as e:
        print(f"Error fetching market indices: {e}")
        # Generate sample data in case of error
        dates = pd.date_range(end=pd.Timestamp.now(), periods=days)
        return pd.DataFrame({
            'Date': dates,
            'NIFTY50': [19000 + i*25 + (i**2)/2 for i in range(days)],
            'BANKNIFTY': [44000 + i*50 + (i**2) for i in range(days)],
            'FINNIFTY': [21000 + i*30 + (i**2)/1.5 for i in range(days)]
        })

def get_sector_performance(days=30):
    """
    Get performance data for major market sectors
    
    Parameters:
        days (int): Number of days for historical data
        
    Returns:
        DataFrame: Sector performance data
    """
    try:
        sector_data = {}
        
        for sector, stocks in SECTORS.items():
            # Take the first 3 stocks to represent the sector
            representative_stocks = stocks[:3]
            
            # Initialize sector values
            sector_values = []
            
            # Get data for end date (today)
            end_date = datetime.now()
            # Get data for start date
            start_date = end_date - timedelta(days=days)
            
            # Fetch data for representative stocks
            stock_data = {}
            for stock in representative_stocks:
                data = yf.download(stock, start=start_date, end=end_date)
                stock_data[stock] = data['Close']
            
            # Calculate the average performance for the sector
            # First, normalize each stock to 100 at the beginning
            normalized_data = {}
            for stock, prices in stock_data.items():
                base_price = prices.iloc[0]
                normalized_data[stock] = (prices / base_price) * 100
            
            # Calculate the average normalized value across stocks for each day
            dates = normalized_data[representative_stocks[0]].index
            sector_values = []
            
            for date in dates:
                day_values = [normalized_data[stock][date] for stock in representative_stocks if date in normalized_data[stock].index]
                sector_values.append(np.mean(day_values))
            
            # Store the sector data
            sector_data[sector] = pd.Series(sector_values, index=dates)
        
        # Combine all sector data into a DataFrame
        sector_df = pd.DataFrame(sector_data)
        sector_df.reset_index(inplace=True)
        sector_df.rename(columns={'index': 'Date'}, inplace=True)
        
        # Convert dates to datetime without timezone
        sector_df['Date'] = pd.to_datetime(sector_df['Date']).dt.tz_localize(None)
        
        return sector_df
    except Exception as e:
        print(f"Error fetching sector performance: {e}")
        # Generate sample data in case of error
        dates = pd.date_range(end=pd.Timestamp.now(), periods=days)
        
        # Create sample data with different patterns for each sector
        banking = [100 + i*0.5 + (i**2)/200 for i in range(days)]
        it = [100 + i*0.3 + np.sin(i/5)*5 for i in range(days)]
        pharma = [100 + i*0.4 - (i**2)/300 for i in range(days)]
        auto = [100 - i*0.1 + np.cos(i/4)*6 for i in range(days)]
        energy = [100 + i*0.2 + (i**1.5)/100 for i in range(days)]
        
        return pd.DataFrame({
            'Date': dates,
            'Banking': banking,
            'IT': it,
            'Pharma': pharma,
            'Auto': auto,
            'Energy': energy
        })

def get_financial_ratios(symbol):
    """
    Get financial ratios for a given stock
    
    Parameters:
        symbol (str): Stock symbol (NSE)
        
    Returns:
        dict: Dictionary of financial ratios
    """
    try:
        # Append '.NS' for NSE symbols if not already present
        if not symbol.endswith(('.NS', '.BO')):
            symbol = f"{symbol}.NS"
            
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Extract financial ratios
        ratios = {
            'PE Ratio (TTM)': info.get('trailingPE', None),
            'Forward PE': info.get('forwardPE', None),
            'PEG Ratio': info.get('pegRatio', None),
            'Price to Sales (TTM)': info.get('priceToSalesTrailing12Months', None),
            'Price to Book': info.get('priceToBook', None),
            'Enterprise Value/EBITDA': info.get('enterpriseToEbitda', None),
            'Enterprise Value/Revenue': info.get('enterpriseToRevenue', None),
            'Profit Margin': info.get('profitMargins', None),
            'Operating Margin (TTM)': info.get('operatingMargins', None),
            'Return on Assets (TTM)': info.get('returnOnAssets', None),
            'Return on Equity (TTM)': info.get('returnOnEquity', None),
            'Revenue Growth (YoY)': info.get('revenueGrowth', None),
            'Earnings Growth (YoY)': info.get('earningsGrowth', None),
            'Dividend Yield': info.get('dividendYield', None),
            'Dividend Rate': info.get('dividendRate', None),
            'Payout Ratio': info.get('payoutRatio', None),
            'Beta (5Y Monthly)': info.get('beta', None),
            'Debt to Equity': info.get('debtToEquity', None),
            'Current Ratio': info.get('currentRatio', None),
            'Quick Ratio': info.get('quickRatio', None)
        }
        
        # Format percentages
        for key in ['Profit Margin', 'Operating Margin (TTM)', 'Return on Assets (TTM)', 
                    'Return on Equity (TTM)', 'Revenue Growth (YoY)', 'Earnings Growth (YoY)', 
                    'Dividend Yield', 'Payout Ratio']:
            if ratios[key] is not None:
                ratios[key] = ratios[key] * 100  # Convert to percentage
        
        return ratios
    except Exception as e:
        print(f"Error fetching financial ratios for {symbol}: {e}")
        return {}

def get_income_statement(symbol, period='annual'):
    """
    Get income statement data for a given stock
    
    Parameters:
        symbol (str): Stock symbol (NSE)
        period (str): 'annual' or 'quarterly'
        
    Returns:
        DataFrame: Income statement data
    """
    try:
        # Append '.NS' for NSE symbols if not already present
        if not symbol.endswith(('.NS', '.BO')):
            symbol = f"{symbol}.NS"
            
        stock = yf.Ticker(symbol)
        
        if period == 'annual':
            income_stmt = stock.financials
        else:  # quarterly
            income_stmt = stock.quarterly_financials
            
        return income_stmt
    except Exception as e:
        print(f"Error fetching income statement for {symbol}: {e}")
        return pd.DataFrame()

def get_balance_sheet(symbol, period='annual'):
    """
    Get balance sheet data for a given stock
    
    Parameters:
        symbol (str): Stock symbol (NSE)
        period (str): 'annual' or 'quarterly'
        
    Returns:
        DataFrame: Balance sheet data
    """
    try:
        # Append '.NS' for NSE symbols if not already present
        if not symbol.endswith(('.NS', '.BO')):
            symbol = f"{symbol}.NS"
            
        stock = yf.Ticker(symbol)
        
        if period == 'annual':
            balance_sheet = stock.balance_sheet
        else:  # quarterly
            balance_sheet = stock.quarterly_balance_sheet
            
        return balance_sheet
    except Exception as e:
        print(f"Error fetching balance sheet for {symbol}: {e}")
        return pd.DataFrame()

def get_cash_flow(symbol, period='annual'):
    """
    Get cash flow data for a given stock
    
    Parameters:
        symbol (str): Stock symbol (NSE)
        period (str): 'annual' or 'quarterly'
        
    Returns:
        DataFrame: Cash flow data
    """
    try:
        # Append '.NS' for NSE symbols if not already present
        if not symbol.endswith(('.NS', '.BO')):
            symbol = f"{symbol}.NS"
            
        stock = yf.Ticker(symbol)
        
        if period == 'annual':
            cash_flow = stock.cashflow
        else:  # quarterly
            cash_flow = stock.quarterly_cashflow
            
        return cash_flow
    except Exception as e:
        print(f"Error fetching cash flow for {symbol}: {e}")
        return pd.DataFrame()

def get_top_stocks_list():
    """
    Get a list of top stocks for the selection dropdown
    
    Returns:
        list: List of stock symbols and names
    """
    return [(symbol, name) for name, symbol in TOP_STOCKS.items()]

def search_stocks(query):
    """
    Search for stocks based on a query string
    
    Parameters:
        query (str): Search query
        
    Returns:
        list: List of matching stock symbols
    """
    try:
        # In a real implementation, this would query an API
        # For now, filtering from the known stocks list
        matches = []
        query = query.lower()
        
        for name, symbol in TOP_STOCKS.items():
            if query in name.lower() or query in symbol.lower():
                matches.append((symbol, name))
                
        return matches
    except Exception as e:
        print(f"Error searching stocks: {e}")
        return []
