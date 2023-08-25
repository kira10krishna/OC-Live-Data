import os, sys

ab_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../python_scripts'))
sys.path.append(ab_path)


# Import the app instance from RestfulAPI.py
from python_scripts.RestfulAPI import app


# Initialize app.run
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8989, debug=True)

