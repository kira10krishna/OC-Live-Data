import math
import json
import os
import sys
import asyncio
from initializeVariables import InitVars
from sessionRequests import SessionManager

ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../python_scripts'))
sys.path.append(ab_path)

class StrikeCalculator:
    def __init__(self):
        self.vars = InitVars()
        # self.columnsWanted, self.number, self.step, self.stock, self.headURL, self.apiURL, self.headers = init_vars.get_variables()

    def round_nearest(self, x, num=50):
        return int(math.ceil(float(x) / num) * num)

    def nearest_strike_bnf(self, x):
        return self.round_nearest(x, self.vars.step["bnf"])

    def nearest_strike_nf(self, x):
        return self.round_nearest(x, self.vars.step["nf"])

class OpenInterestCalculator:
    def __init__(self):
        self.session_manager = SessionManager()
        self.responseTexts = None

    async def highest_oi_CE(self, num, step, nearest):
        strike = nearest - (step * num)
        start_strike = nearest - (step * num)
        print(start_strike)
        try:
            self.responseTexts = await self.session_manager.getAPIdata()
            # print(response_texts[0])
            if self.responseTexts[1] is None:
                print("Failed to get data from the server.")
                return None

            data = json.loads(self.responseTexts[1])
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
        except Exception as e:
            # Handle exceptions here, log the error, and possibly return a default value
            print(f"An error occurred: {e}")
            return None

    async def highest_oi_PE(self, num, step, nearest):
        strike = nearest - (step * num)
        start_strike = nearest - (step * num)
        try:
            # self.responseTexts = await self.session_manager.getAPIdata()
            if self.responseTexts[1] is None:
                print("Failed to get data from the server.")
                return None

            data = json.loads(self.responseTexts[1])
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
        except Exception as e:
            # Handle exceptions here, log the error, and possibly return a default value
            print(f"An error occurred: {e}")
            return None

# Example usage in an asynchronous context
async def main():
    sc = StrikeCalculator()
    OI_calculator = OpenInterestCalculator()
    ul = 19265
    nearest = sc.nearest_strike_nf(ul)
    # url = sc.apiURL["nf"]  # Replace with your API endpoint
    print("number = ", sc.vars.number)
    print("step =", sc.vars.step['bnf'])
    print("Nearest =", nearest)
    # print("url =", url)
    max_oi_ce = await OI_calculator.highest_oi_CE(sc.vars.number, sc.vars.step['bnf'], nearest)
    max_oi_pe = await OI_calculator.highest_oi_PE(sc.vars.number, sc.vars.step['bnf'], nearest)

    if max_oi_ce is not None:
        print(f"Highest OI CE of BankNifty: {max_oi_ce}")
    else:
        print("Failed to calculate Highest OI CE")

    if max_oi_pe is not None:
        print(f"Highest OI PE of BankNifty: {max_oi_pe}")
    else:
        print("Failed to calculate Highest OI PE")

if __name__ == "__main__":
    asyncio.run(main())