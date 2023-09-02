import asyncio
import datetime
import logging
import os, sys

ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../python_scripts'))
sys.path.append(ab_path)

import paths_logging

class MarketTimings:
    def __init__(self):
        self.start_time = datetime.time(8, 0)
        self.end_time = datetime.time(10, 19)
        self.market_open_event = asyncio.Event()

    async def wait_until_market_open(self):
        try:
            current_time = datetime.datetime.now().time()

            if current_time >= self.start_time:
                # The market is already open, no need to wait.
                return

            # Calculate the time until the market opens.
            time_until_open = datetime.datetime.combine(datetime.date.today(), self.start_time) - datetime.datetime.now()

            if time_until_open.total_seconds() < 0:
                raise Exception("Market open time calculation error")

            # Schedule the market_open_event to be set when the market opens.
            asyncio.get_event_loop().call_later(time_until_open.total_seconds(), self.market_open_event.set)

            # Wait for the market_open_event to be set.
            await self.market_open_event.wait()
        except Exception as e:
            logging.error(f"Error in wait_until_market_open: {e}")

    async def is_market_open(self):
        try:
            current_time = datetime.datetime.now().time()
            return self.start_time <= current_time <= self.end_time
        except Exception as e:
            logging.error(f"Error in is_market_open: {e}")

async def main():
    try:
        paths_logging.PathManager()

        market_timings = MarketTimings()

        # Wait until the market opens
        await market_timings.wait_until_market_open()

        # Check if the market is open
        is_open = await market_timings.is_market_open()
        if is_open:
            print("The market is currently open.")
            logging.info("The market is currently open.")
        else:
            print("The market is currently closed.")
            logging.info("The market is currently closed.")
    except Exception as e:
        logging.error(f"Error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main())
