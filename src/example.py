from stock_analysis_agent import StockAnalysisAgent
from datetime import datetime
import argparse
import textwrap

def format_market_cap(market_cap):
    if not market_cap or market_cap == 'N/A':
        return 'N/A'
    if market_cap >= 1e12:
        return f"${market_cap/1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap/1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap/1e6:.2f}M"
    else:
        return f"${market_cap:,.2f}"

def format_number(num):
    return f"{num:,.0f}" if isinstance(num, (int, float)) else "N/A"

def print_analysis(symbol: str, insights: dict):
    print(f"\n{'='*50}")
    print(f"Analysis for {symbol} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    
    # Company Info
    print("\nCompany Information:")
    print(f"Sector: {insights['company_info']['sector']}")
    print(f"Industry: {insights['company_info']['industry']}")
    print(f"Market Cap: {format_market_cap(insights['company_info']['market_cap'])}")
    print(f"Forward P/E: {insights['company_info']['forward_pe']}")
    print(f"Dividend Yield: {insights['company_info']['dividend_yield']:.2%}" if isinstance(insights['company_info']['dividend_yield'], float) else "Dividend Yield: N/A")
    print(f"Beta: {insights['company_info']['beta']}")
    
    # Business Summary
    print("\nBusiness Summary:")
    summary = insights['company_info']['business_summary']
    if summary and summary != 'N/A':
        # Print summary with word wrap at 80 characters
        print(textwrap.fill(summary, width=80))
    else:
        print("No business summary available")
    
    # Technical Analysis
    print("\nTechnical Analysis:")
    for insight in insights['technical_analysis']:
        print(f"- {insight}")
    
    # Institutional Holders
    print("\nTop Institutional Holders:")
    if insights['institutional_holders']:
        for holder in insights['institutional_holders'][:3]:
            shares = format_number(holder.get('Shares', 0))
            value = format_number(holder.get('Value', 0))
            print(f"- {holder.get('Holder', 'Unknown')}: {shares} shares (${value})")
    else:
        print("No institutional holder data available")
    
    # Recent News
    print("\nRecent News:")
    if insights['recent_news']:
        for news in insights['recent_news'][:3]:
            print(f"\n- {news['title']}")
            print(f"  Published: {news['published']} by {news['publisher']}")
            print("  Summary:")
            if news['summary']:
                # Indent the summary and wrap it at 75 characters (allowing for the 4-space indent)
                wrapped_summary = textwrap.fill(news['summary'], width=75, initial_indent="    ", subsequent_indent="    ")
                print(wrapped_summary)
            else:
                print("    No summary available")
    else:
        print("No recent news available")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Stock Analysis Tool')
    parser.add_argument('symbol', type=str, help='Stock symbol to analyze (e.g., AAPL)')
    parser.add_argument('--period', type=str, default='1y', 
                      help='Time period for analysis (e.g., 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)')
    
    args = parser.parse_args()
    
    # Initialize the agent
    agent = StockAnalysisAgent()
    
    print(f"\nFetching data for {args.symbol}...")
    
    # Fetch data
    data = agent.fetch_stock_data(args.symbol, args.period)
    if data is None:
        print(f"Failed to fetch data for {args.symbol}")
        return
        
    # Generate insights
    insights = agent.generate_insights()
    
    # Print analysis
    print_analysis(args.symbol, insights)

if __name__ == "__main__":
    main()
