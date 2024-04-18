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
    grid_size = 2

   

    # - store info in dictionary where keys are the year and the values are a list of scores

    year_score_dict ={}
    title_scores_dict = {}
    key_highdif_dict = {}
    title_list= []
    for i in range(n_articles):
        article = articles[i]
        article_year = article["Year"]
        
        article_title = article['Title']
        sentiment_list = eval(article['Sentiment List'])
        sentiment_scores = [float(score) for score in sentiment_list]
        if len(sentiment_scores) > 0:
            max_score = max(sentiment_scores)
            min_score = min(sentiment_scores)

            difference = abs(max_score-min_score)
        
            title_scores_dict[article_title] = difference

        year_score_dict[article_year] = title_scores_dict

    for year in year_score_dict:
        highest_difference = float('-inf')
        for title, score in year_score_dict[year].items():
            if score > highest_difference:
                highest_difference = score
                title_list.append(title)
                key_highdif_dict[year] = highest_difference

    plotyears = list(key_highdif_dict.keys())
    plotscores = list(key_highdif_dict.values())
    plottitles = list(title_scores_dict)
    print(key_highdif_dict)
    
    mpl.rcParams['font.size'] = 4
    fig, axs = plt.subplots(2, 2)
    fig.suptitle("Most Controversial Article Per Year")
    axs[0, 0].bar( plotyears[0], plotscores[0], width = 0.4)
    axs[0, 0].set_title(title_list[0])
    axs[1, 0].bar(plotyears[2], plotscores[2])
    axs[1, 0].set_title(title_list[1])
    
    axs[0, 1].bar(plotyears[1], plotscores[1])
    axs[0, 1].set_title(title_list[2])
    axs[1, 1].bar(plotyears[3], plotscores[3])
    axs[1, 1].set_title(title_list[3])
    fig.tight_layout()
    # plt.show()


 


    
highest_lowest("output.csv")



        
        


    
