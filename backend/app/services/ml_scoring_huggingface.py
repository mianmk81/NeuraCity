"""
ML-based scoring using HuggingFace models for local inference.
This approach trains/uses classification models instead of hardcoded rules.

NOTE: This is an alternative to ml_scoring_service.py (Gemini-based).
Requires training data to work well in production.
"""
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from app.core.config import get_settings
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from functools import lru_cache
import torch

logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache(maxsize=1)
def get_severity_classifier():
    """
    Get a cached text classifier for severity prediction.
    
    In production, you would:
    1. Collect labeled training data (issues with known severity scores)
    2. Fine-tune a BERT model on your data
    3. Load that custom model here
    
    For now, using zero-shot classification as a demo.
    """
    try:
        classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1  # CPU
        )
        logger.info("Severity classifier loaded (HuggingFace)")
        return classifier
    except Exception as e:
        logger.error(f"Failed to load severity classifier: {e}")
        return None


@lru_cache(maxsize=1)
def get_urgency_classifier():
    """
    Get a cached classifier for urgency prediction.
    Same as above - in production, use fine-tuned model.
    """
    try:
        classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1
        )
        logger.info("Urgency classifier loaded (HuggingFace)")
        return classifier
    except Exception as e:
        logger.error(f"Failed to load urgency classifier: {e}")
        return None


async def calculate_severity_ml_hf(
    issue_type: str,
    description: Optional[str] = None,
    image_available: bool = True
) -> float:
    """
    Use HuggingFace zero-shot classification to predict severity.
    
    In production, replace with fine-tuned model trained on your data.
    
    Args:
        issue_type: Type of issue
        description: User description
        image_available: Whether image was provided
        
    Returns:
        float: Severity score 0-1
    """
    classifier = get_severity_classifier()
    if not classifier:
        return _fallback_severity(issue_type)
    
    try:
        # Create text input for classification
        text = f"{issue_type}: {description or 'No description'}"
        
        # Define severity categories
        severity_labels = [
            "minor issue with low impact",
            "moderate issue with medium impact", 
            "significant issue with high impact",
            "severe issue with very high impact",
            "critical emergency with immediate danger"
        ]
        
        # Get zero-shot classification
        result = classifier(text, candidate_labels=severity_labels)
        
        # Convert to 0-1 score based on predicted label
        top_label = result['labels'][0]
        confidence = result['scores'][0]
        
        # Map labels to scores
        label_scores = {
            "minor issue with low impact": 0.2,
            "moderate issue with medium impact": 0.4,
            "significant issue with high impact": 0.6,
            "severe issue with very high impact": 0.8,
            "critical emergency with immediate danger": 0.95
        }
        
        base_score = label_scores.get(top_label, 0.5)
        # Weight by confidence
        severity = base_score * confidence + (0.5 * (1 - confidence))
        
        logger.info(f"HF Severity: {severity:.2f} (predicted: {top_label})")
        return round(severity, 2)
        
    except Exception as e:
        logger.error(f"Error in HF severity calculation: {e}")
        return _fallback_severity(issue_type)


async def calculate_urgency_ml_hf(
    issue_type: str,
    description: Optional[str] = None,
    severity: float = 0.5,
    traffic_congestion: Optional[float] = None,
    time_of_day: Optional[datetime] = None
) -> float:
    """
    Use HuggingFace models to predict urgency.
    
    Combines text classification with contextual factors.
    
    Args:
        issue_type: Type of issue
        description: User description
        severity: Calculated severity
        traffic_congestion: Traffic level 0-1
        time_of_day: Current time
        
    Returns:
        float: Urgency score 0-1
    """
    classifier = get_urgency_classifier()
    if not classifier:
        return _fallback_urgency(issue_type, time_of_day)
    
    try:
        # Build context-aware text
        hour_str = ""
        if time_of_day:
            hour = time_of_day.hour
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                hour_str = "during rush hour"
            elif 22 <= hour or hour <= 6:
                hour_str = "at night"
            else:
                hour_str = "during normal hours"
        
        traffic_str = ""
        if traffic_congestion is not None:
            if traffic_congestion > 0.7:
                traffic_str = "with heavy traffic"
            elif traffic_congestion > 0.4:
                traffic_str = "with moderate traffic"
            else:
                traffic_str = "with light traffic"
        
        text = f"{issue_type} {hour_str} {traffic_str}: {description or 'No details'}"
        
        # Define urgency categories
        urgency_labels = [
            "can wait days or weeks",
            "should be addressed within days",
            "should be addressed within hours",
            "requires response within one hour",
            "requires immediate response within minutes"
        ]
        
        result = classifier(text, candidate_labels=urgency_labels)
        top_label = result['labels'][0]
        confidence = result['scores'][0]
        
        label_scores = {
            "can wait days or weeks": 0.2,
            "should be addressed within days": 0.4,
            "should be addressed within hours": 0.6,
            "requires response within one hour": 0.8,
            "requires immediate response within minutes": 0.95
        }
        
        base_score = label_scores.get(top_label, 0.5)
        
        # Boost urgency if severity is high
        if severity > 0.7:
            base_score = min(1.0, base_score + 0.1)
        
        urgency = base_score * confidence + (0.5 * (1 - confidence))
        
        logger.info(f"HF Urgency: {urgency:.2f} (predicted: {top_label})")
        return round(urgency, 2)
        
    except Exception as e:
        logger.error(f"Error in HF urgency calculation: {e}")
        return _fallback_urgency(issue_type, time_of_day)


async def calculate_priority_ml_hf(severity: float, urgency: float) -> str:
    """
    Determine priority based on ML-calculated severity and urgency.
    """
    weighted_score = (severity * 0.4) + (urgency * 0.6)
    
    if weighted_score >= 0.85:
        return "critical"
    elif weighted_score >= 0.65:
        return "high"
    elif weighted_score >= 0.40:
        return "medium"
    else:
        return "low"


async def determine_action_type_ml_hf(
    issue_type: str,
    description: Optional[str] = None,
    severity: float = 0.5,
    urgency: float = 0.5
) -> str:
    """
    Use zero-shot classification to determine action type.
    
    Args:
        issue_type: Type of issue
        description: User description
        severity: ML severity score
        urgency: ML urgency score
        
    Returns:
        str: Action type (emergency, work_order, monitor)
    """
    try:
        classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1
        )
        
        text = f"{issue_type} (severity: {severity}, urgency: {urgency}): {description or ''}"
        
        action_labels = [
            "requires emergency response",
            "requires scheduled maintenance work order",
            "should be monitored but no immediate action needed"
        ]
        
        result = classifier(text, candidate_labels=action_labels)
        top_label = result['labels'][0]
        
        if "emergency" in top_label:
            return "emergency"
        elif "maintenance" in top_label or "work order" in top_label:
            return "work_order"
        else:
            return "monitor"
            
    except Exception as e:
        logger.error(f"Error in HF action type determination: {e}")
        return _fallback_action_type(issue_type)


# Fallback functions (same as original)
def _fallback_severity(issue_type: str) -> float:
    base_severity = {
        "accident": 0.9,
        "pothole": 0.5,
        "traffic_light": 0.7,
        "other": 0.3
    }
    return base_severity.get(issue_type, 0.3)


def _fallback_urgency(issue_type: str, time_of_day: Optional[datetime] = None) -> float:
    base_urgency = {
        "accident": 0.95,
        "pothole": 0.4,
        "traffic_light": 0.75,
        "other": 0.3
    }
    urgency = base_urgency.get(issue_type, 0.3)
    
    if time_of_day:
        hour = time_of_day.hour
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            urgency = min(1.0, urgency + 0.1)
    
    return round(urgency, 2)


def _fallback_action_type(issue_type: str) -> str:
    action_map = {
        "accident": "emergency",
        "pothole": "work_order",
        "traffic_light": "work_order",
        "other": "monitor"
    }
    return action_map.get(issue_type, "monitor")


# ===================================================================
# TRAINING CUSTOM MODELS (For Production)
# ===================================================================

"""
To train custom models for production:

1. COLLECT TRAINING DATA
   - Export historical issues from database
   - Have experts label severity (0-1), urgency (0-1), action type
   - Need at least 1000+ labeled examples for good performance

2. PREPARE DATASET
   import pandas as pd
   
   data = pd.DataFrame({
       'text': ["accident near school with injuries", ...],
       'severity': [0.9, 0.7, 0.5, ...],
       'urgency': [0.95, 0.8, 0.6, ...],
       'action': ["emergency", "work_order", ...]
   })

3. FINE-TUNE BERT MODEL
   from transformers import AutoModelForSequenceClassification, Trainer, TrainingArguments
   from datasets import Dataset
   
   # For severity prediction (regression)
   model = AutoModelForSequenceClassification.from_pretrained(
       "distilbert-base-uncased",
       num_labels=1  # Single output for regression
   )
   
   # Train model
   training_args = TrainingArguments(
       output_dir="./severity_model",
       num_train_epochs=3,
       per_device_train_batch_size=16,
       save_steps=500
   )
   
   trainer = Trainer(
       model=model,
       args=training_args,
       train_dataset=train_dataset
   )
   
   trainer.train()
   model.save_pretrained("./severity_model")

4. USE TRAINED MODEL
   model = AutoModelForSequenceClassification.from_pretrained("./severity_model")
   tokenizer = AutoTokenizer.from_pretrained("./severity_model")
   
   # Make predictions
   inputs = tokenizer(text, return_tensors="pt")
   outputs = model(**inputs)
   severity_score = torch.sigmoid(outputs.logits).item()

5. DEPLOY
   - Replace the zero-shot classifiers with your fine-tuned models
   - Much faster and more accurate than zero-shot
   - Specific to your city's patterns
"""


