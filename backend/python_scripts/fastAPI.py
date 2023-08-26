# Pre-defined Libraries
from fastapi import FastAPI, HTTPException, BackgroundTasks
import pandas as pd
import os, sys
import asyncio

ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../python_scripts'))
sys.path.append(ab_path)

# User-defined Libraries
from python_scripts.paths_logging import PathManager
from python_scripts.DBoperations import DatabaseManager
from python_scripts.Fetch_NSE_OC_data import MainApplication

app = FastAPI()

path_manager = PathManager()
db_manager = DatabaseManager()
db_manager.create_table_if_not_exists()
main_app = MainApplication()

class MainFunctionExecutor:
    def __init__(self, main_app_instance):
        self.main_function_lock = asyncio.Lock()
        self.main_function_executing = False
        self.mainApp = main_app

    async def main_function(self):
        async with self.main_function_lock:
            if not self.main_function_executing:
                self.main_function_executing = True
                await self.mainApp.main()
                print("Main function executed")
        self.main_function_executing = False

main_executor = MainFunctionExecutor(main_app)

@app.get('/')
def index():
    return "Hello, I am FastAPI, up and running. Welcome to the new fast moving world"

@app.get('/run-main-code')
async def run_main_code(background_tasks: BackgroundTasks):
    background_tasks.add_task(main_executor.main_function)
    return "Main code execution triggered successfully"

@app.get('/api/strikePrice')
async def get_strike_price():
    try:
        dateTime, nf_SP, bnf_SP = db_manager.fetch_strike_prices()

        if nf_SP is not None and bnf_SP is not None:
            return {'dateTime': dateTime, 'nf_SP': nf_SP, 'bnf_SP': bnf_SP}
        else:
            raise HTTPException(status_code=404, detail="Strike price data not available")

    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")

@app.get('/api/exported-excel-files')
async def get_exported_excel_files():
    try:
        xl_folder_path = path_manager.create_xl_folder_path()
        all_files = os.listdir(xl_folder_path)
        excel_files = [f for f in all_files if f.endswith('.xlsx')]
        excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(xl_folder_path, x)), reverse=True)
        exported_files = excel_files[:6]

        return {'latest_excel_files': exported_files}

    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5001, debug = True)