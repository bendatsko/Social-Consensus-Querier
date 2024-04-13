import sqlite3
import os
import praw
import spacy
from utils import Loader
from dotenv import load_dotenv

load_dotenv()

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

def clean_comment(text):
    """Remove newlines and excessive whitespace from comments."""
    return ' '.join(text.strip().split())

def extract_keywords(title):
    """Extracts keywords from the given title using SpaCy."""
    doc = nlp(title)
    keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
    return " ".join(keywords)

def search_reddit_for_articles(reddit_client):
    loader = Loader("Searching for articles on Reddit...").start()
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()

    # Select the next 5 unprocessed articles
    cursor.execute('SELECT article_id, title FROM news WHERE is_searched = 0 LIMIT 5')
    articles = cursor.fetchall()

    if articles:
        for article in articles:
            article_id, title = article
            keywords = extract_keywords(title)
            print(f"\n{'-'*50}\nSearching Reddit for keywords: '{keywords}' from article titled: '{title}'\n{'-'*50}")

            search_results = reddit_client.subreddit('all').search(keywords, limit=5)
            
            for submission in search_results:
                print(f"\nFound Reddit post: {submission.title}\nURL: {submission.url}")
                
                submission.comments.replace_more(limit=0)
                top_comments = submission.comments.list()[:5]
                comments_text = [clean_comment(comment.body) for comment in top_comments] + [''] * (5 - len(top_comments))
                
                cursor.execute('''
                    INSERT INTO reddit_posts (article_id, reddit_title, reddit_url, comment1, comment2, comment3, comment4, comment5)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                    (article_id, submission.title, submission.url, *comments_text))

                print(f"\nTop 5 comments for '{submission.title}':")
                for idx, comment in enumerate(comments_text, 1):
                    print(f"\tComment {idx}: {comment}")

            cursor.execute('UPDATE news SET is_searched = 1 WHERE article_id = ?', (article_id,))

    else:
        print("\nNo unsearched articles left.")

    connection.commit()
    connection.close()
    loader.stop()
    print("\nCompleted searching Reddit for news articles.")

if __name__ == "__main__":
    reddit_client = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent='script by /u/test')
    for i in range(0,5):
        search_reddit_for_articles(reddit_client)
