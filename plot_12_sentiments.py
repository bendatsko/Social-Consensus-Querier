import csv
import math
import random
import textwrap
import webbrowser

import matplotlib.pyplot as plt


def clip_summary(summary, max_chars=90):
    if len(summary) > max_chars:
        return summary[:max_chars] + '...'
    return summary


def plot_selected_news_opinions(filename, sample_size=12):
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        articles = list(reader)

    if not articles:
        print("No news articles found in CSV.")
        return

    if len(articles) > sample_size:
        articles = random.sample(articles, sample_size)

    n_articles = len(articles)
    cols = 4  # Fixed number of columns
    rows = math.ceil(n_articles / cols)  # Calculate number of rows needed

    fig, axs = plt.subplots(rows, cols, figsize=(12, 2 * rows))
    axs = axs.flatten() if n_articles > 1 else [axs]

    for i, article in enumerate(articles):
        ax = axs[i]
        title = article['Title']
        year = article['Year']
        url = article['URL']
        sentiment_list = eval(article['Sentiment List'])
        summary = article['Summary']

        wrapped_title = textwrap.fill(f"{clip_summary(title)} ({year})", width=50)
        clipped_summary = clip_summary(summary)
        wrapped_summary = textwrap.fill(f"Summary: {clipped_summary}", width=50)

        sentiment_scores = [float(score) for score in sentiment_list]
        categories = ['Negative', 'Neutral', 'Positive']
        category_counts = [0, 0, 0]
        for score in sentiment_scores:
            if score < 0:
                category_counts[0] += 1
            elif score == 0:
                category_counts[1] += 1
            else:
                category_counts[2] += 1

        ax.bar(categories, category_counts, color=['red', 'gray', 'green'])
        ax.set_title(wrapped_title, fontsize=8, color='blue', picker=True)
        ax.text(0.5, -0.30, wrapped_summary, transform=ax.transAxes, fontsize=8, ha='center', va='top', wrap=True)
        ax.set_xlabel('Sentiment Category', fontsize=8)
        ax.set_ylabel('Number of Comments', fontsize=8)

        def on_pick(event):
            artist = event.artist
            if isinstance(artist, plt.Text):
                webbrowser.open(url)

        fig.canvas.mpl_connect('pick_event', on_pick)

    for ax in axs[n_articles:]:
        ax.axis('off')

    plt.subplots_adjust(left=0.052, right=0.952, top=0.887, bottom=0.11, wspace=0.435, hspace=0.887)
    fig.suptitle('Sentiment Analysis for 12 New York Times Articles Based on Reddit Comments', fontsize=16,
                 fontweight='bold')
    plt.show()


plot_selected_news_opinions("output.csv")
