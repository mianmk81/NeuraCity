"""
Example Usage of NeuraCity AI Services

This script demonstrates how to use all AI services:
1. Generate synthetic social media posts
2. Analyze mood for city areas
3. Process accident issues (emergency summaries)
4. Process infrastructure issues (work orders)

Run with:
    python scripts/example_ai_usage.py
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.services import (
    MoodAnalysisService,
    GeminiService,
    ActionEngine
)


# ============================================================================
# Example 1: Mood Analysis
# ============================================================================

async def example_mood_analysis():
    """
    Demonstrate mood analysis on synthetic social media posts.
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Mood Analysis")
    print("="*70 + "\n")

    # Initialize service
    service = MoodAnalysisService()

    # Sample posts for different areas
    sample_posts = {
        'MIDTOWN': [
            {'text': 'Traffic is absolutely terrible in Midtown right now', 'area_id': 'MIDTOWN'},
            {'text': 'Love the new coffee shop in Midtown!', 'area_id': 'MIDTOWN'},
            {'text': 'Just another day at the office in Midtown', 'area_id': 'MIDTOWN'},
            {'text': 'Midtown construction noise is unbearable', 'area_id': 'MIDTOWN'},
            {'text': 'Beautiful weather in Midtown today', 'area_id': 'MIDTOWN'},
        ],
        'PARK_DISTRICT': [
            {'text': 'Amazing walk in the park today!', 'area_id': 'PARK_DISTRICT'},
            {'text': 'The Park District is so peaceful and clean', 'area_id': 'PARK_DISTRICT'},
            {'text': 'Love spending time in the Park District', 'area_id': 'PARK_DISTRICT'},
            {'text': 'Perfect day for a picnic in the park', 'area_id': 'PARK_DISTRICT'},
            {'text': 'The Park District improvements look fantastic', 'area_id': 'PARK_DISTRICT'},
        ]
    }

    # Analyze each area
    for area_id, posts in sample_posts.items():
        print(f"\n--- {area_id} ---")

        # Analyze individual posts
        print("\nIndividual Post Analysis:")
        for post in posts:
            score = service.analyze_post_sentiment(post['text'])
            sentiment_label = 'POSITIVE' if score > 0.3 else 'NEGATIVE' if score < -0.3 else 'NEUTRAL'
            print(f"  {sentiment_label:8s} ({score:+.2f}): {post['text'][:50]}...")

        # Calculate area mood
        mood_data = await service.calculate_area_mood(area_id, posts)

        print(f"\nArea Mood Summary:")
        print(f"  Mood Score: {mood_data['mood_score']:.3f}")
        print(f"  Post Count: {mood_data['post_count']}")
        print(f"  Distribution:")
        dist = mood_data['sentiment_distribution']
        print(f"    Positive: {dist['positive']}")
        print(f"    Neutral:  {dist['neutral']}")
        print(f"    Negative: {dist['negative']}")


# ============================================================================
# Example 2: Emergency Summary Generation
# ============================================================================

async def example_emergency_summary():
    """
    Demonstrate emergency summary generation for accidents.
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Emergency Summary Generation")
    print("="*70 + "\n")

    # Initialize service (no API key = fallback mode)
    service = GeminiService()

    # Sample accident scenarios
    accidents = [
        {
            'id': 'accident-001',
            'lat': 40.7589,
            'lng': -73.9851,
            'issue_type': 'accident',
            'description': 'Multi-car collision on highway, multiple injuries reported',
            'severity': 0.90,
            'urgency': 0.95,
            'created_at': datetime.utcnow().isoformat()
        },
        {
            'id': 'accident-002',
            'lat': 40.7128,
            'lng': -74.0060,
            'issue_type': 'accident',
            'description': 'Minor fender bender at intersection',
            'severity': 0.35,
            'urgency': 0.40,
            'created_at': datetime.utcnow().isoformat()
        }
    ]

    for accident in accidents:
        print(f"\n--- Accident {accident['id']} ---")
        print(f"Severity: {accident['severity']:.2f}")
        print(f"Description: {accident['description']}")

        # Generate emergency summary
        summary = await service.generate_emergency_summary(accident)

        print(f"\nGenerated Emergency Summary:")
        print("-" * 70)
        print(summary)
        print("-" * 70)


# ============================================================================
# Example 3: Work Order Generation
# ============================================================================

async def example_work_order_generation():
    """
    Demonstrate work order generation for infrastructure issues.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Work Order Generation")
    print("="*70 + "\n")

    # Initialize service
    service = GeminiService()

    # Sample infrastructure issues
    issues = [
        {
            'id': 'issue-001',
            'issue_type': 'pothole',
            'description': 'Large pothole on Main Street causing damage to vehicles',
            'severity': 0.75,
            'lat': 40.7589,
            'lng': -73.9851,
            'created_at': datetime.utcnow().isoformat()
        },
        {
            'id': 'issue-002',
            'issue_type': 'traffic_light',
            'description': 'Traffic signal not working at 5th Ave intersection',
            'severity': 0.85,
            'lat': 40.7128,
            'lng': -74.0060,
            'created_at': datetime.utcnow().isoformat()
        },
        {
            'id': 'issue-003',
            'issue_type': 'other',
            'description': 'Broken water main flooding street',
            'severity': 0.80,
            'lat': 40.7282,
            'lng': -73.7949,
            'created_at': datetime.utcnow().isoformat()
        }
    ]

    for issue in issues:
        print(f"\n--- Issue {issue['id']} ---")
        print(f"Type: {issue['issue_type']}")
        print(f"Severity: {issue['severity']:.2f}")
        print(f"Description: {issue['description']}")

        # Generate work order suggestion
        work_order = await service.generate_work_order_suggestion(issue)

        print(f"\nGenerated Work Order:")
        print(f"  Priority: {work_order['estimated_priority']}")
        print(f"  Contractor Specialty: {work_order['contractor_specialty']}")
        print(f"  Materials: {work_order['materials'][:100]}...")
        print(f"  Notes: {work_order['notes'][:100]}...")


# ============================================================================
# Example 4: Action Engine (Full Workflow)
# ============================================================================

async def example_action_engine():
    """
    Demonstrate full action engine workflow.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Action Engine (Full Workflow)")
    print("="*70 + "\n")

    print("NOTE: This example shows the workflow without database.")
    print("In production, ActionEngine would:")
    print("  1. Fetch issue from database")
    print("  2. Route to appropriate AI service")
    print("  3. Store results in database")
    print("  4. Update issue status\n")

    # Initialize services
    gemini = GeminiService()

    # Simulate different issue types
    test_issues = [
        {
            'id': 'test-accident-123',
            'issue_type': 'accident',
            'description': 'Serious accident on highway',
            'severity': 0.85,
            'lat': 40.7589,
            'lng': -73.9851
        },
        {
            'id': 'test-pothole-456',
            'issue_type': 'pothole',
            'description': 'Deep pothole on residential street',
            'severity': 0.60,
            'lat': 40.7128,
            'lng': -74.0060
        }
    ]

    for issue in test_issues:
        print(f"\n--- Processing Issue: {issue['id']} ---")
        print(f"Type: {issue['issue_type']}")

        if issue['issue_type'] == 'accident':
            print("Action: Generating emergency summary...")
            summary = await gemini.generate_emergency_summary(issue)
            print("Result: Emergency summary created")
            print(f"  -> Would be stored in 'emergency_queue' table")

        elif issue['issue_type'] in ['pothole', 'traffic_light']:
            print("Action: Generating work order...")
            work_order = await gemini.generate_work_order_suggestion(issue)
            print("Result: Work order created")
            print(f"  -> Contractor specialty: {work_order['contractor_specialty']}")
            print(f"  -> Priority: {work_order['estimated_priority']}")
            print(f"  -> Would be stored in 'work_orders' table")

        else:
            print("Action: Logging for manual review...")
            print("Result: Issue logged")


# ============================================================================
# Example 5: Batch Processing
# ============================================================================

async def example_batch_processing():
    """
    Demonstrate efficient batch processing of multiple posts.
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Batch Processing")
    print("="*70 + "\n")

    # Initialize service
    service = MoodAnalysisService()

    # Generate larger batch of posts
    posts = [
        {'text': f'Sample post number {i} about the city', 'area_id': 'TEST'}
        for i in range(20)
    ]

    # Add some specific sentiment posts
    posts.extend([
        {'text': 'I absolutely love living in this city!', 'area_id': 'TEST'},
        {'text': 'Traffic and noise are getting worse every day', 'area_id': 'TEST'},
        {'text': 'The new park is beautiful and well maintained', 'area_id': 'TEST'},
        {'text': 'Infrastructure is falling apart, streets full of potholes', 'area_id': 'TEST'},
    ])

    print(f"Processing {len(posts)} posts in batch...")

    # Batch process
    import time
    start = time.time()
    analyzed = await service.analyze_posts_batch(posts)
    elapsed = time.time() - start

    print(f"Completed in {elapsed:.2f} seconds")
    print(f"Average: {elapsed/len(posts)*1000:.1f} ms per post")

    # Show sentiment distribution
    positive = sum(1 for p in analyzed if p['sentiment_score'] > 0.3)
    negative = sum(1 for p in analyzed if p['sentiment_score'] < -0.3)
    neutral = len(analyzed) - positive - negative

    print(f"\nSentiment Distribution:")
    print(f"  Positive: {positive} ({positive/len(analyzed)*100:.1f}%)")
    print(f"  Neutral:  {neutral} ({neutral/len(analyzed)*100:.1f}%)")
    print(f"  Negative: {negative} ({negative/len(analyzed)*100:.1f}%)")


# ============================================================================
# Main Function
# ============================================================================

async def main():
    """
    Run all examples.
    """
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "NeuraCity AI Services Examples" + " "*23 + "║")
    print("╚" + "="*68 + "╝")

    try:
        # Run all examples
        await example_mood_analysis()
        await example_emergency_summary()
        await example_work_order_generation()
        await example_action_engine()
        await example_batch_processing()

        print("\n" + "="*70)
        print("All examples completed successfully!")
        print("="*70 + "\n")

        print("Next Steps:")
        print("  1. Set GEMINI_API_KEY to use actual AI generation")
        print("  2. Configure Supabase to enable database storage")
        print("  3. Generate synthetic posts: python scripts/generate_synthetic_posts.py")
        print("  4. Run tests: pytest backend/tests/test_ai_services.py -v")
        print("  5. Integrate with FastAPI backend\n")

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
