# Pre-defined Libraries
from flask import Flask, request, jsonify
import pandas as pd
import datetime
import requests
import os

# Defined Libraries
import paths_logging
import DBoperations

app = Flask(__name__)

# Define a route for the root URL ("/")
@app.route('/')
def index():
    return "Hello, I am flask API, up  and running."


# Read Excel data and convert to JSON
folderPath = paths_logging.savedData_folder_path()
# Define a relative path to the Excel file
file_path = os.path.join(folderPath, f"Data for {datetime.date.today().strftime('%d-%b-%Y')}", 'Nifty_Data_31-Aug-2023.xlsx')

df = pd.read_excel(file_path)
df_json = df.to_json(orient="split")

@app.route('/api/dfData')
def get_df_data():
    return jsonify({'df': df_json})

@app.route('/api/getChartData')
def get_chart_data():
    r = requests.get('http://127.0.0.1:5000/api/strikePrice')
    json_SP = r.json()
    strike_price = json_SP["nf_SP"]
    df_filtered = df[df['strikePrice'] == strike_price]
    chart_data = {
        'x': df_filtered['Date'].tolist(),
        'lastPrice_CE': df_filtered['lastPrice_CE'].tolist(),
        'lastPrice_PE': df_filtered['lastPrice_PE'].tolist(),
        # Add more data fields as needed
    }
    return jsonify(chart_data)


# Initialize the SQLite database
DBoperations.createTableIfNotExists()

@app.route('/api/strikePrice')
def get_strike_price():
    try:
        # Retrieve nf_SP and bnf_SP from the database
        dateTime, nf_SP, bnf_SP = DBoperations.fetch_strike_prices()

        if nf_SP is not None and bnf_SP is not None:
            return jsonify({'dateTime': dateTime,'nf_SP': nf_SP, 'bnf_SP': bnf_SP})
        else:
            return jsonify({'error': 'Strike price data not available'}), 404  # Return a 404 status code if data is not available

    except Exception as e:
        return jsonify({'error': 'An error occurred while processing your request'}), 500  # Return a 500 status code for server errors


if __name__ == '__main__':
    app.run(debug=True)