# Financial Analysis AI Agent

A powerful web application built with Dash for analyzing stocks, screening for investment opportunities, and tracking financial news. The application combines real-time market data with advanced analytics to help users make informed investment decisions.

## Features

### 1. Stock Analysis
- Real-time stock price tracking using Yahoo Finance API
- Interactive candlestick charts with customizable time periods
- Key metrics display (Current Price, Market Cap, Volume)
- Latest news integration from Yahoo Finance RSS feeds

### 2. Stock Screener
- Pre-configured small-cap stock screening
- Comprehensive stock analysis using multiple metrics:
  - Market Capitalization
  - Price-to-Earnings (P/E) Ratio
  - Price-to-Book (P/B) Ratio
  - Debt-to-Equity Ratio
  - Profit Margins
- Intelligent scoring system (0-100) based on fundamental analysis
- Parallel processing for efficient stock analysis

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd finance_agent
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with your API keys (if needed):
```env
OPENAI_API_KEY=your_key_here
```

## Usage

1. Start the application:
```bash
python src/main.py
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:8050
```

### Stock Analysis Tab
1. Enter a stock symbol (e.g., AAPL, MSFT)
2. Select a time period from the dropdown
3. View the interactive candlestick chart
4. Check key metrics and latest news

### Stock Screener Tab
1. Click the "Refresh Stocks" button
2. View the analysis of pre-selected small-cap stocks
3. Stocks are scored based on multiple metrics:
   - Market Cap (20 points): Preference for true small-caps < $2B
   - P/E Ratio (20 points): Optimal range 5-15
   - P/B Ratio (20 points): Preference for < 1
   - Debt/Equity (20 points): Lower is better
   - Profit Margins (20 points): Higher margins preferred

## Technical Details

### Dependencies
- `dash`: Web application framework
- `yfinance`: Yahoo Finance API wrapper
- `pandas`: Data manipulation
- `plotly`: Interactive charts
- `beautifulsoup4`: Web scraping
- `feedparser`: RSS feed parsing

### Architecture
- `src/main.py`: Main application file containing:
  - Dash layout and callbacks
  - Stock data fetching and analysis
  - News integration
  - Stock screening logic

### Error Handling
- Comprehensive logging system
- Graceful error handling for API failures
- User-friendly error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Future Enhancements

1. Additional Data Sources
   - Integration with more financial APIs
   - Alternative data sources for market sentiment

2. Enhanced Analysis
   - Technical indicators
   - Machine learning-based predictions
   - Portfolio optimization

3. User Experience
   - Customizable watchlists
   - Email alerts
   - Mobile responsiveness

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments

- Yahoo Finance for financial data
- Dash and Plotly for the interactive visualization framework
- The open-source community for various tools and libraries
