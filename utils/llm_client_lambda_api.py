import anthropic
import os
import json
import logging
import requests
from typing import Dict, Any

# Import news components (keep these local)
from .news_api import NewsAPI
from .news_summarizer import NewsSummarizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LambdaAPILLMClient:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key or self.api_key == 'your_anthropic_api_key_here':
            logger.warning("ANTHROPIC_API_KEY not found or not configured in environment variables")
            self.client = None
        else:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {str(e)}")
                self.client = None
        
        # Lambda API endpoint for RAG - Updated to new fast semantic search endpoint
        self.lambda_api_endpoint = "https://7dg4etgob2uxmrv23yv5tawslu0dnhvj.lambda-url.us-east-2.on.aws/"
        
        # Initialize news components (keep these local)
        try:
            self.news_api = NewsAPI()
            self.news_summarizer = NewsSummarizer()
            logger.info("News components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize news systems: {e}")
            self.news_api = None
            self.news_summarizer = None
    
    def search_investment_books(self, query):
        """Search investment books using Lambda API"""
        try:
            response = requests.post(
                self.lambda_api_endpoint,
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                logger.error(f"Lambda API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error calling Lambda API: {e}")
            return []
    
    def get_stock_analysis(self, company_data, price_data, news_articles):
        """Get comprehensive stock analysis using Lambda-powered RAG"""
        try:
            if not self.client:
                return {
                    'recommendation': 'HOLD',
                    'confidence_score': 0,
                    'rationale': 'LLM client not available - Anthropic API key may be missing or invalid.',
                    'key_factors': [],
                    'risks': ['LLM analysis unavailable'],
                    'price_target': 'N/A',
                    'rag_context': {
                        'sources': [],
                        'reasoning': 'LLM client not initialized.',
                        'global_news': []
                    }
                }
            
            # Get global news and investment themes
            global_news = []
            investment_themes = "investment principles risk management diversification"
            
            if self.news_api and self.news_summarizer:
                try:
                    # Get global affairs news
                    global_topics = ['Global Tension', 'Wars', 'Trading co-operations', 'Federal Reserve', 'Interest Rates']
                    global_news = self.news_api.get_global_affairs_news(topics=global_topics, max_articles=8)
                    
                    # Summarize how news affects markets
                    if global_news:
                        investment_themes = self.news_summarizer.summarize_market_impact(global_news)
                    
                    logger.info(f"Retrieved {len(global_news)} news articles, themes: '{investment_themes[:50]}...'")
                except Exception as e:
                    logger.error(f"Error getting news: {e}")
            
            # Search books using investment themes
            rag_results = self.search_investment_books(investment_themes)
            
            # Format RAG context
            book_context = ""
            if rag_results:
                book_context = "Relevant Investment Principles from Literature:\n\n"
                for i, result in enumerate(rag_results[:3], 1):
                    book_context += f"{i}. From '{result['book_name']}' (Page {result['page']}):\n"
                    book_context += f"   {result['text'][:400]}{'...' if len(result['text']) > 400 else ''}\n\n"
            else:
                book_context = "Investment literature context not available."
            
            # Simple analysis prompt with Lambda RAG
            company_name = company_data.get('name', 'Unknown Company')
            ticker = company_data.get('symbol', 'UNKNOWN')
            current_price = company_data.get('current_price', 'N/A')
            
            prompt = f"""
You are a professional stock analyst. Analyze {company_name} ({ticker}) and provide a recommendation.

RELEVANT INVESTMENT PRINCIPLES:
{book_context}

COMPANY FUNDAMENTALS:
- Name: {company_name}
- Ticker: {ticker}
- Current Price: ${current_price}
- Market Cap: ${company_data.get('market_cap', 'N/A')}
- P/E Ratio: {company_data.get('pe_ratio', 'N/A')}
- Sector: {company_data.get('sector', 'N/A')}

Please provide your analysis in JSON format:
{{
    "recommendation": "BUY|HOLD|SELL",
    "confidence_score": <number between 0-100>,
    "rationale": "<detailed explanation>",
    "key_factors": ["<factor 1>", "<factor 2>"],
    "risks": ["<risk 1>", "<risk 2>"],
    "price_target": "<12-month target or N/A>"
}}

Reference the investment principles above when relevant.
"""
            
            # Get analysis from Claude
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Parse JSON response
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start:json_end]
                    analysis = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse JSON: {e}")
                analysis = {
                    'recommendation': 'HOLD',
                    'confidence_score': 50,
                    'rationale': f'Analysis completed but parsing failed: {response_text[:300]}...',
                    'key_factors': ['LLM analysis available'],
                    'risks': ['JSON parsing error'],
                    'price_target': 'N/A'
                }
            
            # Add RAG context in the format expected by frontend
            formatted_sources = []
            for r in rag_results[:3]:
                formatted_sources.append({
                    'book': r.get('book_name', 'Unknown'),
                    'chapter': 'Investment Principles',  # Generic since we don't have chapter info
                    'page': r.get('page', 'N/A'),
                    'text_preview': r.get('text', '')[:300] + ('...' if len(r.get('text', '')) > 300 else ''),
                    'relevance_score': r.get('similarity', 0.5)  # Use similarity from new Lambda API
                })
            
            analysis['rag_context'] = {
                'sources': formatted_sources,
                'reasoning': f"Found {len(rag_results)} relevant investment principles from classic literature",
                'global_news': global_news[:5]  # Include top 5 news articles
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in stock analysis: {e}")
            return {
                'recommendation': 'HOLD',
                'confidence_score': 0,
                'rationale': f'Analysis failed: {str(e)}',
                'key_factors': [],
                'risks': ['Technical error'],
                'price_target': 'N/A',
                'rag_context': {'sources': [], 'reasoning': 'Error occurred.', 'global_news': []}
            } 