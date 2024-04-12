import sqlite3
import requests
from dotenv import load_dotenv
import os
import praw
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
import csv
from utils import Loader
from utils import color
from azure.ai.textanalytics import TextAnalyticsClient, ExtractiveSummaryAction
from azure.core.credentials import AzureKeyCredential

load_dotenv()
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe('spacytextblob')
reddit_client = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'), client_secret=os.getenv('REDDIT_CLIENT_SECRET'), user_agent='script by /u/test')
nyt_key = os.getenv('NYT_API_KEY')

def authenticate_azure():
    ta_credential = AzureKeyCredential(os.environ.get('AZURE_LANGUAGE_KEY'))
    text_analytics_client = TextAnalyticsClient(
            endpoint=os.environ.get('AZURE_LANGUAGE_ENDPOINT'),
            credential=ta_credential)
    return text_analytics_client
azure_client = authenticate_azure()


def main():
    title = color.BOLD + """
    -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

                           Current Event Opinion Aggregator
                                 SI 206 Final Project

    -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n""" + color.END
    print(title)
    num_articles = 10

    setup_database()
    fetch_titles_from_nyt(nyt_key, num_articles)
    search_reddit_for_articles(reddit_client)
    summarize_comments(azure_client)
    dump_to_csv("output.csv")


def setup_database():
    loader = Loader("Setting up database...").start()
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()

    cursor.execute('DROP TABLE IF EXISTS reddit_posts')

    cursor.execute('''
         CREATE TABLE IF NOT EXISTS news (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             article_id INTEGER UNIQUE,
             title TEXT,
             url TEXT,
             summary TEXT,
             processed INTEGER DEFAULT 0
         );
     ''')
    cursor.execute('''
         CREATE TABLE IF NOT EXISTS reddit_posts (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             article_id INTEGER,
             reddit_title TEXT,
             reddit_url TEXT,
             comment1 TEXT,
             comment2 TEXT,
             comment3 TEXT,
             FOREIGN KEY (article_id) REFERENCES news(article_id)
         );
     ''')

    connection.commit()
    connection.close()
    loader.stop()

def fetch_titles_from_nyt(nyt_key, num_articles):
    loader = Loader("Fetching news from New York Times...").start()
    base_url = "https://api.nytimes.com/svc/topstories/v2/home.json"
    query_params = {"api-key": nyt_key}
    response = requests.get(base_url, params=query_params)
    if response.status_code == 200:
        news_data = response.json()['results'][:num_articles]

        connection = sqlite3.connect('news.db')
        cursor = connection.cursor()
        cursor.execute('DELETE FROM news') # if it's a new day, then clear the news database

        cursor.execute('SELECT MAX(article_id) FROM news')
        max_id = cursor.fetchone()[0]
        if max_id is None:
            max_id = 0

        for story in news_data:
            max_id += 1
            cursor.execute('INSERT INTO news (article_id, title, url) VALUES (?, ?, ?)', (max_id, story['title'], story['url']))

        connection.commit()
        connection.close()

        loader.stop()
        print(f"vSaved {len(news_data)} New York Times article titles to news database.")

def search_reddit_for_articles(reddit_client):
    loader = Loader("Searching for articles on Reddit...").start()
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()

    cursor.execute('SELECT article_id, title FROM news')
    articles = cursor.fetchall()

    for article in articles:
        article_id, title = article
        print(f"\nSearching Reddit for: {title}")
        search_results = reddit_client.subreddit('all').search(title, limit=10)

        for submission in search_results:
            print(f"\nFound Reddit post: {submission.title} URL: {submission.url}")
            submission.comments.replace_more(limit=0)  # Load the top comments; limit=0 means no "MoreComments" objects
            top_comments = submission.comments.list()[:3]
            comments_text = [comment.body for comment in top_comments]

            while len(comments_text) < 3:
                comments_text.append("")

            cursor.execute('''
                INSERT INTO reddit_posts (article_id, reddit_title, reddit_url, comment1, comment2, comment3)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (article_id, submission.title, submission.url, *comments_text[:3]))

    connection.commit()
    connection.close()
    loader.stop()
    print("\nCompleted searching Reddit for news articles.")

def summarize_comments(client):
    loader = Loader("Summarizing Reddit comments...").start()
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()

    # Fetch the article_id and associated comments
    cursor.execute('''
        SELECT r.article_id, r.comment1, r.comment2, r.comment3
        FROM reddit_posts r
        JOIN news n ON r.article_id = n.article_id
    ''')
    rows = cursor.fetchall()

    for row in rows:
        article_id = row[0]
        comments = row[1:4]  # Get comment1, comment2, and comment3
        comments_text = " ".join([comment for comment in comments if comment])  # Concatenate non-empty comments

        if comments_text:
            # Perform summarization using the Azure client
            document = [comments_text]
            poller = client.begin_analyze_actions(
                document,
                actions=[ExtractiveSummaryAction(max_sentence_count=1)],
            )
            document_results = poller.result()

            # Process summarization results
            for result in document_results:
                for summary_result in result:  # Iterate through the summaries
                    if summary_result.is_error:
                        print(f"\nError: {summary_result.code} - {summary_result.message}")
                    else:
                        summary = "".join([sentence.text for sentence in summary_result.sentences])
                        # Update summary column in the news table for the corresponding article
                        cursor.execute('UPDATE news SET summary = ? WHERE article_id = ?', (summary, article_id))

    connection.commit()
    connection.close()
    loader.stop()
    print("\nCompleted summarizing Reddit comments.")

def analyze_comment_sentiment(article_id):
    def analyze_comment_sentiment(comment):
        doc = nlp(comment)
        return doc._.blob.polarity

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
                sentiment = analyze_comment_sentiment(comment)
                # print(f"Article ID {article_id}, Comment: {comment[:50]}... Sentiment: {sentiment}")
                sentiments.append(sentiment)

    connection.close()
    # print(f"Article ID {article_id} Sentiment List: {sentiments}")
    return sentiments

def dump_to_csv(filename='output.csv'):
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()

    cursor.execute('''
        SELECT n.article_id, n.title, n.url, n.summary
        FROM news n
    ''')
    articles = cursor.fetchall()

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Article ID', 'Title', 'Sentiment List', 'URL', 'Summary'])

        for article in articles:
            article_id, title, url, summary = article

            sentiments = analyze_comment_sentiment(article_id)
            if not sentiments:
                print(f"\nEmpty sentiment list for article_id {article_id}")

            sentiments_sorted = sorted(sentiments)  # Sorting the sentiment values
            writer.writerow([article_id, title, sentiments_sorted, url, summary])

    connection.close()
    print(f"Data exported to {filename}.")


if __name__ == "__main__":
    main()