# Libraries
import requests
import json
import math
import pandas as pd
import datetime
import time
import schedule
import os
import logging
import traceback
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display
#import tkinter as tk
#from tkinter import messagebox

# Declaring variables
columnsWanted = ['strikePrice', 'expiryDate', 'openInterest', 'changeinOpenInterest', 'pchangeinOpenInterest', 'totalTradedVolume', 'impliedVolatility', 'lastPrice', 'change', 'pChange','totalBuyQuantity', 'totalSellQuantity', 'underlyingValue']
number = 3
step = {"nf":50, "bnf":100}
stock = {"nf":"NIFTY 50","bnf":"NIFTY BANK"}

# Variables for Urls to fetch Data
urls = {
    "url_oc"      : "https://www.nseindia.com/option-chain",
    "url_bnf"     : "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY",
    "url_nf"      : "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY",
    "url_indices" : "https://www.nseindia.com/api/allIndices"
    }

# Headers
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8',
            'accept-encoding': 'gzip, deflate, br'}


# Set up the logging
log_file_path = os.path.join("python_Scripts", "script_log.txt")
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"  # Use the desired time format here
    )

# session variables and methods
sess = requests.Session()
#cookies = dict()

def set_cookie():
    try:
        request = sess.get(urls["url_oc"], headers=headers, timeout=5)
        cookies = dict(request.cookies)
        return cookies
    except requests.exceptions.Timeout as e:
        logging.error("Request timeout error: %s", e)
        return None

def make_request(url, cookies):
    return sess.get(url, headers=headers, timeout=20, cookies=cookies)

def get_data_with_retry(url, max_retries=5, retry_delay=2):
    for attempt in range(max_retries):
        if attempt > 0:
            print("Retrying... Attempt =", attempt+1)
            logging.info("Retrying... Attempt - %s", attempt+1)
        try:
            cookies = set_cookie()
            if cookies: # is not None:
                response = make_request(url, cookies)
                if response.status_code == 200:
                    #logging.info("Response data collected successfully in attempt %s", attempt)
                    return response.text  # Return the response data if successful
                else:
                    # Retry for non-200 status codes
                    logging.warning("Request returned non-200 status code: %s", response.status_code)                    
        except requests.exceptions.Timeout as e:
            logging.error("Request timeout error: %s", e)
        except requests.exceptions.RequestException as e:
            logging.error("Request error: %s", e)
        except TypeError as e:
            logging.error("Error fetching cookies: %s", e)
        time.sleep(retry_delay)  # Wait for a few seconds before retrying

    # If all retries failed, log an error and return an empty string
    logging.error("Request failed after multiple retries.")
    return ""


# Method to get nearest strikes
def round_nearest(x,num=50): return int(math.ceil(float(x)/num)*num)
def nearest_strike_bnf(x): return round_nearest(x,step["bnf"])
def nearest_strike_nf(x): return round_nearest(x,step["nf"])

# Fetching Underlying data of given stock
def set_header(stock):
    global ul
    global nearest
    response_text = get_data_with_retry(urls["url_indices"])
    data = json.loads(response_text)
    for index in data["data"]:
        if index["index"]==stock:
            ul = index["last"]
    if stock =="NIFTY 50":
        nearest=nearest_strike_nf(ul)
    elif stock =="NIFTY BANK":
        nearest=nearest_strike_bnf(ul)
    return nearest

    
# Saving dataframes for CE and PE data based on Nearest Expiry Date
def loadDataframes(num,step,nearest,expDate,url):
    strike = nearest - (step*num)
    start_strike = nearest - (step*num)
    response_text = get_data_with_retry(url)
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
    return df_list


# Finding highest Open Interest of People's in CE based on CE data         
def highest_oi_CE(num,step,nearest,url):
    strike = nearest - (step*num)
    start_strike = nearest - (step*num)
    response_text = get_data_with_retry(url)
    data = json.loads(response_text)
    currExpiryDate = data["records"]["expiryDates"][0]
    max_oi = 0
    max_oi_strike = 0
    for item in data['records']['data']:
        if item["expiryDate"] == currExpiryDate:
            if item["strikePrice"] == strike and item["strikePrice"] < start_strike+(step*num*2):
                if item["CE"]["openInterest"] > max_oi:
                    max_oi = item["CE"]["openInterest"]
                    max_oi_strike = item["strikePrice"]
                strike = strike + step
    return max_oi_strike

# Finding highest Open Interest of People's in PE based on PE data 
def highest_oi_PE(num,step,nearest,url):
    strike = nearest - (step*num)
    start_strike = nearest - (step*num)
    response_text = get_data_with_retry(url)
    data = json.loads(response_text)
    currExpiryDate = data["records"]["expiryDates"][0]
    max_oi = 0
    max_oi_strike = 0
    for item in data['records']['data']:
        if item["expiryDate"] == currExpiryDate:
            if item["strikePrice"] == strike and item["strikePrice"] < start_strike+(step*num*2):
                if item["PE"]["openInterest"] > max_oi:
                    max_oi = item["PE"]["openInterest"]
                    max_oi_strike = item["strikePrice"]
                strike = strike + step
    return max_oi_strike


# Calculation of expiry dates
def near_expiry():
    #today = datetime.datetime.strptime("2023-08-3","%Y-%m-%d").date()
    today = datetime.date.today()
    current_weekday = today.weekday()
    # Calculate the number of days until the next Thursday (Thursday is 3, 0=Monday, 1=Tuesday, ..., 6=Sunday)
    days_until_thursday = (3 - current_weekday + 7) % 7
    
    # Calculate the date of the next Thursday
    next_thursday = today + datetime.timedelta(days=days_until_thursday)
    next_to_next_thursday = next_thursday + datetime.timedelta(days=7)
    
    return next_thursday.strftime("%d-%b-%Y"), next_to_next_thursday.strftime("%d-%b-%Y")

def last_thursday_current_month(month = datetime.date.today().month):
    if month == 0: month=12
    #today = datetime.datetime.strptime("2023-06-3","%Y-%m-%d").date()
    today = datetime.date.today()
    year = today.year;

    # Find the last day of the current month
    last_day_of_month = datetime.date(year, month, 1) + datetime.timedelta(days=32)
    last_day_of_month = last_day_of_month.replace(day=1) - datetime.timedelta(days=1)

    # Find the weekday of the last day of the month (0 = Monday, 6 = Sunday)
    last_weekday = last_day_of_month.weekday()

    # Calculate the number of days to go back to reach the last Thursday
    days_to_last_thursday = (last_weekday - 3 + 7) % 7

    # Calculate the date of the last Thursday of the current month
    last_thursday = last_day_of_month - datetime.timedelta(days=days_to_last_thursday)

    return last_thursday.strftime("%d-%b-%Y")
    
def monthly_expiry():
    near_expiry_date,next_expiry_date = near_expiry()
    curr_month_last_thursday = last_thursday_current_month()
    if (curr_month_last_thursday == near_expiry_date) or (curr_month_last_thursday == next_expiry_date):
        monthly_expiry_date = last_thursday_current_month((datetime.date.today().month + 1)%12)
        return monthly_expiry_date
    else:
        return curr_month_last_thursday

def expiry_dates():
    near_expiry_date,next_expiry_date = near_expiry()
    monthly_expiry_date = monthly_expiry()
    return [near_expiry_date, next_expiry_date, monthly_expiry_date]



# Method to fetch and process data for Nifty and Bank Nifty
def fetch_and_process_data(exp_date):
    print("Fetching and processing data for", exp_date, "at",datetime.datetime.now().replace(microsecond=0))
    logging.info("Fetching and processing data for %s", exp_date)

    # Nifty data
    logging.info("Fetching Nifty data...")
    start_fetch = time.time()
    df_nifty_list = fetchData(number, step["nf"], stock["nf"], urls["url_nf"], exp_date)

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
    df_bank_nifty_list = fetchData(number, step["bnf"], stock["bnf"], urls["url_bnf"], exp_date)

    # Export data to Excel for Bank Nifty
    for i, df_bank_nifty in enumerate(df_bank_nifty_list):
        export_to_excel(df_bank_nifty, "Bank_Nifty_Data", exp_date[i])
    
    end_fetch = time.time()
    # Calculate the time taken during this iteration
    elapsed_time = end_fetch - start_fetch
    print("Time elapsed to fetch and save Bank Nifty data =", int(elapsed_time), "seconds")
    logging.info("Time elapsed to fetch and save Bank Nifty data = %s seconds", str(int(elapsed_time)))
    
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
    # Create folder if Saved data folder does not exist
    # folder_path = os.path.join("C:\\Users\\kira1\\Documents\\Python Scripts\\Saved Data", f"Data for {datetime.date.today().strftime('%d-%b-%Y')}")
    folder_path = os.path.join("backend\\data", f"Data for {datetime.date.today().strftime('%d-%b-%Y')}")
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            # print("Created 'Saved data' folder.")
            logging.info("Created 'Saved data' folder.")
        except Exception as e:
            # print("Error creating 'Saved data' folder:", e)
            logging.info("Error creating 'Saved data' folder: %s", e)
    try:
        # Create the full file path
        file_path = os.path.join(folder_path, f"{filename}_{expiry_date}.xlsx")

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


# Main function to fetch and process data
def main():
    try:
        # Wait until the market opens
        wait_until_market_open()
        
        # Processing expiry dates
        expiryDates = expiry_dates()



        # Looping each minute to collect data with variable sleep timer
        while is_market_open():
            start_fetch = time.time()
            fetch_and_process_data(expiryDates)
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
    end_time = datetime.time(19, 40)
    main()

