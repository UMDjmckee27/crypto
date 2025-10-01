import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from main import Crypto
from trend_analyzer import TrendAnalyzer

class TestCryptoMethods(unittest.TestCase):
    """
    Unit tests for all methods in main.py Crypto class
    """
    #patch basically just createsa fake object to simulate Api response
    @patch("main.requests.get")
    def test_get_prices(self, mock_get):
        """
        Tests the get_prices method of Crypto class

        A mock response of "200" being included means checking prices are gotten correctly/processed
        into our DataFrame
        """
        #mock Api response with 4 price data points and epoch/UNIX timestamp
        mock_response = {
            'prices': [
                [1733832000000, 97077.22],  #12/10
                [1733918400000, 99807.41],  #12/11
                [1733832000000, 97779.31],  #12/10
                [1733918400000, 97343.92]   #12/11
            ]
        }
        
        #set up mock response using MagicMock which just sims successful HTTP response recieved from CG Api
        mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_response)
        
        #creates an instance of Crypto class with bitcoin and a test API key
        crypto = Crypto(["bitcoin"], api_key="test_key")
        
        #see price data across 2 days (12/10 & 12/11)
        crypto.get_prices(days=2)

        #checks bitcoin price data is obtained from CG Api and stored properly
        self.assertIn("bitcoin", crypto.prices_data)
        self.assertIsInstance(crypto.prices_data["bitcoin"], pd.DataFrame)
        self.assertEqual(len(crypto.prices_data["bitcoin"]), 4)
        
        #checks that each of the 4 prices are correct for the given dates
        self.assertAlmostEqual(crypto.prices_data["bitcoin"].iloc[0]["price_usd"], 97077.22, places=2)
        self.assertAlmostEqual(crypto.prices_data["bitcoin"].iloc[1]["price_usd"], 99807.41, places=2)
        self.assertAlmostEqual(crypto.prices_data["bitcoin"].iloc[2]["price_usd"], 97779.31, places=2)
        self.assertAlmostEqual(crypto.prices_data["bitcoin"].iloc[3]["price_usd"], 97343.92, places=2)

    #create fake objects to simulate the TrendAnalyzer class thats modulated
    @patch("main.TrendAnalyzer")
    #simulates the requests.get 
    @patch("main.requests.get")
    def test_suggest_investments(self, mock_get, mock_trend_analyzer):
        """
        Test the suggest_investments method to ensure recommendations are made based on trends.
        """ 
        #fake Api response with 4 price points and epoch/unix timestamp
        mock_response = {
            'prices': [
                [1733832000000, 97077.22],  #12/10
                [1733918400000, 99807.41],  #12/11
                [1733832000000, 97779.31],  #12/10
                [1733918400000, 97343.92]   #12/11
            ]
        }
               
        #set up mock response using MagicMock which just sims successful HTTP response recieved from CG Api
        mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_response)

        #trend analysis test with all accurate change in percent, volatility, avg price values
        #allows our TrendAnalysis class logic to be checked properly
        mock_trend_analyzer.return_value.analyze_trends.return_value = {
            "bitcoin": {
                "change_percentage": 0.27,
                "volatility": 0.025,        
                "average_price": 98001.965  
            }
        }

        #create instance of Crypto class with bitcoin and test Api key
        crypto = Crypto(["bitcoin"], api_key="test_key")
        
        #get investment recs based on 4 price data points over 2 days
        trends, recommendations = crypto.suggest_investments(days=2)

        #see that the trends include bitcoin and match the expected values
        self.assertIn("bitcoin", trends)
        #change percentage should be 0.27
        self.assertAlmostEqual(trends["bitcoin"]["change_percentage"], 0.27, places=2)
        #volatility should be roughly 0.025
        self.assertEqual(trends["bitcoin"]["volatility"], 0.025)
        #avg price should be 98001.965
        self.assertAlmostEqual(trends["bitcoin"]["average_price"], 98001.965, places=2)

        #see that the recommendations include the average price (98001.965) and coin name (bitcoin)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]["coin"], "bitcoin")
        self.assertAlmostEqual(recommendations[0]["average_price"], 98001.965, places=2)


class TestTrendAnalyzerMethods(unittest.TestCase):

    def test_analyze_trends(self):
        """
        Tests the analyze_trends method to confirm its logic is correct.
        
        """
        #sample btc dataframe data with each price point
        prices_data = {
            "bitcoin": pd.DataFrame({
                "date": ["2024-12-10", "2024-12-11", "2024-12-10", "2024-12-11"],
                "price_usd": [97077.22, 99807.41, 97779.31, 97343.92]
            })
        }

        #create instance of TrendAnalyzer with price data
        analyzer = TrendAnalyzer(prices_data)
        
        #see the trends
        trends = analyzer.analyze_trends()

        #check the trends for bitcoin
        self.assertIn("bitcoin", trends)
        #change in percentage should be rounded out to a final value of ~ 0.27
        self.assertAlmostEqual(trends["bitcoin"]["change_percentage"], 0.27, places=2)
        #btc volatility value among all 4 prices is a float 
        self.assertIsInstance(trends["bitcoin"]["volatility"], float)
        #volatility value should be rrounded out to a final value of ~ 0.025
        self.assertAlmostEqual(trends["bitcoin"]["volatility"], 0.025, places=3)
        #average price value among all 4 prices is a float
        self.assertIsInstance(trends["bitcoin"]["average_price"], float)
        #average price among all 4 prices is 98001.965
        self.assertAlmostEqual(trends["bitcoin"]["average_price"], 98001.965, places=3                                                                                                                  )

#simulate each methods unittest
if __name__ == "__main__":
    unittest.main()
