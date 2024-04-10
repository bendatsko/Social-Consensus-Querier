import sqlite3
import requests
from dotenv import load_dotenv
import os
import praw
import matplotlib.pyplot as plt
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from llamaapi import LlamaAPI
import csv
from Loader import Loader
from time import sleep

load_dotenv()

# Initialize Llama API
llama_api_key = os.getenv('LLAMA_API_KEY')
llama = LlamaAPI(llama_api_key)

# Initialize Reddit API
reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'), client_secret=os.getenv('REDDIT_CLIENT_SECRET'), user_agent='script by /u/electrobleach')
news_data = []

# Load in NLP with polarity from spacy
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('spacytextblob')


# Helper functions
def get_reddit_post_id(reddit_url):
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM reddit_posts WHERE reddit_url = ?', (reddit_url,))
    result = cursor.fetchone()
    connection.close()
    return result[0] if result else None

def get_news_id(title):
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM news WHERE title = ?', (title,))
    result = cursor.fetchone()
    connection.close()
    return result[0] if result else None

def get_summary(text):
    request_json = {
        "messages": [
            {"role": "user", "content": f"Summarize this text concisely IN LESS than 10 words: {text}"}
        ],
        "stream": False,
    }
    response = llama.run(request_json)
    response_json = response.json()

    if 'choices' in response_json and len(response_json['choices']) > 0:
        content = response_json['choices'][0].get('message', {}).get('content')
        return content.strip()
    return "Summary not available"

def analyze_comment_sentiment(comment):
    doc = nlp(comment)
    return doc._.blob.polarity

def get_sentiment_category(sentiment_score):
    if sentiment_score > 0.1:
        return 'Positive'
    elif sentiment_score < -0.1:
        return 'Negative'
    else:
        return 'Neutral'
    
def summarize_comments(comments):
    combined_text = " ".join(comments)
    return get_summary(combined_text)

def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]
    return keywords

def export_to_csv(data, filename='output.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Summary', 'Frequency'])
        for summary, frequency in data.items():
            writer.writerow([summary, frequency])

def is_relevant_comment(comment):
    irrelevant_phrases = [
        "Please reply to this comment",
        "your post will be removed",
        "bot",
        "hello",
        "hi",
        "I'm here to help"
    ]
    return not any(phrase in comment.lower() for phrase in irrelevant_phrases) and len(comment.split()) > 10


# Actual implementation
def setup_database():
    loader = Loader("Setting up database...").start()
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()
    cursor.execute('DROP TABLE IF EXISTS opinions;')
    cursor.execute('DROP TABLE IF EXISTS reddit_posts;')
    cursor.execute('DROP TABLE IF EXISTS news;')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY,
            title TEXT,
            url TEXT,
            processed INTEGER DEFAULT 0
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reddit_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_id INTEGER,
            reddit_title TEXT,
            reddit_url TEXT,
            FOREIGN KEY (news_id) REFERENCES news(id)
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reddit_post_id INTEGER,
            comment_text TEXT,
            FOREIGN KEY (reddit_post_id) REFERENCES reddit_posts(id)
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opinions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reddit_post_id INTEGER,
            opinion_text TEXT,
            sentiment FLOAT,
            FOREIGN KEY (reddit_post_id) REFERENCES reddit_posts(id)
        );
    ''')
    cursor.execute('''
        ALTER TABLE opinions
        ADD COLUMN opinion_category TEXT
    ''')
    connection.commit()
    connection.close()
    loader.stop()

def process_reddit_posts(news_id, reddit_posts):
    for post in reddit_posts:
        submission = reddit.submission(url=post['reddit_url'])
        submission.comment_sort = 'top'
        submission.comments.replace_more(limit=0)  # Load all top-level comments
        comments = []
        for comment in submission.comments.list()[:100]:
            comments.append(comment.body)

        substantive_comments = [comment for comment in comments if is_relevant_comment(comment)]
        if not substantive_comments:
            continue

        sentiment_scores = [analyze_comment_sentiment(comment) for comment in substantive_comments]

        # Group comments by sentiment
        sentiment_groups = {'Positive': [], 'Negative': [], 'Neutral': []}
        for comment, score in zip(substantive_comments, sentiment_scores):
            category = get_sentiment_category(score)
            sentiment_groups[category].append(comment)

        # Find the most common sentiment
        sentiment_count = {category: len(group) for category, group in sentiment_groups.items()}
        most_common_sentiment = max(sentiment_count, key=sentiment_count.get)
        most_common_comments = sentiment_groups[most_common_sentiment]
        if most_common_comments:
            summary = summarize_comments(most_common_comments)
            return most_common_sentiment, sentiment_count[most_common_sentiment], summary

def get_trending_news(api_key):
    loader = Loader("Fetching news from New York Times...").start()
    base_url = "https://api.nytimes.com/svc/topstories/v2/home.json"
    query_params = {"api-key": api_key}
    response = requests.get(base_url, params=query_params)
    if response.status_code == 200:
        news_data = response.json()['results']

        connection = sqlite3.connect('news.db')
        cursor = connection.cursor()
        for story in news_data:
            cursor.execute('INSERT INTO news (title, url) VALUES (?, ?)', (story['title'], story['url']))
        connection.commit()
        connection.close()
        loader.stop()
        print(f"Saved {len(news_data)} New York Times article titles to news database.")
        return news_data
    else:
        print(f"Failed to retrieve news stories: HTTP {response.status_code}")
        exit(1)

def process_news_articles():
    for news_article in news_data:
        print("\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        loader = Loader("Fetching article news id...").start()
        title = news_article['title']
        news_id = get_news_id(title)
        if news_id:
            keywords = extract_keywords(title)
            search_query = " ".join(keywords)
            reddit_posts = []
            loader.desc = f"Fetching Reddit posts relevant to news id {news_id}..."
            for submission in reddit.subreddit('AskReddit').search(search_query, limit=10):
                reddit_posts.append({
                    'title': submission.title,
                    'url': submission.url,
                    'reddit_url': f"https://www.reddit.com{submission.permalink}"
                })
            
            reddit_tuple = process_reddit_posts(news_id, reddit_posts)
            most_common_sentiment = reddit_tuple[0]
            most_common_sentiment_count = reddit_tuple[1]
            sentiment_consensus = reddit_tuple[2]
            loader.stop()
            
            print(f"[news_id: {news_id}]: {title}")
            print(f"Most popular sentiment: {most_common_sentiment} with {most_common_sentiment_count} occurrences")
            print(f"Popular sentiment consensus: {sentiment_consensus}")
        else:
            loader.stop()
            print(f"News ID not found for title: {title}")



if __name__ == "__main__":
    title = """
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    
   Current Event Opinion Aggregator
         SI 206 Final Project

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-="""
    print(title)
    setup_database()
    news_data = get_trending_news(os.getenv('NYT_API_KEY'))
    process_news_articles()


print("\nFinished gathering opinion data.")
