import sqlite3

def create_databases():
    """
    Creates tables for the database.
    """
    #connect/create database file
    conn = sqlite3.connect('crypto_data.db')
    #create a cursor object for executing SQL commands
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS prices")
    cursor.execute("DROP TABLE IF EXISTS trends")

    #create prices table with table id, coin_name, date, and price in USD
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY,
            coin_name TEXT,
            date TEXT,
            price_usd REAL
        )
    ''')

    #create trends table with table id, coin_name, change in percentage, and volatility
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trends (
            id INTEGER PRIMARY KEY,
            coin_name TEXT,
            change_percentage REAL,
            volatility REAL
        )
    ''')
    #commit changes to save the above structure
    conn.commit()
    #close connection 
    conn.close()

def save_prices_db(prices):
    """Saves price data to the database.
    
    Args:
        prices(dict): A dictionary where the key is the coin name and the 
                      value is a pandas DataFrame containing price data.
    """
    #connect to the database
    conn = sqlite3.connect('crypto_data.db')
    #create cursor object for executing SQL commands
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prices")

    #loop through each coin and its associated DataFrame of price data
    for coin_name, price_data in prices.items():
        #iterate through Df rows
        for _, row in price_data.iterrows():
            #insert each row into 'prices table with coin name, date, and price
            cursor.execute('''
                INSERT INTO prices (coin_name, date, price_usd) VALUES (?, ?, ?)
            ''', (coin_name, row['date'].strftime('%Y-%m-%d'), row['price_usd']))

    #commit changes 
    conn.commit()
    #close connection
    conn.close()

def save_trends_db(trends):
    """Saves trend data to the database.
    Args:
         trends (dict): A dictionary where the key is the coin name and the 
                       value is a dictionary containing 'change_percentage' and 
                       'volatility'.
    """
    #connect to database 
    conn = sqlite3.connect('crypto_data.db')
    #create cursor object for executing SQL commands
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trends")

    #insert trend data
    for coin_name, trend in trends.items():
        #insert coin name, change percentage, and volatility 
        cursor.execute('''
            INSERT INTO trends (coin_name, change_percentage, volatility) VALUES (?, ?, ?)
        ''', (coin_name, trend['change_percentage'], trend['volatility']))

    #commit changes
    conn.commit()
    #close connection
    conn.close()

def display_db():
    """
    Displays the data from the SQLite database.
    """
    #connect to database
    conn = sqlite3.connect('crypto_data.db')
    #create cursor object for executing SQL commands
    cursor = conn.cursor()

    #get and display all data from prices table
    #header
    print("\nPrice Data:")
    cursor.execute('SELECT coin_name, date, price_usd FROM prices ORDER BY date DESC')
    #fetch all rows from the query
    prices = cursor.fetchall()
    #loop through and print each row of price data
    for row in prices:
        #format
        print(f"{row[0]} - {row[1]}: ${row[2]:.2f}")

    #get and display all data from trends table
    #header
    print("\nTrend Data:")
    cursor.execute('SELECT coin_name, change_percentage, volatility FROM trends')
    #fetch all rows from the query
    trends = cursor.fetchall()
    #loop through and print each row of trend data
    for row in trends:
        #format
        print(f"{row[0]} - Change: {row[1]:.2f}%, Volatility: {row[2]:.4f}")

    #close database connection
    conn.close()
