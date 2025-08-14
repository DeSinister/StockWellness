import finnhub
import logging
import os
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockAPI:
    def __init__(self):
        """Initialize Finnhub client using API key from environment variable."""
        api_key = os.getenv("FINNHUB_API_KEY")
        if not api_key:
            raise ValueError("FINNHUB_API_KEY not found in environment variables.")
        self.client = finnhub.Client(api_key=api_key)

    def get_company_info(self, ticker):
        """Get company information and key metrics."""
        try:
            profile = self.client.company_profile2(symbol=ticker)
            quote = self.client.quote(ticker)

            company_data = {
                'symbol': ticker.upper(),
                'name': profile.get('name', 'N/A'),
                'sector': profile.get('finnhubIndustry', 'N/A'),
                'industry': profile.get('industry', 'N/A'),
                'market_cap': profile.get('marketCapitalization', 'N/A'),
                'pe_ratio': profile.get('pe', 'N/A'),
                'forward_pe': profile.get('forwardPE', 'N/A'),
                'price_to_book': profile.get('priceToBook', 'N/A'),
                'dividend_yield': profile.get('dividendYield', 'N/A'),
                'current_price': quote.get('c', 'N/A'),
                'target_high_price': 'N/A',
                'target_low_price': 'N/A',
                'target_mean_price': 'N/A',
                'recommendation': 'N/A',
                'summary': profile.get('description', 'N/A')
            }

            logger.info(f"Successfully fetched company info for {ticker}")
            return company_data

        except Exception as e:
            logger.error(f"Error fetching company info for {ticker}: {str(e)}")
            return None

    def get_historical_data(self, ticker, months=6):
        """Get historical stock prices for the last specified months."""
        try:
            end_date = int(datetime.now().timestamp())
            start_date = int((datetime.now() - timedelta(days=months * 30)).timestamp())
            candles = self.client.stock_candles(ticker, 'D', start_date, end_date)

            if not candles or 'c' not in candles:
                logger.warning(f"No historical data found for {ticker}")
                return None

            price_data = []
            for i in range(len(candles['t'])):
                price_data.append({
                    'date': datetime.fromtimestamp(candles['t'][i]).strftime('%Y-%m-%d'),
                    'open': round(candles['o'][i], 2),
                    'high': round(candles['h'][i], 2),
                    'low': round(candles['l'][i], 2),
                    'close': round(candles['c'][i], 2),
                    'volume': int(candles['v'][i])
                })

            logger.info(f"Successfully fetched {len(price_data)} days of historical data for {ticker}")
            return price_data

        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {str(e)}")
            return None

    def validate_ticker(self, ticker):
        """Validate if the ticker symbol exists."""
        try:
            profile = self.client.company_profile2(symbol=ticker)
            return bool(profile.get('name'))
        except Exception as e:
            logger.error(f"Error validating ticker {ticker}: {str(e)}")
            return False
