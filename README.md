# Social Opinion Miner For Current Events

## Overview
This tool integrates article data from the New York Times API and public opinion from Reddit. It aggregates and analyzes the public's perception of global events using sentiment analysis and Azure's AI Language API. It categorizes sentiments from Reddit comments as positive, neutral, or negative and provides a summarized view of public opinion, helping users understand prevailing attitudes toward current events at a glance.

Completed as part of SI 206 at the University of Michigan for final project.

## Workflow
1. **Article Fetching**: Retrieve trending articles from the New York Times API.
2. **Opinion Mining**: Search for related discussions on Reddit using PRAW (Python Reddit API Wrapper).
3. **Sentiment Analysis**: Categorize comments into positive, neutral, or negative sentiments.
4. **Discussion Summarization**: Summarize articles' associated Reddit discussions using Azure AI Language API.
5. **Data Visualization**: Gain unique insights into opinion trends and how they correlate with global events.

## Project Structure
- `setup.py`: Sets up the SQLite database to store article and discussion data.
- `get_articles.py`: Fetches articles from the New York Times API.
- `search_reddit.py`: Searches for and stores Reddit discussions related to the fetched articles.
- `get_summaries.py`: Summarizes articles and discussions using Azure AI.
- `dump_to_csv.py`: Exports collected and processed data to a CSV file.
- `plot_selected_news_opinions.py`: Visualizes the sentiment analysis results using matplotlib.
- `run.py`: A convenience script to execute all the above scripts sequentially.
- `utils.py`: Contains helper classes and functions to improve the user interface in the command line.

## Visualizations
- `plot_12_sentiments.py`: Creates sentiment visualizations for 12 randomly-selected articles in the database with matplotlib, and provides a summarized public opinion on the matters addressed by the article.
- `plot_by_year.py`: Plots the average sentiment over the years data is pulled for.


## Getting Started
### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/bendatsko/206-final-project
   ```
2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3. **Environment Variables**: <br>
    Set the following environment variables in `.env`:
    * `NYT_API_KEY`: New York Times Developer API key.
    * `REDDIT_CLIENT_ID`: Reddit application client ID.
    * `REDDIT_CLIENT_SECRET`: Reddit application client secret.
    * `AZURE_LANGUAGE_KEY`: Azure AI Language API key.
    * `AZURE_LANGUAGE_ENDPOINT`: Endpoint for the Azure AI Language service.

### Automated Execution <br>
Run all processes in one sequence and aggregate data for approximately 25 articles. This process is slow and should take around 3 minutes.
```bash
python3 run.py
```
<br>
These can also be invoked manually, of course, with the following commands:

**Database Initialization**:
```bash
python3 setup.py
```
Use `--clear` to drop all tables:
```bash
python3 setup.py --clear
```
**Fetching Articles:**:
```bash
python3 get_articles.py
```
**Searching Reddit:**:
```bash
python3 search_reddit.py
```
**Generating Summaries:**:
```bash
python3 get_summaries.py
```
**Exporting Data to CSV:**:
```bash
python3 dump_to_csv.py
```


