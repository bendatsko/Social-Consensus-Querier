# Public Opinion Aggregator For Current Events
This project pulls current events from the New York Times API and aggregates public opinions on these events from Reddit comments using Azure AI text summarization.

We also plot the frequency a "positive", "neutral", or "negative" perception on a current event which we gain by categorizing each comment using sentiment analysis before storing it in our database. 

Based on how a global event is percieved by the general public and how controversial it is, we can get a better understand the world around us at a glance.

# APIs Used
- New York Times Trending Articles API
- PRAW API (Python Reddit API Wrapper)
- Azure AI Language API  

# Getting Started
All dependencies are listed in requirements.txt. To install them, execute the following command in your command line interface: `pip install -r requirements.txt`

* Setup the database with `python3 setup.py`. To drop all tables, you can run with same program with the `--clear` flag, i.e., `python3 setup.py --clear`
* Fetch New York Times article titles with `python3 get_articles.py`. Stores 25 articles in the `news` table at a time.
* Search Reddit using PRAW for comments and opinions relevant to the articles fetched wtih `python3 search_reddit.py`. Stores search results for the next 25 non-searched articles in the `reddit_posts` table, and includes post titles, post url, and 5 post comments.
* Send the comments and article titles for in-context analysis via the Azure language summarization API using `python3 get_summaries.py`. Stores summaries for the next 25 non-summaried articles in the `article_summaries` table.
* Join the contents of the `news`, `reddit_posts` and `article_summaries` tables and export database contents to a csv file with `python3 dump_to_csv.py`.

For convenience, execute `python3 run.py` one time. This program run each one of these programs sequentially. 

To generate plots with matplotlib from the data outputted to our csv file, run `python3 plot.py`.

For completeness, `utils.py ` contains helper classes for command line interface styling. 