from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from joblib import load
import feedparser
from urllib.parse import urlparse
from datetime import datetime
from dateutil import parser
import pytz
from bs4 import BeautifulSoup
from data_cleaner import clean_text
import random
import requests

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['cybersecurity_news']

model = load('model.pkl')

def get_credibility_score(source):
    credibility_scores = {
        'The Hacker News': 9,
        'Graham Cluley': 9.5,
        'Naked Security': 8,
        'Infosecurity Magazine': 8.5,
        'Cyberscoop': 8,
        'SecurityWeek': 9,
        'CSO Online': 8.5,
        'ZDNet Zero Day': 8,
        'Schneier on Security': 9.5
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
    if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
        thumbnail = entry.media_thumbnail[0]['url']

    # Check if the entry has 'enclosures'
    elif 'links' in entry:
        for link in entry.links:
            if link.rel == 'enclosure' and link.type.startswith('image'):
                thumbnail = link.href
                break

    # If no thumbnail found, retrieve a random image from Pixabay
    if not thumbnail:
        api_key = "38297032-8bacc7c47db30f0e9b5ac6218"
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
        "per_page": 10
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


def get_articles(offset=0, per_page=18):
    articles = []
    sources = {
        'The Hacker News': 'https://thehackernews.com/feeds/posts/default',
        'Graham Cluley': 'https://grahamcluley.com/feed/',
        'Naked Security': 'https://nakedsecurity.sophos.com/feed/',
        'The Last Watchdog': 'https://www.lastwatchdog.com/feed/',
        'The State of Security – Tripwire': 'https://www.tripwire.com/state-of-security/feed/',
        'CSO Online': 'https://www.csoonline.com/index.rss',
        'Infosecurity Magazine': 'https://www.infosecurity-magazine.com/rss/news/',
        'Cyber Magazine': 'https://cybermagazine.com/rss',
        'Security Weekly': 'https://securityweekly.com/feed/',
        'IT Security Guru': 'https://www.itsecurityguru.org/feed/'
    }

    for source_name, source_url in sources.items():
        feed = feedparser.parse(source_url)
        for entry in feed.entries:
            credibility = get_credibility_score(source_name)
            freshness = get_freshness_score(entry.published_parsed)
            engagement = get_engagement_score()
            overall_score = get_overall_score(credibility, freshness, engagement)

            title = entry.get('title', '')
            summary = entry.get('summary', '')

            cleaned_title = clean_text(title)

            soup = BeautifulSoup(summary, 'html.parser')
            cleaned_summary = soup.get_text()

            published_date = parser.parse(entry.published)

            thumbnail = extract_thumbnail(entry)

            article = {
                'source': source_name,
                'title': title,
                'cleaned_title': cleaned_title,
                'link': entry.link,
                'published': published_date,
                'summary': cleaned_summary,
                'credibility_score': credibility,
                'freshness_score': freshness,
                'engagement_score': engagement,
                'overall_score': overall_score,
                'thumbnail': thumbnail
            }

            articles.append(article)

    articles.sort(key=lambda x: x['published'], reverse=True)

    formatted_articles = []
    for article in articles:
        formatted_published_date = article['published'].strftime('%d %B')
        article['published'] = formatted_published_date
        formatted_articles.append(article)

    return formatted_articles[offset:offset + per_page]


@app.route('/', methods=['GET'])
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 18
    offset = (page - 1) * per_page
    articles = get_articles(offset, per_page)
    total_articles = db.articles_cleaned.count_documents({})
    total_pages = total_articles // per_page
    if total_articles % per_page > 0:
        total_pages += 1
    return render_template('index.html', articles=articles, total_pages=total_pages, page=page)



@app.route('/articles/<int:page>', methods=['GET'])
def articles_page(page):
    per_page = 18
    offset = (page - 1) * per_page
    articles = get_articles(offset, per_page)
    total_articles = db.articles_cleaned.count_documents({})
    total_pages = total_articles // per_page
    if total_articles % per_page > 0:
        total_pages += 1
    return render_template('index.html', articles=articles, total_pages=total_pages, page=page)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    article = data['article']
    prediction = model.predict([article])[0]
    return jsonify({'prediction': prediction})

@app.template_filter('format_date')
def format_date(value):
    date = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    return date.strftime('%d %B')

@app.template_filter('truncate_words')
def truncate_words(s, num=20):
    words = s.split()
    if len(words) > num:
        words = words[:num]
    return ' '.join(words)

if __name__ == '__main__':
    app.run()
