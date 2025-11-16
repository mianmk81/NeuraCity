#!/usr/bin/env python3
"""
NeuraCity Risk Index Synthetic Data Generator

Generates realistic synthetic data for community risk assessment:
- Risk blocks with geographic grid
- Crime incidents with area-specific patterns
- Blight data (abandoned buildings, vacant lots, violations)
- Emergency response times with spatial variation
- Air quality measurements (AQI, PM2.5)
- Heat exposure data (temperature, tree canopy, impervious surfaces)
- Traffic speed data with road type classification

Usage:
    python generate_risk_data.py [--blocks=200] [--days=30]
"""

import os
import sys
import random
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    from supabase import create_client, Client
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)


# =====================================================
# CONFIGURATION
# =====================================================

# NYC coordinates for consistency with existing data
NYC_BOUNDS = {
    'lat_min': 40.70,
    'lat_max': 40.80,
    'lng_min': -74.02,
    'lng_max': -73.95
}

# Block grid size (approximately 100m x 100m)
BLOCK_GRID_SIZE = 0.001  # degrees (roughly 100m at NYC latitude)

# Area-specific risk profiles
AREA_RISK_PROFILES = {
    'DOWNTOWN': {
        'crime_base': 0.6,
        'blight_base': 0.3,
        'emergency_base': 0.4,
        'air_quality_base': 0.6,
        'heat_base': 0.7,
        'traffic_base': 0.7
    },
    'MIDTOWN': {
        'crime_base': 0.5,
        'blight_base': 0.2,
        'emergency_base': 0.3,
        'air_quality_base': 0.7,
        'heat_base': 0.8,
        'traffic_base': 0.8
    },
    'RESIDENTIAL': {
        'crime_base': 0.3,
        'blight_base': 0.4,
        'emergency_base': 0.5,
        'air_quality_base': 0.4,
        'heat_base': 0.5,
        'traffic_base': 0.4
    },
    'INDUSTRIAL': {
        'crime_base': 0.7,
        'blight_base': 0.8,
        'emergency_base': 0.7,
        'air_quality_base': 0.9,
        'heat_base': 0.9,
        'traffic_base': 0.6
    },
    'PARK_DISTRICT': {
        'crime_base': 0.2,
        'blight_base': 0.1,
        'emergency_base': 0.4,
        'air_quality_base': 0.2,
        'heat_base': 0.2,
        'traffic_base': 0.3
    },
    'CAMPUS': {
        'crime_base': 0.3,
        'blight_base': 0.2,
        'emergency_base': 0.3,
        'air_quality_base': 0.3,
        'heat_base': 0.4,
        'traffic_base': 0.5
    }
}

# Road type distribution
ROAD_TYPES = ['residential', 'arterial', 'highway']


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def get_area_for_location(lat: float, lng: float) -> str:
    """Determine area based on location (simplified)."""
    # Simple grid-based assignment
    if lat > 40.76:
        if lng < -73.99:
            return 'MIDTOWN'
        else:
            return 'PARK_DISTRICT'
    elif lat > 40.73:
        if lng < -73.99:
            return 'DOWNTOWN'
        else:
            return 'CAMPUS'
    elif lat > 40.71:
        return 'RESIDENTIAL'
    else:
        if lng < -74.00:
            return 'INDUSTRIAL'
        else:
            return 'RESIDENTIAL'


def add_noise(base_value: float, variance: float = 0.2) -> float:
    """Add random variance to a base value."""
    noise = random.uniform(-variance, variance)
    return max(0.0, min(1.0, base_value + noise))


def generate_block_id(lat: float, lng: float) -> str:
    """Generate unique block ID from coordinates."""
    return f"BLK_{lat:.4f}_{lng:.4f}"


# =====================================================
# DATA GENERATORS
# =====================================================

def generate_risk_blocks(num_blocks: int) -> List[Dict]:
    """Generate geographic blocks with initial risk data."""
    print(f"Generating {num_blocks} risk blocks...")
    blocks = []

    # Create grid of blocks
    blocks_per_side = int(math.sqrt(num_blocks))
    lat_step = (NYC_BOUNDS['lat_max'] - NYC_BOUNDS['lat_min']) / blocks_per_side
    lng_step = (NYC_BOUNDS['lng_max'] - NYC_BOUNDS['lng_min']) / blocks_per_side

    for i in range(blocks_per_side):
        for j in range(blocks_per_side):
            lat = NYC_BOUNDS['lat_min'] + (i * lat_step) + (lat_step / 2)
            lng = NYC_BOUNDS['lng_min'] + (j * lng_step) + (lng_step / 2)

            area = get_area_for_location(lat, lng)
            profile = AREA_RISK_PROFILES.get(area, AREA_RISK_PROFILES['RESIDENTIAL'])

            # Generate scores with area-specific baselines and random variance
            crime_score = add_noise(profile['crime_base'], 0.15)
            blight_score = add_noise(profile['blight_base'], 0.15)
            emergency_score = add_noise(profile['emergency_base'], 0.15)
            air_quality_score = add_noise(profile['air_quality_base'], 0.15)
            heat_score = add_noise(profile['heat_base'], 0.15)
            traffic_score = add_noise(profile['traffic_base'], 0.15)

            # Calculate composite (weighted average)
            composite = (
                crime_score * 0.25 +
                blight_score * 0.15 +
                emergency_score * 0.20 +
                air_quality_score * 0.15 +
                heat_score * 0.10 +
                traffic_score * 0.15
            )

            # Determine category
            if composite < 0.3:
                category = 'low'
            elif composite < 0.5:
                category = 'moderate'
            elif composite < 0.7:
                category = 'high'
            else:
                category = 'critical'

            blocks.append({
                'block_id': generate_block_id(lat, lng),
                'lat': lat,
                'lng': lng,
                'crime_score': round(crime_score, 3),
                'blight_score': round(blight_score, 3),
                'emergency_response_score': round(emergency_score, 3),
                'air_quality_score': round(air_quality_score, 3),
                'heat_exposure_score': round(heat_score, 3),
                'traffic_speed_score': round(traffic_score, 3),
                'composite_risk_index': round(composite, 3),
                'risk_category': category
            })

    print(f"Generated {len(blocks)} blocks")
    return blocks


def generate_crime_factors(blocks: List[Dict], days: int) -> List[Dict]:
    """Generate synthetic crime incident data."""
    print(f"Generating crime data for {days} days...")
    factors = []

    for block in blocks:
        # Crime incidents vary by block risk
        base_incidents = int(block['crime_score'] * 50)  # Max 50 incidents/month

        # Add temporal variation
        for day_offset in range(0, days, 7):  # Weekly snapshots
            incidents = max(0, base_incidents + random.randint(-10, 10))

            # Severity multiplier based on area
            area = get_area_for_location(block['lat'], block['lng'])
            if area in ['INDUSTRIAL', 'DOWNTOWN']:
                severity = random.uniform(1.0, 1.5)
            else:
                severity = random.uniform(0.8, 1.2)

            measurement_date = datetime.now() - timedelta(days=day_offset)

            factors.append({
                'block_id': block['block_id'],
                'factor_type': 'crime',
                'raw_value': incidents,
                'raw_unit': 'incidents',
                'normalized_score': block['crime_score'],
                'data_source': 'synthetic',
                'measurement_date': measurement_date.isoformat()
            })

    print(f"Generated {len(factors)} crime factor records")
    return factors


def generate_blight_factors(blocks: List[Dict]) -> List[Dict]:
    """Generate synthetic blight data (buildings, lots, violations)."""
    print("Generating blight data...")
    factors = []

    for block in blocks:
        # Blight components vary by block risk
        base_blight = block['blight_score']

        abandoned_buildings = int(base_blight * 10)
        vacant_lots = int(base_blight * 15)
        code_violations = int(base_blight * 20)

        # Total weighted blight value
        total_blight = (abandoned_buildings * 3) + (code_violations * 2) + (vacant_lots * 1)

        factors.append({
            'block_id': block['block_id'],
            'factor_type': 'blight',
            'raw_value': total_blight,
            'raw_unit': 'weighted_properties',
            'normalized_score': block['blight_score'],
            'data_source': 'synthetic',
            'measurement_date': datetime.now().isoformat()
        })

    print(f"Generated {len(factors)} blight factor records")
    return factors


def generate_emergency_response_factors(blocks: List[Dict], days: int) -> List[Dict]:
    """Generate synthetic emergency response time data."""
    print(f"Generating emergency response data for {days} days...")
    factors = []

    for block in blocks:
        # Response time varies by block risk
        base_avg_time = block['emergency_response_score'] * 30  # Max 30 minutes

        # Weekly snapshots
        for day_offset in range(0, days, 7):
            avg_time = max(2.0, base_avg_time + random.uniform(-3, 3))

            measurement_date = datetime.now() - timedelta(days=day_offset)

            factors.append({
                'block_id': block['block_id'],
                'factor_type': 'emergency_response',
                'raw_value': round(avg_time, 1),
                'raw_unit': 'minutes',
                'normalized_score': block['emergency_response_score'],
                'data_source': 'synthetic',
                'measurement_date': measurement_date.isoformat()
            })

    print(f"Generated {len(factors)} emergency response factor records")
    return factors


def generate_air_quality_factors(blocks: List[Dict], days: int) -> List[Dict]:
    """Generate synthetic air quality data (AQI, PM2.5)."""
    print(f"Generating air quality data for {days} days...")
    factors = []

    for block in blocks:
        # AQI varies by block risk
        base_aqi = block['air_quality_score'] * 200  # Max AQI 200

        # Daily measurements
        for day_offset in range(0, days, 1):
            # Add daily variation (pollution varies by weather)
            daily_aqi = max(0, base_aqi + random.uniform(-20, 20))

            measurement_date = datetime.now() - timedelta(days=day_offset)

            factors.append({
                'block_id': block['block_id'],
                'factor_type': 'air_quality',
                'raw_value': round(daily_aqi, 0),
                'raw_unit': 'aqi',
                'normalized_score': block['air_quality_score'],
                'data_source': 'synthetic',
                'measurement_date': measurement_date.isoformat()
            })

    print(f"Generated {len(factors)} air quality factor records")
    return factors


def generate_heat_exposure_factors(blocks: List[Dict]) -> List[Dict]:
    """Generate synthetic heat exposure data (temp, canopy, impervious)."""
    print("Generating heat exposure data...")
    factors = []

    for block in blocks:
        # Temperature varies by heat score
        base_temp = 20 + (block['heat_exposure_score'] * 25)  # 20-45°C

        factors.append({
            'block_id': block['block_id'],
            'factor_type': 'heat_exposure',
            'raw_value': round(base_temp, 1),
            'raw_unit': 'celsius',
            'normalized_score': block['heat_exposure_score'],
            'data_source': 'synthetic',
            'measurement_date': datetime.now().isoformat()
        })

    print(f"Generated {len(factors)} heat exposure factor records")
    return factors


def generate_traffic_speed_factors(blocks: List[Dict], days: int) -> List[Dict]:
    """Generate synthetic traffic speed data."""
    print(f"Generating traffic speed data for {days} days...")
    factors = []

    for block in blocks:
        # Assign road type based on location
        area = get_area_for_location(block['lat'], block['lng'])
        if area in ['MIDTOWN', 'DOWNTOWN']:
            road_type = random.choice(['arterial', 'residential'])
        elif area == 'INDUSTRIAL':
            road_type = random.choice(['arterial', 'highway'])
        else:
            road_type = 'residential'

        # Speed thresholds by road type
        thresholds = {'residential': 25, 'arterial': 35, 'highway': 55}
        safe_speed = thresholds[road_type]

        # Calculate speed from traffic score
        base_speed = safe_speed + (block['traffic_speed_score'] * 30)

        # Weekly snapshots
        for day_offset in range(0, days, 7):
            avg_speed = max(15, base_speed + random.uniform(-5, 5))

            measurement_date = datetime.now() - timedelta(days=day_offset)

            factors.append({
                'block_id': block['block_id'],
                'factor_type': 'traffic_speed',
                'raw_value': round(avg_speed, 1),
                'raw_unit': 'mph',
                'normalized_score': block['traffic_speed_score'],
                'data_source': 'synthetic',
                'measurement_date': measurement_date.isoformat()
            })

    print(f"Generated {len(factors)} traffic speed factor records")
    return factors


def generate_risk_history(blocks: List[Dict], days: int) -> List[Dict]:
    """Generate historical risk snapshots."""
    print(f"Generating risk history for {days} days...")
    history = []

    # Generate weekly snapshots
    for day_offset in range(0, days, 7):
        snapshot_date = datetime.now() - timedelta(days=day_offset)

        for block in blocks:
            # Add slight variation to historical data
            variance = 0.05
            history.append({
                'block_id': block['block_id'],
                'composite_risk_index': round(add_noise(block['composite_risk_index'], variance), 3),
                'risk_category': block['risk_category'],
                'crime_score': round(add_noise(block['crime_score'], variance), 3),
                'blight_score': round(add_noise(block['blight_score'], variance), 3),
                'emergency_response_score': round(add_noise(block['emergency_response_score'], variance), 3),
                'air_quality_score': round(add_noise(block['air_quality_score'], variance), 3),
                'heat_exposure_score': round(add_noise(block['heat_exposure_score'], variance), 3),
                'traffic_speed_score': round(add_noise(block['traffic_speed_score'], variance), 3),
                'snapshot_date': snapshot_date.isoformat()
            })

    print(f"Generated {len(history)} historical snapshots")
    return history


# =====================================================
# DATABASE INSERTION
# =====================================================

def insert_data_to_supabase(
    blocks: List[Dict],
    factors: List[Dict],
    history: List[Dict],
    supabase: Client
):
    """Insert generated data into Supabase."""
    print("\n" + "=" * 50)
    print("Inserting data into Supabase...")
    print("=" * 50)

    # Insert risk blocks
    print("\nInserting risk blocks...")
    try:
        # Batch insert (Supabase supports up to 1000 rows)
        batch_size = 500
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]
            supabase.table('risk_blocks').insert(batch).execute()
            print(f"  Inserted {min(i + batch_size, len(blocks))}/{len(blocks)} blocks")
        print(f"✓ Successfully inserted {len(blocks)} blocks")
    except Exception as e:
        print(f"✗ Error inserting blocks: {e}")

    # Insert risk factors
    print("\nInserting risk factors...")
    try:
        batch_size = 500
        for i in range(0, len(factors), batch_size):
            batch = factors[i:i + batch_size]
            supabase.table('risk_factors').insert(batch).execute()
            print(f"  Inserted {min(i + batch_size, len(factors))}/{len(factors)} factors")
        print(f"✓ Successfully inserted {len(factors)} factor records")
    except Exception as e:
        print(f"✗ Error inserting factors: {e}")

    # Insert risk history
    print("\nInserting risk history...")
    try:
        batch_size = 500
        for i in range(0, len(history), batch_size):
            batch = history[i:i + batch_size]
            supabase.table('risk_history').insert(batch).execute()
            print(f"  Inserted {min(i + batch_size, len(history))}/{len(history)} history records")
        print(f"✓ Successfully inserted {len(history)} historical snapshots")
    except Exception as e:
        print(f"✗ Error inserting history: {e}")


# =====================================================
# MAIN EXECUTION
# =====================================================

def main():
    parser = argparse.ArgumentParser(description='Generate synthetic risk index data')
    parser.add_argument('--blocks', type=int, default=200,
                       help='Number of geographic blocks to generate (default: 200)')
    parser.add_argument('--days', type=int, default=30,
                       help='Number of days of historical data (default: 30)')
    args = parser.parse_args()

    print("=" * 50)
    print("NeuraCity Risk Index Data Generator")
    print("=" * 50)
    print(f"Blocks: {args.blocks}")
    print(f"Historical days: {args.days}")
    print("=" * 50)

    # Load environment variables
    load_dotenv()

    # Check for required environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("\n✗ Error: Missing Supabase credentials")
        print("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
        sys.exit(1)

    # Initialize Supabase client
    supabase: Client = create_client(supabase_url, supabase_key)

    # Generate data
    print("\n" + "=" * 50)
    print("GENERATING DATA")
    print("=" * 50)

    blocks = generate_risk_blocks(args.blocks)

    all_factors = []
    all_factors.extend(generate_crime_factors(blocks, args.days))
    all_factors.extend(generate_blight_factors(blocks))
    all_factors.extend(generate_emergency_response_factors(blocks, args.days))
    all_factors.extend(generate_air_quality_factors(blocks, args.days))
    all_factors.extend(generate_heat_exposure_factors(blocks))
    all_factors.extend(generate_traffic_speed_factors(blocks, args.days))

    history = generate_risk_history(blocks, args.days)

    # Insert data
    insert_data_to_supabase(blocks, all_factors, history, supabase)

    # Summary statistics
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Total blocks: {len(blocks)}")
    print(f"Total factor measurements: {len(all_factors)}")
    print(f"Total historical snapshots: {len(history)}")

    # Risk category breakdown
    categories = {'low': 0, 'moderate': 0, 'high': 0, 'critical': 0}
    for block in blocks:
        categories[block['risk_category']] += 1

    print("\nRisk category distribution:")
    for category, count in categories.items():
        percentage = (count / len(blocks)) * 100
        print(f"  {category.upper()}: {count} ({percentage:.1f}%)")

    print("\n✓ Data generation complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
