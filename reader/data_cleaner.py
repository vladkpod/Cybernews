import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from pymongo import MongoClient


# Download nltk data if not already downloaded
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)


def clean_text(text):
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


def preprocess_text(text):
    # Convert text to lowercase
    text = text.lower()

    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)

    # Tokenize text
    words = text.split()

    # Remove stopwords and lemmatize words
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words if word not in set(stopwords.words('english'))]

    # Return preprocessed text
    return ' '.join(words)


def clean_data():
    client = MongoClient('localhost', 27017)
    db = client['cybersecurity_news']

    data = pd.DataFrame(list(db.articles.find()))

    data.drop_duplicates(subset=['title', 'link'], keep='first', inplace=True)
    data.dropna(subset=['summary'], inplace=True)  # Drop documents with empty summaries

    # Remove stop word-only documents
    stop_words = set(stopwords.words('english'))
    data['summary_processed'] = data['summary'].apply(lambda x: preprocess_text(x))
    data['word_count'] = data['summary_processed'].apply(lambda x: len([word for word in x.split() if word not in stop_words]))
    data = data[data['word_count'] > 0]

    for article_data in data.to_dict('records'):
        db.articles_cleaned.update_one(
            {'title': article_data['title'], 'link': article_data['link']},
            {'$set': article_data},
            upsert=True
        )

    return data

if __name__ == '__main__':
    clean_data()
