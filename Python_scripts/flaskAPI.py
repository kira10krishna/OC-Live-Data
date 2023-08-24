from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/strikePrice')
def get_strike_price():
    # Logic to fetch the strikePrice from your Python script
    
    strike_price = 1000  # Replace with your actual logic
    return jsonify({'strikePrice': strike_price})

if __name__ == '__main__':
    app.run(debug=True)