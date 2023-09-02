
class InitVars:
    def __init__(self):
        self.columnsWanted = ['strikePrice', 'expiryDate', 'openInterest', 'changeinOpenInterest', 'pchangeinOpenInterest', 'totalTradedVolume', 'impliedVolatility', 'lastPrice', 'change', 'pChange','totalBuyQuantity', 'totalSellQuantity', 'underlyingValue']
        self.number = 3
        self.step = {"nf": 50, "bnf": 100}
        self.stock = {"nf": "NIFTY 50", "bnf": "NIFTY BANK"}

        # Variables for Urls to fetch Data
        self.headURL = {
            "oc": "https://www.nseindia.com/option-chain",
            "all_indices": "https://www.nseindia.com/api/allIndices"
        }
        self.apiURL = {
            "bnf": "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY",
            "nf": "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY",
        }

        # Headers
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8',
            'accept-encoding': 'gzip, deflate, br'
        }

    def get_variables(self):
        return self.columnsWanted, self.number, self.step, self.stock, self.headURL, self.apiURL, self.headers