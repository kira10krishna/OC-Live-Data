import requests
import os,sys

ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../python_scripts'))
sys.path.append(ab_path)

import paths_logging
import logging
import initializeVariables


# Set up logging config
paths_logging.setup_logging()

# Initialize Variables
columnsWanted,number,step,stock,urls,headers = initializeVariables.initVars()

# session variables and methods
sess = requests.Session()
#cookies = dict()

def set_cookie():
    try:
        request = sess.get(urls["url_oc"], headers=headers, timeout=5)
        cookies = dict(request.cookies)
        return cookies
    except requests.exceptions.Timeout as e:
        logging.error("Request timeout error: %s", e)
        return None

def make_request(url, cookies):
    return sess.get(url, headers=headers, timeout=20, cookies=cookies)

def get_data_with_retry(url, max_retries=5, retry_delay=2):
    import time
    for attempt in range(max_retries):
        if attempt > 0:
            print("Retrying... Attempt =", attempt+1)
            logging.info("Retrying... Attempt - %s", attempt+1)
        try:
            cookies = set_cookie()
            if cookies: # is not None:
                response = make_request(url, cookies)
                if response.status_code == 200:
                    #logging.info("Response data collected successfully in attempt %s", attempt)
                    return response.text  # Return the response data if successful
                else:
                    # Retry for non-200 status codes
                    logging.warning("Request returned non-200 status code: %s", response.status_code)                    
        except requests.exceptions.Timeout as e:
            logging.error("Request timeout error: %s", e)
        except requests.exceptions.RequestException as e:
            logging.error("Request error: %s", e)
        except TypeError as e:
            logging.error("Error fetching cookies: %s", e)
        time.sleep(retry_delay)  # Wait for a few seconds before retrying

    # If all retries failed, log an error and return an empty string
    logging.error("Request failed after multiple retries.")
    return ""