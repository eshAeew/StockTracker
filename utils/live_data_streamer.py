import asyncio
import websockets
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

class LiveDataStreamer:
    """
    A class to manage live data streaming for stock prices.
    In a production environment, this would connect to a real-time market data API.
    For demonstration, it generates simulated tick data.
    """
    
    def __init__(self):
        self.is_running = False
        self.current_symbol = None
        self.current_price = 0
        self.price_history = []
        self.subscribers = set()
        self.candlestick_data = pd.DataFrame()
        self.last_update = datetime.now()
        self.timeframe = "1m"
        
    async def start_streaming(self, symbol, initial_price=None):
        """Start streaming data for a symbol"""
        self.is_running = True
        self.current_symbol = symbol
        
        # Set initial price
        if initial_price:
            self.current_price = initial_price
        else:
            # Random initial price between 100 and 5000
            self.current_price = np.random.uniform(100, 5000)
        
        # Initialize price history
        self.price_history = []
        
        # Initialize candlestick data
        self.candlestick_data = self._initialize_candlestick_data()
        
        # Start the streaming loop
        asyncio.create_task(self._stream_data())
        
    def stop_streaming(self):
        """Stop streaming data"""
        self.is_running = False
        
    async def _stream_data(self):
        """Generate and stream simulated tick data"""
        while self.is_running:
            # Calculate price movement (simulated)
            price_volatility = self.current_price * 0.0005  # 0.05% volatility per tick
            price_change = np.random.normal(0, price_volatility)
            
            # Update price
            self.current_price += price_change
            
            # Ensure price doesn't go below a minimum
            self.current_price = max(self.current_price, 1.0)
            
            # Create tick data
            tick_data = {
                'symbol': self.current_symbol,
                'price': self.current_price,
                'timestamp': datetime.now().isoformat(),
                'volume': np.random.randint(10, 1000)
            }
            
            # Add to price history (keep last 1000 ticks)
            self.price_history.append(tick_data)
            if len(self.price_history) > 1000:
                self.price_history = self.price_history[-1000:]
            
            # Update candlestick data
            self._update_candlestick_data(tick_data)
            
            # Notify subscribers
            await self._notify_subscribers(tick_data)
            
            # Pause briefly to simulate real-time (multiple ticks per second)
            await asyncio.sleep(0.2)  # 5 ticks per second
    
    def _initialize_candlestick_data(self):
        """Initialize candlestick data for different timeframes"""
        now = datetime.now()
        
        # Create times for the past 100 candles based on timeframe
        times = []
        if self.timeframe == "1m":
            times = [now - timedelta(minutes=i) for i in range(100, 0, -1)]
        elif self.timeframe == "5m":
            times = [now - timedelta(minutes=5*i) for i in range(100, 0, -1)]
        elif self.timeframe == "15m":
            times = [now - timedelta(minutes=15*i) for i in range(100, 0, -1)]
        elif self.timeframe == "30m":
            times = [now - timedelta(minutes=30*i) for i in range(100, 0, -1)]
        elif self.timeframe == "60m":
            times = [now - timedelta(hours=i) for i in range(100, 0, -1)]
        elif self.timeframe == "1d":
            times = [now - timedelta(days=i) for i in range(100, 0, -1)]
        else:
            # Default to 1-minute candles
            times = [now - timedelta(minutes=i) for i in range(100, 0, -1)]
        
        # Generate a price series with random walk
        prices = []
        price = self.current_price
        for i in range(100):
            price_volatility = price * 0.002  # 0.2% volatility between candles
            price_change = np.random.normal(0, price_volatility)
            price += price_change
            prices.append(price)
        
        # Create candlestick data
        candles = []
        for i in range(100):
            open_price = prices[i]
            
            # Randomize high, low, and close prices around the open
            price_volatility = open_price * 0.003  # 0.3% volatility within candle
            high_price = open_price + abs(np.random.normal(0, price_volatility))
            low_price = open_price - abs(np.random.normal(0, price_volatility))
            close_price = np.random.uniform(low_price, high_price)
            
            volume = np.random.randint(1000, 100000)
            
            candles.append({
                'Time': times[i],
                'Open': open_price,
                'High': high_price,
                'Low': low_price,
                'Close': close_price,
                'Volume': volume
            })
        
        # Create DataFrame
        df = pd.DataFrame(candles)
        df = df.sort_values('Time')
        
        return df
    
    def _update_candlestick_data(self, tick_data):
        """Update candlestick data with new tick"""
        now = datetime.now()
        price = tick_data['price']
        
        # Determine the current candle's time
        current_candle_time = None
        if self.timeframe == "1m":
            current_candle_time = datetime(now.year, now.month, now.day, now.hour, now.minute)
        elif self.timeframe == "5m":
            minute = (now.minute // 5) * 5
            current_candle_time = datetime(now.year, now.month, now.day, now.hour, minute)
        elif self.timeframe == "15m":
            minute = (now.minute // 15) * 15
            current_candle_time = datetime(now.year, now.month, now.day, now.hour, minute)
        elif self.timeframe == "30m":
            minute = (now.minute // 30) * 30
            current_candle_time = datetime(now.year, now.month, now.day, now.hour, minute)
        elif self.timeframe == "60m":
            current_candle_time = datetime(now.year, now.month, now.day, now.hour)
        elif self.timeframe == "1d":
            current_candle_time = datetime(now.year, now.month, now.day)
        else:
            # Default to 1-minute candles
            current_candle_time = datetime(now.year, now.month, now.day, now.hour, now.minute)
        
        # Check if the current candle exists in the data
        if current_candle_time in self.candlestick_data['Time'].values:
            # Update existing candle
            candle_idx = self.candlestick_data[self.candlestick_data['Time'] == current_candle_time].index[0]
            
            # Update high and low
            if price > self.candlestick_data.loc[candle_idx, 'High']:
                self.candlestick_data.loc[candle_idx, 'High'] = price
            
            if price < self.candlestick_data.loc[candle_idx, 'Low']:
                self.candlestick_data.loc[candle_idx, 'Low'] = price
            
            # Update close price
            self.candlestick_data.loc[candle_idx, 'Close'] = price
            
            # Update volume
            self.candlestick_data.loc[candle_idx, 'Volume'] += tick_data['volume']
        else:
            # Create a new candle
            new_candle = pd.DataFrame({
                'Time': [current_candle_time],
                'Open': [price],
                'High': [price],
                'Low': [price],
                'Close': [price],
                'Volume': [tick_data['volume']]
            })
            
            # Append the new candle
            self.candlestick_data = pd.concat([self.candlestick_data, new_candle], ignore_index=True)
            
            # Keep only the last 100 candles
            if len(self.candlestick_data) > 100:
                self.candlestick_data = self.candlestick_data.tail(100)
    
    async def _notify_subscribers(self, data):
        """Send data to all subscribers"""
        if not self.subscribers:
            return
            
        message = json.dumps(data)
        
        # List to track disconnected subscribers
        disconnected = set()
        
        for subscriber in self.subscribers:
            try:
                await subscriber.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(subscriber)
        
        # Remove disconnected subscribers
        self.subscribers -= disconnected
    
    async def register(self, websocket):
        """Register a new subscriber"""
        self.subscribers.add(websocket)
        
    async def unregister(self, websocket):
        """Unregister a subscriber"""
        self.subscribers.remove(websocket)
    
    def get_current_candlestick_data(self):
        """Get the current candlestick data"""
        return self.candlestick_data
    
    def set_timeframe(self, timeframe):
        """Set the candlestick timeframe"""
        if timeframe != self.timeframe:
            self.timeframe = timeframe
            self.candlestick_data = self._initialize_candlestick_data()
    
    def get_last_price(self):
        """Get the last price"""
        return self.current_price

# Create a global instance of the streamer
live_streamer = LiveDataStreamer()

# Server function to handle websocket connections
async def ws_handler(websocket, path):
    # Register the new client
    await live_streamer.register(websocket)
    
    try:
        async for message in websocket:
            # Process client messages (commands)
            try:
                cmd = json.loads(message)
                
                if cmd['action'] == 'subscribe':
                    symbol = cmd.get('symbol', 'RELIANCE.NS')
                    
                    # Start streaming if not already or if symbol changed
                    if not live_streamer.is_running or live_streamer.current_symbol != symbol:
                        await live_streamer.start_streaming(symbol)
                
                elif cmd['action'] == 'unsubscribe':
                    if live_streamer.is_running:
                        live_streamer.stop_streaming()
                
                elif cmd['action'] == 'set_timeframe':
                    timeframe = cmd.get('timeframe', '1m')
                    live_streamer.set_timeframe(timeframe)
            
            except json.JSONDecodeError:
                print("Invalid JSON received")
    
    finally:
        # Unregister when the client disconnects
        await live_streamer.unregister(websocket)

async def start_server():
    """Start the websocket server"""
    server = await websockets.serve(ws_handler, "0.0.0.0", 8765)
    print("WebSocket server started on port 8765")
    await server.wait_closed()

def start_websocket_server():
    """Start the websocket server in a new thread"""
    asyncio.run(start_server())

# Function to get current candlestick data (for use without websockets)
def get_current_candlestick_data(symbol=None, timeframe="1m"):
    """Get current candlestick data for a symbol"""
    global live_streamer
    
    # Set the timeframe
    live_streamer.set_timeframe(timeframe)
    
    # If not running or different symbol, initialize with the new symbol
    if not live_streamer.is_running or (symbol and live_streamer.current_symbol != symbol):
        # Run in a non-blocking way
        asyncio.run(live_streamer.start_streaming(symbol if symbol else "RELIANCE.NS"))
    
    # Get the current data
    return live_streamer.get_current_candlestick_data()

# Mock function for generating live data immediately (without websockets)
def generate_live_data(symbol, timeframe="1m", num_points=100):
    """
    Generate live data for a stock without using websockets
    This is a simplified version for use within Streamlit
    """
    # Create a temporary instance for generating data
    temp_streamer = LiveDataStreamer()
    temp_streamer.timeframe = timeframe
    
    # Generate data synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(temp_streamer.start_streaming(symbol))
    loop.close()
    
    # Get the data
    data = temp_streamer.get_current_candlestick_data()
    
    # Return the requested number of points
    return data.tail(num_points)