#!/usr/bin/env python3
"""
NeuraCity Synthetic Data Generator

This script generates realistic synthetic data for:
- Social posts for mood analysis (using Faker)
- Time-series traffic patterns with rush hour cycles
- Noise level data for road segments
- Sample issues for testing

The data is inserted into Supabase and can be used for:
- Testing the mood analysis pipeline
- Simulating traffic patterns for routing
- Demonstrating noise-aware routing
- Populating the map with realistic data

Requirements:
- pip install faker supabase python-dotenv

Environment variables required (in .env):
- SUPABASE_URL
- SUPABASE_KEY
"""

import os
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from faker import Faker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Faker with US locale for Atlanta, Georgia
fake = Faker('en_US')

# ============================================================================
# Configuration
# ============================================================================

# City areas with coordinates and characteristics (Atlanta, Georgia - for mood analysis)
CITY_AREAS = {
    'MIDTOWN': {
        'lat': 33.7850,
        'lng': -84.3850,
        'base_mood': 0.15,
        'mood_variance': 0.3,
        'traffic_base': 0.65,
        'noise_base': 78.0,
    },
    'DOWNTOWN': {
        'lat': 33.7490,
        'lng': -84.3880,
        'base_mood': 0.05,
        'mood_variance': 0.25,
        'traffic_base': 0.75,
        'noise_base': 83.0,
    },
    'CAMPUS': {
        'lat': 33.7750,
        'lng': -84.3960,
        'base_mood': 0.45,
        'mood_variance': 0.35,
        'traffic_base': 0.30,
        'noise_base': 56.0,
    },
    'PARK_DISTRICT': {
        'lat': 33.7850,
        'lng': -84.3730,
        'base_mood': 0.65,
        'mood_variance': 0.20,
        'traffic_base': 0.15,
        'noise_base': 42.0,
    },
    'RESIDENTIAL_ZONE': {
        'lat': 33.7600,
        'lng': -84.3800,
        'base_mood': 0.25,
        'mood_variance': 0.30,
        'traffic_base': 0.40,
        'noise_base': 58.0,
    }
}

# Sentiment templates for social posts (Atlanta, Georgia)
POSITIVE_TEMPLATES = [
    "Beautiful weather in {area} today!",
    "Just had an amazing lunch in {area}",
    "Love the energy in {area} this morning",
    "Great community event in {area}!",
    "The new park in {area} is wonderful",
    "Friendly neighbors in {area} make my day",
    "Coffee shop in {area} has the best service",
    "Loving the vibe in {area} lately",
    "{area} is looking beautiful this season",
    "Perfect day for a walk in {area}",
    "Atlanta's {area} is amazing!",
    "Love the ATL vibes in {area}!",
    "Peachtree Street area {area} is great",
    "Georgia Tech area {area} is so vibrant",
    "Piedmont Park near {area} is beautiful",
]

NEGATIVE_TEMPLATES = [
    "Terrible traffic in {area} this morning",
    "Road construction in {area} is frustrating",
    "Noise levels in {area} are unbearable today",
    "Pothole on main street in {area} damaged my car",
    "Traffic light broken in {area} causing chaos",
    "Parking situation in {area} is terrible",
    "Too crowded in {area} lately",
    "{area} needs better infrastructure",
    "Accident blocking traffic in {area}",
    "Power outage in {area} again",
    "Atlanta traffic in {area} is the worst",
    "I-75/I-85 merge near {area} is a nightmare",
    "Peachtree traffic in {area} is insane",
    "The connector near {area} is always backed up",
]

NEUTRAL_TEMPLATES = [
    "Another day in {area}",
    "Heading to work from {area}",
    "Meeting friends in {area}",
    "Running errands in {area}",
    "Just passing through {area}",
    "Quick stop in {area}",
    "{area} looks the same as always",
    "Normal day in {area}",
    "Traffic is what it is in {area}",
    "Another morning commute in {area}",
]

# ============================================================================
# Helper Functions
# ============================================================================

def get_rush_hour_multiplier(hour: int) -> float:
    """
    Returns a traffic multiplier based on time of day.
    Rush hours: 7-9 AM and 5-7 PM have higher multipliers.
    """
    if 7 <= hour <= 9 or 17 <= hour <= 19:
        return 1.5  # 50% increase during rush hour
    elif 22 <= hour or hour <= 6:
        return 0.5  # 50% decrease at night
    else:
        return 1.0  # Normal traffic


def get_weekday_multiplier(weekday: int) -> float:
    """
    Returns a traffic multiplier based on day of week.
    0 = Monday, 6 = Sunday
    """
    if weekday >= 5:  # Weekend
        return 0.7  # 30% decrease on weekends
    else:
        return 1.0


def calculate_congestion(base: float, hour: int, weekday: int, variance: float = 0.15) -> float:
    """
    Calculates congestion level based on base traffic, time, and random variance.
    Returns a value between 0 and 1.
    """
    rush_mult = get_rush_hour_multiplier(hour)
    weekday_mult = get_weekday_multiplier(weekday)
    random_factor = random.uniform(-variance, variance)

    congestion = base * rush_mult * weekday_mult + random_factor
    return max(0.0, min(1.0, congestion))  # Clamp to [0, 1]


def calculate_noise(base: float, congestion: float, variance: float = 5.0) -> float:
    """
    Calculates noise level based on base noise and current congestion.
    Higher congestion = higher noise.
    Returns dB value.
    """
    congestion_bonus = congestion * 10  # Up to +10 dB for high congestion
    random_factor = random.uniform(-variance, variance)

    noise = base + congestion_bonus + random_factor
    return max(30.0, min(100.0, noise))  # Clamp to realistic range


def generate_social_post(area_id: str, sentiment: str) -> str:
    """
    Generates a synthetic social post for the given area and sentiment.
    """
    if sentiment == 'positive':
        template = random.choice(POSITIVE_TEMPLATES)
    elif sentiment == 'negative':
        template = random.choice(NEGATIVE_TEMPLATES)
    else:
        template = random.choice(NEUTRAL_TEMPLATES)

    return template.format(area=area_id.replace('_', ' ').title())


def calculate_mood_score(sentiment: str) -> float:
    """
    Returns a mood score based on sentiment.
    Positive: 0.5 to 1.0
    Negative: -1.0 to -0.5
    Neutral: -0.2 to 0.2
    """
    if sentiment == 'positive':
        return random.uniform(0.5, 1.0)
    elif sentiment == 'negative':
        return random.uniform(-1.0, -0.5)
    else:
        return random.uniform(-0.2, 0.2)


# ============================================================================
# Data Generation Functions
# ============================================================================

def generate_mood_data(days: int = 7, posts_per_day_per_area: int = 10) -> List[Dict]:
    """
    Generates synthetic social posts and aggregated mood data.

    Returns:
        List of mood_areas records with aggregated sentiment
    """
    mood_records = []
    base_date = datetime.now() - timedelta(days=days)

    for day in range(days):
        current_date = base_date + timedelta(days=day)

        for area_id, area_data in CITY_AREAS.items():
            # Generate multiple posts for this area on this day
            post_sentiments = []

            for _ in range(posts_per_day_per_area):
                # Determine sentiment based on area's base mood
                rand = random.random()
                if rand < (area_data['base_mood'] + 1) / 2:  # Convert [-1,1] to [0,1] probability
                    sentiment = random.choice(['positive', 'positive', 'neutral'])
                else:
                    sentiment = random.choice(['negative', 'negative', 'neutral'])

                mood_score = calculate_mood_score(sentiment)
                post_sentiments.append(mood_score)

            # Aggregate mood for this area on this day
            avg_mood = sum(post_sentiments) / len(post_sentiments)

            # Add some time variation throughout the day
            hour = random.randint(0, 23)
            timestamp = current_date.replace(hour=hour, minute=random.randint(0, 59))

            mood_records.append({
                'area_id': area_id,
                'lat': area_data['lat'],
                'lng': area_data['lng'],
                'mood_score': round(avg_mood, 3),
                'post_count': posts_per_day_per_area,
                'created_at': timestamp.isoformat()
            })

    return mood_records


def generate_traffic_data(days: int = 7, samples_per_day: int = 24) -> List[Dict]:
    """
    Generates time-series traffic data with rush hour patterns.

    Returns:
        List of traffic_segments records
    """
    traffic_records = []
    base_date = datetime.now() - timedelta(days=days)

    # Generate segments for each area
    segment_definitions = []
    for area_id, area_data in CITY_AREAS.items():
        # Create 5 segments per area (main roads)
        for i in range(5):
            segment_definitions.append({
                'segment_id': f'{area_id}_SEG_{i+1}',
                'base_lat': area_data['lat'],
                'base_lng': area_data['lng'],
                'base_congestion': area_data['traffic_base'],
                'offset': i * 0.001  # Small offset for each segment
            })

    for day in range(days):
        for hour in range(0, 24, 24 // samples_per_day):
            current_time = base_date + timedelta(days=day, hours=hour)
            weekday = current_time.weekday()

            for segment in segment_definitions:
                congestion = calculate_congestion(
                    segment['base_congestion'],
                    hour,
                    weekday,
                    variance=0.15
                )

                traffic_records.append({
                    'segment_id': segment['segment_id'],
                    'lat': segment['base_lat'] + segment['offset'],
                    'lng': segment['base_lng'] + segment['offset'],
                    'congestion': round(congestion, 3),
                    'ts': current_time.isoformat()
                })

    return traffic_records


def generate_noise_data(days: int = 7, samples_per_day: int = 24) -> List[Dict]:
    """
    Generates time-series noise data correlated with traffic.

    Returns:
        List of noise_segments records
    """
    noise_records = []
    base_date = datetime.now() - timedelta(days=days)

    # Generate segments for each area
    segment_definitions = []
    for area_id, area_data in CITY_AREAS.items():
        for i in range(5):
            segment_definitions.append({
                'segment_id': f'{area_id}_SEG_{i+1}',
                'base_lat': area_data['lat'],
                'base_lng': area_data['lng'],
                'base_noise': area_data['noise_base'],
                'base_congestion': area_data['traffic_base'],
                'offset': i * 0.001
            })

    for day in range(days):
        for hour in range(0, 24, 24 // samples_per_day):
            current_time = base_date + timedelta(days=day, hours=hour)
            weekday = current_time.weekday()

            for segment in segment_definitions:
                # Calculate congestion for this time
                congestion = calculate_congestion(
                    segment['base_congestion'],
                    hour,
                    weekday,
                    variance=0.15
                )

                # Calculate noise based on congestion
                noise_db = calculate_noise(
                    segment['base_noise'],
                    congestion,
                    variance=5.0
                )

                noise_records.append({
                    'segment_id': segment['segment_id'],
                    'lat': segment['base_lat'] + segment['offset'],
                    'lng': segment['base_lng'] + segment['offset'],
                    'noise_db': round(noise_db, 1),
                    'ts': current_time.isoformat()
                })

    return noise_records


def generate_sample_issues(count: int = 20) -> List[Dict]:
    """
    Generates sample issues for testing.

    Returns:
        List of issues records
    """
    issues = []
    issue_types = ['accident', 'pothole', 'traffic_light', 'other']

    for _ in range(count):
        # Select random area
        area_id = random.choice(list(CITY_AREAS.keys()))
        area_data = CITY_AREAS[area_id]

        # Random location near area center
        lat = area_data['lat'] + random.uniform(-0.01, 0.01)
        lng = area_data['lng'] + random.uniform(-0.01, 0.01)

        # Random issue type
        issue_type = random.choice(issue_types)

        # Generate realistic description
        descriptions = {
            'accident': f"Multi-vehicle collision on main road in {area_id}",
            'pothole': f"Large pothole causing damage to vehicles in {area_id}",
            'traffic_light': f"Malfunctioning traffic signal at intersection in {area_id}",
            'other': f"Broken sidewalk hazard in {area_id}",
        }

        # Calculate severity and urgency
        severity = random.uniform(0.3, 1.0) if issue_type == 'accident' else random.uniform(0.2, 0.8)
        urgency = random.uniform(0.5, 1.0) if issue_type == 'accident' else random.uniform(0.2, 0.7)

        # Determine priority
        if severity > 0.7 or urgency > 0.7:
            priority = 'critical' if severity > 0.85 else 'high'
        elif severity > 0.4 or urgency > 0.4:
            priority = 'medium'
        else:
            priority = 'low'

        # Action type
        action_type = 'emergency_summary' if issue_type == 'accident' else 'work_order'

        issues.append({
            'lat': round(lat, 6),
            'lng': round(lng, 6),
            'issue_type': issue_type,
            'description': descriptions[issue_type],
            'image_url': f'https://placeholder.com/issue_{fake.uuid4()}.jpg',
            'severity': round(severity, 3),
            'urgency': round(urgency, 3),
            'priority': priority,
            'action_type': action_type,
            'status': random.choice(['open', 'open', 'open', 'in_progress']),
            'created_at': (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat()
        })

    return issues


# ============================================================================
# Database Insertion Functions
# ============================================================================

def insert_data_to_supabase():
    """
    Inserts generated data into Supabase.
    """
    try:
        from supabase import create_client, Client
    except ImportError:
        print("ERROR: supabase library not installed. Run: pip install supabase")
        return

    # Get Supabase credentials
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')

    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return

    # Create Supabase client
    supabase: Client = create_client(url, key)

    print("Generating synthetic data...")

    # Generate data
    print("  - Generating mood data...")
    mood_data = generate_mood_data(days=7, posts_per_day_per_area=10)

    print("  - Generating traffic data...")
    traffic_data = generate_traffic_data(days=7, samples_per_day=24)

    print("  - Generating noise data...")
    noise_data = generate_noise_data(days=7, samples_per_day=24)

    print("  - Generating sample issues...")
    issues_data = generate_sample_issues(count=20)

    print(f"\nInserting data into Supabase...")

    # Insert mood data
    print(f"  - Inserting {len(mood_data)} mood records...")
    try:
        supabase.table('mood_areas').insert(mood_data).execute()
        print(f"    ✓ Mood data inserted successfully")
    except Exception as e:
        print(f"    ✗ Error inserting mood data: {e}")

    # Insert traffic data in batches (PostgreSQL has row limits)
    batch_size = 500
    print(f"  - Inserting {len(traffic_data)} traffic records in batches...")
    for i in range(0, len(traffic_data), batch_size):
        batch = traffic_data[i:i + batch_size]
        try:
            supabase.table('traffic_segments').insert(batch).execute()
            print(f"    ✓ Batch {i // batch_size + 1} inserted")
        except Exception as e:
            print(f"    ✗ Error inserting traffic batch: {e}")

    # Insert noise data in batches
    print(f"  - Inserting {len(noise_data)} noise records in batches...")
    for i in range(0, len(noise_data), batch_size):
        batch = noise_data[i:i + batch_size]
        try:
            supabase.table('noise_segments').insert(batch).execute()
            print(f"    ✓ Batch {i // batch_size + 1} inserted")
        except Exception as e:
            print(f"    ✗ Error inserting noise batch: {e}")

    # Insert sample issues
    print(f"  - Inserting {len(issues_data)} sample issues...")
    try:
        supabase.table('issues').insert(issues_data).execute()
        print(f"    ✓ Issues inserted successfully")
    except Exception as e:
        print(f"    ✗ Error inserting issues: {e}")

    print("\n✓ Data generation complete!")
    print(f"\nSummary:")
    print(f"  - Mood records: {len(mood_data)}")
    print(f"  - Traffic records: {len(traffic_data)}")
    print(f"  - Noise records: {len(noise_data)}")
    print(f"  - Sample issues: {len(issues_data)}")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("NeuraCity Synthetic Data Generator")
    print("=" * 60)
    insert_data_to_supabase()
