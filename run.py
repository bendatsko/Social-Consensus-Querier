import subprocess

def main():
    # Run all scripts in the order they should be run. Simulates the user as they run each script in their command line. 
    # Each script will run 25 articles.


    # data aquisition
    # subprocess.call("python3 setup.py --clear", shell=True) # use flag --clear before running to drop all tables
    #subprocess.call("python3 setup.py", shell=True)
    
    # get 25 new york times article titles and store them in the news database using the New York Times API
    #subprocess.call("python3 get_articles.py", shell=True)

    # search for 5 fetched new york times article titles on reddit and gather 5 comments from each article's 5 most relevant posts using PRAW API.
    # Stores 25 articles each time, so we need to run this 5 times for 25 articles.
    # for i in range(0,5):
    #     subprocess.call("python3 search_reddit.py", shell=True)

    # fetch the reddit post titles and comments associated with each new york times article and summarize the article with the opinions in context with Azure API
    #subprocess.call("python3 get_summaries.py", shell=True)

    # join article titles, post titles, post comments, and summaries together and dump to csv file for visualization
    #subprocess.call("python3 dump_to_csv.py", shell=True)


    # generate figures based on the data we've outputted to our csv file
     subprocess.call("python3 plot.py", shell=True)


if __name__ == "__main__":
    main()