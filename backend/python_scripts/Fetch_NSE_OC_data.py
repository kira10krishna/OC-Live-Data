# Pre-defined Libraries
import requests
import json
import pandas as pd
import datetime
import time
import logging
import os
import sys
import traceback
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display
# import schedule
# import tkinter as tk
# from tkinter import messagebox

ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../python_scripts'))
sys.path.append(ab_path)

# Defined Libraries
from initializeVariables import InitVars
from paths_logging import PathManager
from dataFetcher import DataFetcher
from dataProcessor import DataProcessor
from expiryDateCalcs import ExpiryCalculator
from DBoperations import DatabaseManager
from marketTimings import MarketTimings


# Initialize Variables
# Create an instance of the InitializeVariables class
init_vars = InitVars()
# Get the variables
columnsWanted, number, step, stock, urls, headers = init_vars.get_variables()


# Set up logging config
path_manager = PathManager()
path_manager.setup_logging()


class MainApplication:
    def __init__(self):
        # Create instances of your modules
        self.data_fetcher = DataFetcher()
        self.data_processor = DataProcessor()
        self.expiry_dates = ExpiryCalculator()
        self.db_manager = DatabaseManager()
        self.mkt_timings = MarketTimings()


    def main(self):
        try:
            # Wait until the market opens
            self.mkt_timings.wait_until_market_open()
                
            # Processing expiry dates
            expiryDates = self.expiry_dates.expiry_dates()

            # Looping each minute to collect data with variable sleep timer
            while self.mkt_timings.is_market_open():
                start_fetch = time.time()
                nf_SP, bnf_SP = self.data_processor.fetch_and_process_data(expiryDates)
                self.db_manager.store_strike_prices(nf_SP,bnf_SP)
                print(self.db_manager.fetch_strike_prices())
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
        except requests.exceptions.RequestException as e:
            logging.error("Request error: %s", e)
        except Exception as e:
            logging.error("An error occurred in the main function: %s", e)
            logging.error(traceback.format_exc())  # traceback.print_exc()

if __name__ == "__main__":
    main_app = MainApplication()
    main_app.main()



# def post_response():
#     # Define the URL of your Flask API
#     api_url = 'http://127.0.0.1:8989/run-main-code'  # Update with your actual API URL
#     # Rest API Post Method
#     response = requests.post(api_url)
#     # Check the response from the API 
#     if response.status_code == 200:
#         print("Main code executed successfully. This message is coming from python file.")
#     else:
#         print("Failed to execute main code. Status code:", response.status_code)