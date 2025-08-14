import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockAPI:
    def __init__(self):
        self.api_key = os.environ.get("STOCK_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
        if not self.api_key:
            logger.error("ALPHAVANTAGE_API_KEY not set in environment variables")

    def get_company_info(self, ticker):
        """Get company information and key metrics"""
        try:
            params = {
                "function": "OVERVIEW",
                "symbol": ticker,
                "apikey": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if not data or "Symbol" not in data:
                logger.error(f"No company info found for {ticker}")
                return None

            # Use TIME_SERIES_DAILY_ADJUSTED to get current price
            price_data = self.get_historical_data(ticker, months=1)
            current_price = price_data[-1]['close'] if price_data else 'N/A'

            company_data = {
                'symbol': ticker.upper(),
                'name': data.get('Name', 'N/A'),
                'sector': data.get('Sector', 'N/A'),
                'industry': data.get('Industry', 'N/A'),
                'market_cap': float(data.get('MarketCapitalization', 'nan')),
                'pe_ratio': float(data.get('PERatio', 'nan')),
                'forward_pe': float(data.get('ForwardPE', 'nan')),
                'price_to_book': float(data.get('PriceToBookRatio', 'nan')),
                'dividend_yield': float(data.get('DividendYield', 'nan')),
                'current_price': current_price,
                'target_high_price': float(data.get('52WeekHigh', 'nan')),
                'target_low_price': float(data.get('52WeekLow', 'nan')),
                'target_mean_price': 'N/A',  # not provided by Alpha Vantage
                'recommendation': 'N/A',    # not provided
                'summary': data.get('Description', 'N/A')
            }
            
            logger.info(f"Successfully fetched company info for {ticker}")
            return company_data

        except Exception as e:
            logger.error(f"Error fetching company info for {ticker}: {str(e)}")
            return None

    def get_historical_data(self, ticker, months=6):
        """Get historical stock prices for the last specified months"""
        try:
            params = {
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": ticker,
                "outputsize": "full",
                "apikey": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if "Time Series (Daily)" not in data:
                logger.error(f"No historical data found for {ticker}")
                return None
            
            hist_data = data["Time Series (Daily)"]
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)

            price_data = []
            for date_str, daily in hist_data.items():
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                if start_date <= date_obj <= end_date:
                    price_data.append({
                        'date': date_str,
                        'open': round(float(daily['1. open']), 2),
                        'high': round(float(daily['2. high']), 2),
                        'low': round(float(daily['3. low']), 2),
                        'close': round(float(daily['4. close']), 2),
                        'volume': int(daily['6. volume'])
                    })

            # Sort ascending by date
            price_data.sort(key=lambda x: x['date'])
            logger.info(f"Successfully fetched {len(price_data)} days of historical data for {ticker}")
            return price_data

        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {str(e)}")
            return None

    def validate_ticker(self, ticker):
        """Validate if the ticker symbol exists"""
        try:
            info = self.get_company_info(ticker)
            return info is not None
        except Exception as e:
            logger.error(f"Error validating ticker {ticker}: {str(e)}")
            return False
