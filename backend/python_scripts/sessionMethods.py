# Pre-defined Libraries
import requests
import logging
import time
import os, sys

ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../python_scripts'))
sys.path.append(ab_path)

# User-defined Libraries
from paths_logging import PathManager
from initializeVariables import InitVars


# Set up logging config
path_manager = PathManager()
path_manager.setup_logging()

# Initialize Variables

# columnsWanted, number, step, stock, urls, headers = initializeVariables.InitVars()

class SessionManager:
    def __init__(self):
        init_vars = InitVars()
        self.columnsWanted, self.number, self.step, self.stock, self.urls, self.headers = init_vars.get_variables()
        self.sess = requests.Session()

    def set_cookie(self):
        try:
            request = self.sess.get(self.urls["url_oc"], headers=self.headers, timeout=5)
            self.cookies = dict(request.cookies)
            return self.cookies
        except requests.exceptions.Timeout as e:
            logging.error("Request timeout error: %s", e)
            return None

    def make_request(self, url):
        return self.sess.get(url, headers=self.headers, timeout=20, cookies=self.cookies)

    def get_data_with_retry(self, url, max_retries=5, retry_delay=2):
        for attempt in range(max_retries):
            if attempt > 0:
                print("Retrying... Attempt =", attempt + 1)
                logging.info("Retrying... Attempt - %s", attempt + 1)
            try:
                cookies = self.set_cookie()
                if cookies:
                    response = self.make_request(url)
                    if response.status_code == 200:
                        return response.text
                    else:
                        logging.warning("Request returned non-200 status code: %s", response.status_code)
            except requests.exceptions.Timeout as e:
                logging.error("Request timeout error: %s", e)
            except requests.exceptions.RequestException as e:
                logging.error("Request error: %s", e)
            except TypeError as e:
                logging.error("Error fetching cookies: %s", e)
            time.sleep(retry_delay)

        logging.error("Request failed after multiple retries.")
        return ""