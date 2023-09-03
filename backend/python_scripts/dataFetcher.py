import json
import pandas as pd
import os, sys
import logging
import datetime
import asyncio as aio

ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../python_scripts'))
sys.path.append(ab_path)

from paths_logging import PathManager
from sessionRequests import SessionManager
from marketDataCalcs import StrikeCalculator
from expiryDateCalcs import ExpiryCalculator

class DataFetcher:
    def __init__(self):
        self.strike_calc = StrikeCalculator()
        self.sess, self.data, self.ul, self.nearest = None, None, None, None
        self.df, self.df_ce, self.df_pe, self.temp_df_ce, self.temp_df_pe = None, None, None, None, None


    async def setNearest(self,sIndex,data):
        for index in data["data"]:
            if index["index"] == self.strike_calc.vars.stock[sIndex]:
                self.ul = index["last"]
        if self.strike_calc.vars.stock[sIndex] == "NIFTY 50":
            self.nearest = self.strike_calc.nearest_strike_nf(self.ul)
        elif self.strike_calc.vars.stock[sIndex] == "NIFTY BANK":
            self.nearest = self.strike_calc.nearest_strike_bnf(self.ul)
        return self.nearest
    
    async def loadDFsByExpiry(self, stockIndex, expDate):
        self.df, self.df_ce, self.df_pe, self.temp_df_ce, self.temp_df_pe = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        strike = self.nearest - (self.strike_calc.vars.step[stockIndex] * self.strike_calc.vars.number)
        start_strike = self.nearest - (self.strike_calc.vars.step[stockIndex] * self.strike_calc.vars.number)
        for item in self.data['records']['data']:
            if item["expiryDate"] == expDate:
                if item["strikePrice"] == strike and item["strikePrice"] < start_strike + (self.strike_calc.vars.step[stockIndex] * self.strike_calc.vars.number * 2):
                    self.temp_df_ce = pd.DataFrame(item['CE'], index=[strike], columns=self.strike_calc.vars.columnsWanted)
                    self.temp_df_pe = pd.DataFrame(item['PE'], index=[strike], columns=self.strike_calc.vars.columnsWanted)
                    strike = strike + self.sess.vars.step[stockIndex]
                    self.df_ce = pd.concat([self.df_ce, self.temp_df_ce], ignore_index=True)
                    self.df_pe = pd.concat([self.df_pe, self.temp_df_pe], ignore_index=True)
        self.df = pd.merge(self.df_ce, self.df_pe, how="inner", on="strikePrice", suffixes=("_CE", "_PE"))
        self.df.insert(loc=0, column='Date', value=datetime.datetime.now().replace(microsecond=0))
        self.df.drop(columns=["expiryDate_PE", "underlyingValue_CE"], inplace=True)
        return self.df

    async def loadStockDFs(self, stockIndex, expDates):
        try:
            self.sess = SessionManager()
            response_texts = await self.sess.getAPIdata([self.strike_calc.vars.apiURL["all_indices"], self.strike_calc.vars.apiURL[stockIndex]])
            self.data = json.loads(response_texts[0])
            await self.setNearest(stockIndex,self.data)
            self.data = json.loads(response_texts[1])
            df_list = await aio.gather(*[self.loadDFsByExpiry(stockIndex, expDate) for expDate in expDates], return_exceptions=True)
            return self.nearest, df_list
        except json.JSONDecodeError as e:
            logging.error("JSON decoding error: %s", e)
            logging.error("JSON Response: %s", response_texts[0])
            return []
        except Exception as e:
            logging.error("An error occurred while loading or processing dataframe: %s", e)
            return []


    async def getAllDFs(self, expDates):
        nf, bnf = await aio.gather(*[self.loadStockDFs(sIndex,expDates) for sIndex in ['nf','bnf']], return_exceptions=True)
        return nf, bnf



async def main():
    try:
        # Set up logging config
        PathManager()
        data_fetcher = DataFetcher()
        # sInd = list(data_fetcher.sess.vars.stock.keys())
        # nearest = await data_fetcher.setNearest(sInd[0])
        # print("nearest_nf = ", nearest)
        expDate = ExpiryCalculator()
        expDates = await expDate.expiry_dates()
        print("Expiry dates =", expDates)
        nf,bnf = await data_fetcher.getAllDFs(expDates)
        print("Nifty result = \n",nf[1][0])
        print("Bank Nifty result = \n",bnf[1][0])
    finally:
        pass


if __name__ == "__main__":
    # Run the asynchronous code within an event loop
    aio.run(main())