"""
run.py
------
This script coordinates the execution of our data collection pipeline.

Workflow:
- Sets up database.
- Fetches articles from the New York Times.
- Searches for related Reddit discussions.
- Summarizes the articles and discussions.
- Dumps all data into a CSV file for further analysis.

Usage:
- Run script directly to execute pipeline: `python run.py`
"""

import subprocess

def main():
    print("Starting the setup process...")
    subprocess.call(
        "python3 setup.py", shell=True
    )  # Use flag --clear to drop all tables

    print("Fetching New York Times articles...")
    subprocess.call("python3 get_articles.py", shell=True)

    print("Searching for Reddit discussions related to fetched articles...")
    for i in range(5):
        print(f"Initiating search for batch {i + 1}/5...")
        subprocess.call("python3 search_reddit.py", shell=True)
    print("Reddit searches completed and data stored.")

    print("Summarizing articles and Reddit discussions...")
    subprocess.call("python3 get_summaries.py", shell=True)
    print("Summaries generated and stored.")

    print("Compiling all data into a single CSV file...")
    subprocess.call("python3 dump_to_csv.py", shell=True)
    print("Data compilation complete. CSV file ready.")


if __name__ == "__main__":
    main()
