import anthropic
import os
import json
import logging
from typing import Dict, Any

# Import RAG system and news components
from .rag_system import BookRAGSystem
from .news_api import NewsAPI
from .news_summarizer import NewsSummarizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
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
        
        # Initialize RAG system and news components
        try:
            self.rag_system = BookRAGSystem()
            self.news_api = NewsAPI()
            self.news_summarizer = NewsSummarizer()
            logger.info("RAG system and news components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG/news systems: {e}")
            self.rag_system = None
            self.news_api = None
            self.news_summarizer = None
    
    def create_analysis_prompt(self, company_data, price_data, news_articles):
        """Create a comprehensive prompt for stock analysis with RAG context"""
        
        # Enhanced RAG with global news analysis
        book_context = ""
        global_news_context = ""
        
        if self.rag_system and self.news_api and self.news_summarizer:
            try:
                company_name = company_data.get('name', 'Unknown Company')
                ticker = company_data.get('symbol', 'UNKNOWN')
                
                # Step 1: Get global affairs news
                global_topics = ['Global Tension', 'Wars', 'Trading co-operations']
                global_news = self.news_api.get_global_affairs_news(topics=global_topics, max_articles=10)
                
                # Step 2: Summarize how news affects markets (generic themes)
                investment_themes = self.news_summarizer.summarize_market_impact(global_news)
                
                # Step 3: Search books using investment themes (not company-specific)
                relevant_chunks = self.rag_system.retrieve_relevant_content_by_theme(
                    investment_themes=investment_themes,
                    top_k=3
                )
                
                book_context = self.rag_system.format_context_for_llm(relevant_chunks)
                
                # Format global news context with specific details
                global_news_context = "Current Global Affairs (include specific details in your analysis):\n\n"
                for i, article in enumerate(global_news[:3], 1):
                    global_news_context += f"{i}. {article['title']}\n"
                    global_news_context += f"   Details: {article['description']}\n"
                    global_news_context += f"   Source: {article['source']}\n"
                    global_news_context += f"   Published: {article['published_at']}\n"
                    if article.get('url'):
                        global_news_context += f"   URL: {article['url']}\n"
                    global_news_context += "\n"
                
                logger.info(f"Enhanced RAG: themes='{investment_themes[:50]}...', {len(relevant_chunks)} book chunks, {len(global_news)} news articles")
                
                # Store context for frontend display
                self.last_rag_context = {
                    'chunks': relevant_chunks,
                    'formatted_context': book_context,
                    'investment_themes': investment_themes,
                    'global_news': global_news
                }
                
            except Exception as e:
                logger.error(f"Error in enhanced RAG analysis: {e}")
                book_context = "Investment literature context not available."
                global_news_context = "Global affairs context not available."
                self.last_rag_context = {'chunks': [], 'formatted_context': book_context}
        else:
            book_context = "Investment literature context not available."
            global_news_context = "Global affairs context not available."
            self.last_rag_context = {'chunks': [], 'formatted_context': book_context}
        
        # Format company information
        company_info = f"""
Company Information:
- Name: {company_data.get('name', 'N/A')}
- Ticker: {company_data.get('symbol', 'N/A')}
- Sector: {company_data.get('sector', 'N/A')}
- Industry: {company_data.get('industry', 'N/A')}
- Market Cap: ${company_data.get('market_cap', 'N/A'):,}
- P/E Ratio: {company_data.get('pe_ratio', 'N/A')}
- Forward P/E: {company_data.get('forward_pe', 'N/A')}
- Price to Book: {company_data.get('price_to_book', 'N/A')}
- Dividend Yield: {company_data.get('dividend_yield', 'N/A')}
- Current Price: ${company_data.get('current_price', 'N/A')}
- Analyst Target (High): ${company_data.get('target_high_price', 'N/A')}
- Analyst Target (Mean): ${company_data.get('target_mean_price', 'N/A')}
- Analyst Target (Low): ${company_data.get('target_low_price', 'N/A')}
- Current Recommendation: {company_data.get('recommendation', 'N/A')}
"""
        
        # Format price trend
        if price_data and len(price_data) > 0:
            recent_prices = price_data[-10:]  # Last 10 trading days
            price_trend = "Recent Price Movement (Last 10 Trading Days):\n"
            for day in recent_prices:
                price_trend += f"- {day['date']}: Open ${day['open']}, Close ${day['close']}, Volume {day['volume']:,}\n"
            
            # Calculate price performance
            if len(price_data) > 30:
                price_6m_ago = price_data[0]['close']
                price_1m_ago = price_data[-21]['close'] if len(price_data) >= 21 else price_data[0]['close']
                current_price = price_data[-1]['close']
                
                perf_6m = ((current_price - price_6m_ago) / price_6m_ago) * 100
                perf_1m = ((current_price - price_1m_ago) / price_1m_ago) * 100
                
                price_trend += f"\nPerformance:\n"
                price_trend += f"- 6-Month Return: {perf_6m:.2f}%\n"
                price_trend += f"- 1-Month Return: {perf_1m:.2f}%\n"
        else:
            price_trend = "Price data not available.\n"
        
        # Format news
        news_summary = ""
        if news_articles:
            news_summary = "Recent News Headlines:\n"
            for i, article in enumerate(news_articles[:5], 1):  # Top 5 articles
                news_summary += f"{i}. {article['title']} ({article['source']})\n"
                news_summary += f"   {article['description']}\n\n"
        else:
            news_summary = "No recent news articles available.\n"
        
        prompt = f"""
You are a professional stock analyst. Based on current global affairs, established investment principles, and company fundamentals, provide a comprehensive stock analysis and recommendation.

CURRENT GLOBAL CONTEXT:
{global_news_context}

RELEVANT INVESTMENT PRINCIPLES:
{book_context}

COMPANY FUNDAMENTALS:
{company_info}

{price_trend}

{news_summary}

Please provide your analysis in the following JSON format:
{{
    "recommendation": "BUY|HOLD|SELL",
    "confidence_score": <number between 0-100>,
    "rationale": "<detailed explanation for your recommendation>",
    "key_factors": [
        "<factor 1>",
        "<factor 2>",
        "<factor 3>"
    ],
    "risks": [
        "<risk 1>",
        "<risk 2>"
    ],
    "price_target": "<your 12-month price target or N/A>"
}}

Consider the following in your analysis:
1. Fundamental metrics (P/E, market cap, financial health)
2. Recent price performance and trends
3. News sentiment and company developments
4. Industry and market conditions
5. Technical indicators from price movement
6. Established investment principles from the literature context above

IMPORTANT: When referencing global affairs in your key_factors and risks, include SPECIFIC DETAILS from the current events such as:
- Exact dates, locations, countries, or regions involved
- Specific numbers, percentages, or quantities mentioned
- Names of leaders, organizations, or institutions
- Specific events, agreements, or conflicts referenced
- Concrete impacts or outcomes described

For example, instead of saying "Rising oil prices may impact costs", say "Iran's closure of the Hormuz Strait (affecting 20% of global oil supply) may increase operational costs by 15-20% and impact consumer spending."

Ground your recommendation in proven investment methodologies. Reference specific concepts from the investment literature when relevant. Explicitly mention how the investment literature above supports or challenges your analysis. Be objective and consider both positive and negative factors.
"""
        
        return prompt
    
    def get_stock_analysis(self, company_data, price_data, news_articles):
        """Get LLM analysis of stock data with RAG context"""
        if not self.client:
            logger.warning("Anthropic client not available - returning demo analysis")
            demo_analysis = {
                'recommendation': 'BUY',
                'confidence_score': 85,
                'rationale': f'Based on technical analysis of {company_data.get("name", "the company")}, the stock shows strong fundamentals with positive market sentiment. The company demonstrates solid financial performance and growth potential in its sector.',
                'key_factors': [
                    'Strong revenue growth trajectory',
                    'Positive market sentiment',
                    'Solid financial fundamentals',
                    'Industry leadership position'
                ],
                'risks': [
                    'Market volatility concerns',
                    'Sector-specific headwinds',
                    'Economic uncertainty factors'
                ],
                'price_target': f'${float(str(company_data.get("current_price", "100")).replace("$", "")) * 1.15:.2f}',
                'rag_context': {
                    'sources': [],
                    'reasoning': "Demo mode - RAG context not available without API key."
                }
            }
            return demo_analysis
            
        try:
            prompt = self.create_analysis_prompt(company_data, price_data, news_articles)
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Will update to claude-4 when available
                max_tokens=500,
                temperature=0.3,
                system="You are a professional stock analyst providing concise investment recommendations grounded in established investment literature and principles.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Handle response content properly
            if hasattr(response.content[0], 'text'):
                analysis_text = response.content[0].text.strip()
            else:
                analysis_text = str(response.content[0]).strip()
            
            # Try to parse JSON response
            try:
                logger.info(f"Raw LLM response: {analysis_text[:200]}...")
                
                # Extract and clean JSON from the response
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                
                if json_start != -1 and json_end != -1:
                    json_str = analysis_text[json_start:json_end]
                    logger.info(f"Extracted JSON: {json_str[:200]}...")
                    
                    # Clean common JSON formatting issues
                    json_str = json_str.replace('\n', ' ').replace('\r', ' ')
                    json_str = json_str.replace('\\', '\\\\')  # Escape backslashes
                    
                    # Try to fix common quote issues
                    import re
                    # Fix unescaped quotes in strings (basic attempt)
                    json_str = re.sub(r'(?<!\\)"(?=[^,}\]]*[,}\]])', '\\"', json_str)
                    
                    analysis = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
                
                # Validate required fields
                required_fields = ['recommendation', 'confidence_score', 'rationale']
                for field in required_fields:
                    if field not in analysis:
                        analysis[field] = "N/A"
                
                # Ensure recommendation is valid
                if analysis['recommendation'] not in ['BUY', 'HOLD', 'SELL']:
                    analysis['recommendation'] = 'HOLD'
                
                # Ensure confidence score is valid
                try:
                    confidence = float(analysis['confidence_score'])
                    if confidence < 0 or confidence > 100:
                        analysis['confidence_score'] = 50
                except (ValueError, TypeError):
                    analysis['confidence_score'] = 50
                
                # Add RAG context to response
                analysis['rag_context'] = {
                    'sources': [
                        {
                            'book': chunk['book_name'],
                            'chapter': chunk['chapter'],
                            'page': chunk['page_number'],
                            'relevance_score': chunk['relevance_score'],
                            'text_preview': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text']
                        }
                        for chunk in self.last_rag_context.get('chunks', [])
                    ],
                    'global_news': self.last_rag_context.get('global_news', []),
                    'reasoning': "Analysis grounded in established investment principles from classic literature."
                }
                
                logger.info(f"Successfully generated stock analysis with {len(analysis['rag_context']['sources'])} RAG sources")
                return analysis
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response that failed to parse: {analysis_text}")
                
                # Try to extract just the rationale from the text if JSON parsing fails
                rationale_text = "Analysis could not be properly parsed. Please try again."
                
                # If we can find a coherent text response, extract it
                if "rationale" in analysis_text.lower():
                    # Try to extract rationale from failed JSON
                    try:
                        import re
                        rationale_match = re.search(r'"rationale":\s*"([^"]*(?:\\.[^"]*)*)"', analysis_text)
                        if rationale_match:
                            rationale_text = rationale_match.group(1).replace('\\"', '"')
                    except:
                        pass
                
                # Fallback analysis
                return {
                    'recommendation': 'HOLD',
                    'confidence_score': 50,
                    'rationale': rationale_text,
                    'key_factors': ['Unable to parse detailed factors - please retry analysis'],
                    'risks': ['JSON parsing failed - please retry analysis'],
                    'price_target': 'N/A',
                    'rag_context': {
                        'sources': getattr(self, 'last_rag_context', {}).get('chunks', []),
                        'global_news': getattr(self, 'last_rag_context', {}).get('global_news', []),
                        'reasoning': "Analysis attempted but JSON parsing failed."
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting LLM analysis: {str(e)}")
            return {
                'recommendation': 'HOLD',
                'confidence_score': 0,
                'rationale': f'Analysis failed due to error: {str(e)}',
                'key_factors': [],
                'risks': [],
                'price_target': 'N/A',
                'rag_context': {
                    'sources': [],
                    'reasoning': "Analysis failed due to technical error."
                }
            } 