# Importing all the necessary dependencies.
# ************************************************************

# Requests is being used to access the Binance API via a GET request.
import requests

# Playsound allows us to play an MP3 File directly via Python without having
# to call third party programs.
from playsound import playsound

# The sleep function allows us to pause the program to not check the API
# too often.
from time import sleep

# In order to save the data from the Binance API and check whether the
# current price is lower than the price within a previous time frame, we
# have to save the data in a simply SQL Database.
import sqlalchemy

# Pandas is the best (challenge me!) library for working with data.
# It allows us to get the min value of the Price within a specified range.
import pandas as pd

# Lastly, just to have the data structured, I have given each API request a
# date-time stamp, just in case someone wants to tinker with calling the alarm
# based on a value within a date range or whatever. It is not really necessary
# but it's always good to think ahead.
from datetime import datetime

# Simple command line interface that let's the user know the program is running.
print("\n")
print("Hello and Welcome to the Bitcoin Alert!")
print("\n")
print("***************************************")
print("\n")
print("The program has been started.")
print("Good luck not falling out of your chair!")


# This function is responsible for calling the Binance API.
def fetchBinanceData():
    # Try-Except loop because the connection can timeout if you call it too frequently.
    try:
        response = requests.get("https://api.binance.com/api/v3/avgPrice?symbol=BTCUSDT")
        # Response comes back as json, which makes it nice and easy to clean the data.
        response_json = round(float(response.json()['price']), 2)
        return response_json
    except:
        print("Error connecting to Binance API!")


# This function converts the GET Requests to structured data by creating a
# Pandas dataframe out of it.
def to_dataframe():
    # This is the current date-time stamp.
    date = datetime.now()
    # Structuring the data
    df = pd.DataFrame([{'s': "BTC", 'd': date, 'p': fetchBinanceData()}])
    df.columns = ['Symbol', 'Date', 'Price']
    return df


while True:
    # As previously mentioned, we do not want to call the API too often or
    # else it may be timing out.
    sleep(30)
    # The engine is the database connection in the form of a sqlite db.
    engine = sqlalchemy.create_engine("sqlite:///BinanceData.db")
    # Retrieving the dataframe
    frame = to_dataframe()
    # Converting the dataframe to SQL and appending the row.
    frame.to_sql("BTC", engine, if_exists="append", index=False)
    # Current value which will be compared to a price range.
    current_value = frame["Price"][0]
    # Reading the whole SQL db to be able to define the range within we
    # want to compare the price.
    df = pd.read_sql("BTC", engine)
    # In this instance, the price is checked on the last 20 entries of the database
    # which corresponds with the sleep function to 30*20 seconds, thus 10 minutes.
    last_X = df.iloc[-20:-2]
    benchmark = last_X.Price.min()
    try:
        # If the current price is the lowest price within the specified time window
        # of 10 minutes, ger rowdy!
        if current_value < benchmark:
            # The soundtrack is called
            playsound('AlertSound.mp3')
    except:
        # For now, we are not interested in the reason why an iteration did
        # not work. We'll just skip it. Bad error handling but w/e.
        None