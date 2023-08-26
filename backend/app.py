import os, sys
import uvicorn
from fastapi import FastAPI

ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../python_scripts'))
sys.path.append(ab_path)

# Import your FastAPI app instance
from python_scripts.fastAPI import app

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=5000, debug=True)