#!/usr/bin/env python3
"""
NeuraCity Synthetic Data Generator

Generates realistic synthetic data for:
- Social media posts for mood analysis
- Time-series traffic data with rush hour patterns
- Correlated noise data
- Sample issues with realistic coordinates

Usage:
    python generate_data.py [--days=7] [--posts-per-day=100] [--traffic-intervals=96]
"""

import os
import sys
import random
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math

try:
    from faker import Faker
    from supabase import create_client, Client
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)


# =====================================================
# CONFIGURATION
# =====================================================

# City areas with coordinates and characteristics
CITY_AREAS = {
    'DOWNTOWN': {
        'lat': 40.7128,
        'lng': -74.0060,
        'mood_bias': -0.1,  # Slightly negative (business stress)
        'base_traffic': 0.6,
        'base_noise': 70.0
    },
    'MIDTOWN': {
        'lat': 40.7589,
        'lng': -73.9851,
        'mood_bias': 0.0,  # Neutral
        'base_traffic': 0.7,
        'base_noise': 72.0
    },
    'CAMPUS': {
        'lat': 40.7295,
        'lng': -73.9965,
        'mood_bias': 0.2,  # Positive (students, learning)
        'base_traffic': 0.3,
        'base_noise': 50.0
    },
    'PARK_DISTRICT': {
        'lat': 40.7812,
        'lng': -73.9665,
        'mood_bias': 0.4,  # Very positive (recreation)
        'base_traffic': 0.3,
        'base_noise': 43.0
    },
    'RESIDENTIAL': {
        'lat': 40.7480,
        'lng': -73.9862,
        'mood_bias': 0.15,  # Slightly positive (home)
        'base_traffic': 0.2,
        'base_noise': 48.0
    },
    'INDUSTRIAL': {
        'lat': 40.7015,
        'lng': -74.0150,
        'mood_bias': -0.2,  # Negative (work, pollution)
        'base_traffic': 0.5,
        'base_noise': 75.0
    },
    'WATERFRONT': {
        'lat': 40.7061,
        'lng': -74.0087,
        'mood_bias': 0.25,  # Positive (tourism, views)
        'base_traffic': 0.4,
        'base_noise': 60.0
    },
    'ARTS_DISTRICT': {
        'lat': 40.7250,
        'lng': -73.9967,
        'mood_bias': 0.2,  # Positive (culture)
        'base_traffic': 0.4,
        'base_noise': 65.0
    }
}

# Road segments for traffic and noise
ROAD_SEGMENTS = [
    # Main Street
    {'id': 'MAIN_ST_01', 'lat': 40.7128, 'lng': -74.0060, 'type': 'arterial'},
    {'id': 'MAIN_ST_02', 'lat': 40.7138, 'lng': -74.0050, 'type': 'arterial'},
    {'id': 'MAIN_ST_03', 'lat': 40.7148, 'lng': -74.0040, 'type': 'arterial'},
    {'id': 'MAIN_ST_04', 'lat': 40.7158, 'lng': -74.0030, 'type': 'arterial'},
    # Broadway
    {'id': 'BROADWAY_01', 'lat': 40.7589, 'lng': -73.9851, 'type': 'arterial'},
    {'id': 'BROADWAY_02', 'lat': 40.7599, 'lng': -73.9841, 'type': 'arterial'},
    {'id': 'BROADWAY_03', 'lat': 40.7609, 'lng': -73.9831, 'type': 'arterial'},
    {'id': 'BROADWAY_04', 'lat': 40.7619, 'lng': -73.9821, 'type': 'arterial'},
    # Campus Drive
    {'id': 'CAMPUS_DR_01', 'lat': 40.7295, 'lng': -73.9965, 'type': 'local'},
    {'id': 'CAMPUS_DR_02', 'lat': 40.7305, 'lng': -73.9955, 'type': 'local'},
    {'id': 'CAMPUS_DR_03', 'lat': 40.7315, 'lng': -73.9945, 'type': 'local'},
    # Park Avenue
    {'id': 'PARK_AVE_01', 'lat': 40.7812, 'lng': -73.9665, 'type': 'local'},
    {'id': 'PARK_AVE_02', 'lat': 40.7822, 'lng': -73.9655, 'type': 'local'},
    {'id': 'PARK_AVE_03', 'lat': 40.7832, 'lng': -73.9645, 'type': 'local'},
    # Residential streets
    {'id': 'RESI_ST_01', 'lat': 40.7480, 'lng': -73.9862, 'type': 'residential'},
    {'id': 'RESI_ST_02', 'lat': 40.7490, 'lng': -73.9852, 'type': 'residential'},
    {'id': 'RESI_ST_03', 'lat': 40.7500, 'lng': -73.9842, 'type': 'residential'},
    # Highway
    {'id': 'HIGHWAY_01', 'lat': 40.7015, 'lng': -74.0150, 'type': 'highway'},
    {'id': 'HIGHWAY_02', 'lat': 40.7025, 'lng': -74.0140, 'type': 'highway'},
    {'id': 'HIGHWAY_03', 'lat': 40.7035, 'lng': -74.0130, 'type': 'highway'},
    # Waterfront
    {'id': 'WATER_01', 'lat': 40.7061, 'lng': -74.0087, 'type': 'local'},
    {'id': 'WATER_02', 'lat': 40.7071, 'lng': -74.0077, 'type': 'local'},
]

# Post templates for different moods
POSITIVE_TEMPLATES = [
    "Beautiful weather today! Perfect for a walk.",
    "Love this neighborhood! So vibrant.",
    "Great coffee shop opened nearby!",
    "Just had an amazing experience at the local park.",
    "This city keeps getting better!",
    "Finally some sunshine! Feeling great.",
    "Weekend vibes are immaculate here.",
    "Can't believe how friendly everyone is today.",
    "This place has the best energy!",
    "Loving the new improvements around here."
]

NEGATIVE_TEMPLATES = [
    "Traffic is absolutely terrible this morning.",
    "So much construction noise everywhere.",
    "Really frustrated with the road conditions.",
    "Another pothole damaged my tire today.",
    "The traffic lights are not synced at all.",
    "Rush hour is getting worse every day.",
    "Need better infrastructure around here.",
    "So tired of the constant honking.",
    "This area needs serious attention.",
    "Infrastructure is falling apart."
]

NEUTRAL_TEMPLATES = [
    "Just another day in the city.",
    "Heading to work as usual.",
    "Traffic is about average today.",
    "Weather is okay, nothing special.",
    "Regular Wednesday afternoon.",
    "Not much happening around here.",
    "Same route, same traffic.",
    "Another typical commute.",
    "Business as usual downtown.",
    "Standard day at the office."
]


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_rush_hour_multiplier(hour: int) -> float:
    """Calculate traffic multiplier based on time of day"""
    if 7 <= hour <= 9:  # Morning rush
        return 1.5 + 0.3 * math.sin((hour - 7) * math.pi / 2)
    elif 17 <= hour <= 19:  # Evening rush
        return 1.6 + 0.4 * math.sin((hour - 17) * math.pi / 2)
    elif 22 <= hour or hour <= 5:  # Late night
        return 0.3
    else:  # Normal hours
        return 1.0


def get_road_type_traffic_base(road_type: str) -> float:
    """Get base traffic congestion for road type"""
    return {
        'highway': 0.6,
        'arterial': 0.5,
        'local': 0.3,
        'residential': 0.15
    }.get(road_type, 0.4)


def get_road_type_noise_base(road_type: str) -> float:
    """Get base noise level for road type"""
    return {
        'highway': 80.0,
        'arterial': 70.0,
        'local': 55.0,
        'residential': 47.0
    }.get(road_type, 60.0)


def calculate_mood_score(sentiment_type: str, area_bias: float) -> float:
    """Calculate mood score with area bias"""
    base_score = {
        'positive': random.uniform(0.5, 0.9),
        'negative': random.uniform(-0.9, -0.5),
        'neutral': random.uniform(-0.2, 0.2)
    }.get(sentiment_type, 0.0)

    # Apply area bias
    final_score = base_score + area_bias * 0.3
    # Clamp to [-1, 1]
    return max(-1.0, min(1.0, final_score))


def generate_post_text(sentiment_type: str, faker: Faker) -> str:
    """Generate realistic social media post text"""
    templates = {
        'positive': POSITIVE_TEMPLATES,
        'negative': NEGATIVE_TEMPLATES,
        'neutral': NEUTRAL_TEMPLATES
    }

    template = random.choice(templates.get(sentiment_type, NEUTRAL_TEMPLATES))

    # Sometimes add emoji
    if random.random() < 0.3:
        emoji_map = {
            'positive': ['😊', '❤️', '✨', '🌟', '👍'],
            'negative': ['😤', '😓', '😡', '😔', '😩'],
            'neutral': ['🤔', '😐', '📍', '🚗', '☁️']
        }
        emoji = random.choice(emoji_map.get(sentiment_type, emoji_map['neutral']))
        template = f"{template} {emoji}"

    return template


# =====================================================
# DATA GENERATORS
# =====================================================

class SyntheticDataGenerator:
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize generator with Supabase connection"""
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.faker = Faker()
        print("✓ Connected to Supabase")

    def generate_mood_posts(self, days: int, posts_per_day: int) -> int:
        """Generate synthetic social media posts for mood analysis"""
        print(f"\n📝 Generating mood posts for {days} days ({posts_per_day} posts/day)...")

        total_posts = 0
        batch_size = 100
        batch = []

        for day in range(days):
            date_offset = timedelta(days=days - day - 1)

            for _ in range(posts_per_day):
                # Random time during the day
                hour = random.randint(6, 23)
                minute = random.randint(0, 59)
                timestamp = datetime.now() - date_offset + timedelta(hours=hour, minutes=minute)

                # Random area
                area_id = random.choice(list(CITY_AREAS.keys()))
                area_data = CITY_AREAS[area_id]

                # Sentiment type based on area bias and randomness
                rand = random.random()
                if rand < 0.35:
                    sentiment = 'positive'
                elif rand < 0.65:
                    sentiment = 'neutral'
                else:
                    sentiment = 'negative'

                # Adjust based on time (morning rush = more negative)
                if 7 <= hour <= 9 or 17 <= hour <= 19:
                    if random.random() < 0.3:
                        sentiment = 'negative'

                post_text = generate_post_text(sentiment, self.faker)
                mood_score = calculate_mood_score(sentiment, area_data['mood_bias'])

                # Store in batch (posts aren't directly stored, but we aggregate mood)
                batch.append({
                    'area_id': area_id,
                    'lat': area_data['lat'] + random.uniform(-0.01, 0.01),
                    'lng': area_data['lng'] + random.uniform(-0.01, 0.01),
                    'mood_score': mood_score,
                    'post_count': 1,
                    'created_at': timestamp.isoformat()
                })

                total_posts += 1

                # Insert batch
                if len(batch) >= batch_size:
                    try:
                        self.supabase.table('mood_areas').insert(batch).execute()
                        print(f"  ✓ Inserted {len(batch)} mood data points (Total: {total_posts})")
                        batch = []
                    except Exception as e:
                        print(f"  ✗ Error inserting batch: {e}")

        # Insert remaining
        if batch:
            try:
                self.supabase.table('mood_areas').insert(batch).execute()
                print(f"  ✓ Inserted {len(batch)} mood data points (Total: {total_posts})")
            except Exception as e:
                print(f"  ✗ Error inserting final batch: {e}")

        print(f"✓ Generated {total_posts} mood data points")
        return total_posts

    def generate_traffic_data(self, days: int, intervals_per_day: int = 96) -> int:
        """Generate time-series traffic data with rush hour patterns"""
        print(f"\n🚗 Generating traffic data for {days} days ({intervals_per_day} intervals/day)...")

        total_records = 0
        batch_size = 100
        batch = []
        minutes_per_interval = 24 * 60 // intervals_per_day

        for day in range(days):
            date_offset = timedelta(days=days - day - 1)

            for interval in range(intervals_per_day):
                timestamp = datetime.now() - date_offset + timedelta(minutes=interval * minutes_per_interval)
                hour = timestamp.hour
                rush_multiplier = get_rush_hour_multiplier(hour)

                for segment in ROAD_SEGMENTS:
                    base_traffic = get_road_type_traffic_base(segment['type'])

                    # Apply rush hour multiplier
                    congestion = base_traffic * rush_multiplier

                    # Add random variance
                    congestion += random.uniform(-0.1, 0.1)

                    # Random traffic events (accidents, construction)
                    if random.random() < 0.02:  # 2% chance of incident
                        congestion += random.uniform(0.2, 0.4)

                    # Clamp to [0, 1]
                    congestion = max(0.0, min(1.0, congestion))

                    batch.append({
                        'segment_id': segment['id'],
                        'lat': segment['lat'],
                        'lng': segment['lng'],
                        'congestion': round(congestion, 3),
                        'ts': timestamp.isoformat()
                    })

                    total_records += 1

                    # Insert batch
                    if len(batch) >= batch_size:
                        try:
                            self.supabase.table('traffic_segments').insert(batch).execute()
                            print(f"  ✓ Inserted {len(batch)} traffic records (Total: {total_records})")
                            batch = []
                        except Exception as e:
                            print(f"  ✗ Error inserting batch: {e}")

        # Insert remaining
        if batch:
            try:
                self.supabase.table('traffic_segments').insert(batch).execute()
                print(f"  ✓ Inserted {len(batch)} traffic records (Total: {total_records})")
            except Exception as e:
                print(f"  ✗ Error inserting final batch: {e}")

        print(f"✓ Generated {total_records} traffic records")
        return total_records

    def generate_noise_data(self, days: int, intervals_per_day: int = 96) -> int:
        """Generate correlated noise data"""
        print(f"\n🔊 Generating noise data for {days} days ({intervals_per_day} intervals/day)...")

        total_records = 0
        batch_size = 100
        batch = []
        minutes_per_interval = 24 * 60 // intervals_per_day

        for day in range(days):
            date_offset = timedelta(days=days - day - 1)

            for interval in range(intervals_per_day):
                timestamp = datetime.now() - date_offset + timedelta(minutes=interval * minutes_per_interval)
                hour = timestamp.hour

                for segment in ROAD_SEGMENTS:
                    base_noise = get_road_type_noise_base(segment['type'])

                    # Noise correlates with time of day
                    if 22 <= hour or hour <= 6:  # Night time
                        noise_multiplier = 0.7
                    elif 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hour
                        noise_multiplier = 1.2
                    else:
                        noise_multiplier = 1.0

                    noise_db = base_noise * noise_multiplier

                    # Add random variance
                    noise_db += random.uniform(-3, 3)

                    # Clamp to reasonable range
                    noise_db = max(35.0, min(95.0, noise_db))

                    batch.append({
                        'segment_id': segment['id'],
                        'lat': segment['lat'],
                        'lng': segment['lng'],
                        'noise_db': round(noise_db, 1),
                        'ts': timestamp.isoformat()
                    })

                    total_records += 1

                    # Insert batch
                    if len(batch) >= batch_size:
                        try:
                            self.supabase.table('noise_segments').insert(batch).execute()
                            print(f"  ✓ Inserted {len(batch)} noise records (Total: {total_records})")
                            batch = []
                        except Exception as e:
                            print(f"  ✗ Error inserting batch: {e}")

        # Insert remaining
        if batch:
            try:
                self.supabase.table('noise_segments').insert(batch).execute()
                print(f"  ✓ Inserted {len(batch)} noise records (Total: {total_records})")
            except Exception as e:
                print(f"  ✗ Error inserting final batch: {e}")

        print(f"✓ Generated {total_records} noise records")
        return total_records

    def generate_sample_issues(self, count: int = 50) -> int:
        """Generate sample infrastructure issues"""
        print(f"\n🚧 Generating {count} sample issues...")

        issue_types = ['pothole', 'traffic_light', 'accident', 'other']
        statuses = ['open', 'in_progress', 'resolved']

        batch = []

        for i in range(count):
            # Random location near a road segment
            segment = random.choice(ROAD_SEGMENTS)
            lat = segment['lat'] + random.uniform(-0.005, 0.005)
            lng = segment['lng'] + random.uniform(-0.005, 0.005)

            issue_type = random.choice(issue_types)

            # Generate realistic description
            descriptions = {
                'pothole': [
                    'Large pothole causing vehicle damage',
                    'Deep hole in road surface',
                    'Pothole near intersection',
                    'Multiple potholes in this area'
                ],
                'traffic_light': [
                    'Traffic signal not working',
                    'Light stuck on red',
                    'Pedestrian crossing signal broken',
                    'Traffic light timing issue'
                ],
                'accident': [
                    'Multi-vehicle collision',
                    'Minor fender bender',
                    'Vehicle blocking lane',
                    'Traffic accident requiring assistance'
                ],
                'other': [
                    'Fallen tree blocking road',
                    'Broken street sign',
                    'Graffiti on public property',
                    'Street flooding after rain'
                ]
            }

            description = random.choice(descriptions[issue_type])

            # Calculate severity and urgency
            if issue_type == 'accident':
                severity = random.uniform(0.7, 1.0)
                urgency = random.uniform(0.8, 1.0)
                priority = 'critical'
                action_type = 'emergency_summary'
            elif issue_type == 'traffic_light':
                severity = random.uniform(0.6, 0.9)
                urgency = random.uniform(0.7, 0.95)
                priority = random.choice(['high', 'critical'])
                action_type = 'work_order'
            elif issue_type == 'pothole':
                severity = random.uniform(0.3, 0.8)
                urgency = random.uniform(0.4, 0.8)
                priority = random.choice(['low', 'medium', 'high'])
                action_type = 'work_order'
            else:
                severity = random.uniform(0.2, 0.7)
                urgency = random.uniform(0.3, 0.7)
                priority = random.choice(['low', 'medium'])
                action_type = random.choice(['work_order', 'none'])

            status = random.choices(
                statuses,
                weights=[0.6, 0.3, 0.1],  # Most are open
                k=1
            )[0]

            created_at = datetime.now() - timedelta(
                hours=random.randint(1, 72)
            )

            batch.append({
                'lat': round(lat, 6),
                'lng': round(lng, 6),
                'issue_type': issue_type,
                'description': description,
                'image_url': f'https://example.com/images/{issue_type}_{i+1:03d}.jpg',
                'severity': round(severity, 2),
                'urgency': round(urgency, 2),
                'priority': priority,
                'action_type': action_type,
                'status': status,
                'created_at': created_at.isoformat()
            })

        try:
            result = self.supabase.table('issues').insert(batch).execute()
            print(f"✓ Generated {len(batch)} sample issues")
            return len(batch)
        except Exception as e:
            print(f"✗ Error inserting issues: {e}")
            return 0


# =====================================================
# MAIN
# =====================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generate synthetic data for NeuraCity database'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days of historical data to generate (default: 7)'
    )
    parser.add_argument(
        '--posts-per-day',
        type=int,
        default=100,
        help='Number of mood posts per day (default: 100)'
    )
    parser.add_argument(
        '--traffic-intervals',
        type=int,
        default=96,
        help='Traffic data intervals per day (default: 96, every 15 min)'
    )
    parser.add_argument(
        '--issues',
        type=int,
        default=50,
        help='Number of sample issues to generate (default: 50)'
    )
    parser.add_argument(
        '--skip-mood',
        action='store_true',
        help='Skip mood data generation'
    )
    parser.add_argument(
        '--skip-traffic',
        action='store_true',
        help='Skip traffic data generation'
    )
    parser.add_argument(
        '--skip-noise',
        action='store_true',
        help='Skip noise data generation'
    )
    parser.add_argument(
        '--skip-issues',
        action='store_true',
        help='Skip issues generation'
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        print("Copy .env.example to .env and fill in your Supabase credentials")
        sys.exit(1)

    print("=" * 60)
    print("NeuraCity Synthetic Data Generator")
    print("=" * 60)

    try:
        generator = SyntheticDataGenerator(supabase_url, supabase_key)

        stats = {
            'mood': 0,
            'traffic': 0,
            'noise': 0,
            'issues': 0
        }

        if not args.skip_mood:
            stats['mood'] = generator.generate_mood_posts(
                args.days,
                args.posts_per_day
            )

        if not args.skip_traffic:
            stats['traffic'] = generator.generate_traffic_data(
                args.days,
                args.traffic_intervals
            )

        if not args.skip_noise:
            stats['noise'] = generator.generate_noise_data(
                args.days,
                args.traffic_intervals
            )

        if not args.skip_issues:
            stats['issues'] = generator.generate_sample_issues(args.issues)

        print("\n" + "=" * 60)
        print("✓ Data generation complete!")
        print("=" * 60)
        print(f"Mood data points:    {stats['mood']:,}")
        print(f"Traffic records:     {stats['traffic']:,}")
        print(f"Noise records:       {stats['noise']:,}")
        print(f"Sample issues:       {stats['issues']:,}")
        print(f"Total records:       {sum(stats.values()):,}")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
