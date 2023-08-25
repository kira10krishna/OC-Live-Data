# Pre-defined Libraries
import math
import json
import os, sys

ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../python_scripts'))
sys.path.append(ab_path)

# User-defined Libraries
from initializeVariables import InitVars
from sessionMethods import SessionManager

class StrikeCalculator:
    def __init__(self):
        init_vars = InitVars()
        self.columnsWanted, self.number, self.step, self.stock, self.urls, self.headers = init_vars.get_variables()

    def round_nearest(self, x, num=50):
        return int(math.ceil(float(x) / num) * num)

    def nearest_strike_bnf(self, x):
        return self.round_nearest(x, self.step["bnf"])

    def nearest_strike_nf(self, x):
        return self.round_nearest(x, self.step["nf"])

class OpenInterestCalculator:
    def __init__(self):
        self.session_manager = SessionManager()

    def highest_oi_CE(self, num, step, nearest, url):
        strike = nearest - (step * num)
        start_strike = nearest - (step * num)
        response_text = self.session_manager.get_data_with_retry(url)
        data = json.loads(response_text)
        currExpiryDate = data["records"]["expiryDates"][0]
        max_oi = 0
        max_oi_strike = 0
        for item in data['records']['data']:
            if item["expiryDate"] == currExpiryDate:
                if item["strikePrice"] == strike and item["strikePrice"] < start_strike + (step * num * 2):
                    if item["CE"]["openInterest"] > max_oi:
                        max_oi = item["CE"]["openInterest"]
                        max_oi_strike = item["strikePrice"]
                    strike = strike + step
        return max_oi_strike

    def highest_oi_PE(self, num, step, nearest, url):
        strike = nearest - (step * num)
        start_strike = nearest - (step * num)
        response_text = self.session_manager.get_data_with_retry(url)
        data = json.loads(response_text)
        currExpiryDate = data["records"]["expiryDates"][0]
        max_oi = 0
        max_oi_strike = 0
        for item in data['records']['data']:
            if item["expiryDate"] == currExpiryDate:
                if item["strikePrice"] == strike and item["strikePrice"] < start_strike + (step * num * 2):
                    if item["PE"]["openInterest"] > max_oi:
                        max_oi = item["PE"]["openInterest"]
                        max_oi_strike = item["strikePrice"]
                    strike = strike + step
        return max_oi_strike