"""
get_summaries.py
----------------
This script generates summaries for articles based on their related Reddit discussions using Azure's Text Analytics API.

Features:
- Summarizes discussions and the article content and updates `article_summaries` database.
- Marks articles as summarized in the database (news table) once processed.

Usage:
- Run script directly to summarize content and update database: `python get_summaries.py`
"""

import os
import sqlite3
import spacy
from azure.ai.textanalytics import TextAnalyticsClient, ExtractiveSummaryAction
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from utils import Loader

load_dotenv()

def authenticate_azure():
    ta_credential = AzureKeyCredential(os.getenv("AZURE_LANGUAGE_KEY"))
    text_analytics_client = TextAnalyticsClient(
        endpoint=os.getenv("AZURE_LANGUAGE_ENDPOINT"), credential=ta_credential
    )
    return text_analytics_client


azure_client = authenticate_azure()


def is_relevant(comment, keywords):
    return any(keyword in comment.lower() for keyword in keywords)


def summarize_comments(client):
    loader = Loader("Summarizing...").start()
    connection = sqlite3.connect("news.db")
    cursor = connection.cursor()

    nlp = spacy.load("en_core_web_sm")

    cursor.execute(
        """
        SELECT DISTINCT n.article_id, n.title
        FROM news n
        WHERE n.is_summarized = 0
        LIMIT 25
    """
    )
    articles = cursor.fetchall()

    for article_id, ny_times_title in articles:
        loader.desc = f"Summarizing article {article_id}..."
        cursor.execute(
            """
            SELECT r.reddit_title, r.comment1, r.comment2, r.comment3, r.comment4, r.comment5
            FROM reddit_posts r
            WHERE r.article_id = ?
        """,
            (article_id,),
        )
        reddit_posts = cursor.fetchall()

        doc = nlp(ny_times_title)
        keywords = [
            token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"]
        ]
        text_components = [ny_times_title]

        for reddit_post in reddit_posts:
            reddit_title = reddit_post[0]
            comments = reddit_post[1:]
            relevant_texts = [reddit_title] + [
                comment
                for comment in comments
                if comment and is_relevant(comment, keywords)
            ]
            text_components.extend(relevant_texts)

        full_text = " ".join([str(text) for text in text_components])

        if full_text:
            document = [full_text]
            poller = client.begin_analyze_actions(
                document, actions=[ExtractiveSummaryAction(max_sentence_count=1)]
            )
            document_results = poller.result()

            for result in document_results:
                for summary_result in result:
                    if summary_result.is_error:
                        print(
                            f"Error: {summary_result.code} - {summary_result.message}"
                        )
                    else:
                        summary = "".join(
                            sentence.text for sentence in summary_result.sentences
                        )
                        cursor.execute(
                            "INSERT INTO article_summaries (article_id, summary) VALUES (?, ?)",
                            (article_id, summary),
                        )
                        cursor.execute(
                            "UPDATE news SET is_summarized = 1 WHERE article_id = ?",
                            (article_id,),
                        )
    if not articles:
        print("\nNo unprocessed articles left.")

    connection.commit()
    connection.close()
    loader.desc = "Summarizing next 25 un-summarized articles..."
    loader.stop()


if __name__ == "__main__":
    summarize_comments(azure_client)
