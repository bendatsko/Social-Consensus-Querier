import math
import matplotlib.pyplot as plt
import textwrap
import sqlite3

def plot_all_news_opinions():
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()
    cursor.execute('SELECT id, title FROM news')
    news_articles = cursor.fetchall()

    if not news_articles:
        print("No news articles found.")
        return


    # Calculate grid size for subplots
    n_articles = len(news_articles)
    grid_size = math.ceil(math.sqrt(n_articles))  # Square root to get even grid

    fig, axs = plt.subplots(grid_size, grid_size, figsize=(16, 9))
    axs = axs.flatten()  # Flatten array to make it easier to iterate

    for ax, (news_id, title) in zip(axs, news_articles):
        wrapped_title = textwrap.fill(title, width=30)  # Wrap title if it's too long

        cursor.execute('''
            SELECT opinion_category, COUNT(*) as count
            FROM opinions
            WHERE reddit_post_id IN (
                SELECT id FROM reddit_posts WHERE news_id = ?)
            GROUP BY opinion_category
        ''', (news_id,))
        data = cursor.fetchall()

        if data:
            categories = [row[0] for row in data]
            counts = [row[1] for row in data]

            ax.bar(categories, counts)
            ax.set_title(wrapped_title, fontsize=10)  # smaller font size for title
            ax.set_xlabel('Opinion Category', fontsize=8)  # smaller font size for labels
            ax.set_ylabel('Number of Comments', fontsize=8)  # smaller font size for labels
        else:
            ax.set_title(wrapped_title, fontsize=10)  # smaller font size for title
            ax.axis('off')  # Hide axis for empty plots


    for ax in axs[len(news_articles):]:
        ax.axis('off')

    plt.subplots_adjust(wspace=0.3, hspace=0.5)  # space between plots
    plt.tight_layout()
    plt.show()

    connection.close()



plot_all_news_opinions()