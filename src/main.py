import os
from dash import Dash, html, dcc, Input, Output, State
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging
import requests
from bs4 import BeautifulSoup
import feedparser
import json
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
    logger.info("Environment variables loaded successfully")
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")

def get_stock_data(symbol, period='1y'):
    """Fetch stock data using yfinance"""
    try:
        logger.info(f"Fetching data for symbol: {symbol}, period: {period}")
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        info = stock.info
        logger.info(f"Successfully fetched data for {symbol}")
        return hist, info
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return None, None

def get_small_cap_stocks():
    """Fetch small-cap stocks from various sources"""
    try:
        logger.info("Starting to fetch small-cap stocks from Finviz")
        # Use Yahoo Finance API instead of scraping
        # Get all S&P 600 Small Cap stocks (example tickers)
        small_cap_tickers = [
            'AAON', 'AATI', 'ABCB', 'ABG', 'ABM', 'ACLS', 'ADTN', 'AEIS', 'AEL', 'AF',
            'AGYS', 'AJRD', 'AKS', 'ALEX', 'AM', 'AMED', 'AMPH', 'AMSF', 'AMWD', 'ANIK'
        ]
        
        logger.info(f"Found {len(small_cap_tickers)} small-cap stocks")
        return small_cap_tickers
    except Exception as e:
        logger.error(f"Error fetching small-cap stocks: {e}")
        return []

def analyze_stock(symbol):
    """Analyze a stock using various metrics"""
    try:
        logger.info(f"Analyzing stock: {symbol}")
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Calculate basic metrics
        market_cap = info.get('marketCap', 0)
        pe_ratio = info.get('forwardPE', 0)
        price_to_book = info.get('priceToBook', 0)
        debt_to_equity = info.get('debtToEquity', 0)
        profit_margins = info.get('profitMargins', 0)
        
        # Enhanced scoring system (0-100)
        score = 0
        
        # Market Cap (max 20 points)
        if market_cap < 2e9:
            score += 20
        elif market_cap < 3e9:
            score += 10
            
        # P/E Ratio (max 20 points)
        if 5 < pe_ratio < 15:
            score += 20
        elif 15 <= pe_ratio < 20:
            score += 10
            
        # Price to Book (max 20 points)
        if 0 < price_to_book < 1:
            score += 20
        elif 1 <= price_to_book < 2:
            score += 10
            
        # Debt to Equity (max 20 points)
        if 0 < debt_to_equity < 50:
            score += 20
        elif 50 <= debt_to_equity < 100:
            score += 10
            
        # Profit Margins (max 20 points)
        if profit_margins > 0.2:  # 20% margin
            score += 20
        elif profit_margins > 0.1:  # 10% margin
            score += 10
            
        result = {
            'symbol': symbol,
            'company_name': info.get('longName', symbol),
            'market_cap': f"${market_cap/1e9:.2f}B",
            'pe_ratio': f"{pe_ratio:.2f}",
            'price_to_book': f"{price_to_book:.2f}",
            'debt_to_equity': f"{debt_to_equity:.2f}",
            'profit_margins': f"{profit_margins*100:.1f}%",
            'score': score
        }
        
        logger.info(f"Successfully analyzed {symbol} with score {score}")
        return result
    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {e}")
        return None

def get_stock_news(symbol):
    """Fetch news for a specific stock"""
    try:
        # Fetch from Yahoo Finance RSS
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        feed = feedparser.parse(url)
        
        news = []
        for entry in feed.entries[:5]:  # Get latest 5 news items
            news.append({
                'title': entry.title,
                'link': entry.link,
                'date': entry.published
            })
        
        return news
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        return []

# Initialize the Dash app
app = Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Financial Analysis AI Agent", style={'textAlign': 'center'}),
    
    # Tabs for different features
    dcc.Tabs([
        # Stock Analysis Tab
        dcc.Tab(label='Stock Analysis', children=[
            html.Div([
                html.Div([
                    html.H3("Settings"),
                    dcc.Input(
                        id='symbol-input',
                        value='AAPL',
                        type='text',
                        placeholder="Enter Stock Symbol",
                        style={'marginBottom': '10px'}
                    ),
                    dcc.Dropdown(
                        id='period-dropdown',
                        options=[
                            {'label': '1 Month', 'value': '1mo'},
                            {'label': '3 Months', 'value': '3mo'},
                            {'label': '6 Months', 'value': '6mo'},
                            {'label': '1 Year', 'value': '1y'},
                            {'label': '2 Years', 'value': '2y'},
                            {'label': '5 Years', 'value': '5y'}
                        ],
                        value='1y',
                        style={'marginBottom': '20px'}
                    )
                ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'}),
                
                html.Div([
                    html.H2(id='company-name'),
                    dcc.Graph(id='stock-chart'),
                    
                    # Metrics
                    html.Div([
                        html.Div([
                            html.H4("Current Price"),
                            html.H3(id='current-price')
                        ], style={'textAlign': 'center', 'flex': '1'}),
                        
                        html.Div([
                            html.H4("Market Cap"),
                            html.H3(id='market-cap')
                        ], style={'textAlign': 'center', 'flex': '1'}),
                        
                        html.Div([
                            html.H4("Volume"),
                            html.H3(id='volume')
                        ], style={'textAlign': 'center', 'flex': '1'})
                    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginTop': '20px'}),
                    
                    # News Section
                    html.Div([
                        html.H3("Latest News"),
                        html.Div(id='news-content')
                    ], style={'marginTop': '20px'})
                ])
            ])
        ]),
        
        # Stock Screening Tab
        dcc.Tab(label='Stock Screener', children=[
            html.Div([
                html.H3("Small-Cap Stock Screener"),
                html.Button('Refresh Stocks', id='refresh-button', n_clicks=0),
                html.Div(id='screener-content', style={'marginTop': '20px'})
            ], style={'padding': '20px'})
        ])
    ])
])

@app.callback(
    [Output('company-name', 'children'),
     Output('stock-chart', 'figure'),
     Output('current-price', 'children'),
     Output('market-cap', 'children'),
     Output('volume', 'children'),
     Output('news-content', 'children')],
    [Input('symbol-input', 'value'),
     Input('period-dropdown', 'value')]
)
def update_data(symbol, period):
    if not symbol:
        return "Please enter a stock symbol", {}, "", "", "", []
    
    data, info = get_stock_data(symbol.upper(), period)
    
    if data is None or data.empty:
        return f"No data available for {symbol}", {}, "", "", "", []
    
    # Create candlestick chart
    fig = go.Figure(data=[
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        )
    ])
    fig.update_layout(
        title=f"{symbol} Stock Price",
        yaxis_title="Price (USD)",
        xaxis_title="Date",
        template="plotly_white"
    )
    
    # Format metrics
    current_price = f"${data['Close'][-1]:.2f}"
    market_cap = f"${info.get('marketCap', 0)/1e9:.2f}B"
    volume = f"{data['Volume'][-1]:,.0f}"
    
    # Get news
    news = get_stock_news(symbol)
    news_content = [
        html.Div([
            html.A(item['title'], href=item['link'], target="_blank"),
            html.P(item['date'])
        ], style={'marginBottom': '10px'})
        for item in news
    ]
    
    return f"{info.get('longName', symbol)} ({symbol})", fig, current_price, market_cap, volume, news_content

@app.callback(
    Output('screener-content', 'children'),
    [Input('refresh-button', 'n_clicks')]
)
def update_screener(n_clicks):
    if n_clicks == 0:
        return "Click 'Refresh Stocks' to start screening"
    
    logger.info("Starting stock screening process")
    
    # Get small-cap stocks
    stocks = get_small_cap_stocks()
    if not stocks:
        return "Error: Could not fetch stock list. Please try again."
    
    logger.info(f"Analyzing {len(stocks)} stocks")
    
    # Analyze stocks in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(filter(None, executor.map(analyze_stock, stocks)))
    
    if not results:
        return "Error: Could not analyze stocks. Please try again."
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    logger.info(f"Successfully analyzed {len(results)} stocks")
    
    # Create table with more metrics
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in [
            'Symbol', 'Company', 'Market Cap', 'P/E Ratio', 
            'P/B Ratio', 'Debt/Equity', 'Profit Margin', 'Score'
        ]])] +
        # Data rows
        [html.Tr([
            html.Td(result['symbol']),
            html.Td(result['company_name']),
            html.Td(result['market_cap']),
            html.Td(result['pe_ratio']),
            html.Td(result['price_to_book']),
            html.Td(result['debt_to_equity']),
            html.Td(result['profit_margins']),
            html.Td(f"{result['score']}/100")
        ]) for result in results],
        style={
            'width': '100%',
            'textAlign': 'left',
            'borderCollapse': 'collapse',
            'border': '1px solid #ddd'
        }
    )

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
