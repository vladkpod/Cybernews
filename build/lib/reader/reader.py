import feedparser
from pymongo import MongoClient
import pandas as pd
from data_cleaner import clean_text

def parse_feeds(sources, db):
    for source_name, source_url in sources.items():
        print(f'Parsing feed from {source_name}...')

        feed = feedparser.parse(source_url)

        for entry in feed.entries:
            print('Title: ', entry.title)
            print('Link: ', entry.link)
            print('Published: ', entry.published)
            print('Summary: ', entry.summary)
            print()

            article = {
                'source': source_name,
                'title': clean_text(entry.title),
                'link': entry.link,
                'published': entry.published,
                'summary': clean_text(entry.summary),
            }
            db.articles.insert_one(article)

def run_parser():
    client = MongoClient('localhost', 27017)
    db = client['cybersecurity_news']

    sources = {
        'The Hacker News': 'https://thehackernews.com/feeds/posts/default',
        'Krebs on Security': 'http://krebsonsecurity.com/feed/',
        'Dark Reading': 'https://www.darkreading.com/rss_simple.asp',
        'Infosecurity Magazine': 'https://www.infosecurity-magazine.com/rss/news/',
        'Cyberscoop': 'https://www.cyberscoop.com/feed/',
        'SecurityWeek': 'https://www.securityweek.com/rss/feed',
        'CSO Online': 'https://www.csoonline.com/index.rss',
        'ZDNet Zero Day': 'https://www.zdnet.com/topic/zero-day/rss.xml',
        'Schneier on Security': 'https://www.schneier.com/blog/atom.xml'
    }

    parse_feeds(sources, db)

if __name__ == '__main__':
    run_parser()
