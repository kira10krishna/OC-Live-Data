import os
import datetime
import logging

class PathManager:
    def __init__(self):
        self.backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def backend_path(self):
        return self.backend_dir

    def log_file_path(self):
        logfile_path = os.path.join(self.backend_dir, "python_Scripts", "script_log.txt")
        return logfile_path

    def setup_logging(self):
        file_path = self.log_file_path()
        logging.basicConfig(
            filename=file_path,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def savedData_folder_path(self):
        sd_folder_path = os.path.join(self.backend_dir, 'saved data')
        return sd_folder_path

    def create_xl_folder_path(self):
        xl_folder_path = os.path.join(self.savedData_folder_path(), f"Data for {datetime.date.today().strftime('%d-%b-%Y')}")
        if not os.path.exists(xl_folder_path):
            try:
                os.makedirs(xl_folder_path)
                logging.info("Created 'Saved data' folder.")
            except Exception as e:
                logging.info("Error creating 'Saved data' folder: %s", e)
        return xl_folder_path

    def db_folderfile_path(self):
        folder_path = os.path.join(self.backend_dir, 'DB files')
        file_path = os.path.join(self.backend_dir, 'DB files', 'strike_prices.db')
        return folder_path, file_path

    def create_db_folder_path(self):
        folder_path, file_path = self.db_folderfile_path()
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                logging.info("Created 'DB files' folder.")
            except Exception as e:
                logging.info("Error creating 'Saved data' folder: %s", e)
        return file_path