"""
Synthetic Social Media Posts Generator

Generates realistic synthetic social media posts for mood analysis.
Posts are distributed across city areas with varying sentiment to simulate
realistic urban social media activity.

Areas:
- Midtown
- Downtown
- Campus
- Park District
- Residential Zone

Usage:
    python generate_synthetic_posts.py --output posts.json --posts-per-area 150
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import argparse
from pathlib import Path

try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
    print("WARNING: faker library not available. Install with: pip install faker")


# Define city areas with coordinates
CITY_AREAS = {
    'MIDTOWN': {
        'lat': 40.7589,
        'lng': -73.9851,
        'name': 'Midtown',
        'characteristics': 'busy, commercial, office buildings, high traffic'
    },
    'DOWNTOWN': {
        'lat': 40.7128,
        'lng': -74.0060,
        'name': 'Downtown',
        'characteristics': 'financial district, historic, mixed use, tourist attractions'
    },
    'CAMPUS': {
        'lat': 40.8075,
        'lng': -73.9626,
        'name': 'Campus',
        'characteristics': 'university area, young crowd, cafes, student life'
    },
    'PARK_DISTRICT': {
        'lat': 40.7829,
        'lng': -73.9654,
        'name': 'Park District',
        'characteristics': 'green spaces, quiet, recreational, family-friendly'
    },
    'RESIDENTIAL_ZONE': {
        'lat': 40.7282,
        'lng': -73.7949,
        'name': 'Residential Zone',
        'characteristics': 'residential, quiet streets, neighborhoods, community feel'
    }
}


# Sentiment-specific post templates
POSITIVE_TEMPLATES = [
    "Beautiful day in {area}! Love this city!",
    "Just had an amazing coffee at the new cafe in {area}",
    "The {area} area is looking great today!",
    "Wonderful atmosphere in {area} this morning",
    "Really enjoying the vibe in {area} lately",
    "Great to see so many people out and about in {area}",
    "The improvements in {area} are really paying off",
    "Love walking through {area} on days like this",
    "Best neighborhood in the city hands down - {area}!",
    "Such a positive energy in {area} today",
    "Grateful to live near {area}, it's beautiful",
    "The community feel in {area} is unmatched",
    "Perfect weather for a walk in {area}",
    "The new developments in {area} look fantastic",
    "So peaceful and clean in {area} today",
]

NEGATIVE_TEMPLATES = [
    "Traffic is absolutely terrible in {area} right now",
    "Why is {area} always so congested?",
    "Avoid {area} if you can, complete gridlock",
    "The noise level in {area} is getting out of hand",
    "Getting worse and worse in {area} every day",
    "Streets in {area} need serious attention",
    "Another pothole on my street in {area}",
    "Construction noise in {area} is unbearable",
    "Getting stuck in {area} traffic again...",
    "When will they fix the roads in {area}?",
    "So crowded and chaotic in {area} lately",
    "Infrastructure in {area} is falling apart",
    "Disappointed with how dirty {area} has become",
    "Too much traffic and not enough parking in {area}",
    "The quality of life in {area} is declining",
]

NEUTRAL_TEMPLATES = [
    "Heading to work through {area} as usual",
    "Another day in {area}",
    "Passing through {area} on my commute",
    "Meeting someone in {area} later today",
    "Just another Monday in {area}",
    "Running errands in {area} this afternoon",
    "Typical day in the {area} area",
    "Grabbing lunch in {area}",
    "Stopped by the store in {area}",
    "Waiting for my appointment in {area}",
    "Taking the usual route through {area}",
    "Weather is okay in {area} today",
    "Normal amount of traffic in {area}",
    "Routine trip to {area} this morning",
    "Nothing special happening in {area} today",
]


class SyntheticPostGenerator:
    """
    Generator for realistic synthetic social media posts.
    """

    def __init__(self, seed: int = 42):
        """
        Initialize the generator.

        Args:
            seed: Random seed for reproducibility
        """
        random.seed(seed)

        if FAKER_AVAILABLE:
            self.fake = Faker()
            Faker.seed(seed)
        else:
            self.fake = None

    def generate_post(
        self,
        area_id: str,
        area_info: Dict,
        timestamp: datetime,
        sentiment_bias: str = 'mixed'
    ) -> Dict:
        """
        Generate a single synthetic post.

        Args:
            area_id: Area identifier (e.g., 'MIDTOWN')
            area_info: Area information dictionary
            timestamp: Post timestamp
            sentiment_bias: 'positive', 'negative', 'neutral', or 'mixed'

        Returns:
            Post dictionary with text, area, timestamp, etc.
        """
        # Select sentiment based on bias
        if sentiment_bias == 'mixed':
            sentiment = random.choices(
                ['positive', 'negative', 'neutral'],
                weights=[0.4, 0.3, 0.3]  # Slightly optimistic bias
            )[0]
        else:
            sentiment = sentiment_bias

        # Select template based on sentiment
        if sentiment == 'positive':
            template = random.choice(POSITIVE_TEMPLATES)
        elif sentiment == 'negative':
            template = random.choice(NEGATIVE_TEMPLATES)
        else:
            template = random.choice(NEUTRAL_TEMPLATES)

        # Generate post text
        text = template.format(area=area_info['name'])

        # Add some variation with Faker if available
        if self.fake and random.random() < 0.3:
            # 30% chance to add more realistic detail
            if sentiment == 'positive':
                additions = [
                    f" {self.fake.catch_phrase()}",
                    f" Highly recommend!",
                    f" {self.fake.emoji()}",
                ]
            elif sentiment == 'negative':
                additions = [
                    f" Seriously frustrating.",
                    f" This needs to be fixed ASAP.",
                    f" Not acceptable.",
                ]
            else:
                additions = [
                    f" As expected.",
                    f" Same as yesterday.",
                    f" Nothing new.",
                ]

            text += random.choice(additions)

        return {
            'area_id': area_id,
            'area_name': area_info['name'],
            'lat': area_info['lat'],
            'lng': area_info['lng'],
            'text': text,
            'timestamp': timestamp.isoformat(),
            'sentiment_expected': sentiment,  # For testing purposes
            'author': self.fake.user_name() if self.fake else f"user_{random.randint(1000, 9999)}"
        }

    def generate_area_posts(
        self,
        area_id: str,
        area_info: Dict,
        count: int = 150,
        start_date: datetime = None,
        sentiment_bias: str = 'mixed'
    ) -> List[Dict]:
        """
        Generate multiple posts for a specific area.

        Args:
            area_id: Area identifier
            area_info: Area information
            count: Number of posts to generate
            start_date: Starting timestamp (defaults to 7 days ago)
            sentiment_bias: Overall sentiment bias for this area

        Returns:
            List of post dictionaries
        """
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(days=7)

        posts = []
        time_range = timedelta(days=7)

        for i in range(count):
            # Random timestamp within the range
            random_offset = timedelta(
                seconds=random.randint(0, int(time_range.total_seconds()))
            )
            timestamp = start_date + random_offset

            post = self.generate_post(area_id, area_info, timestamp, sentiment_bias)
            posts.append(post)

        # Sort by timestamp
        posts.sort(key=lambda x: x['timestamp'])

        return posts

    def generate_all_areas(
        self,
        posts_per_area: int = 150,
        area_sentiments: Dict[str, str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Generate posts for all city areas.

        Args:
            posts_per_area: Number of posts per area
            area_sentiments: Optional dict mapping area_id to sentiment bias

        Returns:
            Dictionary mapping area_id to list of posts
        """
        if area_sentiments is None:
            # Default sentiment biases for different areas
            area_sentiments = {
                'MIDTOWN': 'mixed',  # Busy, mixed feelings
                'DOWNTOWN': 'mixed',  # Tourist area, varied
                'CAMPUS': 'positive',  # Young, energetic
                'PARK_DISTRICT': 'positive',  # Peaceful, liked
                'RESIDENTIAL_ZONE': 'neutral',  # Quiet, routine
            }

        all_posts = {}

        for area_id, area_info in CITY_AREAS.items():
            sentiment_bias = area_sentiments.get(area_id, 'mixed')

            print(f"Generating {posts_per_area} posts for {area_info['name']} (bias: {sentiment_bias})...")

            posts = self.generate_area_posts(
                area_id,
                area_info,
                count=posts_per_area,
                sentiment_bias=sentiment_bias
            )

            all_posts[area_id] = posts

        return all_posts

    def save_to_json(self, posts_data: Dict[str, List[Dict]], output_path: str):
        """
        Save posts to JSON file.

        Args:
            posts_data: Posts data from generate_all_areas()
            output_path: Output file path
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(posts_data, f, indent=2, ensure_ascii=False)

        total_posts = sum(len(posts) for posts in posts_data.values())
        print(f"\nSaved {total_posts} posts to {output_path}")

    def save_flat_format(self, posts_data: Dict[str, List[Dict]], output_path: str):
        """
        Save posts in flat array format (all posts in one array).

        Args:
            posts_data: Posts data from generate_all_areas()
            output_path: Output file path
        """
        flat_posts = []
        for area_posts in posts_data.values():
            flat_posts.extend(area_posts)

        # Sort by timestamp
        flat_posts.sort(key=lambda x: x['timestamp'])

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(flat_posts, f, indent=2, ensure_ascii=False)

        print(f"\nSaved {len(flat_posts)} posts (flat format) to {output_path}")


def main():
    """
    Main entry point for command-line usage.
    """
    parser = argparse.ArgumentParser(
        description='Generate synthetic social media posts for mood analysis'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='data/synthetic_posts.json',
        help='Output JSON file path (default: data/synthetic_posts.json)'
    )

    parser.add_argument(
        '--posts-per-area',
        type=int,
        default=150,
        help='Number of posts to generate per area (default: 150)'
    )

    parser.add_argument(
        '--flat',
        action='store_true',
        help='Save in flat array format instead of grouped by area'
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )

    args = parser.parse_args()

    if not FAKER_AVAILABLE:
        print("\nWARNING: faker library not installed. Posts will be less realistic.")
        print("Install with: pip install faker\n")

    # Generate posts
    generator = SyntheticPostGenerator(seed=args.seed)

    print(f"Generating synthetic posts...")
    print(f"Posts per area: {args.posts_per_area}")
    print(f"Random seed: {args.seed}\n")

    posts_data = generator.generate_all_areas(posts_per_area=args.posts_per_area)

    # Save to file
    if args.flat:
        generator.save_flat_format(posts_data, args.output)
    else:
        generator.save_to_json(posts_data, args.output)

    # Print summary
    print("\nSummary:")
    print(f"{'Area':<20} {'Posts':<10} {'Sentiment Bias':<15}")
    print("-" * 45)

    area_sentiments = {
        'MIDTOWN': 'mixed',
        'DOWNTOWN': 'mixed',
        'CAMPUS': 'positive',
        'PARK_DISTRICT': 'positive',
        'RESIDENTIAL_ZONE': 'neutral',
    }

    for area_id in posts_data:
        count = len(posts_data[area_id])
        bias = area_sentiments.get(area_id, 'mixed')
        print(f"{CITY_AREAS[area_id]['name']:<20} {count:<10} {bias:<15}")

    total = sum(len(posts) for posts in posts_data.values())
    print("-" * 45)
    print(f"{'TOTAL':<20} {total:<10}")

    print("\nDone! Use this file with mood_analysis.py to calculate area moods.")


if __name__ == '__main__':
    main()
