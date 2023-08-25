# Pre-defined Libraries
import sqlite3

# Defined Libraries
import paths_logging


file_path = paths_logging.create_db_folder_path()

def createTableIfNotExists():
    conn = sqlite3.connect(file_path)
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



# Function to store nf_SP and bnf_SP in the database
def store_strike_prices(nf_SP, bnf_SP):
    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()
    
    # Insert or update the nf_SP and bnf_SP values in the database
    cursor.execute("INSERT INTO strike_prices (dateTime, nf_SP, bnf_SP) VALUES (datetime('now', 'localtime'), ?, ?)", (nf_SP, bnf_SP))
    
    conn.commit()
    conn.close()



def fetch_strike_prices():
    try:
        conn = sqlite3.connect(file_path)
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