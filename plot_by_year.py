import matplotlib.pyplot as plt
import csv


def plot_average_sentiment(filename):
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        articles = list(reader)

    if not articles:
        print("No news articles found in CSV.")
        return

    # Dictionary to hold year and list of sentiment scores
    sentiment_by_year = {}
    for article in articles:
        year = article["Year"]
        sentiment_scores = eval(article['Sentiment List'])
        if year in sentiment_by_year:
            sentiment_by_year[year].extend(sentiment_scores)
        else:
            sentiment_by_year[year] = sentiment_scores

    # Calculate the average sentiment per year
    average_sentiment_by_year = {}
    for year, scores in sentiment_by_year.items():
        average = sum(scores) / len(scores)
        average_sentiment_by_year[year] = average

    # Sort years
    years = sorted(average_sentiment_by_year.keys())
    averages = []
    for year in years:
        averages.append(average_sentiment_by_year[year])

    # Determine bar colors based on sentiment value
    colors = []
    for avg in averages:
        if avg < 0:
            colors.append('red')
        elif avg > 0:
            colors.append('green')
        else:
            colors.append('gray')

    # Plotting
    plt.figure(figsize=(10, 5))
    bars = plt.bar(years, averages, color=colors)
    plt.title('Average Sentiment per Year', fontweight='bold', fontsize=16)
    plt.xlabel('Year')
    plt.ylabel('Average Sentiment')
    plt.legend(bars, ['Negative', 'Positive', 'Neutral'], title="Sentiment", bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.grid(True)
    plt.tight_layout()
    plt.show()


plot_average_sentiment("output.csv")
