import anthropic
import os
import json
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsSummarizer:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key or self.api_key == 'your_anthropic_api_key_here':
            logger.warning("ANTHROPIC_API_KEY not found - news summarizer will use fallback")
            self.client = None
        else:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {str(e)}")
                self.client = None
    
    def summarize_market_impact(self, news_articles: List[Dict[str, Any]]) -> str:
        """Summarize how global news affects stock markets in generic terms"""
        
        if not news_articles:
            return "stable market conditions defensive investing risk management"
        
        # Format news for analysis
        news_context = "Recent Global News:\n\n"
        for i, article in enumerate(news_articles[:5], 1):
            news_context += f"{i}. {article['title']}\n"
            news_context += f"   {article['description']}\n\n"
        
        if not self.client:
            return self._get_fallback_summary(news_articles)
        
        try:
            prompt = f"""
Analyze the following global news and identify the general investment themes and market conditions they suggest. 
Focus on broad investment patterns rather than specific companies.

{news_context}

Provide a concise analysis in 2-3 sentences about:
1. What general market conditions these events suggest (volatility, uncertainty, growth, etc.)
2. What investment themes or principles would be most relevant (defensive strategies, growth opportunities, risk management, etc.)
3. What economic factors investors should consider (inflation, supply chains, geopolitical risk, etc.)

Return ONLY the key investment themes and patterns as a short summary suitable for searching investment literature.
"""
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=0.3,
                system="You are a financial analyst who identifies general investment themes from current events.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Handle response content
            if hasattr(response.content[0], 'text'):
                summary = response.content[0].text.strip()
            else:
                summary = str(response.content[0]).strip()
            
            logger.info(f"Generated market impact summary: {summary[:100]}...")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating news summary: {e}")
            return self._get_fallback_summary(news_articles)
    
    def _get_fallback_summary(self, news_articles: List[Dict[str, Any]]) -> str:
        """Provide fallback summary when LLM is not available"""
        
        # Simple keyword-based analysis
        keywords = []
        for article in news_articles:
            title_lower = article.get('title', '').lower()
            desc_lower = article.get('description', '').lower()
            text = f"{title_lower} {desc_lower}"
            
            # Check for various themes
            if any(word in text for word in ['tension', 'war', 'conflict', 'dispute']):
                keywords.extend(['geopolitical risk', 'defensive investing', 'volatility management'])
            
            if any(word in text for word in ['trade', 'tariff', 'agreement', 'cooperation']):
                keywords.extend(['international trade', 'supply chain risk', 'global commerce'])
            
            if any(word in text for word in ['oil', 'energy', 'commodity']):
                keywords.extend(['commodity investing', 'inflation hedging', 'energy sector'])
            
            if any(word in text for word in ['economic', 'growth', 'recession']):
                keywords.extend(['economic cycles', 'market timing', 'recession preparation'])
        
        # Default themes if no specific keywords found
        if not keywords:
            keywords = ['market uncertainty', 'risk management', 'diversification strategies']
        
        # Remove duplicates and create summary
        unique_keywords = list(set(keywords))
        summary = f"Current global events suggest focus on {' '.join(unique_keywords[:6])} when evaluating investment strategies."
        
        logger.info(f"Generated fallback summary with themes: {unique_keywords[:3]}")
        return summary 