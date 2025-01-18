import numpy as np
import pandas as pd

def calculate_moving_average(data, window):
    """Calculate moving average of closing prices"""
    return data['Close'].rolling(window=window).mean()

def calculate_rsi(data, periods=14):
    """Calculate Relative Strength Index"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_volatility(data, window=21):
    """Calculate historical volatility"""
    returns = np.log(data['Close'] / data['Close'].shift(1))
    return returns.rolling(window=window).std() * np.sqrt(252)

def calculate_beta(stock_data, market_data):
    """Calculate beta relative to market"""
    stock_returns = stock_data['Close'].pct_change()
    market_returns = market_data['Close'].pct_change()
    
    covariance = stock_returns.cov(market_returns)
    market_variance = market_returns.var()
    
    return covariance / market_variance

def calculate_sharpe_ratio(data, risk_free_rate=0.02):
    """Calculate Sharpe Ratio"""
    returns = data['Close'].pct_change()
    excess_returns = returns - risk_free_rate/252
    return np.sqrt(252) * excess_returns.mean() / returns.std()
