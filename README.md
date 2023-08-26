# OC-Live-Data
Option chain live data display/save for each min whenever the market is open

There are some excel files for daily analysis of Stock EOD Analysis and OC Live data (refreshed each min, not saved)

Building Backend (python), RestfulAPIs (flask, python) and Frontend (react)

Upcoming Updates (Maybe):
- Add hoidays list and excute program only on non-holidays
- Add progress bar widget

Just run the program and enjoy.

Feel free to comment on the code



Execute the following in order:
    Step 1 : Creating virtual environment in root folder (OC-LIVE-DATA folder) -
        - python -m venv venv
        - Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
        - venv\Scripts\activate
        - cd backend\python_scripts
        - pip install -r requirements.txt
    Step 2 : Node modules in (frontend folder) -
        - npm install
        - npm install axios react-plotly.js
    Step 3 : You must have 2 terminals for this -
        To start Flask API run below command in /backend/python_scripts directory/:
            - python flaskAPI.py 
        To start react dev server run below command in /frontend directory/:
            - npm start
    

Note to self -
- Add logging for api requests


Current actions:-
- Learn get method and also other methods of API (again)
- Learn API testing and test all APIs

Next steps:-
- Check for all logging exceptions, place it wherever necessary
- Connect API by frontend, i.e., Fetch APIs at frontend (Frontend and API talking to each other)
- Prepare frontend development to display live charts
    

    
