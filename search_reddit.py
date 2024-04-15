"""
search_reddit.py
----------------
This program searches Reddit for discussions related to articles fetched from the New York Times.

Features:
- Searches for the top relevant 5 Reddit posts and their 5 most relevant comments for each article.
- Updates the database with Reddit titles, URLs, and top comments.
- Mark articles as `searched` in the database (news table) once they are processed.

Usage:
- Running script directly: `python search_reddit.py`
"""

import sqlite3
import os
import praw
import spacy
from utils import Loader
from dotenv import load_dotenv

load_dotenv()

nlp = spacy.load("en_core_web_sm")

def clean_comment(text):
    """Remove newlines and excessive whitespace from comments."""
    return " ".join(text.strip().split())


def extract_keywords(title):
    """Extracts keywords from the given title using SpaCy."""
    doc = nlp(title)
    keywords = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]]
    return " ".join(keywords)


def truncate_description(title, max_length=100):
    """Truncate the title if it exceeds the maximum length allowed in the description"""
    if len(title) > max_length:
        return title[: max_length - 3] + "..."
    return title


def search_reddit_for_articles(reddit_client):
    loader = Loader("Searching Reddit...").start()

    connection = sqlite3.connect("news.db")
    cursor = connection.cursor()

    # Select the next 5 unprocessed articles
    cursor.execute("SELECT article_id, title FROM news WHERE is_searched = 0 LIMIT 5")
    articles = cursor.fetchall()

    if articles:
        for article in articles:
            article_id, title = article
            truncated_title = truncate_description(title)
            keywords = extract_keywords(title)
            loader.desc = f"Searching for Reddit posts and opinions related to article {article_id}: '{truncated_title}'"
            search_results = reddit_client.subreddit("all").search(keywords, limit=5)

            for submission in search_results:
                submission.comments.replace_more(limit=0)
                top_comments = submission.comments.list()[:5]
                comments_text = [
                    clean_comment(comment.body) for comment in top_comments
                ] + [""] * (5 - len(top_comments))

                cursor.execute(
                    """
                    INSERT INTO reddit_posts (article_id, reddit_title, reddit_url, comment1, comment2, comment3, comment4, comment5)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (article_id, submission.title, submission.url, *comments_text),
                )

            cursor.execute(
                "UPDATE news SET is_searched = 1 WHERE article_id = ?", (article_id,)
            )

    else:
        print("\nNo unsearched articles left.")

    connection.commit()
    connection.close()
    loader.desc = f"Search for 5 New York Times articles on Reddit and getting 5 relevant comments (storing 25 elements in reddit_posts table)..."
    loader.stop()


if __name__ == "__main__":
    reddit_client = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent="script by /u/si206",
    )
    search_reddit_for_articles(reddit_client)
