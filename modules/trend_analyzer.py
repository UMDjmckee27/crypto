import pandas as pd 

class TrendAnalyzer:
    """Class that analyzes cryptocurrency price trends."""
    
    def __init__(self,price_data):
        """Initializes the price data of crypto for analysis
         
         Args:
            price_data (dict): A dictionary of price data, where keys are coin names and values are DataFrames.
        """
        
        self.price_data = price_data
    
    def analyze_trends(self):
        """Does the analyzing of the cryptocurrency
        
        Returns:
            (dict): Dictionary of trends for each coin. 
        """
        #dictionary to store the found trends for each crypto coin
        trends = {}

        #iterate over coin name/its associated DataFrame of price data
        for coin_name, df in self.price_data.items():
            #skip if DF is empty
            if df.empty:
                continue
            
            #get the first and last price of coin to find coin's percentage change
            if not df.empty and 'price_usd' in df.columns:
                first_price = df['price_usd'].iloc[0] #first
                last_price = df['price_usd'].iloc[-1] #last
            else:
                print("DataFrame is empty or missing")

            #calculate the percentahe change by subtracting last price from first then dividing value by first price. mult that value by 100 to find percentage
            change_percentage = ((last_price - first_price) / first_price) * 100
            
            #get the price values as a NumPy array to find daily change
            price_changes = df['price_usd'].values
            #calculate daily price changes as percentage relative to most previous day
            daily_changes = [(price_changes[i] - price_changes[i - 1]) / price_changes[i - 1] for i in range(1, len(price_changes))]

            #find volatility
            #this part of the logic included for sake of unittesing: if only one price change --> vol = 0.0
            if len(daily_changes) > 1: 
                volatility = pd.Series(daily_changes).std()
            else:
                volatility = 0.0
            
            #calculate the average price across price data
            average_price = price_changes.mean()
            
            #store each of the above metrics in trends dictionary
            trends[coin_name] = {
                'change_percentage': change_percentage,
                'volatility': volatility,
                'average_price': average_price
            }
        
        #return complete dictionary of trends
        return trends

        
