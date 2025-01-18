import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Union
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import json
import os
import openai
from dotenv import load_dotenv, find_dotenv
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = find_dotenv()
logger.info(f"Found .env file at: {env_path}")
load_dotenv(env_path)

class StockAnalysisAgent:
    def __init__(self):
        """Initialize the Stock Analysis Agent"""
        self.data = None
        self.symbol = None
        self.ticker = None
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OpenAI API key not found in environment variables")
            sys.exit(1)
            
        openai.api_key = api_key
        logger.info("Successfully initialized OpenAI client")
        
    def summarize_with_openai(self, text: str) -> str:
        """
        Use OpenAI to generate a concise summary of the text
        
        Args:
            text (str): Text to summarize
            
        Returns:
            str: Summarized text
        """
        try:
            if not text:
                return ""
                
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial news summarizer. Create a concise, informative summary of the given text in 2-3 sentences."},
                    {"role": "user", "content": text}
                ],
                max_tokens=150,
                temperature=0.5
            )
            
            return response.choices[0].message['content'].strip()
        except Exception as e:
            logger.error(f"Error generating summary with OpenAI: {str(e)}")
            return text[:200] + "..."  # Fallback to truncated text
    
    def get_article_content(self, url: str) -> str:
        """
        Get article content from URL
        
        Args:
            url (str): Article URL
            
        Returns:
            str: Article content
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try to get meta description
                meta_desc = soup.find('meta', {'name': ['description', 'og:description']})
                if meta_desc and meta_desc.get('content'):
                    return meta_desc.get('content')
                
                # Try to get article content
                article = soup.find('article')
                if article:
                    paragraphs = article.find_all('p')
                    content = ' '.join([p.get_text().strip() for p in paragraphs[:3]])
                    return content
                
                # Fallback to first few paragraphs
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs[:3]])
                return content
                
        except Exception as e:
            logger.debug(f"Error fetching article content: {str(e)}")
            return ""
    
    def fetch_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        Fetch stock data for the given symbol
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            period (str): Time period to fetch data for (default: '1y')
            
        Returns:
            pd.DataFrame: Historical stock data
        """
        try:
            self.symbol = symbol
            self.ticker = yf.Ticker(symbol)
            self.data = self.ticker.history(period=period)
            return self.data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def calculate_technical_indicators(self) -> Dict[str, float]:
        """
        Calculate basic technical indicators for the stock
        
        Returns:
            Dict[str, float]: Dictionary containing technical indicators
        """
        if self.data is None:
            logger.error("No data available. Please fetch stock data first.")
            return {}
        
        try:
            # Calculate moving averages
            self.data['MA20'] = self.data['Close'].rolling(window=20).mean()
            self.data['MA50'] = self.data['Close'].rolling(window=50).mean()
            
            # Calculate RSI
            delta = self.data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            self.data['RSI'] = 100 - (100 / (1 + rs))
            
            # Get latest values
            latest = self.data.iloc[-1]
            return {
                'current_price': latest['Close'],
                'ma20': latest['MA20'],
                'ma50': latest['MA50'],
                'rsi': latest['RSI'],
                'volume': latest['Volume']
            }
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return {}

    def get_institutional_holders(self) -> List[Dict]:
        """
        Get major institutional holders
        
        Returns:
            List[Dict]: List of major institutional holders
        """
        try:
            holders = self.ticker.institutional_holders
            if holders is not None and not holders.empty:
                return holders.head().to_dict('records')
            return []
        except Exception as e:
            logger.error(f"Error fetching institutional holders: {str(e)}")
            return []

    def get_news_sentiment(self) -> List[Dict]:
        """
        Get recent news and sentiment
        
        Returns:
            List[Dict]: List of recent news items with metadata
        """
        try:
            # Get news from Yahoo Finance API
            news_items = self.ticker.news
            
            if not news_items:
                return []
            
            processed_news = []
            
            for item in news_items[:5]:  # Process only the 5 most recent news
                news_dict = {
                    'title': item.get('title', ''),
                    'publisher': item.get('publisher', ''),
                    'link': item.get('link', ''),
                    'published': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                    'type': item.get('type', ''),
                    'summary': ''
                }
                
                # Try to get article content and generate summary
                if news_dict['link']:
                    article_content = self.get_article_content(news_dict['link'])
                    if article_content:
                        news_dict['summary'] = self.summarize_with_openai(article_content)
                
                processed_news.append(news_dict)
                
            return processed_news
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []

    def generate_insights(self) -> Dict:
        """
        Generate comprehensive insights about the stock
        
        Returns:
            Dict: Dictionary containing various insights
        """
        insights = {
            'technical_analysis': [],
            'institutional_holders': [],
            'recent_news': [],
            'company_info': {}
        }
        
        try:
            # Technical Analysis
            indicators = self.calculate_technical_indicators()
            
            if indicators:
                current_price = indicators['current_price']
                ma20 = indicators['ma20']
                ma50 = indicators['ma50']
                rsi = indicators['rsi']
                
                # Price vs Moving Averages
                if current_price > ma20:
                    insights['technical_analysis'].append(f"Price is above 20-day MA, indicating short-term upward trend")
                else:
                    insights['technical_analysis'].append(f"Price is below 20-day MA, indicating short-term downward trend")
                    
                if current_price > ma50:
                    insights['technical_analysis'].append(f"Price is above 50-day MA, indicating medium-term upward trend")
                else:
                    insights['technical_analysis'].append(f"Price is below 50-day MA, indicating medium-term downward trend")
                
                # RSI Analysis
                if rsi > 70:
                    insights['technical_analysis'].append(f"RSI is {rsi:.2f}, suggesting the stock might be overbought")
                elif rsi < 30:
                    insights['technical_analysis'].append(f"RSI is {rsi:.2f}, suggesting the stock might be oversold")
                else:
                    insights['technical_analysis'].append(f"RSI is {rsi:.2f}, indicating neutral momentum")
            
            # Institutional Holders
            insights['institutional_holders'] = self.get_institutional_holders()
            
            # Recent News
            insights['recent_news'] = self.get_news_sentiment()
            
            # Company Info
            info = self.ticker.info
            insights['company_info'] = {
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'forward_pe': info.get('forwardPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'beta': info.get('beta', 'N/A'),
                'business_summary': info.get('longBusinessSummary', 'N/A')
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return insights
