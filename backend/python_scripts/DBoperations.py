# Pre-defined Libraries
import os, sys
import sqlite3

ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../python_scripts'))
sys.path.append(ab_path)

# User-defined Libraries
from paths_logging import PathManager

class DatabaseManager:
    def __init__(self):
        self.path_manager = PathManager()
        self.file_path = self.path_manager.create_db_folder_path()

    def create_table_if_not_exists(self):
        conn = sqlite3.connect(self.file_path)
        cursor = conn.cursor()
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

    def store_strike_prices(self, nf_SP, bnf_SP):
        conn = sqlite3.connect(self.file_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO strike_prices (dateTime, nf_SP, bnf_SP) VALUES (datetime('now', 'localtime'), ?, ?)", (nf_SP, bnf_SP))
        conn.commit()
        conn.close()

    def fetch_strike_prices(self):
        try:
            conn = sqlite3.connect(self.file_path)
            cursor = conn.cursor()
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