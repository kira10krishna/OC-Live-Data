# Pre-defined Libraries
import datetime, time

class MarketTimings:
    def __init__(self):
        self.start_time = datetime.time(9, 0)
        self.end_time = datetime.time(15, 30)

    def wait_until_market_open(self):
        current_time = datetime.datetime.now().time()
        while current_time < self.start_time:
            current_time = datetime.datetime.now().time()
            time.sleep(1)

    def is_market_open(self):
        current_time = datetime.datetime.now().time()
        return self.start_time <= current_time <= self.end_time