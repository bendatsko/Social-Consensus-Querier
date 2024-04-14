import pandas as pd
import matplotlib.pyplot as plt
import ast  # To convert string representations of lists into actual list objects

def load_data(filepath):
    # Load data
    data = pd.read_csv(filepath)
    # Convert 'Sentiment List' from string to actual list
    data['Sentiment List'] = data['Sentiment List'].apply(ast.literal_eval)
    return data

def calculate_yearly_average(data):
    # Calculate average sentiment for each article
    data['Average Sentiment'] = data['Sentiment List'].apply(lambda x: sum(x) / len(x) if x else None)
    # Group by 'Year' and calculate the mean of 'Average Sentiment'
    yearly_data = data.groupby('Year')['Average Sentiment'].mean().reset_index()
    return yearly_data

def plot_sentiment_trends(yearly_data):
    plt.figure(figsize=(10, 5))
    plt.plot(yearly_data['Year'], yearly_data['Average Sentiment'], marker='o', linestyle='-', color='b')
    
    # Defining sentiment categories based on values
    plt.axhline(0, color='gray', linestyle='--', label='Neutral (0)')
    plt.axhline(0.5, color='green', linestyle='--', linewidth=0.5, label='Positive Threshold (>0.5)')
    plt.axhline(-0.5, color='red', linestyle='--', linewidth=0.5, label='Negative Threshold (<-0.5)')

    # Setting up plot title and labels
    plt.title('Average Sentiment by Year', fontsize=16, fontweight='bold') 
    plt.xlabel('Year')
    plt.ylabel('Average Sentiment')
    plt.grid(True)
    plt.xticks(yearly_data['Year'])  # Ensure all years are marked
    
    # Handling legend
    plt.legend(loc='upper left')

    plt.ylim(-1, 1)  # Ensuring the y-axis shows the full range from -1 to 1
    plt.show()



def main():
    filepath = 'output.csv'
    data = load_data(filepath)
    yearly_data = calculate_yearly_average(data)
    plot_sentiment_trends(yearly_data)
    


if __name__ == '__main__':
    main()
