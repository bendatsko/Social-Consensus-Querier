import sqlite3
import requests
from dotenv import load_dotenv
import os
from utils import Loader
load_dotenv()

def fetch_titles_from_nyt(nyt_key, num_articles, db):
    loader = Loader("Fetching news from New York Times...").start()

    # Establish connection to the database and get the current count of articles
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute('''SELECT COUNT(*) FROM news''')
    numRows = cursor.fetchone()[0]

    # Determine the appropriate year for the NYT API based on the number of existing articles
    if 0 <= numRows < 25:
        year = 2015
    elif 25 <= numRows < 50:
        year = 2016
    elif 50 <= numRows < 75:
        year = 2017
    elif 75 <= numRows < 100:
        year = 2018
    else:
        year = 2019

    base_url = f"https://api.nytimes.com/svc/archive/v1/{year}/1.json"
    query_params = {"api-key": nyt_key}
    response = requests.get(base_url, params=query_params)

    if response.status_code == 200:
        news_data = response.json()["response"]['docs'][:num_articles]
        cursor.execute('SELECT MAX(article_id) FROM news')
        max_id = cursor.fetchone()[0] or 0

        for story in news_data:
            max_id += 1
            cursor.execute('INSERT INTO news (article_id, title, url) VALUES (?, ?, ?)', (max_id, story['abstract'], story['web_url']))

        connection.commit()
        loader.stop()
        print(f"Saved {len(news_data)} New York Times article titles to news database.")
    else:
        loader.stop()
        print("Failed to fetch data from New York Times API.")

    connection.close()

if __name__ == "__main__":
    nyt_key = os.getenv('NYT_API_KEY')
    fetch_titles_from_nyt(nyt_key, 25, 'news.db')
