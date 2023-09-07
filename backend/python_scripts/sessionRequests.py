import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry
import asyncio as aio
import logging
import os, sys, time, json

ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../python_scripts'))
sys.path.append(ab_path)

# Defined Libraries

from paths_logging import PathManager
from initializeVariables import InitVars


class SessionManager:
    def __init__(self):
        self.vars = InitVars()
        self.cookies = None
        self.session = None


    async def set_cookie(self):
        try:
            async with self.session.get(self.vars.headURL["oc"], headers=self.vars.headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                self.cookies = response.cookies
                # await self.session.close()
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
                    # print("json data collected from", url)
                    logging.info("json data collected from %s", url)
                    return response_text
                else:  
                    logging.warning("Request returned empty response.")     
        except aiohttp.ClientError as e:
            # print("Request error: %s", e)
            logging.error("Request error: %s", e)
    

    async def getAPIdata(self, sIndexes):
        try:
            async with aiohttp.ClientSession() as self.session:
                async with aio.TaskGroup() as tg:
                    cookies = await tg.create_task(self.set_cookie())
                    if cookies:
                        URLs = [self.vars.apiURL[sIndex] for sIndex in sIndexes]
                        tasks = [(sIndex, self.getDataTasks(url)) for sIndex,url in zip(sIndexes,URLs)]
                        results = await aio.gather(*[task[1] for task in tasks], return_exceptions=True)
                        data_dict = {url: json.loads(result) for url, result in zip(sIndexes, results)}
                        return data_dict
        except aiohttp.ClientError as e:
            logging.error("Request error: %s", e)



# Define an asynchronous function to run the asyncio code
async def main():
    try:   
        # Set up logging config
        PathManager()
        start_fetch = time.time()
        session_manager = SessionManager()
        
        res = await session_manager.getAPIdata(['all_indices','nf','bnf'])
        print("Result =\n",res.keys())
        end_fetch = time.time()
        elapsed_time = end_fetch - start_fetch
        print("Total time elapsed =", elapsed_time, "seconds")
    finally:
        # Don't manually close the session here if you're using asyncio.run()
        pass

if __name__ == "__main__":
    # Run the asynchronous code within an event loop
    aio.run(main())