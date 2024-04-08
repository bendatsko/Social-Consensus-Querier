import sqlite3
import requests
from dotenv import load_dotenv
import os
import praw
import matplotlib.pyplot as plt
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

load_dotenv()

# Load spaCy model
nlp = spacy.load("en_core_web_sm")
# Add spacytextblob to the pipeline
nlp.add_pipe('spacytextblob')

# Initialize Reddit client
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent='script by /u/electrobleach'
)

def analyze_comment_sentiment(comment):
    doc = nlp(comment)
    return doc._.blob.polarity  # Access sentiment polarity
def search_reddit_for_opinions(query, subreddit='AskReddit', limit=10):
    results = []
    for submission in reddit.subreddit(subreddit).search(query, limit=limit):
        results.append({
            'title': submission.title,
            'url': submission.url,
            'reddit_url': f"https://www.reddit.com{submission.permalink}"
        })

    return results



def summarize_opinions(comments, sentiments):
    # Pair each comment with its sentiment score
    comment_sentiment_pairs = zip(comments, sentiments)

    # Sort the comments by sentiment score, focusing on the most extreme values
    sorted_pairs = sorted(comment_sentiment_pairs, key=lambda x: abs(x[1]), reverse=True)

    # Select the top comments based on sentiment extremity
    top_comments = [pair[0] for pair in sorted_pairs[:3]]

    return top_comments





def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]
    return keywords



def setup_database():
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



def categorize_sentiment(sentiment):
    if sentiment > 0.1:
        return 'Positive'
    elif sentiment < -0.1:
        return 'Negative'
    else:
        return 'Neutral'


def save_opinions_to_database(reddit_post_id, top_opinions, sentiments):
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()
    for opinion, sentiment in zip(top_opinions, sentiments):
        category = categorize_sentiment(sentiment)
        cursor.execute('''
            INSERT INTO opinions (reddit_post_id, opinion_text, sentiment, opinion_category) 
            VALUES (?, ?, ?, ?)
        ''', (reddit_post_id, opinion, sentiment, category))
    connection.commit()
    connection.close()
def save_news_to_database(news_data):
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()
    for story in news_data:
        cursor.execute('INSERT INTO news (title, url) VALUES (?, ?)', (story['title'], story['url']))
    connection.commit()
    connection.close()


def fetch_comments_from_post(post_url, limit=10):
    submission = reddit.submission(url=post_url)
    submission.comment_sort = 'top'
    submission.comments.replace_more(limit=0)  # Load all top-level comments
    comments = []

    for comment in submission.comments.list()[:limit]:
        comments.append(comment.body)

    return comments

def save_comments_to_database(reddit_post_id, comments):
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()
    for comment in comments:
        cursor.execute('''
            INSERT INTO comments (reddit_post_id, comment_text) 
            VALUES (?, ?)
        ''', (reddit_post_id, comment))
    connection.commit()
    connection.close()

def save_reddit_posts_to_database(news_id, reddit_posts):
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()
    post_ids = []
    for post in reddit_posts:
        cursor.execute('''
            INSERT INTO reddit_posts (news_id, reddit_title, reddit_url) 
            VALUES (?, ?, ?)
        ''', (news_id, post['title'], post['reddit_url']))
        post_ids.append(cursor.lastrowid)
    connection.commit()
    connection.close()
    return post_ids

def get_news_id(title):
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM news WHERE title = ?', (title,))
    result = cursor.fetchone()
    connection.close()
    return result[0] if result else None


def get_trending_news(api_key):
    base_url = "https://api.nytimes.com/svc/topstories/v2/home.json"
    query_params = {"api-key": api_key}
    response = requests.get(base_url, params=query_params)
    if response.status_code == 200:
        news_data = response.json()['results']
        save_news_to_database(news_data)
        print(f"{len(news_data)} news stories have been saved to the database.")
        return news_data  # Return the fetched news data
    else:
        print("Failed to retrieve news stories: HTTP", response.status_code)
        return []  # Return an empty list if the API call fails


def process_reddit_posts(news_id, reddit_posts):
    post_ids = save_reddit_posts_to_database(news_id, reddit_posts)
    for post_id, post in zip(post_ids, reddit_posts):
        comments = fetch_comments_from_post(post['reddit_url'], limit=100)
        comments = [comment for comment in comments if len(comment.split()) > 5]
        save_comments_to_database(post_id, comments)

        if comments:
            sentiments = [analyze_comment_sentiment(comment) for comment in comments]
            top_opinions = summarize_opinions(comments, sentiments)
            save_opinions_to_database(post_id, top_opinions, sentiments[:len(top_opinions)])

            print(f"\nTop opinions for post '{post['title']}':")
            for opinion in top_opinions:
                print(f"- {opinion}")
            print("\n")
        else:
            print(f"\nNo comments fetched for post '{post['title']}'")


def process_news_articles(api_key):
    news_data = get_trending_news(api_key)
    for news_article in news_data:
        title = news_article['title']
        news_id = get_news_id(title)
        if news_id:
            keywords = extract_keywords(title)
            search_query = " ".join(keywords)
            reddit_posts = search_reddit_for_opinions(search_query, 'all', 5)
            save_reddit_posts_to_database(news_id, reddit_posts)
            process_reddit_posts(news_id, reddit_posts)
        else:
            print(f"News ID not found for title: {title}")


def get_reddit_post_id(reddit_url):
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM reddit_posts WHERE reddit_url = ?', (reddit_url,))
    result = cursor.fetchone()
    connection.close()
    return result[0] if result else None




if __name__ == "__main__":
    api_key = os.getenv('NYT_API_KEY')
    setup_database()
    process_news_articles(api_key)

