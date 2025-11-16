#!/usr/bin/env python3
"""
NeuraCity Gamification and Risk Data Generator

Generates synthetic data for:
- Users with varying point levels and ranks
- Points transactions linked to issues
- Accident history with spatial distribution
- Block risk scores across city areas

Usage:
    python generate_gamification_data.py [--users=100] [--days=30] [--blocks=200]
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

# City areas (matching existing schema - New York City)
CITY_AREAS = {
    'DOWNTOWN': {'lat': 40.7128, 'lng': -74.0060, 'risk_bias': 0.6},
    'MIDTOWN': {'lat': 40.7589, 'lng': -73.9851, 'risk_bias': 0.7},
    'CAMPUS': {'lat': 40.7295, 'lng': -73.9965, 'risk_bias': 0.3},
    'PARK_DISTRICT': {'lat': 40.7812, 'lng': -73.9665, 'risk_bias': 0.2},
    'RESIDENTIAL': {'lat': 40.7480, 'lng': -73.9862, 'risk_bias': 0.4},
    'INDUSTRIAL': {'lat': 40.7015, 'lng': -74.0150, 'risk_bias': 0.8},
    'WATERFRONT': {'lat': 40.7061, 'lng': -74.0087, 'risk_bias': 0.5},
    'ARTS_DISTRICT': {'lat': 40.7250, 'lng': -73.9967, 'risk_bias': 0.4}
}

# Point awards for different transaction types
POINT_AWARDS = {
    'issue_report': (10, 25),  # (min, max)
    'issue_verified': (15, 30),
    'issue_resolved': (30, 50),
    'community_vote': (2, 5),
    'helpful_description': (5, 15),
    'photo_quality': (10, 20),
    'repeat_reporter': (25, 40),
    'first_in_area': (50, 75),
    'streak_bonus': (100, 200)
}

# Rank thresholds
RANK_THRESHOLDS = {
    'bronze': 0,
    'silver': 500,
    'gold': 2000,
    'platinum': 5000,
    'diamond': 10000
}

# Time of day ranges
TIME_RANGES = {
    'morning': (6, 12),
    'afternoon': (12, 18),
    'evening': (18, 22),
    'night': (22, 6)
}

WEATHER_CONDITIONS = [
    'clear', 'cloudy', 'rainy', 'foggy', 'snowy', 'windy', 'stormy'
]


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_time_of_day(hour: int) -> str:
    """Determine time of day from hour"""
    if 6 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 18:
        return 'afternoon'
    elif 18 <= hour < 22:
        return 'evening'
    else:
        return 'night'


def generate_random_coord_near(base_lat: float, base_lng: float, max_offset: float = 0.01) -> Tuple[float, float]:
    """Generate random coordinates near a base point"""
    lat = base_lat + random.uniform(-max_offset, max_offset)
    lng = base_lng + random.uniform(-max_offset, max_offset)
    return round(lat, 6), round(lng, 6)


def get_rank_from_points(points: int) -> str:
    """Calculate rank from total points"""
    if points >= RANK_THRESHOLDS['diamond']:
        return 'diamond'
    elif points >= RANK_THRESHOLDS['platinum']:
        return 'platinum'
    elif points >= RANK_THRESHOLDS['gold']:
        return 'gold'
    elif points >= RANK_THRESHOLDS['silver']:
        return 'silver'
    else:
        return 'bronze'


# =====================================================
# DATA GENERATORS
# =====================================================

def generate_users(fake: Faker, count: int) -> List[Dict]:
    """Generate synthetic users with varying point levels"""
    print(f"\n📊 Generating {count} users...")

    users = []
    for i in range(count):
        # Skew towards lower point totals (more bronze/silver than diamond)
        points_distribution = random.choices(
            [
                random.randint(0, 499),      # bronze
                random.randint(500, 1999),   # silver
                random.randint(2000, 4999),  # gold
                random.randint(5000, 9999),  # platinum
                random.randint(10000, 25000) # diamond
            ],
            weights=[50, 30, 12, 6, 2]
        )[0]

        total_points = points_distribution
        rank = get_rank_from_points(total_points)

        user = {
            'username': fake.unique.user_name(),
            'email': fake.unique.email(),
            'total_points': total_points,
            'rank': rank,
            'bio': fake.sentence() if random.random() > 0.5 else None,
            'created_at': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
        }
        users.append(user)

        if (i + 1) % 20 == 0:
            print(f"   Generated {i + 1}/{count} users...")

    return users


def generate_points_transactions(
    user_ids: List[str],
    issue_ids: List[str],
    days: int
) -> List[Dict]:
    """Generate points transactions for users"""
    print(f"\n💎 Generating points transactions for {days} days...")

    transactions = []
    transaction_types = list(POINT_AWARDS.keys())

    for user_id in user_ids:
        # Each user gets random number of transactions
        num_transactions = random.randint(1, min(50, days * 2))

        for _ in range(num_transactions):
            trans_type = random.choice(transaction_types)
            points_range = POINT_AWARDS[trans_type]
            points = random.randint(points_range[0], points_range[1])

            # 70% of transactions link to issues
            issue_id = random.choice(issue_ids) if issue_ids and random.random() > 0.3 else None

            transaction = {
                'user_id': user_id,
                'issue_id': issue_id,
                'points_earned': points,
                'transaction_type': trans_type,
                'description': f"Earned {points} points for {trans_type.replace('_', ' ')}",
                'created_at': (datetime.now() - timedelta(days=random.randint(0, days))).isoformat()
            }
            transactions.append(transaction)

    print(f"   Generated {len(transactions)} transactions")
    return transactions


def generate_accident_history(
    issue_ids: List[str],
    days: int
) -> List[Dict]:
    """Generate accident history records with spatial distribution"""
    print(f"\n🚨 Generating accident history for {days} days...")

    accidents = []
    areas = list(CITY_AREAS.keys())

    # Accidents concentrated in high-traffic areas
    high_risk_areas = ['DOWNTOWN', 'MIDTOWN', 'INDUSTRIAL']
    area_weights = [3 if area in high_risk_areas else 1 for area in areas]

    num_accidents = min(len(issue_ids), days * random.randint(2, 8))

    for i in range(num_accidents):
        area_name = random.choices(areas, weights=area_weights)[0]
        area_info = CITY_AREAS[area_name]

        lat, lng = generate_random_coord_near(area_info['lat'], area_info['lng'], 0.015)

        # Generate timestamp
        occurred_at = datetime.now() - timedelta(
            days=random.randint(0, days),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        time_of_day = get_time_of_day(occurred_at.hour)

        # Higher severity during night and bad weather
        base_severity = random.uniform(0.4, 0.95)
        if time_of_day == 'night':
            base_severity = min(1.0, base_severity + 0.1)

        weather = random.choice(WEATHER_CONDITIONS)
        if weather in ['rainy', 'foggy', 'snowy', 'stormy']:
            base_severity = min(1.0, base_severity + 0.15)

        accident = {
            'issue_id': random.choice(issue_ids) if issue_ids else None,
            'lat': lat,
            'lng': lng,
            'severity': round(base_severity, 3),
            'urgency': round(random.uniform(0.6, 1.0), 3),
            'area_name': area_name,
            'description': f"Accident in {area_name} - {weather} conditions",
            'weather_conditions': weather,
            'time_of_day': time_of_day,
            'occurred_at': occurred_at.isoformat()
        }
        accidents.append(accident)

        if (i + 1) % 50 == 0:
            print(f"   Generated {i + 1}/{num_accidents} accidents...")

    return accidents


def generate_block_risk_scores(num_blocks: int) -> List[Dict]:
    """Generate risk scores for city blocks"""
    print(f"\n🏙️  Generating risk scores for {num_blocks} blocks...")

    blocks = []
    areas = list(CITY_AREAS.keys())

    for i in range(num_blocks):
        area_name = random.choice(areas)
        area_info = CITY_AREAS[area_name]

        lat, lng = generate_random_coord_near(area_info['lat'], area_info['lng'], 0.02)

        # Base risk on area characteristics
        risk_bias = area_info['risk_bias']

        # Generate individual risk components
        crime_score = max(0, min(1, random.gauss(risk_bias, 0.15)))
        blight_score = max(0, min(1, random.gauss(risk_bias * 0.8, 0.2)))
        traffic_score = max(0, min(1, random.gauss(risk_bias * 0.9, 0.15)))
        noise_score = max(0, min(1, random.gauss(risk_bias * 0.85, 0.18)))
        air_quality_score = max(0, min(1, random.gauss(risk_bias * 0.7, 0.2)))
        heat_score = max(0, min(1, random.gauss(risk_bias * 0.6, 0.25)))
        wait_time_score = max(0, min(1, random.gauss(risk_bias * 0.75, 0.2)))

        # Calculate weighted overall risk
        overall_risk = (
            crime_score * 0.25 +
            traffic_score * 0.20 +
            blight_score * 0.15 +
            noise_score * 0.12 +
            air_quality_score * 0.12 +
            heat_score * 0.08 +
            wait_time_score * 0.08
        )

        block = {
            'block_id': f'BLOCK_{area_name[:4]}_{i:04d}',
            'lat': lat,
            'lng': lng,
            'overall_risk_score': round(overall_risk, 3),
            'crime_score': round(crime_score, 3),
            'blight_score': round(blight_score, 3),
            'wait_time_score': round(wait_time_score, 3),
            'air_quality_score': round(air_quality_score, 3),
            'heat_score': round(heat_score, 3),
            'traffic_score': round(traffic_score, 3),
            'noise_score': round(noise_score, 3),
            'accident_count': random.randint(0, int(overall_risk * 20)),
            'issue_count': random.randint(0, int(overall_risk * 50)),
            'area_name': area_name
        }
        blocks.append(block)

        if (i + 1) % 50 == 0:
            print(f"   Generated {i + 1}/{num_blocks} blocks...")

    return blocks


# =====================================================
# DATABASE OPERATIONS
# =====================================================

def insert_users(supabase: Client, users: List[Dict]) -> List[str]:
    """Insert users and return their IDs"""
    print(f"\n📥 Inserting {len(users)} users into database...")

    # Insert in batches
    batch_size = 100
    all_user_ids = []

    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]
        result = supabase.table('users').insert(batch).execute()
        user_ids = [record['id'] for record in result.data]
        all_user_ids.extend(user_ids)
        print(f"   Inserted batch {i // batch_size + 1}/{(len(users) + batch_size - 1) // batch_size}")

    print(f"✓ Successfully inserted {len(all_user_ids)} users")
    return all_user_ids


def insert_points_transactions(supabase: Client, transactions: List[Dict]) -> int:
    """Insert points transactions"""
    print(f"\n📥 Inserting {len(transactions)} points transactions...")

    # Insert in batches
    batch_size = 500
    total_inserted = 0

    for i in range(0, len(transactions), batch_size):
        batch = transactions[i:i + batch_size]
        result = supabase.table('points_transactions').insert(batch).execute()
        total_inserted += len(result.data)
        print(f"   Inserted batch {i // batch_size + 1}/{(len(transactions) + batch_size - 1) // batch_size}")

    print(f"✓ Successfully inserted {total_inserted} transactions")
    return total_inserted


def insert_accident_history(supabase: Client, accidents: List[Dict]) -> int:
    """Insert accident history records"""
    print(f"\n📥 Inserting {len(accidents)} accident records...")

    # Insert in batches
    batch_size = 100
    total_inserted = 0

    for i in range(0, len(accidents), batch_size):
        batch = accidents[i:i + batch_size]
        result = supabase.table('accident_history').insert(batch).execute()
        total_inserted += len(result.data)
        print(f"   Inserted batch {i // batch_size + 1}/{(len(accidents) + batch_size - 1) // batch_size}")

    print(f"✓ Successfully inserted {total_inserted} accident records")
    return total_inserted


def insert_block_risk_scores(supabase: Client, blocks: List[Dict]) -> int:
    """Insert block risk scores"""
    print(f"\n📥 Inserting {len(blocks)} block risk scores...")

    # Insert in batches
    batch_size = 100
    total_inserted = 0

    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i + batch_size]
        result = supabase.table('block_risk_scores').insert(batch).execute()
        total_inserted += len(result.data)
        print(f"   Inserted batch {i // batch_size + 1}/{(len(blocks) + batch_size - 1) // batch_size}")

    print(f"✓ Successfully inserted {total_inserted} block risk scores")
    return total_inserted


def fetch_existing_issue_ids(supabase: Client) -> List[str]:
    """Fetch existing issue IDs to link transactions and accidents"""
    print("\n🔍 Fetching existing issue IDs...")
    try:
        result = supabase.table('issues').select('id').execute()
        issue_ids = [record['id'] for record in result.data]
        print(f"✓ Found {len(issue_ids)} existing issues")
        return issue_ids
    except Exception as e:
        print(f"⚠️  Could not fetch issues: {e}")
        return []


def refresh_leaderboard(supabase: Client):
    """Refresh the leaderboard table"""
    print("\n🏆 Refreshing leaderboard...")
    try:
        # Call the refresh function
        supabase.rpc('refresh_leaderboard').execute()
        print("✓ Leaderboard refreshed successfully")
    except Exception as e:
        print(f"⚠️  Could not refresh leaderboard: {e}")
        print("   You may need to manually refresh using: SELECT refresh_leaderboard();")


# =====================================================
# MAIN
# =====================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generate synthetic gamification and risk data for NeuraCity'
    )
    parser.add_argument(
        '--users',
        type=int,
        default=100,
        help='Number of users to generate (default: 100)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Days of historical data (default: 30)'
    )
    parser.add_argument(
        '--blocks',
        type=int,
        default=200,
        help='Number of city blocks (default: 200)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("NeuraCity Gamification & Risk Data Generator")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Users: {args.users}")
    print(f"  Days of history: {args.days}")
    print(f"  City blocks: {args.blocks}")

    # Load environment variables
    load_dotenv()
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("\n✗ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        sys.exit(1)

    # Connect to Supabase
    print("\n🔌 Connecting to Supabase...")
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✓ Connected successfully")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        sys.exit(1)

    # Initialize Faker
    fake = Faker()
    Faker.seed(42)  # Reproducible data
    random.seed(42)

    # Fetch existing issue IDs
    issue_ids = fetch_existing_issue_ids(supabase)

    # Generate data
    users = generate_users(fake, args.users)

    # Insert users first to get IDs
    user_ids = insert_users(supabase, users)

    # Generate and insert dependent data
    transactions = generate_points_transactions(user_ids, issue_ids, args.days)
    insert_points_transactions(supabase, transactions)

    accidents = generate_accident_history(issue_ids, args.days)
    insert_accident_history(supabase, accidents)

    blocks = generate_block_risk_scores(args.blocks)
    insert_block_risk_scores(supabase, blocks)

    # Refresh leaderboard
    refresh_leaderboard(supabase)

    # Print summary
    print("\n" + "=" * 60)
    print("Data Generation Complete!")
    print("=" * 60)
    print(f"✓ Users: {len(user_ids)}")
    print(f"✓ Points Transactions: {len(transactions)}")
    print(f"✓ Accident Records: {len(accidents)}")
    print(f"✓ Block Risk Scores: {len(blocks)}")
    print("\nYou can now:")
    print("  - View leaderboard: SELECT * FROM top_users_leaderboard LIMIT 10;")
    print("  - View accident hotspots: SELECT * FROM accident_hotspots;")
    print("  - View high risk blocks: SELECT * FROM high_risk_blocks;")
    print("  - Find nearby accidents: SELECT * FROM get_nearby_accidents(40.7128, -74.0060, 1000);")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nData generation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
