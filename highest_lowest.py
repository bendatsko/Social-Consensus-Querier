import matplotlib.pyplot as plt
import csv
import textwrap
import math
import webbrowser
from statistics import mean
import matplotlib as mpl

def highest_lowest(filename):
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        articles = list(reader)

    if not articles:
        print("No news articles found in CSV.")
        return

    n_articles = len(articles)
    
    year_score_dict = {}
    for i in range(n_articles):
        article = articles[i]
        article_year = article["Year"]
        article_title = article["Title"]
        sentiment_list = eval(article['Sentiment List'])
        sentiment_scores = [float(score) for score in sentiment_list]
        
        if sentiment_scores:
            max_score = max(sentiment_scores)
            min_score = min(sentiment_scores)
            difference = abs(max_score - min_score)

            # make sure we only keep the max difference for a given year
            if article_year not in year_score_dict or year_score_dict[article_year][1] < difference:
                year_score_dict[article_year] = (article_title, difference)
    
    # fetch years, fetch differences, fetch titles
    years = sorted(year_score_dict.keys())
    differences = [year_score_dict[year][1] for year in years]
    titles = [year_score_dict[year][0] for year in years]
    
    # do plot stuff
    # Plotting
    plt.figure(figsize=(10, 5))
    plt.bar(years, differences)
    plt.xlabel('Year')
    plt.ylabel('Max Sentiment Difference')
    plt.title('Most Controversial News Article Per Year')
    
    for i in range(len(years)):
        plt.text(i, differences[i], textwrap.shorten(titles[i], width=30), ha='center', va='bottom')
    
    plt.show()


 


    
highest_lowest("output.csv")



        
        


    
