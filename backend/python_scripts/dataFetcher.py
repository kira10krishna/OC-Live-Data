# Pre-defined Libraries
import requests
import json
import pandas as pd
import os, sys
import logging
import datetime

ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../python_scripts'))
sys.path.append(ab_path)

# User-defined Libraries
from initializeVariables import InitVars
from paths_logging import PathManager
from sessionMethods import SessionManager  # Import SessionManager class
from marketDataCalcs import StrikeCalculator



class DataFetcher:
    def __init__(self):
        init_vars = InitVars()
        self.columnsWanted, self.number, self.step, self.stock, self.urls, self.headers = init_vars.get_variables()
        self.sess = SessionManager()
        self.strike_calc = StrikeCalculator()
        self.ul = None
        self.nearest = None

    def set_header(self, stock):
        response_text = self.sess.get_data_with_retry(self.urls["url_indices"])
        data = json.loads(response_text)
        for index in data["data"]:
            if index["index"] == stock:
                self.ul = index["last"]
        if stock == "NIFTY 50":
            self.nearest = self.strike_calc.nearest_strike_nf(self.ul)
        elif stock == "NIFTY BANK":
            self.nearest = self.strike_calc.nearest_strike_bnf(self.ul)
        return self.nearest

    def load_dataframes(self, num, step, expDate, url):
        strike = self.nearest - (step * num)
        start_strike = self.nearest - (step * num)
        response_text = self.sess.get_data_with_retry(url)
        try:
            data = json.loads(response_text)
            df_list = []
            for expiry_date in expDate:
                df = pd.DataFrame()
                df_ce = pd.DataFrame()
                df_pe = pd.DataFrame()
                temp_df_ce = pd.DataFrame()
                temp_df_pe = pd.DataFrame()
                strike = self.nearest - (step * num)
                start_strike = self.nearest - (step * num)
                for item in data['records']['data']:
                    if item["expiryDate"] == expiry_date:
                        if item["strikePrice"] == strike and item["strikePrice"] < start_strike + (step * num * 2):
                            temp_df_ce = pd.DataFrame(item['CE'], index=[strike], columns=self.columnsWanted)
                            temp_df_pe = pd.DataFrame(item['PE'], index=[strike], columns=self.columnsWanted)
                            strike = strike + step
                            df_ce = pd.concat([df_ce, temp_df_ce], ignore_index=True)
                            df_pe = pd.concat([df_pe, temp_df_pe], ignore_index=True)
                df = pd.merge(df_ce, df_pe, how="inner", on="strikePrice", suffixes=("_CE", "_PE"))
                df.insert(loc=0, column='Date', value=datetime.datetime.now().replace(microsecond=0))
                df.drop(columns=["expiryDate_PE", "underlyingValue_CE"], inplace=True)
                df_list.append(df)
            return df_list

        except json.JSONDecodeError as e:
            logging.error("JSON decoding error: %s", e)
            logging.error("JSON Response: %s", response_text)
            return []
        except Exception as e:
            logging.error("An error occurred while loading or processing dataframe: %s", e)
            return []

    def fetch_data(self, num, step, stockIndex, indexUrl, expDate):
        self.nearest = self.set_header(stockIndex)
        df_list = self.load_dataframes(num, step, expDate, indexUrl)
        return self.nearest, df_list

if __name__ == "__main__":
    # Set up logging config
    path_manager = PathManager()
    path_manager.setup_logging()
    data_fetcher = DataFetcher()
