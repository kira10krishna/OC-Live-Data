from flask import Flask, jsonify
import pandas as pd
import sqlite3

app = Flask(__name__)


# Replace with the path to your Excel file
file_path = "backend/data/Data_for_24-Aug-2023/Nifty_Data_24-Aug-2023.xlsx"

# Read Excel data and convert to JSON
df = pd.read_excel(file_path)
df_json = df.to_json(orient="split")

@app.route('/api/dfData')
def get_df_data():
    return jsonify({'df': df_json})



# Initialize the SQLite database
conn = sqlite3.connect('strike_prices.db')
cursor = conn.cursor()
# Create a table to store nf_SP and bnf_SP
cursor.execute('''
    CREATE TABLE IF NOT EXISTS strike_prices (
        id INTEGER PRIMARY KEY,
        nf_SP REAL,
        bnf_SP REAL
    )
''')
conn.commit()
conn.close()

def fetch_strike_prices():
    try:
        conn = sqlite3.connect('strike_prices.db')
        cursor = conn.cursor()

        # Retrieve the nf_SP and bnf_SP values from the database
        cursor.execute('SELECT nf_SP, bnf_SP FROM strike_prices WHERE id = 1')
        result = cursor.fetchone()

        conn.close()

        if result:
            nf_SP, bnf_SP = result
            return nf_SP, bnf_SP
        else:
            return None, None

    except Exception as e:
        raise e  # You can log or handle the exception as needed


@app.route('/api/strikePrice')
def get_strike_price():
    try:
        # Retrieve nf_SP and bnf_SP from the database
        nf_SP, bnf_SP = fetch_strike_prices()

        if nf_SP is not None and bnf_SP is not None:
            return jsonify({'nf_SP': nf_SP, 'bnf_SP': bnf_SP})
        else:
            return jsonify({'error': 'Strike price data not available'}), 404  # Return a 404 status code if data is not available

    except Exception as e:
        return jsonify({'error': 'An error occurred while processing your request'}), 500  # Return a 500 status code for server errors


if __name__ == '__main__':
    app.run(debug=True)