import matplotlib.pyplot as plt
import csv
import textwrap
import math
import webbrowser

def plot_all_news_opinions(filename):
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        articles = list(reader)

    if not articles:
        print("No news articles found in CSV.")
        return

    n_articles = len(articles)
    grid_size = int(n_articles / 25)

    fig, axs = plt.subplots(grid_size, grid_size, figsize=(16, 9))
    axs = axs.flatten()

    # loop through and aggregate the avg sentiment scores for each year
    # - store info in dictionary where keys are the year and the values are a list of scores
    year_scores_dict = {}
    for i in range(n_articles):
        article = articles[i]
        article_year = article["Year"]
        sentiment_list = eval(article['Sentiment List'])

        if article_year in year_scores_dict:
            # get sentiment scores
            sentiment_scores = [float(score) for score in sentiment_list]
            for score in sentiment_scores:
                if score < 0:
                    year_scores_dict[article_year]["Category Counts"][0] += 1
                elif score == 0:
                    year_scores_dict[article_year]["Category Counts"][1] += 1
                else:
                    year_scores_dict[article_year]["Category Counts"][2] += 1
        else:
            year_scores_dict[article_year] = {}
            # get sentiment scores
            sentiment_scores = [float(score) for score in sentiment_list]
            category_counts = [0, 0, 0]
            for score in sentiment_scores:
                if score < 0:
                    category_counts[0] += 1
                elif score == 0:
                    category_counts[1] += 1
                else:
                    category_counts[2] += 1
            year_scores_dict[article_year]["Category Counts"] = category_counts

    counter = 0
    for year, year_dict in year_scores_dict.items():
        ax = axs[counter]
        counter += 1

        wrapped_title = textwrap.fill(year, width=40)

        categories = ['Negative', 'Neutral', 'Positive']
        ax.bar(categories, year_dict["Category Counts"], color=['red', 'grey', 'green'])
        ax.set_title(wrapped_title, fontsize=10, color='blue', picker=True)
        ax.set_xlabel('Sentiment Category', fontsize=8)
        ax.set_ylabel('Number of Comments', fontsize=8)

    # for i in range(n_articles):
    #     ax = axs[i]
    #     article = articles[i]

    #     title = article['Title']
    #     url = article['URL']
    #     sentiment_list = eval(article['Sentiment List'])
    #     summary = article['Summary']

    #     wrapped_title = textwrap.fill(title, width=40)
    #     wrapped_summary = textwrap.fill(summary, width=40)

    #     sentiment_scores = [float(score) for score in sentiment_list]

    #     categories = ['Negative', 'Neutral', 'Positive']
    #     category_counts = [0, 0, 0]
    #     for score in sentiment_scores:
    #         if score < 0:
    #             category_counts[0] += 1
    #         elif score == 0:
    #             category_counts[1] += 1
    #         else:
    #             category_counts[2] += 1

    #     ax.bar(categories, category_counts, color=['red', 'grey', 'green'])
    #     ax.set_title(wrapped_title, fontsize=10, color='blue', picker=True)

    #     # Separate text objects for label and summary
    #     # ax.text(0.5, -0.0, "Public Sentiment Summarized:", transform=ax.transAxes, fontsize=8, ha='center', va='top', weight='bold')
    #     ax.text(0.5, -0.9, "Summarized Sentiment: " + wrapped_summary, transform=ax.transAxes, fontsize=8, ha='center', va='top', wrap=True)

    #     ax.set_xlabel('Sentiment Category', fontsize=8)
    #     ax.set_ylabel('Number of Comments', fontsize=8)

    #     def on_pick(event):
    #         artist = event.artist
    #         if isinstance(artist, plt.Text):
    #             webbrowser.open(url)

    #     fig.canvas.mpl_connect('pick_event', on_pick)

    # Hide unused axes
    for ax in axs[n_articles:]:
        ax.axis('off')

    plt.subplots_adjust(wspace=0.3, hspace=0.6, bottom=0.2)
    plt.tight_layout()
    plt.show()

plot_all_news_opinions("output.csv")