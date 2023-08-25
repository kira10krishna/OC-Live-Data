# OC-Live-Data
Option chain live data display/save for each min whenever the market is open

There are some excel files for daily analysis of Stock EOD Analysis and OC Live data (refreshed each min, not saved)

What does this .ipynb it do ?
- Running this programs saves the option chain live data every single minute with self adjusting sleep timer for a minute
- Data is exported to excel file. Everyday a new excel file will be created
- Data is saved within the "Save data" folder. If no folder is there then it creates one
- Folder/File paths are given manually for now, due to personal use. Saved data folder is created inside "user/documents/Python Scripts"


Upcoming Updates:
- Adding hoidays list and excute program only on non-holidays
- Add progress bar widget
- Make python application instead of jupyter notebook file
- Display live charts through JS


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
- File name is static in app.py
- Add logging for api requests
- Build main python file in modular format

Current actions:-
- API building : (All api's are mostly built)
- Build a modular code for API
- Adjust app.py and flaskAPI.py to work in sync and is mainly app.py
- Learn get method and also other methods of API

Next steps:-
- Connect API by frontend, i.e., Fetch APIs at frontend (Frontend and API talking to each other)
- Prepare frontend development to display live charts
    

    
