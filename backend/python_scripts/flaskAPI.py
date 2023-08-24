from flask import Flask, request, jsonify
import pandas as pd
import sqlite3
import requests
import os

app = Flask(__name__)

# Define a route for the root URL ("/")
@app.route('/')
def index():
    r = requests.get('http://127.0.0.1:5000/api/strikePrice')
    return r.json()

# Get the current directory of the Flask app
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define a relative path to the Excel file
file_path = os.path.join(current_dir, 'saved data', 'Data for 24-Aug-2023', 'Nifty_Data_24-Aug-2023.xlsx')

# Read Excel data and convert to JSON
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


folder_path = os.path.join(current_dir,"DB files")

if not os.path.exists(folder_path):
    try:
        os.makedirs(folder_path)
    except Exception as e:
        print(e)

DB_file_path = os.path.join(folder_path,'strike_prices.db')
# Initialize the SQLite database
conn = sqlite3.connect(DB_file_path)
cursor = conn.cursor()
# Create a table to store nf_SP and bnf_SP
cursor.execute('''
    CREATE TABLE IF NOT EXISTS strike_prices (
        id INTEGER PRIMARY KEY,
        dateTime DATETIME,
        nf_SP REAL,
        bnf_SP REAL
    )
''')
conn.commit()
conn.close()

def fetch_strike_prices():
    try:
        conn = sqlite3.connect(DB_file_path)
        cursor = conn.cursor()

        # Retrieve the nf_SP and bnf_SP values from the database
        cursor.execute('SELECT dateTime, nf_SP, bnf_SP FROM strike_prices ORDER BY dateTime DESC LIMIT 1')
        result = cursor.fetchone()

        conn.close()

        if result:
            dateTime, nf_SP, bnf_SP = result
            return dateTime, nf_SP, bnf_SP
        else:
            return None, None, None

    except Exception as e:
        raise e  # You can log or handle the exception as needed


@app.route('/api/strikePrice')
def get_strike_price():
    try:
        # Retrieve nf_SP and bnf_SP from the database
        dateTime, nf_SP, bnf_SP = fetch_strike_prices()

        if nf_SP is not None and bnf_SP is not None:
            return jsonify({'dateTime': dateTime,'nf_SP': nf_SP, 'bnf_SP': bnf_SP})
        else:
            return jsonify({'error': 'Strike price data not available'}), 404  # Return a 404 status code if data is not available

    except Exception as e:
        return jsonify({'error': 'An error occurred while processing your request'}), 500  # Return a 500 status code for server errors


if __name__ == '__main__':
    app.run(debug=True)