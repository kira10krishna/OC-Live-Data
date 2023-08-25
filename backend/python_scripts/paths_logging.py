import os
import datetime
import logging


# Get the current directory of the Flask app
def backend_path():
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return backend_dir

# Define path to the log file
def log_file_path():
    backend_dir = backend_path()
    logfile_path = os.path.join(backend_dir,"python_Scripts", "script_log.txt")
    return logfile_path

# Set up the logging config
def setup_logging():
    file_path = log_file_path()
    logging.basicConfig(
        filename=file_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"  # Use the desired time format here
        )
setup_logging()


# Saved Excel data paths
# Define a relative path to the folder of Excel file
def savedData_folder_path():
    backend_dir = backend_path()
    sd_folder_path = os.path.join(backend_dir, 'saved data')
    return sd_folder_path

def create_xl_folder_path():
    sd_folder_path = savedData_folder_path()
    xl_folder_path = os.path.join(sd_folder_path, f"Data for {datetime.date.today().strftime('%d-%b-%Y')}")
    if not os.path.exists(xl_folder_path):
        try:
            os.makedirs(xl_folder_path)
            # print("Created 'Saved data' folder.")
            logging.info("Created 'Saved data' folder.")
        except Exception as e:
            # print("Error creating 'Saved data' folder:", e)
            logging.info("Error creating 'Saved data' folder: %s", e)
    return xl_folder_path


# DB Paths -
# Define a relative path to the DB file
def db_folderfile_path():
    backend_dir = backend_path()
    folder_path = os.path.join(backend_dir, 'DB files')
    file_path = os.path.join(backend_dir, 'DB files','strike_prices.db')
    return folder_path, file_path

# Create DB folder paths if not found and return file path
def create_db_folder_path():
    folder_path, file_path = db_folderfile_path()
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            # print("Created 'DB files' folder.")
            logging.info("Created 'DB files' folder.")
        except Exception as e:
            # print("Error creating 'Saved data' folder:", e)
            logging.info("Error creating 'Saved data' folder: %s", e)
    return file_path