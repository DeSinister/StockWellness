import requests
import os
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsAPI:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2/everything"
        
        if not self.api_key:
            logger.warning("NEWS_API_KEY not found in environment variables")
    
    def get_global_affairs_news(self, topics=['Global Tension', 'Wars', 'Trading co-operations'], days=7, max_articles=15):
        """Fetch news about global affairs that could affect markets"""
        if not self.api_key:
            logger.error("News API key not configured")
            return self._get_demo_global_news(topics)
        
        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            # Create comprehensive query for global affairs with specific terms
            query_terms = []
            for topic in topics:
                if topic.lower() == 'global tension':
                    query_terms.extend(['geopolitical tension', 'international crisis', 'diplomatic relations', 'sanctions', 'Iran', 'China', 'Russia', 'NATO'])
                elif topic.lower() == 'wars':
                    query_terms.extend(['war', 'conflict', 'military action', 'Ukraine', 'Middle East', 'oil supply', 'Strait of Hormuz'])
                elif topic.lower() == 'trading co-operations':
                    query_terms.extend(['trade agreement', 'tariffs', 'supply chain', 'US China trade', 'OPEC', 'Federal Reserve'])
            
            query = ' OR '.join(query_terms[:12])  # Include more specific terms
            
            params = {
                'q': query,
                'apiKey': self.api_key,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': max_articles,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d')
            }
            
            logger.info(f"NewsAPI request: {self.base_url} with params: {params}")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"NewsAPI response status: {data.get('status')}, total results: {data.get('totalResults', 0)}")
            
            if data['status'] != 'ok':
                logger.error(f"News API returned error: {data.get('message', 'Unknown error')}")
                return self._get_demo_global_news(topics)
            
            raw_articles = data.get('articles', [])
            logger.info(f"Raw articles found: {len(raw_articles)}")
            
            articles = []
            for i, article in enumerate(raw_articles):
                logger.debug(f"Article {i}: title='{article.get('title', '')[:50]}...', has_desc={bool(article.get('description'))}")
                
                # More lenient filtering - just check if title exists
                if (article.get('title') and 
                    article.get('url') and
                    '[Removed]' not in article.get('title', '')):
                    
                    # Combine description and content for more detailed context
                    description = article.get('description', 'No description available')
                    content = article.get('content', '')
                    
                    # Create comprehensive details from both description and content
                    full_details = description
                    if content and content != description:
                        # Remove [+xxx chars] indicators and combine
                        content_clean = content.split('[+')[0].strip()
                        if content_clean and len(content_clean) > len(description):
                            full_details = f"{description} {content_clean}"
                    
                    articles.append({
                        'title': article['title'],
                        'description': full_details[:500] + '...' if len(full_details) > 500 else full_details,  # More detailed description
                        'url': article['url'],
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'published_at': article.get('publishedAt', ''),
                        'content': content,
                        'author': article.get('author', 'Unknown')
                    })
                else:
                    logger.debug(f"Filtered out article: {article.get('title', 'No title')}")
            
            logger.info(f"Successfully fetched {len(articles)} global affairs articles (filtered from {len(raw_articles)})")
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching global affairs news: {str(e)}")
            return self._get_demo_global_news(topics)
        except Exception as e:
            logger.error(f"Error fetching global affairs news: {str(e)}")
            return self._get_demo_global_news(topics)
    
    def format_news_for_llm(self, articles):
        """Format news articles for LLM context"""
        if not articles:
            return "No recent news articles found."
        
        formatted_news = "Recent News Articles:\n\n"
        
        for i, article in enumerate(articles, 1):
            formatted_news += f"{i}. {article['title']}\n"
            formatted_news += f"   Source: {article['source']}\n"
            formatted_news += f"   Summary: {article['description']}\n"
            if article.get('content'):
                # Truncate content if too long
                content = article['content'][:200] + "..." if len(article['content']) > 200 else article['content']
                formatted_news += f"   Content: {content}\n"
            formatted_news += f"   Published: {article['published_at']}\n\n"
        
        return formatted_news 
    
    def _get_demo_global_news(self, topics):
        """Provide demo global affairs news when real API is not available"""
        from datetime import datetime, timedelta
        
        demo_articles = [
            {
                'title': 'Iran Threatens Strait of Hormuz Closure Amid Rising Oil Tensions',
                'description': 'Iran has indicated it may close the Strait of Hormuz, through which 20% of global oil supply passes, following escalated tensions with Western allies. The closure would affect approximately 21 million barrels per day of oil transit, potentially driving crude prices up 25-30%. Key OPEC members including Saudi Arabia and UAE are monitoring the situation closely.',
                'url': 'https://example.com/energy/iran-hormuz',
                'source': 'Energy Intelligence',
                'published_at': (datetime.now() - timedelta(hours=3)).isoformat() + 'Z',
                'content': '[Demo] The strategic waterway handles roughly 35% of seaborne petroleum liquids...',
                'author': 'Energy Desk'
            },
            {
                'title': 'US-China Trade Relations Deteriorate as New 15% Tariffs Take Effect',
                'description': 'The United States imposed additional 15% tariffs on $250 billion worth of Chinese goods yesterday, affecting semiconductors, electronics, and manufacturing components. China responded with retaliatory measures on US agricultural products worth $120 billion. The escalation may disrupt supply chains for technology companies and increase consumer prices by 3-5% across affected sectors.',
                'url': 'https://example.com/trade/us-china-tariffs',
                'source': 'Global Trade Monitor',
                'published_at': (datetime.now() - timedelta(hours=6)).isoformat() + 'Z',
                'content': '[Demo] Trade war escalation impacts global supply chains significantly...',
                'author': 'Trade Analysis Team'
            },
            {
                'title': 'Federal Reserve Signals 0.75% Interest Rate Hike Following Inflation Data',
                'description': 'Federal Reserve Chairman Jerome Powell announced Wednesday that the Fed will likely implement a 0.75 percentage point interest rate increase next month, bringing the federal funds rate to 5.25-5.50%. The decision follows October inflation data showing core CPI at 4.1%, above the Fed\'s 2% target. Financial markets dropped 2.3% on the announcement, with tech stocks particularly affected.',
                'url': 'https://example.com/economics/fed-rates',
                'source': 'Financial Times',
                'published_at': (datetime.now() - timedelta(hours=12)).isoformat() + 'Z',
                'content': '[Demo] Monetary policy tightening continues to combat persistent inflation...',
                'author': 'Economics Bureau'
            }
        ]
        
        logger.info(f"Using demo global affairs articles for topics: {topics}")
        return demo_articles