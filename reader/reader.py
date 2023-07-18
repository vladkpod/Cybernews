import feedparser
from urllib.parse import urlparse
from pymongo import MongoClient
from datetime import datetime
from dateutil import parser
import pytz
import requests
from bs4 import BeautifulSoup
from data_cleaner import clean_text
import random


def get_credibility_score(source):
    credibility_scores = {
        'The Hacker News': 10,
        'Graham Cluley': 9,
        'Naked Security': 8.5,
        'The Last Watchdog': 8,
        'The State of Security - Tripwire': 7.5,
        'CSO Online': 7,
        'Infosecurity Magazine': 6.5,
        'Cyber Magazine': 6,
        'Security Weekly': 5.5,
        'IT Security Guru': 5
    }
    return credibility_scores.get(source, 5)

def get_freshness_score(published_time):
    current_time = datetime.now(pytz.utc)
    published_time = datetime(*published_time[:6], tzinfo=pytz.utc)
    time_difference = current_time - published_time
    hours_difference = time_difference.total_seconds() / 3600
    return max(10 - hours_difference / 24, 0)

def get_engagement_score():
    return 5

def get_overall_score(credibility, freshness, engagement):
    return credibility * 0.5 + freshness * 0.3 + engagement * 0.2

def extract_thumbnail(entry):
    thumbnail = None

    # Check if the entry has a 'media_thumbnail' field
    if 'media_thumbnail' in entry:
        for media in entry['media_thumbnail']:
            if 'url' in media and media['url']:
                thumbnail = media['url']
                break

    # Check if the entry has 'enclosures'
    elif 'enclosures' in entry:
        for enclosure in entry['enclosures']:
            if 'type' in enclosure and enclosure['type'].startswith('image'):
                if 'href' in enclosure and enclosure['href']:
                    thumbnail = enclosure['href']
                    break

    # Check if the entry has 'content' with 'value' field
    elif 'content' in entry:
        for content in entry['content']:
            if (
                'type' in content and content['type'].startswith('image')
                and 'value' in content and content['value']
            ):
                soup = BeautifulSoup(content['value'], 'html.parser')
                img_tags = soup.find_all('img')
                if img_tags:
                    thumbnail = img_tags[0].get('src')
                    break

    # Retrieve a random image from Pixabay
    if not thumbnail:
        api_key = "your_api_key"
        query = ["technology", "computing", "cybersecurity", "encryption", "firewall", "malware", "phishing", 
                 "ransomware", "spyware", "threat", "vulnerability", "intrusion", "forensics", "network", 
                 "data", "privacy", "protection", "breach", "alert", "defense", "identity", "risk", "scam", 
                 "security", "attack", "cybercrime", "hacker", 
                 "safe", "secure", "system", "information", "internet", "virus", "web", "password"]
        thumbnail = get_random_image_from_pixabay(api_key, query)

    return thumbnail

# Create a set to store used image URLs
used_images = set()

def get_random_image_from_pixabay(api_key, query):
    url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": query,
        "orientation": "horizontal",
        "per_page": 20
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        result = response.json()
        if "hits" in result and len(result["hits"]) > 0:
            # Select a random image and check if it's been used
            image = random.choice(result["hits"])
            while image["largeImageURL"] in used_images and len(used_images) < len(result["hits"]):
                image = random.choice(result["hits"])
            used_images.add(image["largeImageURL"])
            return image["largeImageURL"]
    return None


# List of queries
query = [
    "technology"
          ]

# Usage example
api_key = "38297032-8bacc7c47db30f0e9b5ac6218"

for query in query:
    image_url = get_random_image_from_pixabay(api_key, query)
    if image_url:
        print(f"Random Image URL for query '{query}': {image_url}")
    else:
        print(f"No image found for query '{query}'.")


def parse_feeds(sources, db):
    all_articles = []
    for source_name, source_url in sources.items():
        print(f'Parsing feed from {source_name}...')

        feed = feedparser.parse(source_url)

        for entry in feed.entries:
            print('Title: ', entry.title)
            print('Link: ', entry.link)
            print('Published: ', entry.published)
            print('Summary: ', entry.summary)
            print()

            credibility = get_credibility_score(source_name)
            freshness = get_freshness_score(entry.published_parsed)
            engagement = get_engagement_score()
            overall_score = get_overall_score(credibility, freshness, engagement)

            # Extract the title and summary using the provided entry.get() method
            original_title = entry.get('title', '')
            summary = entry.get('summary', '')

            # Clean the title using the clean_text() function from data_cleaner.py
            cleaned_title = clean_text(original_title)

            # Parse the summary using BeautifulSoup to extract the text content
            soup = BeautifulSoup(summary, 'html.parser')
            cleaned_summary = soup.get_text()

            # Extract the thumbnail image URL
            thumbnail = extract_thumbnail(entry)

            # Parse the published date using dateutil.parser
            published_date = parser.parse(entry.published)
            published_iso = published_date.isoformat()

            article = {
                'source': source_name,
                'title': original_title,  # Use the original title here
                'cleaned_title': cleaned_title,  # You can still store the cleaned title if you need it
                'link': entry.link,
                'published': published_iso,
                'summary': cleaned_summary,
                'credibility_score': credibility,
                'freshness_score': freshness,
                'engagement_score': engagement,
                'overall_score': overall_score,
                'thumbnail': thumbnail
            }
            all_articles.append(article)

    # Sort all_articles by 'published' field
    all_articles.sort(key=lambda article: article['published'], reverse=True)

    # Insert sorted articles into database
    db.articles.insert_many(all_articles)

def run_parser():
    client = MongoClient('localhost', 27017)
    db = client['cybersecurity_news']

    sources = {
        'The Hacker News': 'https://thehackernews.com/feeds/posts/default',
        'Graham Cluley': 'https://feeds.feedburner.com/GrahamCluleysBlog',
        'Naked Security': 'https://nakedsecurity.sophos.com/feed/',
        'The Last Watchdog': 'https://www.lastwatchdog.com/feed/',
        'The State of Security - Tripwire': 'https://www.tripwire.com/state-of-security/feed/',
        'CSO Online': 'https://www.csoonline.com/index.rss',
        'Infosecurity Magazine': 'https://www.infosecurity-magazine.com/rss/news/',
        'Cyber Magazine': 'https://cyber-magazine.nl/feed/',
        'Security Weekly': 'https://securityweekly.com/feed/',
        'IT Security Guru': 'https://www.itsecurityguru.org/feed/'
    }

    parse_feeds(sources, db)  # Pass the 'db' argument

if __name__ == '__main__':
    run_parser()