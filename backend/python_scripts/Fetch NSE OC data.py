# Pre-defined Libraries
import requests
import json
import math
import pandas as pd
import datetime
import time
import logging
import os
import traceback
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display
import sqlite3
# import schedule
# import tkinter as tk
# from tkinter import messagebox

# Defined Libraries
import paths_logging
import initializeVariables
import sessionMethods
import marketDataCalcs
import expiryDateCalcs


# Initialize Variables
columnsWanted,number,step,stock,urls,headers = initializeVariables.initVars()

# Set up logging config
paths_logging.setup_logging()

# session variables and methods
sess = requests.Session()

# Fetching Underlying and nearest SP data of given stock
def set_header(stock):
    global ul
    global nearest
    response_text = sessionMethods.get_data_with_retry(urls["url_indices"])
    data = json.loads(response_text)
    for index in data["data"]:
        if index["index"]==stock:
            ul = index["last"]
    if stock =="NIFTY 50":
        nearest = marketDataCalcs.nearest_strike_nf(ul)
    elif stock =="NIFTY BANK":
        nearest = marketDataCalcs.nearest_strike_bnf(ul)
    return nearest

    
# Saving dataframes for CE and PE data based on Nearest Expiry Date
def loadDataframes(num,step,nearest,expDate,url):
    strike = nearest - (step*num)
    start_strike = nearest - (step*num)
    response_text = sessionMethods.get_data_with_retry(url)
    try:
        data = json.loads(response_text)
        df_list = []
        for expiry_date in expDate:
            df = pd.DataFrame(); df_ce = pd.DataFrame(); df_pe = pd.DataFrame(); temp_df_ce = pd.DataFrame(); temp_df_pe = pd.DataFrame()
            strike = nearest - (step*num)
            start_strike = nearest - (step*num)
            for item in data['records']['data']:
                if item["expiryDate"] == expiry_date:
                    if item["strikePrice"] == strike and item["strikePrice"] < start_strike+(step*num*2):
                        temp_df_ce = pd.DataFrame(item['CE'],index=[strike],columns = columnsWanted)
                        temp_df_pe = pd.DataFrame(item['PE'],index=[strike],columns = columnsWanted)  
                        strike = strike + step
                        df_ce = pd.concat([df_ce,temp_df_ce],ignore_index=True)
                        df_pe = pd.concat([df_pe,temp_df_pe],ignore_index=True)
            df = pd.merge(df_ce,df_pe,how="inner",on="strikePrice",suffixes=("_CE", "_PE"))
            df.insert(loc=0, column='Date', value=datetime.datetime.now().replace(microsecond=0))
            df.drop(columns=["expiryDate_PE","underlyingValue_CE"],inplace=True)
            df_list.append(df)
        return df_list
    
    except json.JSONDecodeError as e:
        logging.error("JSON decoding error: %s", e)
        logging.error("JSON Response: %s", response_text)
        return []            
    except Exception as e:
        logging.error("An error occurred while loading or processing dataframe: %s", e)
        return []     


def fetchData(num, step, stockIndex, indexUrl, expDate):
    nearest = set_header(stockIndex)
    df_list = loadDataframes(num, step, nearest, expDate, indexUrl)
    return nearest, df_list


# Method to fetch and process data for Nifty and Bank Nifty
def fetch_and_process_data(exp_date):
    print("Fetching and processing data for", exp_date, "at",datetime.datetime.now().replace(microsecond=0))
    logging.info("Fetching and processing data for %s", exp_date)

    # Nifty data
    logging.info("Fetching Nifty data...")
    start_fetch = time.time()
    nifty_nearest, df_nifty_list = fetchData(number, step["nf"], stock["nf"], urls["url_nf"], exp_date)

    # Export data to Excel for Nifty
    for i, df_nifty in enumerate(df_nifty_list):
        export_to_excel(df_nifty, "Nifty_Data", exp_date[i])
    
    end_fetch = time.time()
    # Calculate the time taken during this iteration
    elapsed_time = end_fetch - start_fetch
    print("Time elapsed to fetch and save Nifty data =", int(elapsed_time), "seconds")
    logging.info("Time elapsed to fetch and save Nifty data = %s seconds", str(int(elapsed_time)))
    

    # Bank Nifty data
    logging.info("Fetching Bank Nifty data...")
    start_fetch = time.time()
    bank_nifty_nearest, df_bank_nifty_list = fetchData(number, step["bnf"], stock["bnf"], urls["url_bnf"], exp_date)

    # Export data to Excel for Bank Nifty
    for i, df_bank_nifty in enumerate(df_bank_nifty_list):
        export_to_excel(df_bank_nifty, "Bank_Nifty_Data", exp_date[i])
    
    end_fetch = time.time()
    # Calculate the time taken during this iteration
    elapsed_time = end_fetch - start_fetch
    print("Time elapsed to fetch and save Bank Nifty data =", int(elapsed_time), "seconds")
    logging.info("Time elapsed to fetch and save Bank Nifty data = %s seconds", str(int(elapsed_time)))

    return nifty_nearest, bank_nifty_nearest
    
    # Finding Highest OI in Call Option In Nifty
    # nf_highestoi_CE = highest_oi_CE(10, 50, nearest, urls["url_nf"])
    # print("Major Support in Nifty: ",nf_highestoi_CE)
    # logging.info("Major Support in Nifty: %s", nf_highestoi_CE)

    # Finding Highest OI in Put Option In Nifty
    # nf_highestoi_PE = highest_oi_PE(10, 50, nearest, urls["url_nf"])
    # print("Major Resistance in Nifty: ",nf_highestoi_PE)
    # logging.info("Major Resistance in Nifty: %s", nf_highestoi_PE)



    # Finding Highest OI in Call Option In Bank Nifty
    # bnf_highestoi_CE = highest_oi_CE(10, 100, nearest, urls["url_bnf"])
    # print("Major Support in Bank Nifty: ",bnf_highestoi_CE)
    # logging.info("Major Support in Bank Nifty: %s", bnf_highestoi_CE)

    # Finding Highest OI in Put Option In Bank Nifty
    #bnf_highestoi_PE = highest_oi_PE(10, 100, nearest, urls["url_bnf"])
    # print("Major Resistance in Bank Nifty: ",bnf_highestoi_PE)
    #logging.info("Major Resistance in Bank Nifty: %s", bnf_highestoi_PE)


# Export data to Excel method
def export_to_excel(df, filename, expiry_date):
    # Create folder if excel file folder path does not exist
    xl_folder_path = paths_logging.create_xl_folder_path()
    try:
        # Create the full file path
        file_path = os.path.join(xl_folder_path, f"{filename}_{expiry_date}.xlsx")

        # Check if the Excel file already exists
        if os.path.exists(file_path):
            existing_data = pd.read_excel(file_path)
            df = pd.concat([df, existing_data], ignore_index=True)
            df.to_excel(file_path, index=False)
            # print(f"Data appended to existing {filename}_{expiry_date}.xlsx successfully!")
            # logging.info("Data appended to existing %s successfully!", file_path)
        else:
            # Export dataframe to Excel
            df.to_excel(file_path, index=False)
            # print(f"Data appended to {filename}_{expiry_date}.xlsx successfully!")
            # logging.info("Data appended to %s successfully!", file_path)
    except Exception as e:
        print("Error exporting data to Excel:", e)
        logging.error("Error exporting data to Excel: %s", e)


# Method to perform check and wait until market opens
def wait_until_market_open():
    current_time = datetime.datetime.now().time()
    while current_time < start_time:
        current_time = datetime.datetime.now().time()
        time.sleep(1)

def is_market_open():
    # Check if the current time is between the start time (9:00 AM) and the end time (3:30 PM)
    current_time = datetime.datetime.now().time()
    return start_time <= current_time <= end_time


# Function to store nf_SP and bnf_SP in the database
def store_strike_prices(nf_SP, bnf_SP):
    file_path = paths_logging.create_db_folder_path()
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()
    # Create a table to store nf_SP and bnf_SP
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS strike_prices (
            id INTEGER PRIMARY KEY,
            dateTime DATETIME,
            nf_SP REAL,
            bnf_SP REAL
        )
    ''')
    conn.commit()
    
    # Insert or update the nf_SP and bnf_SP values in the database
    cursor.execute("INSERT INTO strike_prices (dateTime, nf_SP, bnf_SP) VALUES (datetime('now', 'localtime'), ?, ?)", (nf_SP, bnf_SP))
    
    conn.commit()
    conn.close()


# Main function to fetch and process data
def main():
    try:
        # Wait until the market opens
        wait_until_market_open()
        
        # Processing expiry dates
        expiryDates = expiryDateCalcs.expiry_dates()



        # Looping each minute to collect data with variable sleep timer
        while is_market_open():
            start_fetch = time.time()
            nf_SP, bnf_SP = fetch_and_process_data(expiryDates)
            store_strike_prices(nf_SP,bnf_SP)
            # print(fetch_strike_prices())
            end_fetch = time.time()
            # Calculate the time taken during this iteration
            elapsed_time = end_fetch - start_fetch
            print("Total time elapsed =", int(elapsed_time), "seconds")
            logging.info("Total time elapsed = %s seconds", str(int(elapsed_time)))

            # Calculate the time to sleep until the next minute
            sleep_duration = 60 - elapsed_time
            print("Sleep duration is set to =", int(sleep_duration), "seconds\n\n")
            logging.info("Sleep duration is set to = %s seconds", str(int(sleep_duration)))

            # Wait until the next minute to start the next iteration
            if 0 < sleep_duration < 60:
                time.sleep(sleep_duration)
                
        # Display the program closed alert
        # show_alert("Program Status", "The program has been closed.")

    except requests.exceptions.RequestException as e:
        # Log any exceptions that occur during the execution of the script
        logging.error("Request error: %s", e)
    except Exception as e:
        # Log any exceptions that occur during the execution of the script
        logging.error("An error occurred in the main function: %s", e)
        logging.error(traceback.format_exc())      # traceback.print_exc()

if __name__ == "__main__":
    # Start time for the script (9:00 AM) and end time (3:30 PM)
    start_time = datetime.time(9, 0)
    end_time = datetime.time(11, 45)
    main()

