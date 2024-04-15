import csv
import sqlite3

import spacy
from dotenv import load_dotenv

from utils import Loader

load_dotenv()

loader = Loader("Parsing tables...")


def analyze_comment_sentiment(article_id):
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe('spacytextblob')
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT comment1, comment2, comment3 FROM reddit_posts WHERE article_id = ?
    ''', (article_id,))
    rows = cursor.fetchall()

    sentiments = []
    for row in rows:
        for comment in row:
            if comment:  # Ensure comment is not None or empty
                doc = nlp(comment)
                sentiment = doc._.blob.polarity
                sentiments.append(sentiment)

    connection.close()
    return sentiments


def get_year(numRows):
    if 0 <= numRows < 25:
        return 2015
    elif 25 <= numRows < 50:
        return 2016
    elif 50 <= numRows < 75:
        return 2017
    elif 75 <= numRows < 100:
        return 2018
    else:
        return 2019


def dump_to_csv(filename='output.csv'):
    loader.start()
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()

    cursor.execute('''
        SELECT n.article_id, n.title, n.url, s.summary
        FROM news n
        LEFT JOIN article_summaries s ON n.article_id = s.article_id
    ''')
    articles = cursor.fetchall()

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Article ID', 'Title', 'Year', 'Sentiment List', 'URL', 'Summary'])

        for i, article in enumerate(articles):
            article_id, title, url, summary = article
            loader.desc = f"Preparing export data for article {article_id}..."

            sentiments = analyze_comment_sentiment(article_id)
            year = get_year(i)  # Determine the year based on row number

            writer.writerow([article_id, title, year, sentiments, url, summary])

    connection.close()
    loader.desc = f"Data dump to {filename}..."
    loader.stop()


if __name__ == "__main__":
    dump_to_csv()
