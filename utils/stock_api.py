import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockAPI:
    def __init__(self):
        pass
    
    def get_company_info(self, ticker):
        """Get company information and key metrics"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract key metrics
            company_data = {
                'symbol': ticker.upper(),
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'forward_pe': info.get('forwardPE', 'N/A'),
                'price_to_book': info.get('priceToBook', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'current_price': info.get('currentPrice', 'N/A'),
                'target_high_price': info.get('targetHighPrice', 'N/A'),
                'target_low_price': info.get('targetLowPrice', 'N/A'),
                'target_mean_price': info.get('targetMeanPrice', 'N/A'),
                'recommendation': info.get('recommendationKey', 'N/A'),
                'summary': info.get('longBusinessSummary', 'N/A')
            }
            
            logger.info(f"Successfully fetched company info for {ticker}")
            return company_data
            
        except Exception as e:
            logger.error(f"Error fetching company info for {ticker}: {str(e)}")
            return None
    
    def get_historical_data(self, ticker, months=6):
        """Get historical stock prices for the last specified months"""
        try:
            # Calculate start date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            stock = yf.Ticker(ticker)
            hist_data = stock.history(start=start_date, end=end_date)
            
            if hist_data.empty:
                logger.warning(f"No historical data found for {ticker}")
                return None
            
            # Clean and format the data
            hist_data.reset_index(inplace=True)
            hist_data['Date'] = hist_data['Date'].dt.strftime('%Y-%m-%d')
            
            # Convert to list of dictionaries for easier handling
            price_data = []
            for _, row in hist_data.iterrows():
                price_data.append({
                    'date': row['Date'],
                    'open': round(row['Open'], 2),
                    'high': round(row['High'], 2),
                    'low': round(row['Low'], 2),
                    'close': round(row['Close'], 2),
                    'volume': int(row['Volume'])
                })
            
            logger.info(f"Successfully fetched {len(price_data)} days of historical data for {ticker}")
            return price_data
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {str(e)}")
            return None
    
    def validate_ticker(self, ticker):
        """Validate if the ticker symbol exists"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check if we got valid data
            if 'symbol' in info or 'longName' in info:
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error validating ticker {ticker}: {str(e)}")
            return False 