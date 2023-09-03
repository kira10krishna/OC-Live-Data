import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry
import asyncio as aio
import logging
from paths_logging import PathManager
from initializeVariables import InitVars


# Set up logging config
path_manager = PathManager()

class SessionManager:
    def __init__(self):
        self.vars = InitVars()
        # self.columnsWanted, self.number, self.step, self.stock, self.headURL, self.apiURL, self.headers = init_vars.get_variables()
        self.cookies = None
        self.session = aiohttp.ClientSession()


    async def set_cookie(self):
        try:
            async with self.session.get(self.vars.headURL["oc"], headers=self.vars.headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                self.cookies = response.cookies
                await self.session.close()
                return self.cookies     
        except aiohttp.ClientError as e:
            logging.error("Request error in set_cookie: %s", e)
            return None


    async def getDataTasks(self, url):
        retry_options = ExponentialRetry(attempts=5)
        retry_client = RetryClient(self.session, retry_options= retry_options, timeout=aiohttp.ClientTimeout(total=10), raise_for_status= True)
        try:
            async with retry_client.get(url, headers=self.vars.headers, cookies=self.cookies) as response:
                response_text = await response.text()
                if response_text:
                    # print("Response text collected from", url)
                    logging.info("Response text collected from %s", url)
                    return response_text
                else:  
                    logging.warning("Request returned empty response.")     
        except aiohttp.ClientError as e:
            print("Request error: %s", e)
            logging.error("Request error: %s", e)
    
    async def getAPIdata(self, urls):
        try:
            cookies = await self.set_cookie()
            if cookies:
                async with aiohttp.ClientSession() as self.session:
                    results = await aio.gather(*[self.getDataTasks(url) for url in urls], return_exceptions=True)
                return results
        except aiohttp.ClientError as e:
            logging.error("Request error: %s", e)



# Define an asynchronous function to run the asyncio code
async def main():
    try:
        session_manager = SessionManager()
        URLs = [session_manager.vars.apiURL['nf'],session_manager.vars.apiURL['bnf']]
        await session_manager.getAPIdata(URLs)
    finally:
        # Don't manually close the session here if you're using asyncio.run()
        pass

if __name__ == "__main__":
    # Run the asynchronous code within an event loop
    aio.run(main())