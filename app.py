from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import plotly
import plotly.graph_objs as go
from datetime import datetime
import logging
from dotenv import load_dotenv

# Import our utility modules
from utils.stock_api import StockAPI
from utils.news_api import NewsAPI
from utils.llm_client import LLMClient
from utils.cache import SimpleCache

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize our services
stock_api = StockAPI()
news_api = NewsAPI()
cache = SimpleCache()

# Popular tickers for the dropdown
POPULAR_TICKERS = [
    ('AAPL', 'Apple Inc.'),
    ('MSFT', 'Microsoft Corporation'),
    ('GOOGL', 'Alphabet Inc.'),
    ('AMZN', 'Amazon.com Inc.'),
    ('TSLA', 'Tesla Inc.'),
    ('META', 'Meta Platforms Inc.'),
    ('NVDA', 'NVIDIA Corporation'),
    ('NFLX', 'Netflix Inc.'),
    ('SPY', 'SPDR S&P 500 ETF Trust'),
    ('QQQ', 'Invesco QQQ Trust')
]

@app.route('/')
def index():
    """Main page with stock analysis form"""
    try:
        return render_template('index.html', popular_tickers=POPULAR_TICKERS)
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return f"Error rendering page: {str(e)}", 500

@app.route('/analyze', methods=['POST'])
def analyze_stock():
    """Analyze a stock and return the results"""
    try:
        ticker = request.form.get('ticker', '').upper().strip()
        
        if not ticker:
            return jsonify({'error': 'Please provide a stock ticker symbol.'}), 400
        
        # Validate ticker
        if not stock_api.validate_ticker(ticker):
            return jsonify({'error': f'Invalid ticker symbol: {ticker}'}), 400
        
        # Create cache key for this analysis
        cache_key = {
            'ticker': ticker,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'type': 'full_analysis'
        }
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached analysis for {ticker}")
            return jsonify(cached_result)
        
        # Get stock data
        logger.info(f"Fetching stock data for {ticker}")
        company_data = stock_api.get_company_info(ticker)
        if not company_data:
            return jsonify({'error': f'Failed to fetch company data for {ticker}'}), 500
        
        price_data = stock_api.get_historical_data(ticker, months=6)
        if not price_data:
            return jsonify({'error': f'Failed to fetch price data for {ticker}'}), 500
        
        # Note: News and RAG analysis now handled internally by LLM client
        # The enhanced RAG system will:
        # 1. Get global affairs news automatically
        # 2. Generate investment themes from current events  
        # 3. Search books for relevant investment principles
        # 4. Use both global context + book wisdom in analysis
        
        # Create price chart
        price_chart = create_price_chart(price_data, company_data['name'])
        
        # Get enhanced LLM analysis with global affairs + investment literature
        logger.info(f"Getting enhanced RAG analysis for {ticker}")
        try:
            llm_client = LLMClient()
            analysis = llm_client.get_stock_analysis(company_data, price_data, [])
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            analysis = {
                'recommendation': 'HOLD',
                'confidence_score': 0,
                'rationale': f'LLM analysis unavailable: {str(e)}',
                'key_factors': [],
                'risks': [],
                'price_target': 'N/A',
                'rag_context': {
                    'sources': [],
                    'reasoning': 'Technical error occurred during analysis.'
                }
            }
        
        # Prepare result
        result = {
            'success': True,
            'ticker': ticker,
            'company_data': company_data,
            'price_data': price_data,
            'news_articles': analysis.get('rag_context', {}).get('global_news', [])[:5],  # Global affairs news from RAG
            'analysis': analysis,
            'price_chart': price_chart,
            'generated_at': datetime.now().isoformat()
        }
        
        # Cache the result for 1 hour
        cache.set(cache_key, result, expiry_hours=1)
        
        logger.info(f"Successfully completed analysis for {ticker}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in analyze_stock: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

def create_price_chart(price_data, company_name):
    """Create a Plotly chart for stock prices"""
    try:
        if not price_data:
            return None
        
        dates = [entry['date'] for entry in price_data]
        closes = [entry['close'] for entry in price_data]
        volumes = [entry['volume'] for entry in price_data]
        
        # Create candlestick chart
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=dates,
            y=closes,
            mode='lines',
            name='Close Price',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='<b>Date:</b> %{x}<br><b>Price:</b> $%{y:.2f}<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title=f'{company_name} - 6 Month Price History',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template='plotly_white',
            height=400,
            showlegend=True,
            hovermode='x unified'
        )
        
        # Convert to JSON for frontend
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON
        
    except Exception as e:
        logger.error(f"Error creating price chart: {str(e)}")
        return None

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check if services are working
        services_status = {
            'stock_api': True,
            'news_api': bool(os.getenv('NEWS_API_KEY')),
            'llm_client': bool(os.getenv('ANTHROPIC_API_KEY') and os.getenv('ANTHROPIC_API_KEY') != 'your_anthropic_api_key_here'),
            'cache': True
        }
        
        cache_stats = cache.get_cache_stats()
        
        return jsonify({
            'status': 'healthy',
            'services': services_status,
            'cache_stats': cache_stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Clear expired cache entries"""
    try:
        cleared_count = cache.clear_expired()
        return jsonify({
            'success': True,
            'message': f'Cleared {cleared_count} expired cache entries'
        })
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    """Serve favicon to prevent 404 errors"""
    return '', 204  # No Content response

if __name__ == '__main__':
    # Check for required environment variables
    required_env_vars = ['ANTHROPIC_API_KEY', 'NEWS_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("Some features may not work properly. Please check your .env file.")
    
    # Run the app in production mode
    port = int(os.getenv('FLASK_RUN_PORT', 8080))
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port) 