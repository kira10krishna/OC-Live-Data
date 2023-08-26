import os
import datetime
import logging
import asyncio

class PathManager:
    def __init__(self):
        self.backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Setup logging in the constructor
        self.setup_logging()

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

    async def create_xl_folder_path(self):
        xl_folder_path = os.path.join(self.savedData_folder_path(), f"Data for {datetime.date.today().strftime('%d-%b-%Y')}")
        try:
            if not os.path.exists(xl_folder_path):
                os.makedirs(xl_folder_path)
                logging.info("Created 'Saved data' folder.")
        except OSError as e:
            logging.error(f"Error creating 'Saved data' folder: {e}")

        return xl_folder_path

    def db_folderfile_path(self):
        folder_path = os.path.join(self.backend_dir, 'DB files')
        file_path = os.path.join(self.backend_dir, 'DB files', 'strike_prices.db')
        return folder_path, file_path

    async def create_db_folder_path(self):
        folder_path, file_path = self.db_folderfile_path()
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                logging.info("Created 'DB files' folder.")
        except OSError as e:
            logging.error(f"Error creating 'DB files' folder: {e}")

        return file_path

async def main():
    path_manager = PathManager()

    xl_folder_path = await path_manager.create_xl_folder_path()
    print(f"XL Folder Path: {xl_folder_path}")

    db_file_path = await path_manager.create_db_folder_path()
    print(f"DB File Path: {db_file_path}")

if __name__ == "__main__":
    asyncio.run(main())