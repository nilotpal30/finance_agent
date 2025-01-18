"""
Configuration settings for the Financial Analysis AI Agent
"""

# API Configuration
API_TIMEOUT = 30
MAX_RETRIES = 3

# Technical Analysis Settings
MOVING_AVERAGE_PERIODS = [20, 50, 200]
RSI_PERIOD = 14
VOLATILITY_WINDOW = 21

# Data Settings
DEFAULT_TIMEFRAME = '1y'
CACHE_EXPIRY = 3600  # 1 hour in seconds

# Visualization Settings
CHART_THEME = 'streamlit'
CHART_HEIGHT = 600
CHART_WIDTH = 1000

# Portfolio Settings
MAX_PORTFOLIO_SIZE = 20
RISK_FREE_RATE = 0.02  # 2% annual rate
