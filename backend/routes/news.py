"""
News API endpoint for fetching health-related news.
Provides endpoints to retrieve health news from external APIs.
"""

import logging
import httpx
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# News API configuration
NEWS_API_KEY = 'pub_32bf0d48456749a2ab6061542060842c'
NEWS_API_URL = 'https://newsdata.io/api/1/news'


class NewsResponse(BaseModel):
    """Response model for news data."""
    status: str
    results: List[Dict[str, Any]]
    totalResults: Optional[int] = None


async def fetch_health_news(country: str = 'in', language: str = 'en') -> Dict[str, Any]:
    """
    Fetch health news from NewsData.io API.
    
    Args:
        country: Country code for news (default: 'in' for India)
        language: Language code for news (default: 'en')
        
    Returns:
        Dict containing news data
    """
    params = {
        'apikey': NEWS_API_KEY,
        'country': country,
        'category': 'health',
        'language': language
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(NEWS_API_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success':
                # Clean and format the results
                results = []
                for article in data.get('results', []):
                    cleaned_article = {
                        'title': article.get('title', 'No title'),
                        'link': article.get('link', ''),
                        'source_id': article.get('source_id', 'Unknown'),
                        'description': article.get('description', ''),
                        'pubDate': article.get('pubDate', ''),
                        'image_url': article.get('image_url', ''),
                        'category': article.get('category', ['health'])
                    }
                    results.append(cleaned_article)
                
                return {
                    'status': 'success',
                    'results': results,
                    'totalResults': len(results)
                }
            else:
                logger.error(f"News API error: {data.get('message', 'Unknown error')}")
                return {
                    'status': 'error',
                    'message': data.get('message', 'Failed to fetch news'),
                    'results': []
                }
                
    except httpx.TimeoutException:
        logger.error("News API request timeout")
        return {
            'status': 'error',
            'message': 'News service timeout',
            'results': []
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"News API HTTP error: {e.response.status_code}")
        return {
            'status': 'error',
            'message': f'News service returned status {e.response.status_code}',
            'results': []
        }
    except Exception as e:
        logger.error(f"Unexpected error fetching news: {e}")
        return {
            'status': 'error',
            'message': 'An unexpected error occurred while fetching news',
            'results': []
        }


@router.get("/news/health")
async def get_health_news(
    country: str = 'in',
    language: str = 'en'
):
    """
    Get health news from NewsData.io API.
    
    Args:
        country: Country code for news filtering (default: 'in')
        language: Language code for news (default: 'en')
        
    Returns:
        JSON response with health news articles
    """
    try:
        logger.info(f"Fetching health news for country: {country}, language: {language}")
        
        news_data = await fetch_health_news(country, language)
        
        if news_data['status'] == 'success':
            logger.info(f"Successfully fetched {len(news_data['results'])} health news articles")
            return JSONResponse(
                status_code=200,
                content=news_data
            )
        else:
            logger.warning(f"News API returned error: {news_data.get('message')}")
            return JSONResponse(
                status_code=503,
                content=news_data
            )
            
    except Exception as e:
        logger.error(f"Health news endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching news"
        )


@router.get("/news/health/latest")
async def get_latest_health_news():
    """
    Get the latest health news with default settings.
    Simplified endpoint for quick access to recent health news.
    """
    try:
        logger.info("Fetching latest health news")
        
        news_data = await fetch_health_news()
        
        if news_data['status'] == 'success':
            # Return only the first 10 articles for latest news
            latest_results = news_data['results'][:10]
            
            return JSONResponse(
                status_code=200,
                content={
                    'status': 'success',
                    'results': latest_results,
                    'totalResults': len(latest_results)
                }
            )
        else:
            return JSONResponse(
                status_code=503,
                content=news_data
            )
            
    except Exception as e:
        logger.error(f"Latest health news endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching latest news"
        )