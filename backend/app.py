from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import datetime
import os

app = Flask(__name__)
CORS(app)

# Replace this with your actual data file path
folder_path = os.path.join("data", f"Data for {(datetime.date.today()).strftime('%d-%b-%Y')}")
# data_file_path = 'data/chart_data.xlsx'
# data_file_path = os.path.join(folder_path, f"{filename}_{expiry_date}.xlsx")
data_file_path = os.path.join(folder_path, "Nifty_Data_24-Jul-2023.xlsx")


# Load data from Excel file
data_df = pd.read_excel(data_file_path)

@app.route('/api/getChartData', methods=['GET'])
def get_chart_data():
    strike_price = request.args.get('strike_price', type=int)
    df_filtered = data_df[data_df['strikePrice'] == strike_price]
    chart_data = {
        'x': df_filtered['Date'].tolist(),
        'lastPrice_CE': df_filtered['lastPrice_CE'].tolist(),
        'lastPrice_PE': df_filtered['lastPrice_PE'].tolist(),
        # Add more data fields as needed
    }
    return jsonify(chart_data)

if __name__ == '__main__':
    app.run(debug=True)