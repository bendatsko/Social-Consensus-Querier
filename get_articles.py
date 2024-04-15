"""
get_articles.py
---------------
This script fetches article titles from New York Times API and stores them in the news table in the news database.

Features:
- Fetches articles from a particular year based on the existing number of articles in the database.

Usage:
- Run script directly to fetch and store articles: `python get_articles.py`
"""

import os
import sqlite3
import time
import requests
from utils import Loader
from dotenv import load_dotenv

load_dotenv()

nyt_key = os.getenv("NYT_API_KEY")


def fetch_titles_from_nyt(num_articles=25, db="news.db"):
    loader = Loader(f"Getting {num_articles} articles from New York Times...").start()

    # Establish connection to the database
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    # Get the current count of articles in the news table
    cursor.execute("""SELECT COUNT(*) FROM news""")
    numRows = cursor.fetchone()[0]

    # Determine the year for the NYT API to fetch article from based on the number of
    # existing articles (to avoid duplicate titles)
    if 0 <= numRows < 25:
        year = 2019
    elif 25 <= numRows < 50:
        year = 2020
    elif 50 <= numRows < 75:
        year = 2021
    elif 75 <= numRows < 100:
        year = 2022
    else:
        year = 2022

    # Construct query
    base_url = f"https://api.nytimes.com/svc/archive/v1/{year}/1.json"
    query_params = {"api-key": nyt_key}
    response = requests.get(base_url, params=query_params)

    if response.status_code == 200:
        # Get the current news table's last element
        news_data = response.json()["response"]["docs"][:num_articles]
        cursor.execute("SELECT MAX(article_id) FROM news")
        max_id = cursor.fetchone()[0] or 0

        # actually insert the elements pulled from the api into the news db
        for story in news_data:
            max_id += 1
            cursor.execute(
                "INSERT INTO news (article_id, title, url) VALUES (?, ?, ?)",
                (max_id, story["abstract"], story["web_url"]),
            )

        loader.desc = (
            f"Saving {len(news_data)} New York Times article titles to news table..."
        )
        connection.commit()
        time.sleep(2)
        loader.stop()
    else:
        loader.stop()
        print("Failed to fetch data from New York Times API.")
    connection.close()


if __name__ == "__main__":
    fetch_titles_from_nyt()
