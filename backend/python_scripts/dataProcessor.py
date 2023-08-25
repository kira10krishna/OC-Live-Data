import pandas as pd
import os, sys
import logging
import datetime
import time


ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../python_scripts'))
sys.path.append(ab_path)

# Defined Libraries
from dataFetcher import DataFetcher  # Import DataFetcher class
from paths_logging import PathManager  # Import create_xl_folder_path function
from initializeVariables import InitVars  # Import initializeVariables class

class DataProcessor:

    def __init__(self):
        self.path_manager = PathManager()
        self.dataFetcher = DataFetcher()
        self.init_vars = InitVars()


    def export_to_excel(self, df, filename, expiry_date):
        xl_folder_path = self.path_manager.create_xl_folder_path()
        try:
            # Create the full file path
            name = f"{filename}_{expiry_date}.xlsx"
            file_path = os.path.join(xl_folder_path, name)

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



    def fetch_and_process_data(self, exp_date):
        print("Fetching and processing data for", exp_date, "at", datetime.datetime.now().replace(microsecond=0))
        logging.info("Fetching and processing data for %s", exp_date)

        # Nifty data
        logging.info("Fetching Nifty data...")
        start_fetch = time.time()
        nifty_nearest, df_nifty_list = self.dataFetcher.fetch_data(self.init_vars.number, self.init_vars.step["nf"], self.init_vars.stock["nf"], self.init_vars.urls["url_nf"], exp_date)

        # Export data to Excel for Nifty
        for i, df_nifty in enumerate(df_nifty_list):
            self.export_to_excel(df_nifty, "Nifty_Data", exp_date[i])

        end_fetch = time.time()
        # Calculate the time taken during this iteration
        elapsed_time = end_fetch - start_fetch
        print("Time elapsed to fetch and save Nifty data =", int(elapsed_time), "seconds")
        logging.info("Time elapsed to fetch and save Nifty data = %s seconds", str(int(elapsed_time)))

        # Bank Nifty data
        logging.info("Fetching Bank Nifty data...")
        start_fetch = time.time()
        bank_nifty_nearest, df_bank_nifty_list = self.dataFetcher.fetch_data(self.init_vars.number, self.init_vars.step["bnf"], self.init_vars.stock["bnf"], self.init_vars.urls["url_bnf"], exp_date)

        # Export data to Excel for Bank Nifty
        for i, df_bank_nifty in enumerate(df_bank_nifty_list):
            self.export_to_excel(df_bank_nifty, "Bank_Nifty_Data", exp_date[i])

        end_fetch = time.time()
        # Calculate the time taken during this iteration
        elapsed_time = end_fetch - start_fetch
        print("Time elapsed to fetch and save Bank Nifty data =", int(elapsed_time), "seconds")
        logging.info("Time elapsed to fetch and save Bank Nifty data = %s seconds", str(int(elapsed_time)))

        return nifty_nearest, bank_nifty_nearest
