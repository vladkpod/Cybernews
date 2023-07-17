import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

def clean_text(text):
    # Download nltk data if not already downloaded
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

    # Convert text to lowercase
    text = text.lower()

    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)

    # Tokenize text
    words = text.split()

    # Remove stopwords and lemmatize words
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words if word not in set(stopwords.words('english'))]

    # Return cleaned text
    return ' '.join(words)



def clean_data():
    client = MongoClient('localhost', 27017)
    db = client['cybersecurity_news']

    data = pd.DataFrame(list(db.articles.find()))

    data.drop_duplicates(subset=['title', 'link'], keep='first', inplace=True)

    data.dropna(inplace=True)

    keywords = ['hack', 'cyber', 'security', 'breach', 'encryption', 
                'malware', 'phishing', 'ransomware', 'virus', 'spyware']

    for article_data in data.to_dict('records'):
        if any(keyword in article_data['title'] or keyword in article_data['summary'] for keyword in keywords):
            try:
                db.articles_cleaned.insert_one(article_data)
            except DuplicateKeyError:
                # If a duplicate key error occurs, update the existing document instead
                db.articles_cleaned.replace_one({'_id': article_data['_id']}, article_data)

    return data
