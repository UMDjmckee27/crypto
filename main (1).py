import argparse 
import requests
import pandas as pd
from datetime import datetime
from trend_analyzer import TrendAnalyzer
from database_creation import create_databases, save_prices_db, save_trends_db, display_db

#For Unit Test, We plan to implement one for each functions return statement 

class Crypto:
    """Crypto class that creates an object using the CoinGecko API"""

    def __init__(self, coin_names, api_key=None):
        """
        Initalizes an instance of the Crypto class with the api key, and coin names to analyze, 
        the obtained price data
        
        Args:
            api_key (str): The key needed to authenticate requests from GeckoCoin 
            coin_names (list of str): List of cryptocurrencies to analyze
        """
        self.coin_names = coin_names
        self.api_key = api_key
        self.prices_data = {}

    #Will have a unit test to check we're getting a dictionary for prices
    def get_prices(self, days):
        """
        Gets the price data for each coin given by the user and organizes it into a DataFrame.

        Args:
            days (int): Number of days to fetch price history for.

        Returns:
            pd.DataFrame: A DataFrame containing daily prices of the coins.
        """
        #dictionary that stores all price data temporarily
        prices = {}

        #gets the CG Api URL with the coin name and each necessary parameter 
        for coin_name in self.coin_names:
            url = f"https://api.coingecko.com/api/v3/coins/{coin_name}/market_chart"
            params = {'vs_currency': 'usd', 'days': days,'interval': 'daily'}

            #implemented try and except for HTTP errors
            try:
                response = requests.get(url, params=params)
                #raise exception for HTTP errors
                response.raise_for_status()
                #parse response JSON
                data = response.json()

                if 'prices' in data:
                    #convert list of price info data into DataFrame
                    price_data = [
                        (datetime.fromtimestamp(ts / 1000).date(), price)
                        for ts, price in data['prices']
                    ]
                    
                    df = pd.DataFrame(price_data, columns=['date', 'price_usd'])
                    df = df.drop_duplicates(subset=['date'], keep='last')
                

                    #structure the dataframe by column using date and price in USD along with the coin name itself
                    prices[coin_name] = df
                    #confirmation message
                    print(f"Retrieved daily prices for {coin_name}.")
                else:
                    print(f"No price data found for {coin_name}.")
            #for HTTP errors prints an error message
            except requests.RequestException as e:
                print(f"Failed to retrieve data for {coin_name}: {e}")

        #update the above instance attributes with the acquired CG price data
        self.prices_data = prices
   
    def suggest_investments(self, days):
        """
        Suggests potential investment opportunities based on positive trends and analyzing trends

        Args:
            days (int): # of days of price data to analyze coin trends

        Returns:
            recommendations (tuple): provides dictionary of coin names recommended for investment
        """
        #get the latest price data
        self.get_prices(days)
        #initialize TrendAnalyzer module
        analyzer = TrendAnalyzer(self.prices_data)
        #analyze trends to find each coins metrics 
        trends = analyzer.analyze_trends()

        #list for investment recommendations
        recommendations = []
        
        for coin_name, trend in trends.items():
            #suggest investment if trend percentage is positive (>0)
            if trend['change_percentage'] > 0:
                #append all relevant coin metrics (change percent, volatility, and avg price)
                recommendations.append({
                    'coin': coin_name,
                    'change_percentage': trend['change_percentage'],
                    'volatility': trend['volatility'],
                    'average_price': trend['average_price']
                })
                
        if recommendations:
            #display recommended coins with their trends
            print("\nThe following coins are recommended for investment:")
            for rec in recommendations:
                print(f"- {rec['coin']}: Change: {rec['change_percentage']:.2f}%, Volatility: {rec['volatility']:.4f}")
                
                #prompts user if they want detailed investment recs (y/n)
                user_choice = input("\nwould you like to view detailed investment recommendations? (yes/no): ").strip().lower()
                if user_choice == 'yes':
                    print("\ndetailed investment recommendations:")
                    for rec in recommendations:
                        print(f"\nCoin: {rec['coin']}")
                        print(f"  Change Percentage: {rec['change_percentage']:.2f}%")
                        print(f"  Volatility: {rec['volatility']:.4f}")
                        print(f"  Average Price: ${rec['average_price']:.2f}")
                        print(f"  Suggestion: {'High potential for growth!' if rec['change_percentage'] > 5 else 'Moderate growth expected.'}")
                else: 
                    print("\nYou chose not to view detailed recommendations.")
                    
        else:
            print("No coins are currently recommended for investment based on the trends.")
            
        #return the coins associated recommendations for investment 
        return trends, recommendations


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Fetch cryptocurrency prices from CoinGecko and analyze trends.")
    #coin
    parser.add_argument("coin_ids", nargs="+", help="List of cryptocurrency IDs (e.g., bitcoin, ethereum)")
    #days
    parser.add_argument("--days", type=int, default=1, help="Number of days of historical data to fetch (default: 1)")
    #CG Api Key
    parser.add_argument("--api_key", type=str, help="API key for CoinGecko. If not provided, will prompt for one.")

    #parse
    args = parser.parse_args()

    #if Api key is not provided as an argument, prompts the user for it
    if not args.api_key:
        args.api_key = input("Enter your CoinGecko API key: ").strip()

    #prompt # of days
    days = int(input("Enter the number of days of historical data to look at for your coins: ").strip())

    #create crypto obj with the inputs
    tracker = Crypto(args.coin_ids, args.api_key)
    
    #ask user if they want their investment suggestions
    suggest_investments = input("Would you like investment suggestions based on trends? (yes/no): ").strip().lower()

    #initialize databses for storing price/trend data
    create_databases()

    #if user says yes
    if suggest_investments == 'yes':
        #get trends and save data 
        trends, recommendations = tracker.suggest_investments(days=days)
        #save trends and price info into respective databases 
        save_trends_db(trends)
        save_prices_db(tracker.prices_data)
    else:
        #get and save price data only
        tracker.get_prices(days=days)
        save_prices_db(tracker.prices_data)
    
    #display the database contents
    display_db()
    
    
    
    
    

