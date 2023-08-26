# Pre-defined Libraries
from flask import Flask, request, jsonify
import pandas as pd
# import datetime
# import requests
import os
import sys
import threading
#import logging


ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../python_scripts'))
sys.path.append(ab_path)


# User-defined Libraries
from python_scripts.paths_logging import PathManager
from python_scripts.DBoperations import DatabaseManager
from python_scripts.Fetch_NSE_OC_data import MainApplication

app = Flask(__name__)


# Configure logging to print to the console
#logging.basicConfig(level=logging.DEBUG)

# Define a route for the root URL ("/")
@app.route('/')
def index():
    return "Helleo, I am flask API, up and running."


# Initialize the path manager
path_manager = PathManager()

# Initialize the SQLite database
db_manager = DatabaseManager()
db_manager.create_table_if_not_exists()

# Create an instance of the MainApplication
main_app = MainApplication()

class MainFunctionExecutor:
    def __init__(self, main_app_instance):
        self.main_function_lock = threading.Lock()
        self.main_function_executing = False
        self.mainApp = main_app

    def main_function(self):
        with self.main_function_lock:
            if not self.main_function_executing:
                self.main_function_executing = True
                # Call the function or code you want to execute in your main file
                self.mainApp.main()
                print("Main function executed")
        self.main_function_executing = False

# Create an instance of the MainFunctionExecutor
main_executor = MainFunctionExecutor(main_app)

@app.route('/run-main-code', methods=['GET'])
def run_main_code():
    if request.method == 'GET':
        # Run the main function in a separate thread
        thread = threading.Thread(target=main_executor.main_function)
        thread.start()
        return "Main code execution triggered successfully"
    else:
        return "Method other than POST not allowed for this endpoint"
    

@app.route('/api/strikePrice', methods=['GET'])
def get_strike_price():
    try:
        # Retrieve nf_SP and bnf_SP from the database
        dateTime, nf_SP, bnf_SP = db_manager.fetch_strike_prices()

        if nf_SP is not None and bnf_SP is not None:
            return jsonify({'dateTime': dateTime,'nf_SP': nf_SP, 'bnf_SP': bnf_SP})
        else:
            return jsonify({'error': 'Strike price data not available'}), 404  # Return a 404 status code if data is not available

    except Exception as e:
        return jsonify({'error': 'An error occurred while processing your request'}), 500  # Return a 500 status code for server errors


@app.route('/api/exported-excel-files', methods=['GET'])
def get_exported_excel_files():
    try:
        # Specify the folder where Excel files are stored
        xl_folder_path = path_manager.create_xl_folder_path()

        # List all files in the folder
        all_files = os.listdir(xl_folder_path)

        # Filter for Excel files (if needed, you can add more specific file filtering logic)
        excel_files = [f for f in all_files if f.endswith('.xlsx')]

        # Sort files by modification time (most recent first)
        excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(xl_folder_path, x)), reverse=True)

        # Get the names of the latest 6 Excel files
        exported_files = excel_files[:6]

        return jsonify({'latest_excel_files': exported_files})

    except Exception as e:
        return jsonify({'error': 'An error occurred while processing your request', 'Error message': e}), 500



if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)



# df = pd.read_excel(file_path)
# df_json = df.to_json(orient="split")

# @app.route('/api/dfData')
# def get_df_data():
#     return jsonify({'df': df_json})

# @app.route('/api/getChartData', methods=['GET'])
# def get_chart_data():
#     r = requests.get('http://127.0.0.1:8989/api/strikePrice')
#     json_SP = r.json()
#     strike_price = json_SP["nf_SP"]
#     df_filtered = df[df['strikePrice'] == strike_price]
#     chart_data = {
#         'x': df_filtered['Date'].tolist(),
#         'lastPrice_CE': df_filtered['lastPrice_CE'].tolist(),
#         'lastPrice_PE': df_filtered['lastPrice_PE'].tolist(),
#         # Add more data fields as needed
#     }
#     return jsonify(chart_data)