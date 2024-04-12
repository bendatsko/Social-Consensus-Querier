# Public Opinion Aggregator For Current Events
This project pulls current events from the New York Times API and aggregates public opinions on these events from Reddit comments using Azure AI text summarization.

We also plot the frequency a "positive", "neutral", or "negative" perception on a current event which we gain by categorizing each comment using sentiment analysis before storing it in our database. 

Based on how a global event is percieved by the general public and how controversial it is, we can get a better understand the world around us at a glance.

# API's Used
- New York Times Trending Articles API
- PRAW API (Python Reddit API Wrapper)
- Azure AI Language API  

# Get Started
All dependencies are listed in requirements.txt. To install them, execute the following command in your command line interface: `pip install -r requirements.txt`

To collect data, run `python main.py`.

To generate plots with matplotlib, run `python plot.py`.

`utils.py ` contains helper classes for command line interface styling