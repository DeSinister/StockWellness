# StockWellness - AI-Powered Stock Analysis

An end-to-end Flask web application that uses Retrieval-Augmented Generation (RAG) to provide comprehensive stock analysis and investment recommendations. The app combines real-time stock data, recent news, and AI-powered analysis to deliver actionable investment insights.

## 🌟 Features

- **Real-time Stock Data**: Fetches company fundamentals, historical prices, and key metrics using Yahoo Finance
- **News Integration**: Pulls recent news articles from NewsAPI to provide market context
- **AI-Powered Analysis**: Uses OpenAI GPT-4 to analyze data and provide BUY/HOLD/SELL recommendations
- **Interactive Charts**: Beautiful price visualization using Plotly
- **Smart Caching**: Reduces API calls and improves performance with built-in caching
- **Responsive Design**: Modern UI built with Bootstrap 5
- **Popular Tickers**: Quick access to commonly analyzed stocks
- **Confidence Scoring**: AI provides confidence levels for its recommendations

## 📊 How It Works

### 1. Data Collection
- **Stock Data**: Uses `yfinance` to fetch:
  - Company information and fundamentals
  - 6 months of historical price data
  - Key metrics (P/E ratio, market cap, etc.)

- **News Data**: Uses NewsAPI to fetch:
  - Recent news articles about the company
  - Market sentiment and developments
  - Context for price movements

### 2. AI Analysis
- **RAG Implementation**: Combines structured data with unstructured news
- **Prompt Engineering**: Creates comprehensive prompts for GPT-4
- **Analysis Output**: Provides:
  - BUY/HOLD/SELL recommendation
  - Confidence score (0-100%)
  - Detailed rationale
  - Key factors and risks
  - Price targets

### 3. Visualization
- **Interactive Charts**: Plotly-powered price history charts
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live data integration

## 🐳 Docker Deployment

### Quick Start with Docker

The easiest way to run StockWellness is using Docker. We provide multiple options:

#### Option 1: Using the Management Script (Recommended)
```bash
# Make the script executable
chmod +x docker-run.sh

# Build and run with docker-compose
./docker-run.sh compose

# Or run directly
./docker-run.sh run

# View logs
./docker-run.sh logs

# Stop the application
./docker-run.sh stop
```

#### Option 2: Using Docker Compose
```bash
# Build and start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

#### Option 3: Using Docker directly
```bash
# Build the image
docker build -t stockwellness:latest .

# Run the container
docker run -d \
  --name stockwellness \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/cache:/app/cache \
  stockwellness:latest
```

### Environment Variables for Docker

Create a `.env` file in the project root:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
NEWS_API_KEY=your_news_api_key_here
SECRET_KEY=your_secret_key_here
```

### Docker Features

- **Port 5000**: Application runs on port 5000 (exposed)
- **Health Checks**: Built-in health monitoring
- **Volume Persistence**: Cache data persists between container restarts
- **Security**: Runs as non-root user
- **Optimized Build**: Multi-stage build with layer caching

Once running, access the application at: http://localhost:5000

## 🎯 Usage

### Basic Analysis
1. Enter a stock ticker symbol (e.g., AAPL, TSLA, MSFT)
2. Click "Analyze Stock" or press Enter
3. Wait for the AI analysis to complete
4. Review the comprehensive results

### Popular Stocks
- Click any of the popular ticker buttons for quick analysis
- Includes major tech stocks and ETFs

### Understanding Results

#### Company Overview
- Basic company information
- Key financial metrics
- Current stock price

#### AI Recommendation
- **BUY**: AI believes the stock is undervalued
- **HOLD**: AI suggests maintaining current position
- **SELL**: AI believes the stock is overvalued


## 🏗️ Project Structure

```
StockWellness/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── env_template.txt       # Environment variables template
├── README.md             # This file
├── utils/
│   ├── __init__.py       # Utils package
│   ├── stock_api.py      # Stock data fetching
│   ├── news_api.py       # News data fetching
│   ├── llm_client.py     # OpenAI integration
│   └── cache.py          # Caching system
├── templates/
│   ├── base.html         # Base template
│   └── index.html        # Main page
└── static/
    ├── css/
    │   └── style.css     # Custom styles
    └── js/
        └── script.js     # Custom JavaScript
```


## 🔍 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application page |
| `/analyze` | POST | Analyze a stock ticker |
| `/health` | GET | Health check endpoint |
| `/clear-cache` | POST | Clear expired cache entries |

