"""Mood analysis service using HuggingFace transformers."""
from transformers import pipeline
from app.core.config import get_settings
import logging
from typing import List, Dict
from functools import lru_cache

logger = logging.getLogger(__name__)
settings = get_settings()

@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    """Get cached sentiment analysis pipeline."""
    try:
        classifier = pipeline(
            "sentiment-analysis",
            model=settings.SENTIMENT_MODEL,
            device=-1  # CPU
        )
        logger.info("Sentiment analysis model loaded")
        return classifier
    except Exception as e:
        logger.error(f"Failed to load sentiment model: {e}")
        return None


async def analyze_sentiment(text: str) -> float:
    """
    Analyze sentiment of text.
    
    Args:
        text: Text to analyze
        
    Returns:
        float: Sentiment score from -1 (negative) to +1 (positive)
    """
    classifier = get_sentiment_pipeline()
    if not classifier:
        return 0.0
    
    try:
        result = classifier(text[:512])[0]  # Limit text length
        label = result['label']
        score = result['score']
        
        if label == 'POSITIVE':
            return round(score, 2)
        else:
            return round(-score, 2)
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return 0.0


async def analyze_batch(texts: List[str]) -> List[float]:
    """
    Analyze sentiment for multiple texts.
    
    Args:
        texts: List of texts to analyze
        
    Returns:
        List of sentiment scores
    """
    classifier = get_sentiment_pipeline()
    if not classifier:
        return [0.0] * len(texts)
    
    try:
        truncated = [t[:512] for t in texts]
        results = classifier(truncated)
        
        scores = []
        for result in results:
            label = result['label']
            score = result['score']
            if label == 'POSITIVE':
                scores.append(round(score, 2))
            else:
                scores.append(round(-score, 2))
        
        return scores
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        return [0.0] * len(texts)


async def calculate_area_mood(posts: List[Dict]) -> float:
    """
    Calculate average mood for an area from multiple posts.
    
    Args:
        posts: List of post dicts with 'text' field
        
    Returns:
        float: Average mood score
    """
    if not posts:
        return 0.0
    
    texts = [p.get('text', '') for p in posts if p.get('text')]
    if not texts:
        return 0.0
    
    scores = await analyze_batch(texts)
    return round(sum(scores) / len(scores), 2)
