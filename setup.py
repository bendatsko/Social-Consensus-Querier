import sqlite3
import argparse
from utils import Loader

def setup_database():
        connection = sqlite3.connect('news.db')
        cursor = connection.cursor()
        loader = Loader("Setting up database...").start()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER UNIQUE,
                title TEXT,
                url TEXT,
                is_searched INTEGER DEFAULT 0,
                is_summarized INTEGER DEFAULT 0
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
                comment4 TEXT,
                comment5 TEXT,
                FOREIGN KEY (article_id) REFERENCES news(article_id)
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS article_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                summary TEXT,
                FOREIGN KEY (article_id) REFERENCES news(article_id)
            );
        ''')

        connection.commit()
        connection.close()
        loader.stop()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--clear', action='store_true')
    args = parser.parse_args()
    
    if args.clear:
        connection = sqlite3.connect('news.db')
        cursor = connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS reddit_posts')
        cursor.execute('DROP TABLE IF EXISTS news')
        cursor.execute('DROP TABLE IF EXISTS article_summaries')
        print("Cleared existing tables.")
    else:
        setup_database()
